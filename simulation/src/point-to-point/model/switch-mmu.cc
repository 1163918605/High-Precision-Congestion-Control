#include <iostream>
#include <fstream>
#include "ns3/packet.h"
#include "ns3/simulator.h"
#include "ns3/object-vector.h"
#include "ns3/uinteger.h"
#include "ns3/log.h"
#include "ns3/assert.h"
#include "ns3/global-value.h"
#include "ns3/boolean.h"
#include "ns3/simulator.h"
#include "ns3/random-variable.h"
#include "switch-mmu.h"

NS_LOG_COMPONENT_DEFINE("SwitchMmu");
namespace ns3 {
	TypeId SwitchMmu::GetTypeId(void){
		static TypeId tid = TypeId("ns3::SwitchMmu")
			.SetParent<Object>()
			.AddConstructor<SwitchMmu>()
			.AddAttribute("LRFCEnabled",
				"Enable loss-tolerant flow control",
				BooleanValue(true),
				MakeBooleanAccessor(&SwitchMmu::m_lrfcEnabled),
				MakeBooleanChecker())
	  ;
		return tid;
	}

	SwitchMmu::SwitchMmu(void){
		buffer_size = 12 * 1024 * 1024;
		reserve = 4 * 1024;
		resume_offset = 3 * 1024;

		// headroom
		shared_used_bytes = 0;
		memset(hdrm_bytes, 0, sizeof(hdrm_bytes));
		memset(ingress_bytes, 0, sizeof(ingress_bytes));
		memset(paused, 0, sizeof(paused));
		memset(egress_bytes, 0, sizeof(egress_bytes));
	}

	void SwitchMmu::UpdateBuffers(double exceed_ratio){
		// std::cout << "exceed ratio:" << exceed_ratio << "\n";
		alpha = 1 - exceed_ratio;
	}

	bool SwitchMmu::CheckIngressAdmission(uint32_t port, uint32_t qIndex, uint32_t psize){
		if (psize + hdrm_bytes[port][qIndex] > headroom[port] && psize + GetSharedUsed(port, qIndex) > GetPfcThreshold(port,qIndex)){
			// for (uint32_t i = 1; i < 64; i++)
			// 	printf("(%u,%u)", hdrm_bytes[i][3], ingress_bytes[i][3]);
			//  printf("\n");
			return false;
		}
		return true;
	}

	bool SwitchMmu::CheckEgressAdmission(uint32_t port, uint32_t qIndex, uint32_t psize){
		return true;
	}
	//update the status of ingress queue
	void SwitchMmu::UpdateIngressAdmission(uint32_t port, uint32_t qIndex, uint32_t psize){
		uint32_t new_bytes = ingress_bytes[port][qIndex] + psize;
		if (new_bytes <= reserve){
			ingress_bytes[port][qIndex] += psize;
		}else {
			uint32_t thresh = GetPfcThreshold(port,qIndex);
			if (new_bytes - reserve > thresh){
				hdrm_bytes[port][qIndex] += psize;
			}else {
				ingress_bytes[port][qIndex] += psize;
				shared_used_bytes += std::min(psize, new_bytes - reserve);
			}
		}
	}

	void SwitchMmu::PrintPortBuffer(uint32_t port){
		std::cout<< "========================= \n";
		// for (int i = 3 ; i < 20 ; i++){
		// 	std::cout << "Port" << i-1 << "Status 3:" << paused[i][3] << "||Port Status 7:" << paused[i][7] << "\n";
		// 	std::cout << "[q-3]node_id:" << i -1 << "|| get shared  buffer:" << GetSharedUsed(i, 3)/1024 <<"KB||PFC threshold: " << GetPfcThreshold(i,3)/1024 << "KB|| total ingress_bytes:" << ingress_bytes[i][3]/1024 << "KB" << "|| hdrm_bytes:" << hdrm_bytes[i][3]/1024 << "kB\n";
		// 	std::cout << "[q-7]node_id:" << i -1 << "|| get shared  buffer:" << GetSharedUsed(i, 7)/1024 <<"KB||PFC threshold: " << GetPfcThreshold(i,7)/1024 << "KB|| total ingress_bytes:" << ingress_bytes[i][7]/1024 << "KB" << "|| hdrm_bytes:" << hdrm_bytes[i][7]/1024 << "kB\n";
		// }
			std::cout << "Port" << port << "Status 3:" << paused[port][3] << "||Port Status 7:" << paused[port][7] << "\n";
			std::cout << "[q-3]node_id:" << port << "|| get shared  buffer:" << GetSharedUsed(port, 3)/1024 <<"KB||PFC threshold: " << GetPfcThreshold(port,3)/1024 << "KB|| total ingress_bytes:" << ingress_bytes[port][3]/1024 << "KB" << "|| hdrm_bytes:" << hdrm_bytes[port][3]/1024 << "kB\n";
			std::cout << "[q-7]node_id:" << port << "|| get shared  buffer:" << GetSharedUsed(port, 7)/1024 <<"KB||PFC threshold: " << GetPfcThreshold(port,7)/1024 << "KB|| total ingress_bytes:" << ingress_bytes[port][7]/1024 << "KB" << "|| hdrm_bytes:" << hdrm_bytes[port][7]/1024 << "kB\n";
		std::cout<< "========================= \n";
	}

	void SwitchMmu::UpdateEgressAdmission(uint32_t port, uint32_t qIndex, uint32_t psize){
		egress_bytes[port][qIndex] += psize;
	}
	void SwitchMmu::RemoveFromIngressAdmission(uint32_t port, uint32_t qIndex, uint32_t psize){
		uint32_t from_hdrm = std::min(hdrm_bytes[port][qIndex], psize);
		uint32_t from_shared = std::min(psize - from_hdrm, ingress_bytes[port][qIndex] > reserve ? ingress_bytes[port][qIndex] - reserve : 0);
		hdrm_bytes[port][qIndex] -= from_hdrm;
		ingress_bytes[port][qIndex] -= psize - from_hdrm;
		shared_used_bytes -= from_shared;
	}
	void SwitchMmu::RemoveFromEgressAdmission(uint32_t port, uint32_t qIndex, uint32_t psize){
		egress_bytes[port][qIndex] -= psize;
	}
	bool SwitchMmu::CheckShouldPause(uint32_t port, uint32_t qIndex){
		return !paused[port][qIndex] && (hdrm_bytes[port][qIndex] > 0 || GetSharedUsed(port, qIndex) >= GetPfcThreshold(port,qIndex));
	}

	bool SwitchMmu::CheckShouldResume(uint32_t port, uint32_t qIndex){
		if(m_lrfcEnabled){
			if (!paused[port][3])
				return false;
		}else{
			if (!paused[port][qIndex])
				return false;
		}
		uint32_t shared_used = GetSharedUsed(port, qIndex);
		std::cout << qIndex << "||headroom" << hdrm_bytes[port][qIndex] << "||shared:" << shared_used/1024 << "||pfc: " << GetPfcThreshold(port,qIndex)/1024  <<"\n";
		return hdrm_bytes[port][qIndex] == 0 && (shared_used == 0 || shared_used + resume_offset <= GetPfcThreshold(port,qIndex));
	}

	void SwitchMmu::SetPause(uint32_t port, uint32_t qIndex){
		std::cout << "alpha:" << alpha << "||qindex = 7 : " << std::min(1.0/alpha , 2.0) << "||qindex = 3 : " << std::max(alpha , 0.5) << "\n";
		paused[port][qIndex] = true;
	}
	void SwitchMmu::SetResume(uint32_t port, uint32_t qIndex){
		paused[port][qIndex] = false;
	}

	uint32_t SwitchMmu::GetPfcThreshold(uint32_t port, uint32_t qIndex){
		// std::cout << "alpha" << alpha << "||qindex = 7" << std::min(1.0/alpha , 2.0) << "||qindex = 3" << std::max(alpha , 0.5) << "\n";
		if (qIndex == 7){
			// return ((buffer_size - total_hdrm - total_rsrv - shared_used_bytes) >> 3 )* std::min(1.0/alpha , 2.0);
			return ((buffer_size - total_hdrm - total_rsrv - shared_used_bytes) >> 3 );
		}else{
			// return ((buffer_size - total_hdrm - total_rsrv - shared_used_bytes) >> 3) * std::max(alpha , 0.5);
			return ((buffer_size - total_hdrm - total_rsrv - shared_used_bytes) >> 3 );
		}
	}
	uint32_t SwitchMmu::GetSharedUsed(uint32_t port, uint32_t qIndex){
			uint32_t used = ingress_bytes[port][qIndex];
			return used > reserve ? used - reserve : 0;
		}
	bool SwitchMmu::ShouldSendCN(uint32_t ifindex, uint32_t qIndex){
		if (qIndex == 0)
			return false;
		if (egress_bytes[ifindex][qIndex] > kmax[ifindex])
			return true;
		if (egress_bytes[ifindex][qIndex] > kmin[ifindex]){
			double p = pmax[ifindex] * double(egress_bytes[ifindex][qIndex] - kmin[ifindex]) / (kmax[ifindex] - kmin[ifindex]);
			if (UniformVariable(0, 1).GetValue() < p)
				return true;
		}
		return false;
	}
	void SwitchMmu::ConfigEcn(uint32_t port, uint32_t _kmin, uint32_t _kmax, double _pmax){
		kmin[port] = _kmin * 1000;
		kmax[port] = _kmax * 1000;
		pmax[port] = _pmax;
	}
	void SwitchMmu::ConfigHdrm(uint32_t port, uint32_t size){
		headroom[port] = size;
	}
	void SwitchMmu::ConfigNPort(uint32_t n_port){
		total_hdrm = 0;
		total_rsrv = 0;
		for (uint32_t i = 1; i <= n_port; i++){
			total_hdrm += headroom[i];
			total_rsrv += reserve;
		}
		std::cout << "======buffer config=======" << "\n";
		std::cout << "total_buffer:" << buffer_size << "KB\n";
		std::cout << "total_hdrm:" << total_hdrm/1024 << "KB\n";
		std::cout << "total_rsrv:" << total_rsrv/1024 << "KB\n";
		std::cout << "shared_buffer:" << (buffer_size- total_hdrm - total_rsrv)/1024 << "KB\n";
		std::cout << "n_port:" << n_port << "\n";
	}
	void SwitchMmu::ConfigBufferSize(uint32_t size){
		buffer_size = size;
	}
}
