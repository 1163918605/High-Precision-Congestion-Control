def calculate_average(filename):
    total = 0
    count = 0
    
    with open(filename, 'r') as file:
        for line in file:
            columns = line.split()  # 按空格分隔列
            if len(columns) >= 7:  # 确保有第七列
                total += float(columns[6])  # 累加第七列的值
                count += 1  # 计数

    if count == 0:
        return None  # 如果没有有效数据，返回None
    average = total / count  # 计算平均值
    return average

if __name__ == "__main__":
    filename = 'fct.txt'  # 替换为你的文件名
    average_value = calculate_average(filename)
    
    if average_value is not None:
        print(f"The average of the seventh column is: {average_value} ns")
    else:
        print("No valid data found.")
