import re
import matplotlib.pyplot as plt
import pandas as pd
import argparse

# Function to calculate throughput for Node 0 in 10us windows and plot the result
def plot_throughput(file_path, node_id, window_size_ns, out_file):
    # Initialize variables
    total_bytes = 0.0
    windows = []
    times_w = []
    current_window_start = None

    # Compile the regex pattern to match lines with Node 0 data
    # 2000000167 n:0 1:3 0 Dequ ecn:0 0b000001 0b000101 10000 100 U 1000 0 3 1048(1000)
    # Recv/Enqu
    pattern = re.compile(r"time:(\d+) node:2.*?event:Dequ.*?size:(\d+)")

    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                time_ns = float(match.group(1))
                size_bytes = float(match.group(2))
                # Check if we are still in the current window
                if current_window_start is None:
                    current_window_start = time_ns
                
                if time_ns < current_window_start + window_size_ns:
                    # We're in the same window, accumulate bytes
                    total_bytes += size_bytes
                else:
                    # We've moved to the next window, save the previous window's data
                    windows.append(total_bytes * 8 / (window_size_ns ) * 1000000000 / (1024 * 1024 * 1024)) 
                    times_w.append((current_window_start + 0.5 * window_size_ns - 2000000000) / 1000)
                    # Reset for the new window
                    while time_ns >= current_window_start + window_size_ns:
                        current_window_start += window_size_ns
                    total_bytes = size_bytes  # Start counting the new window with the size of the current packet
    
    # Add the last window's data
    if total_bytes > 0:
        windows.append(total_bytes * 8 / (window_size_ns ) * 1000000000 / (1024 * 1024 * 1024))
        # windows.append(total_bytes * 8 / (window_size_ns ))
        times_w.append((current_window_start + 0.5 * window_size_ns - 2000000000) / 1000)
    # Plotting
    # times, queue_lengths = parse_log_file(file_path)
    # print(windows)
    # print(times_w)
    plt.figure(figsize=(10, 6))
    plt.plot(times_w, windows, marker='', markersize=4, linestyle='-', linewidth=2)

    # 设置图表标题和标签
    plt.title('Bandwidth Over Time')
    plt.xlabel('Time (μs)')
    plt.ylabel('Bandwidth (Gbps)')
    # plt.ylim(0, 120)
    # plt.yticks(range(0, 121, 20))
    # 显示网格
    plt.grid(True)

    # 显示图表
    plt.show()
    plt.savefig(out_file)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate and plot throughput from log file.")
    parser.add_argument('file_path', type=str, help="Path to the log file")
    parser.add_argument('out_path', type=str, help="Path to the output file")
    parser.add_argument('--node_id', type=int, default=2, help="Node to calculate throughput for (default: 2)")
    parser.add_argument('--window_size_ns', type=int, default=2000, help="Window size in nanoseconds (default: 2000ns)")
    
    # file_path = '/home/bo/High-Precision-Congestion-Control/analysis/demo/trace_HPCC.txt'  # Path to the log file
    args = parser.parse_args()
    plot_throughput(args.file_path, args.node_id, args.window_size_ns, args.out_path)