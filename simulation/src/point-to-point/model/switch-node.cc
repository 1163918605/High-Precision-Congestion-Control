#include "ns3/ipv4.h"
#include <ns3/simulator.h>
#include "ns3/packet.h"
#include "ns3/ipv4-header.h"
#include "ns3/pause-header.h"
#include "ns3/flow-id-tag.h"
#include "ns3/boolean.h"
#include "ns3/uinteger.h"
#include "ns3/double.h"
#include "switch-node.h"
#include "qbb-net-device.h"
#include "ppp-header.h"
#include "ns3/int-header.h"
#include "ns3/log.h"
#include <cmath>

NS_LOG_COMPONENT_DEFINE("SwitchNode");
namespace ns3 {

TypeId SwitchNode::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::SwitchNode")
    .SetParent<Node> ()
    .AddConstructor<SwitchNode> ()
	.AddAttribute("EcnEnabled",
			"Enable ECN marking.",
			BooleanValue(false),
			MakeBooleanAccessor(&SwitchNode::m_ecnEnabled),
			MakeBooleanChecker())
	.AddAttribute("CcMode",
			"CC mode.",
			UintegerValue(0),
			MakeUintegerAccessor(&SwitchNode::m_ccMode),
			MakeUintegerChecker<uint32_t>())
	.AddAttribute("AckHighPrio",
			"Set high priority for ACK/NACK or not",
			UintegerValue(0),
			MakeUintegerAccessor(&SwitchNode::m_ackHighPrio),
			MakeUintegerChecker<uint32_t>())
	.AddAttribute("MaxRtt",
			"Max Rtt of the network",
			UintegerValue(9000),
			MakeUintegerAccessor(&SwitchNode::m_maxRtt),
			MakeUintegerChecker<uint32_t>())
	.AddAttribute("PFCEnabled",
			"Enable PFC pause",
			BooleanValue(false),
			MakeBooleanAccessor(&SwitchNode::m_pfcEnabled),
			MakeBooleanChecker())
	.AddAttribute("LRFCEnabled",
			"Enable loss-tolerant flow control",
			BooleanValue(false),
			MakeBooleanAccessor(&SwitchNode::m_lrfcEnabled),
			MakeBooleanChecker())
	.AddAttribute("NodeId",
			"The node id of this rdma driver",
			UintegerValue(1000),
			MakeUintegerAccessor(&SwitchNode::node_id),
			MakeUintegerChecker<uint32_t>())
  ;
  return tid;
}

SwitchNode::SwitchNode(){
	m_ecmpSeed = m_id;
	m_node_type = 1;
	m_mmu = CreateObject<SwitchMmu>();
	for (uint32_t i = 0; i < pCnt; i++)
		for (uint32_t j = 0; j < pCnt; j++)
			for (uint32_t k = 0; k < qCnt; k++)
				m_bytes[i][j][k] = 0;
	for (uint32_t i = 0; i < pCnt; i++)
		m_txBytes[i] = 0;
	for (uint32_t i = 0; i < pCnt; i++)
		m_lastPktSize[i] = m_lastPktTs[i] = 0;
	for (uint32_t i = 0; i < pCnt; i++)
		m_u[i] = 0;

	// Simulator::Schedule(NanoSeconds(5e3),&SwitchNode::CleanupFlowTable, this);
	// Simulator::Schedule(NanoSeconds(5e3),&SwitchNode::PeriodicBufferUpdate, this);

}

//get the index of device,,ECMP routing selection
int SwitchNode::GetOutDev(Ptr<const Packet> p, CustomHeader &ch){
	// look up entries
	auto entry = m_rtTable.find(ch.dip);

	// no matching entry
	if (entry == m_rtTable.end())
		return -1;

	// entry found
	auto &nexthops = entry->second;

	// pick one next hop based on hash
	union {
		uint8_t u8[4+4+2+2];
		uint32_t u32[3];
	} buf;
	buf.u32[0] = ch.sip;
	buf.u32[1] = ch.dip;
	if (ch.l3Prot == 0x6)
		buf.u32[2] = ch.tcp.sport | ((uint32_t)ch.tcp.dport << 16);
	else if (ch.l3Prot == 0x11)
		buf.u32[2] = ch.udp.sport | ((uint32_t)ch.udp.dport << 16);
	else if (ch.l3Prot == 0xFC || ch.l3Prot == 0xFD)
		buf.u32[2] = ch.ack.sport | ((uint32_t)ch.ack.dport << 16);

	uint32_t idx = EcmpHash(buf.u8, 12, m_ecmpSeed) % nexthops.size();
	return nexthops[idx];
}

//PFC logic
void SwitchNode::CheckAndSendPfc(uint32_t inDev, uint32_t qIndex){
	Ptr<QbbNetDevice> device = DynamicCast<QbbNetDevice>(m_devices[inDev]);
	if (m_mmu->CheckShouldPause(inDev, qIndex)){
		device->SendPfc(3, 0);
		std::cout <<"Send PFC num:"<< Pfc_num <<"||switch node id - " << node_id <<  "||to node id - " << inDev -1 <<"\n";
		// m_mmu->PrintPortBuffer(inDev);
		Pfc_num ++;
		m_mmu->SetPause(inDev, 3);
	}
}
void SwitchNode::CheckAndSendResume(uint32_t inDev, uint32_t qIndex){
	Ptr<QbbNetDevice> device = DynamicCast<QbbNetDevice>(m_devices[inDev]);
	if (m_mmu->CheckShouldResume(inDev, qIndex)){
		device->SendPfc(3, 1);
		m_mmu->SetResume(inDev, 3);
		std::cout <<"Send Resume PFC num to node id - " << inDev -1 << "|| port status:" << m_mmu->paused[inDev][3] << "\n";
		// m_mmu->PrintPortBuffer(inDev);
	}
}

void SwitchNode::PeriodicBufferUpdate(){

	if (!m_flowTable.empty()) {
        UpdateQueueBuffers();  // 流表非空时执行更新
    } else {
        std::cout << "node id :" << node_id << " || Flow table is empty, so need not buffer update: " << Simulator::Now() << "\n";
    }
}

void SwitchNode::UpdateQueueBuffers(){
	uint32_t total_flows = m_flowTable.size();
	uint32_t exceed_flows = 0;

	for (auto &it : m_flowTable){
		auto &flow = it.second;
		if(flow.loss_ratio >= flow.loss_threshold){
			exceed_flows++;
		}
	}
	double exceed_ratio = (double)exceed_flows / total_flows;
	// std::cout << "exceed flow:" << exceed_flows << "||total size: " << total_flows <<  "||exceed ratio:" << exceed_ratio << "\n";
	m_mmu->UpdateBuffers(exceed_ratio);
}

void SwitchNode::CleanupFlowTable(){
	if (!m_lrfcEnabled){
		return;
	}

	if(!m_flowTable.empty()){
		// std::cout << "flow table size:" << m_flowTable.size() << "\n";
		uint64_t now = Simulator::Now().GetTimeStep();
		const uint64_t timeout = 10e9;
		auto it = m_flowTable.begin();
		while (it != m_flowTable.end())
		{	
			if(now - it->second.last_update > timeout){
				it = m_flowTable.erase(it);
				std::cout << "node id :" << node_id << "|| flow table decline one "<< "\n";
			} else{
				++it;
			}
		}
	}else{
		std::cout << "node id :" << node_id << " ||flow table is empty\n";
	}

	static int flow_emptyCount = 0;
    if (m_flowTable.empty()) {
        if (++flow_emptyCount > 3) {  // 连续10次空流表
            std::cout << "node id :" << node_id << "|| Persistent empty flow table, stopping updates \n";
            return;  // 不再调度
        }
    } else {
        flow_emptyCount = 0;  // 重置计数器
    }

	Simulator::Schedule(NanoSeconds(5e3), &SwitchNode::PeriodicBufferUpdate, this);
	Simulator::Schedule(NanoSeconds(5e3),&SwitchNode::CleanupFlowTable, this);
}

uint32_t SwitchNode::GetFlowHash(const CustomHeader &ch){
	return EcmpHash(reinterpret_cast<const uint8_t*>(&ch.sip), 12, m_ecmpSeed);
}

//send package to destination
void SwitchNode::SendToDev(Ptr<Packet>p, CustomHeader &ch){
	int idx = GetOutDev(p, ch);
	if (idx >= 0){
		NS_ASSERT_MSG(m_devices[idx]->IsLinkUp(), "The routing table look up should return link that is up");

		// determine the qIndex
		uint32_t qIndex;
		if (ch.l3Prot == 0xFF || ch.l3Prot == 0xFE || (m_ackHighPrio && (ch.l3Prot == 0xFD || ch.l3Prot == 0xFC))){  //QCN or PFC or NACK, go highest priority
			qIndex = 0;
		}else{
			// std :: cout << "m_ackHighPrio:" << m_ackHighPrio << "\n";
			// if (ch.l3Prot != 0x11)
			// 	std :: cout << "ch.l3Prot:" << ch.l3Prot << "\n";

			if(m_lrfcEnabled && ch.l3Prot == 0x11){ //UDP
				uint32_t flowHash = GetFlowHash(ch);
				auto it = m_flowTable.find(flowHash);
				if(it == m_flowTable.end()){
					FlowEntry flow;
					flow.loss_count = 0;
					flow.total_size = 6625;
					flow.loss_ratio = 0.0;
					flow.loss_threshold = 0.19; // default
					flow.last_update = Simulator::Now().GetTimeStep();
					m_flowTable[flowHash] = flow;

					std::cout << "node id :" << node_id << "============flow table size:" << m_flowTable.size() << "\n";
					for (const auto& entry : m_flowTable) {
						std::cout << "FlowHash: 0x" << std::hex << entry.first 
									<< "|| LossCount: " << std::dec << entry.second.loss_count
									<< "||  TotalSize: " << entry.second.total_size
									<< "||  LossRatio: " << entry.second.loss_ratio
									<< "||  Threshold: " << entry.second.loss_threshold
									<< "||  LastUpdate: " << entry.second.last_update << "ns\n";
;
					}
					std::cout << "=============over==============\n";

				}
				auto &flow = m_flowTable[flowHash];
				flow.loss_ratio = flow.loss_count / (double)flow.total_size;
				bool use_lossless = flow.loss_ratio >= flow.loss_threshold;
				qIndex = use_lossless ? LOSSLESSS_QUEUE +  ch.udp.pg : LOSSY_QUEUE +  ch.udp.pg;
				// std::cout << "flo:" << flowHash << "||seq:" << ch.udp.seq << "\n";
				if(flowHash == 2633235723)
					std::cout << "[switch-node] flowHash:" << flowHash <<"||seq:" << ch.udp.seq <<"|| qindex : " << qIndex << "||loss count:" << flow.loss_count << " ||loss ratio:" << flow.loss_ratio << "|| loss threshold:" << flow.loss_threshold << "\n";
			}else{
				qIndex = (ch.l3Prot == 0x06 ? 1 : ch.udp.pg); // if TCP, put to queue 1
			}
		}
		// admission control
		FlowIdTag t;
		p->PeekPacketTag(t);
		uint32_t inDev = t.GetFlowId();// the index of packet src interface

		// if(inDev == 7){
		// 	m_mmu->PrintPortBuffer(inDev);
		// }
		
		if (m_lrfcEnabled && qIndex < 4){ //not highest priority
			if (!m_mmu->CheckShouldPause(inDev, qIndex)){			// Admission control
				m_mmu->UpdateIngressAdmission(inDev, qIndex, p->GetSize());
				m_mmu->UpdateEgressAdmission(idx, qIndex, p->GetSize());
			}else{
					//calculate five-multi group
					uint32_t flowHash = GetFlowHash(ch);
					auto &flow = m_flowTable[flowHash];
					flow.loss_count ++;
					flow.last_update = Simulator::Now().GetTimeStep();

					if (inDev == 5){
						drop_num++;
						std::cout << "node 4 || drop num:" << drop_num << "||Indev"<< inDev << "\n";
					}

					return; // Drop
				}
		}else if(qIndex != 0){
			if (m_mmu->CheckIngressAdmission(inDev, qIndex, p->GetSize()) && m_mmu->CheckEgressAdmission(idx, qIndex, p->GetSize())){			// Admission control
				m_mmu->UpdateIngressAdmission(inDev, qIndex, p->GetSize());
				m_mmu->UpdateEgressAdmission(idx, qIndex, p->GetSize());
			}else{
				// if(inDev == 5){
				// 	drop_num++;
				// 	std::cout << "node 4 || drop num:" << drop_num << "||Indev"<< inDev << "\n";
				// }
				std::cout << "fffffffffffffffff qindex drop \n";
				return; // Drop
			}
			CheckAndSendPfc(inDev, qIndex);
		}
		m_bytes[inDev][idx][qIndex] += p->GetSize();
		m_devices[idx]->SwitchSend(qIndex, p, ch);
	}else
		return; // Drop
}

uint32_t SwitchNode::EcmpHash(const uint8_t* key, size_t len, uint32_t seed) {
  uint32_t h = seed;
  if (len > 3) {
    const uint32_t* key_x4 = (const uint32_t*) key;
    size_t i = len >> 2;
    do {
      uint32_t k = *key_x4++;
      k *= 0xcc9e2d51;
      k = (k << 15) | (k >> 17);
      k *= 0x1b873593;
      h ^= k;
      h = (h << 13) | (h >> 19);
      h += (h << 2) + 0xe6546b64;
    } while (--i);
    key = (const uint8_t*) key_x4;
  }
  if (len & 3) {
    size_t i = len & 3;
    uint32_t k = 0;
    key = &key[i - 1];
    do {
      k <<= 8;
      k |= *key--;
    } while (--i);
    k *= 0xcc9e2d51;
    k = (k << 15) | (k >> 17);
    k *= 0x1b873593;
    h ^= k;
  }
  h ^= len;
  h ^= h >> 16;
  h *= 0x85ebca6b;
  h ^= h >> 13;
  h *= 0xc2b2ae35;
  h ^= h >> 16;
  return h;
}

void SwitchNode::SetEcmpSeed(uint32_t seed){
	m_ecmpSeed = seed;
}

void SwitchNode::AddTableEntry(Ipv4Address &dstAddr, uint32_t intf_idx){
	uint32_t dip = dstAddr.Get();
	m_rtTable[dip].push_back(intf_idx);
}

void SwitchNode::ClearTable(){
	m_rtTable.clear();
}

// This function can only be called in switch mode
// process packets received from network devices
bool SwitchNode::SwitchReceiveFromDevice(Ptr<NetDevice> device, Ptr<Packet> packet, CustomHeader &ch){
	SendToDev(packet, ch);
	return true;
}

//the logic of package dequeue from switch
void SwitchNode::SwitchNotifyDequeue(uint32_t ifIndex, uint32_t qIndex, Ptr<Packet> p){
	FlowIdTag t;
	//flow id
	p->PeekPacketTag(t);
	if (qIndex != 0){
		uint32_t inDev = t.GetFlowId();
		m_mmu->RemoveFromIngressAdmission(inDev, qIndex, p->GetSize());
		m_mmu->RemoveFromEgressAdmission(ifIndex, qIndex, p->GetSize());
		m_bytes[inDev][ifIndex][qIndex] -= p->GetSize();

		//set ecn config
		if (m_ecnEnabled){
			bool egressCongested = m_mmu->ShouldSendCN(ifIndex, qIndex);
			if (egressCongested){
				PppHeader ppp;
				Ipv4Header h;
				p->RemoveHeader(ppp);
				p->RemoveHeader(h);
				h.SetEcn((Ipv4Header::EcnType)0x03);
				p->AddHeader(h);
				p->AddHeader(ppp);
			}
		}
		//CheckAndSendPfc(inDev, qIndex);
		CheckAndSendResume(inDev, qIndex);
	}
	if (1){
		uint8_t* buf = p->GetBuffer();
		if (buf[PppHeader::GetStaticSize() + 9] == 0x11){ // udp packet
			IntHeader *ih = (IntHeader*)&buf[PppHeader::GetStaticSize() + 20 + 8 + 6]; // ppp, ip, udp, SeqTs, INT
			Ptr<QbbNetDevice> dev = DynamicCast<QbbNetDevice>(m_devices[ifIndex]);
			if (m_ccMode == 3){ // HPCC
				ih->PushHop(Simulator::Now().GetTimeStep(), m_txBytes[ifIndex], dev->GetQueue()->GetNBytesTotal(), dev->GetDataRate().GetBitRate());
			}else if (m_ccMode == 10){ // HPCC-PINT
				uint64_t t = Simulator::Now().GetTimeStep();
				uint64_t dt = t - m_lastPktTs[ifIndex];
				if (dt > m_maxRtt)
					dt = m_maxRtt;
				uint64_t B = dev->GetDataRate().GetBitRate() / 8; //Bps
				uint64_t qlen = dev->GetQueue()->GetNBytesTotal();
				double newU;

				/**************************
				 * approximate calc
				 *************************/
				int b = 20, m = 16, l = 20; // see log2apprx's paremeters
				int sft = logres_shift(b,l);
				double fct = 1<<sft; // (multiplication factor corresponding to sft)
				double log_T = log2(m_maxRtt)*fct; // log2(T)*fct
				double log_B = log2(B)*fct; // log2(B)*fct
				double log_1e9 = log2(1e9)*fct; // log2(1e9)*fct
				double qterm = 0;
				double byteTerm = 0;
				double uTerm = 0;
				if ((qlen >> 8) > 0){
					int log_dt = log2apprx(dt, b, m, l); // ~log2(dt)*fct
					int log_qlen = log2apprx(qlen >> 8, b, m, l); // ~log2(qlen / 256)*fct
					qterm = pow(2, (
								log_dt + log_qlen + log_1e9 - log_B - 2*log_T
								)/fct
							) * 256;
					// 2^((log2(dt)*fct+log2(qlen/256)*fct+log2(1e9)*fct-log2(B)*fct-2*log2(T)*fct)/fct)*256 ~= dt*qlen*1e9/(B*T^2)
				}
				if (m_lastPktSize[ifIndex] > 0){
					int byte = m_lastPktSize[ifIndex];
					int log_byte = log2apprx(byte, b, m, l);
					byteTerm = pow(2, (
								log_byte + log_1e9 - log_B - log_T
								)/fct
							);
					// 2^((log2(byte)*fct+log2(1e9)*fct-log2(B)*fct-log2(T)*fct)/fct) ~= byte*1e9 / (B*T)
				}
				if (m_maxRtt > dt && m_u[ifIndex] > 0){
					int log_T_dt = log2apprx(m_maxRtt - dt, b, m, l); // ~log2(T-dt)*fct
					int log_u = log2apprx(int(round(m_u[ifIndex] * 8192)), b, m, l); // ~log2(u*512)*fct
					uTerm = pow(2, (
								log_T_dt + log_u - log_T
								)/fct
							) / 8192;
					// 2^((log2(T-dt)*fct+log2(u*512)*fct-log2(T)*fct)/fct)/512 = (T-dt)*u/T
				}
				newU = qterm+byteTerm+uTerm;

				#if 0
				/**************************
				 * accurate calc
				 *************************/
				double weight_ewma = double(dt) / m_maxRtt;
				double u;
				if (m_lastPktSize[ifIndex] == 0)
					u = 0;
				else{
					double txRate = m_lastPktSize[ifIndex] / double(dt); // B/ns
					u = (qlen / m_maxRtt + txRate) * 1e9 / B;
				}
				newU = m_u[ifIndex] * (1 - weight_ewma) + u * weight_ewma;
				printf(" %lf\n", newU);
				#endif

				/************************
				 * update PINT header
				 ***********************/
				uint16_t power = Pint::encode_u(newU);
				if (power > ih->GetPower())
					ih->SetPower(power);

				m_u[ifIndex] = newU;
			}
		}
	}
	m_txBytes[ifIndex] += p->GetSize();
	m_lastPktSize[ifIndex] = p->GetSize();
	m_lastPktTs[ifIndex] = Simulator::Now().GetTimeStep();
}

int SwitchNode::logres_shift(int b, int l){
	static int data[] = {0,0,1,2,2,3,3,3,3,4,4,4,4,4,4,4,4,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5};
	return l - data[b];
}

int SwitchNode::log2apprx(int x, int b, int m, int l){
	int x0 = x;
	int msb = int(log2(x)) + 1;
	if (msb > m){
		x = (x >> (msb - m) << (msb - m));
		#if 0
		x += + (1 << (msb - m - 1));
		#else
		int mask = (1 << (msb-m)) - 1;
		if ((x0 & mask) > (rand() & mask))
			x += 1<<(msb-m);
		#endif
	}
	return int(log2(x) * (1<<logres_shift(b, l)));
}

} /* namespace ns3 */
