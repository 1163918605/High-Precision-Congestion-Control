import sys
import argparse

def calculate_average(filename):
    total = 0
    count = 0
    slowdown = 0
    max_fct = 0
    
    with open(filename, 'r') as file:
        for line in file:
            columns = line.split()  # 按空格分隔列
            if len(columns) >= 7:  # 确保有第七列
                if(float(columns[6]) > max_fct):
                    max_fct = float(columns[6])
                total += float(columns[6])  # 累加第七列的值
                slowdown += float(columns[6])/float(columns[7])
                count += 1  # 计数

    if count == 0:
        return None  # 如果没有有效数据，返回None
    average = total / count / 1000  # 计算平均值
    return average, slowdown, max_fct/1000

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python script.py <filename>")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description="Calculate and plot throughput from log file.")    
    parser.add_argument('file_path', type=str, help="Path to the log file")
    parser.add_argument('-i', type=int, default=2, help="Node to calculate throughput for (default: 2)")
    parser.add_argument('-o', '--outfile', type=str, default="/home/bo/High-Precision-Congestion-Control/result/motivation/Drop_fct.txt",
                       help="Path to the output file (default: /home/bo/High-Precision-Congestion-Control/result/motivation/Drop_fct.txt)")
    args = parser.parse_args() 
     
    filename = args.file_path  # 使用解析的参数而不是直接访问sys.argv
    average_value, average_slowdown, last_fct = calculate_average(filename)
    
    with open(args.outfile, 'a') as out_file:
        out_file.write(f"{args.i} {average_value}\n")
    
    if average_value is not None:
        print(f"avg: {average_value} μs", end=" ")
        print(f"avg: {average_slowdown} μs", end=" ")
        print(f"tail: {last_fct} μs")
    else:
        print("No valid data found.")