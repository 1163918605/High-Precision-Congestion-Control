import sys

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
        
    filename = sys.argv[1]  # 替换为你的文件名
    average_value, average_slowdown, last_fct = calculate_average(filename)
    
    if average_value is not None:
        print(f"avg: {average_value} μs", end=" ")
        print(f"avg: {average_slowdown} μs", end=" ")
        print(f"tail: {last_fct} μs")
    else:
        print("No valid data found.")
