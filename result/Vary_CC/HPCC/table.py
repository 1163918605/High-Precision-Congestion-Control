import re

def find_max_flow_table_size(filename):
    max_size = 0
    pattern = re.compile(r'flow table size:(\d+)')
    
    with open(filename, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                size = int(match.group(1))
                if size > max_size:
                    max_size = size
                    
    return max_size

# 使用示例
filename = 'ltfc.log'  # 替换为你的txt文件路径
max_size = find_max_flow_table_size(filename)
print(f"最大的flow table size值是: {max_size}")