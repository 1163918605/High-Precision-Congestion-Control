#include <unistd.h>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <unordered_map>
#include <unordered_set>
#include "sim-setting.h"
#include "trace-format.h"
#include "trace_filter.hpp"
#include "utils.hpp"

using namespace ns3;
using namespace std;

int main(int argc, char** argv) {
  if (argc != 2 && argc != 3) {
    printf("Usage: ./trace_reader <trace_file> [filter_expr]\n");
    return 0;
  }
  FILE* file = fopen(argv[1], "r");
  TraceFilter f;
  if (argc == 3) {
    f.parse(argv[2]);
    if (f.root == NULL) {
      printf("Invalid filter\n");
      return 0;
    }
  }
  // printf("filter: %s\n", f.str().c_str());

  // first read SimSetting
  SimSetting sim_setting;
  sim_setting.Deserialize(file);
#if 0
	// print sim_setting
	for (auto i : sim_setting.port_speed)
		for (auto j : i.second)
			printf("%u,%u:%lu\n", i.first, j.first, j.second);
#endif
  // Get current time
  time_t now = time(0);
  tm* ltm = localtime(&now);
  // creat file name
  char filename[100];
  sprintf(
      filename,
      "/home/bo/High-Precision-Congestion-Control/analysis/demo/trace.txt",
      1900 + ltm->tm_year,
      1 + ltm->tm_mon,
      ltm->tm_mday,
      ltm->tm_hour,
      ltm->tm_min,
      ltm->tm_sec);
  // creat file
  FILE* outfile = fopen(filename, "w");
  if (outfile == NULL) {
    printf("Error opening output file\n");
    return 1; // Return an error code
  }
  // read trace
  TraceFormat tr;
  while (tr.Deserialize(file) > 0) {
    if (!f.test(tr))
      continue;
    print_trace(tr);
    fprintf(outfile, "%s\n", tr.format_trace_as_string().c_str());
  }
  fclose(outfile);
}
