import pandas as pd
import matplotlib.pyplot as plt
from openpyxl.workbook import Workbook
import argparse

data = []
import re

# def parse_trace_file(file_path):
#     times = []
#     lenths = []
#     pattern = re.compile(r"time: (\d+)	lenth: (\d+)")
#     # Open the file and read line by line
#     with open(file_path, 'r') as file:
#         for line in file:
#             match = pattern.search(line)
#             if match:
#                 time,lenth = float(match.group(1)),float(match.group(2))
#                 times.append(time - 2000000000)
#                 lenths.append(lenth)
#     return times,lenths

def parse_trace_file(file_path,node_id):
    # pattern = re.compile(r"time:(\d+) node:0 port:1 queue:3 qlen:(\d+)")
    pattern = re.compile(rf"time:(\d+) node:{node_id} port:2 queue:3 qlen:(\d+)")
    times = []
    lenths = []
    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                times_ns = float(match.group(1))
                lenth = float(match.group(2))
                times.append(times_ns - 2000000000)
                lenths.append(lenth)
    return times,lenths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate and plot throughput from log file.")
    parser.add_argument('file_path', type=str, help="Path to the log file")
    parser.add_argument('out_path', type=str, help="Path to the output file")
    parser.add_argument('--node_id', type=int, default=2, help="Node to calculate throughput for (default: 2)")
    args = parser.parse_args()   
                  
    times,lenths = parse_trace_file(args.file_path, args.node_id)

    df = pd.DataFrame({'time':times, 'lenth':lenths})
    # Convert time from ns to us and queue length from B to KB
    df['time'] = df['time'] / 1000
    df['lenth'] = df['lenth'] / 1024
    
    # df.to_excel(output_file,index=False)

    # print(df)
    # Occupied shared buffer plot
    plt.figure(figsize=(10, 4))

    plt.plot(df['time'], df['lenth'], label='occupied shared buffer', color='red',linewidth=1.5)

    # Labels and title
    plt.title('(a) Variation of queue length (16:1 incast)')
    plt.xlabel('Time (us)')
    plt.ylabel('Queue Length (KB)')
    plt.legend()
    plt.grid(True)

    # Save the figure
    plt.savefig(args.out_path)

    # Show the plot
    # plt.show()
