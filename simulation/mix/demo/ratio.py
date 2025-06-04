import os

def calculate_stats(file_path):
    """
    计算文本文件中每行第二个数值的统计信息
    
    参数:
        file_path (str): 输入文件路径
        
    返回:
        dict: 包含统计信息的字典
    """
    stats = {
        'total_lines': 0,
        'valid_lines': 0,
        'sum': 0.0,
        'average': None,
        'max': None,
        'min': None,
        'invalid_lines': []
    }
    
    try:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, 1):
                stats['total_lines'] += 1
                line = line.strip()
                
                if not line:
                    continue
                    
                parts = line.split()
                
                if len(parts) != 2:
                    stats['invalid_lines'].append(line_num)
                    continue
                
                try:
                    value = float(parts[1])
                    stats['valid_lines'] += 1
                    stats['sum'] += value
                    
                    # 更新最大值和最小值
                    if stats['max'] is None or value > stats['max']:
                        stats['max'] = value
                    if stats['min'] is None or value < stats['min']:
                        stats['min'] = value
                        
                except ValueError:
                    stats['invalid_lines'].append(line_num)
                    
        if stats['valid_lines'] == 0:
            raise ValueError("文件中没有有效数值数据")
            
        stats['average'] = stats['sum'] / stats['valid_lines']
        return stats
        
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")
    except PermissionError:
        raise PermissionError(f"没有权限读取文件: {file_path}")

if __name__ == "__main__":
    input_file = "/home/bo/High-Precision-Congestion-Control/result/Basic/ratio.txt"  # 替换为您的文件路径
    
    try:
        stats = calculate_stats(input_file)
        
        # 打印结果
        print(f"平均值:{stats['average']}", end=" ")
        print(f"最大值:{stats['max']}", end=" ")
        print(f"最小值:{stats['min']}")
        
    except Exception as e:
        print(f"错误: {str(e)}")