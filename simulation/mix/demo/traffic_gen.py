import sys
import random
import math
import heapq
from optparse import OptionParser

class Flow:
    def __init__(self, src, dst, size, t):
        self.src, self.dst, self.size, self.t = src, dst, size, t
    def __str__(self):
        return "%d %d 3 100 %d %.9f" % (self.src, self.dst, self.size, self.t)

def translate_bandwidth(b):
    if b == None:
        return None
    if type(b) != str:
        return None
    if b[-1] == 'G':
        return float(b[:-1]) * 1e9
    if b[-1] == 'M':
        return float(b[:-1]) * 1e6
    if b[-1] == 'K':
        return float(b[:-1]) * 1e3
    return float(b)

def poisson(lam):
    return -math.log(1 - random.random()) * lam


# python3 traffic_gen.py -n 320 -l 0.3 -b 100G 

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--nhost", dest="nhost", help="number of hosts")
    parser.add_option("-l", "--load", dest="load", help="the percentage of the traffic load", default="0.3")
    parser.add_option("-b", "--bandwidth", dest="bandwidth", help="the bandwidth of host link (G/M/K)", default="100G")
    parser.add_option("-o", "--output", dest="output", help="the output file", default="incast_traffic.txt")
    options, args = parser.parse_args()

    if not options.nhost:
        print("please use -n to enter number of hosts")
        sys.exit(0)
    
    num_job = 10    
    nhost = int(options.nhost)
    load = float(options.load)
    bandwidth = translate_bandwidth(options.bandwidth)
    output = options.output

    if bandwidth == None:
        print("bandwidth format incorrect")
        sys.exit(0)

    t = 2  # Start time

    ofile = open(output, "w")
    ofile.write("%d\n" % (num_job * 8))

    # Generate incast traffic
    dst = random.randint(0, nhost - 1)  # Random destination
    flows = []
    
    for index in range(num_job):
        dst = random.randint(0, nhost - 1)
        inter_t = poisson(load) * 1e-5 # Use load for arrival time
        size = 1048576  # Random size based on CDF
        t = t + inter_t
        print(t)
        for i in range(8):
            while True:
                src = random.randint(0, nhost - 1)
                if src != dst:
                    break 
            flows.append(Flow(src, dst, size, t))

    for flow in flows:
        ofile.write(str(flow) + "\n")

    ofile.close()
    print(f"Generated {num_job} 8:1 incast flows.")
