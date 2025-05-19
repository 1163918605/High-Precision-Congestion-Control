#ifndef TRACE_FORMAT_H
#define TRACE_FORMAT_H
#include <arpa/inet.h>
#include <netinet/in.h>
#include <stddef.h>
#include <stdint.h>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <sstream>
#include <string>
#include <vector>
namespace ns3 {

enum Event { Recv = 0, Enqu = 1, Dequ = 2, Drop = 3 };

struct TraceFormat {
  uint64_t time;
  uint16_t node;
  uint8_t intf, qidx;
  uint32_t qlen;
  uint32_t sip, dip;
  uint16_t size;
  uint8_t l3Prot;
  uint8_t event;
  uint8_t ecn; // this is the ip ECN bits
  uint8_t nodeType; // 0: host, 1: switch
  union {
    struct {
      uint16_t sport, dport;
      uint32_t seq;
      uint64_t ts;
      uint16_t pg;
      uint16_t payload; // this does not include SeqTsHeader's size, diff from
                        // udp's payload size.
    } data;
    struct {
      uint16_t fid;
      uint8_t qIndex;
      uint8_t ecnBits; // this is the ECN bits in the CNP
      union {
        struct {
          uint16_t qfb;
          uint16_t total;
        };
        uint32_t seq;
      };
    } cnp;
    struct {
      uint16_t sport, dport;
      uint16_t flags;
      uint16_t pg;
      uint32_t seq;
      uint64_t ts;
    } ack;
    struct {
      uint32_t time;
      uint32_t qlen;
      uint8_t qIndex;
    } pfc;
    struct {
      uint16_t sport, dport;
    } qp;
  };

  void Serialize(FILE* file) {
    fwrite(this, sizeof(TraceFormat), 1, file);
  }
  int Deserialize(FILE* file) {
    int ret = fread(this, sizeof(TraceFormat), 1, file);
    return ret;
  }
  std::string format_trace_as_string() {
    std::stringstream ss;
    char src_ip[INET_ADDRSTRLEN], dest_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(this->sip), src_ip, INET_ADDRSTRLEN);
    inet_ntop(AF_INET, &(this->dip), dest_ip, INET_ADDRSTRLEN);

    ss << "Time: " << this->time << "ns, ";
    ss << "Node: " << this->node << ", ";
    ss << "Intf: " << unsigned(this->intf) << ", ";
    ss << "Queue Idx: " << unsigned(this->qidx) << ", ";
    ss << "Queue Len: " << this->qlen << "B, ";
    ss << "Event: ";
    switch (this->event) {
      case Recv:
        ss << "Recv";
        break;
      case Enqu:
        ss << "Enqu";
        break;
      case Dequ:
        ss << "Dequ";
        break;
      case Drop:
        ss << "Drop";
        break;
      default:
        ss << "????";
        break;
    }
    ss << ", ";
    ss << "ECN: " << unsigned(this->ecn) << ", ";
    ss << "Src IP: " << src_ip << ":" << ntohs(this->data.sport) << ", ";
    ss << "Dest IP: " << dest_ip << ":" << ntohs(this->data.dport) << ", ";
    ss << "Type: "; 
    // << unsigned(this->l3Prot) << ", ";
    switch (unsigned(this->l3Prot))
    {
    case 17:
      ss<< "U";
      break;
    case 252:
      ss<< "A";
      break;
    case 253:
      ss<< "N";
      break;
    case 254:
      ss<< "P";
      break;
    case 255:
      ss<< "C";
      break;
    case 0:
      ss<< "Q";
      break;
    default:
      ss<< "???";
      break;
    }
    ss << "Size: " << this->size << "B, ";
    ss << "Seq: " << ntohl(this->data.seq) << ", ";
    ss << "Timestamp: " << this->data.ts << ", ";
    ss << "PG: " << ntohs(this->data.pg) << ", ";
    ss << "Payload: " << ntohs(this->data.payload) << "B";

    return ss.str();
  }
};

static inline const char* EventToStr(enum Event e) {
  switch (e) {
    case Recv:
      return "Recv";
    case Enqu:
      return "Enqu";
    case Dequ:
      return "Dequ";
    case Drop:
      return "Drop";
    default:
      return "????";
  }
}

} // namespace ns3
#endif
