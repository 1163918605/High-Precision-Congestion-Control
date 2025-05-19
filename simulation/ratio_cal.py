# 提取 dropping package 百分数并计算其平均值、最大值和最小值
total_ratio = 0.0
count = 0
max_ratio = float('-inf')  # 初始化最大值为负无穷大
min_ratio = float('inf')   # 初始化最小值为正无穷大

# 读取 nohup.out 文件并提取特定行
with open('nohup.out', 'r') as infile, open('ratio.txt', 'w') as outfile:
    for line in infile:
        if "the ratio of dropping package:" in line:
            # 写入 ratio.txt
            outfile.write(line)

            # 提取百分数字符串
            parts = line.split(":")
            if len(parts) > 1:
                # 尝试获取后面的部分，并去掉多余的内容
                ratio_str = parts[1].strip().split()[0].rstrip('%')  # 取第一部分并去掉%
                print(ratio_str)
                try:
                    ratio_value = float(ratio_str)
                    total_ratio += ratio_value
                    count += 1
                    if ratio_value > max_ratio:  # 更新最大值
                        max_ratio = ratio_value
                    if ratio_value < min_ratio:  # 更新最小值
                        min_ratio = ratio_value
                except ValueError:
                    print(f"无法转换为浮点数: '{ratio_str}'")

# 计算并输出平均值、最大值和最小值
if count > 0:
    average_ratio = total_ratio / count
    print(f"平均 dropping package 百分比: {average_ratio:.2f}%")
    print(f"最大 dropping package 百分比: {max_ratio:.2f}%")
    print(f"最小 dropping package 百分比: {min_ratio:.2f}%")
else:
    print("没有找到有效的 dropping package 百分比。")
