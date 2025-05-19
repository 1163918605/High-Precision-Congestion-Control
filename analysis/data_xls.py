import re
import pandas as pd

def parse_log_file(file_path):
    # Regular expression pattern to extract time and queue length
    pattern_queue = re.compile(
        r"(?P<Time_ns>\d+)\s+"          # Timestamp
        r"(n:16)\s+"           # Node number
        r"(2:3)\s+" # Port and Queue number
        r"(?P<QueueLength_B>\d+)\s+"    # Queue length in Bytes
        r"(Enqu)\s+"           # Enqueue or Dequeue
        r"ecn:(?P<ECN>\d+)\s+"          # ECN value
        # The rest of the line is ignored for now as it's not included in the example dictionary
    )
    pattern_throughput = re.compile(r"Time: (\d+)ns, Node: 3, .*? Size: (\d+)B")
    
    # Lists to hold the extracted time and queue length values
    times_queue = []
    queue_lengths = []
    times_throughput = []
    throughputs = []
    
    with open(file_path, 'r') as file:
        for line in file:
            match_queue = pattern_queue.search(line)
            match_throughput = pattern_throughput.search(line)
            if match_queue:
                # Extracted values are in nanoseconds and bytes, convert them to seconds and integer
               
                time_ns, queue_len_b = int(match_queue.group(1)), float(match_queue.group(4))
                
                times_queue.append(time_ns)  # Convert nanoseconds to seconds
                queue_lengths.append(queue_len_b/1000)
                print(queue_lengths)
            # elif match_throughput:
            #     time_ns, size_bytes = map(int, match_throughput.groups())
            #     times_throughput.append(time_ns)
            #     throughputs.append(size_bytes*8 / 1e9)  # Convert bytes to Gbps
    
    return times_queue, queue_lengths, times_throughput, throughputs

def save_to_excel(file_path, node_id, window_size_ns, output_file1, output_file2):
    # Initialize variables
    total_bytes = 0
    windows = []
    times_w = []
    current_window_start = None

    # Compile the regex pattern to match lines with Node 0 data
    pattern = re.compile(
        r"(?P<Time_ns>\d+)\s+"          # Timestamp
        r"n:(?P<Node>\d+)\s+"           # Node number
        r"(?P<Port>\d+):(?P<Queue>\d+)\s+" # Port and Queue number
        r"(?P<QueueLength_B>\d+)\s+"    # Queue length in Bytes
        r"(?P<EnqDeq>\w+)\s+"           # Enqueue or Dequeue
        r"ecn:(?P<ECN>\d+)\s+"          # ECN value
        # The rest of the line is ignored for now as it's not included in the example dictionary
    )
    

    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                time_ns, size_bytes = map(int, match.groups())
                # Check if we are still in the current window
                if current_window_start is None:
                    current_window_start = time_ns
                
                if time_ns < current_window_start + window_size_ns:
                    # We're in the same window, accumulate bytes
                    total_bytes += size_bytes
                else:
                    # We've moved to the next window, save the previous window's data
                    windows.append(total_bytes*8 / (window_size_ns ))  # Convert ns to us and bytes to throughput
                    times_w.append(time_ns)
                    # Reset for the new window
                    while time_ns >= current_window_start + window_size_ns:
                        current_window_start += window_size_ns
                    total_bytes = size_bytes  # Start counting the new window with the size of the current packet
    
    # Add the last window's data
    if total_bytes > 0:
        windows.append(total_bytes*8 / (window_size_ns ))
        times_w.append(time_ns)

    # Read data from log file
    times_queue, queue_lengths, times_throughput, throughputs = parse_log_file(file_path)

    # Create DataFrames for each set of data
    df1 = pd.DataFrame({'Window': windows, 'Time_w': times_w})
    df2 = pd.DataFrame({'Time': times_queue, 'Queue Length (KB)': queue_lengths})

    # Save DataFrames to Excel files
    # df1.to_excel(output_file1, index=False)
    df2.to_excel(output_file2, index=False)

# Parameters
file_path = '/home/bo/High-Precision-Congestion-Control/analysis/trace/incast.txt'  # Path to the log file
node_id = 16  # Node to calculate throughput for
window_size_ns = 2500   # Window size of 10ns in nanoseconds
output_file1 = '/home/bo/High-Precision-Congestion-Control/analysis/queue/tracethroughput2.xlsx'  # First output Excel file path
output_file2 = '/home/bo/High-Precision-Congestion-Control/analysis/queue/qlen2.xlsx'  # Second output Excel file path

# Call the function to save data to Excel
times_queue, queue_lengths, times_throughput, throughputs = parse_log_file(file_path)
print(times_queue[22])
print(queue_lengths[22])
df2 = pd.DataFrame({'Time': times_queue, 'Queue Length (KB)': queue_lengths})
# df2.to_excel(output_file2, index=False)
# save_to_excel(file_path, node_id, window_size_ns, output_file1, output_file2)
