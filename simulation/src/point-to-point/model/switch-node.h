#ifndef SWITCH_NODE_H
#define SWITCH_NODE_H

#include <unordered_map>
#include <ns3/node.h>
#include "qbb-net-device.h"
#include "switch-mmu.h"
#include "pint.h"

namespace ns3 {

class Packet;

class SwitchNode : public Node{
	static const uint32_t pCnt = 257;	// Number of ports used
	static const uint32_t qCnt = 8;	// Number of queues/priorities used
	uint32_t m_ecmpSeed;
	std::unordered_map<uint32_t, std::vector<int> > m_rtTable; // map from ip address (u32) to possible ECMP port (index of dev)
	std::unordered_map<uint32_t, double> m_drop_ratio; // map from drop ratio to 
	std::unordered_map<uint32_t, double> m_drop_num; // map from drop ratio to 
	std::unordered_map<uint32_t, uint64_t> m_last_pausetime; // map from drop ratio to 

	// monitor of PFC
	uint16_t Pfc_num = 1;
	uint16_t drop_num = 0;
	uint32_t m_bytes[pCnt][pCnt][qCnt]; // m_bytes[inDev][outDev][qidx] is the bytes from inDev enqueued for outDev at qidx
	uint64_t m_txBytes[pCnt]; // counter of tx bytes
	uint32_t node_id;
	uint32_t m_lastPktSize[pCnt];
	uint64_t m_lastPktTs[pCnt]; // ns
	double m_u[pCnt];
	bool m_lrfcEnabled;
	uint32_t total_flow_count; // node id

	struct FlowEntry
	{
		uint32_t loss_count;
		uint32_t total_size;
		double loss_ratio;
		double loss_threshold;
		uint64_t last_update;
		uint32_t inDev;
	};
	std::unordered_map<uint32_t, FlowEntry> m_flowTable;
	enum QueueType{
		LOSSY_QUEUE = 0,
		LOSSLESSS_QUEUE = 4
	};

protected:
	bool m_ecnEnabled;
	bool m_pfcEnabled;
	uint32_t m_ccMode;
	uint64_t m_maxRtt;

	uint32_t m_ackHighPrio; // set high priority for ACK/NACK

private:
	int GetOutDev(Ptr<const Packet>, CustomHeader &ch);
	void SendToDev(Ptr<Packet>p, CustomHeader &ch);
	static uint32_t EcmpHash(const uint8_t* key, size_t len, uint32_t seed);
	void CheckAndSendPfc(uint32_t inDev, uint32_t qIndex);
	void CheckAndSendResume(uint32_t inDev, uint32_t qIndex);
	uint32_t GetFlowHash(const CustomHeader &ch);
    void CleanupFlowTable();
	void PeriodicBufferUpdate();
	void UpdateQueueBuffers(); 

public:
	Ptr<SwitchMmu> m_mmu;

	static uint64_t GetQpKey(uint32_t dip, uint16_t sport, uint16_t pg); // get the lookup key for m_qpMap
	Ptr<RdmaQueuePair> GetQp(uint32_t dip, uint16_t sport, uint16_t pg); // get the qp
	std::unordered_map<uint64_t, Ptr<RdmaQueuePair> > m_qpMap; // mapping from uint64_t to qp
	
	static TypeId GetTypeId (void);
	SwitchNode();
	void SetEcmpSeed(uint32_t seed);
	void AddTableEntry(Ipv4Address &dstAddr, uint32_t intf_idx);
	void ClearTable();
	bool SwitchReceiveFromDevice(Ptr<NetDevice> device, Ptr<Packet> packet, CustomHeader &ch);
	void SwitchNotifyDequeue(uint32_t ifIndex, uint32_t qIndex, Ptr<Packet> p);

	// for approximate calc in PINT
	int logres_shift(int b, int l);
	int log2apprx(int x, int b, int m, int l); // given x of at most b bits, use most significant m bits of x, calc the result in l bits
};

} /* namespace ns3 */

#endif /* SWITCH_NODE_H */
