import matplotlib.pyplot as plt
import numpy as np
import os

# 全局样式设置
plt.style.use('default')
plt.rcParams.update({
    'font.family': 'Arial',
    'axes.edgecolor': '#999999',
    'grid.color': '#EEEEEE',
    'axes.labelpad': 10
})

# 创建4:3比例图表
fig, ax = plt.subplots(figsize=(8, 6))

# 定义文件路径（请修改为实际路径）
Drop_folder = '/home/bo/High-Precision-Congestion-Control/result/motivation/Drop_fct.txt'
DCQCN_folder = '/home/bo/High-Precision-Congestion-Control/result/motivation/DCQCN_fct.txt'

# 从txt文件读取数据（格式：每行"x值 y值"）
def read_data_file(filename):
    x, y = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():  # 跳过空行
                parts = line.strip().split()
                x.append(float(parts[0]))
                y.append(float(parts[3]))
    print(f"========{filename}=========")
    print(np.array(x))
    print(np.array(y))
    return np.array(x), np.array(y)

# 读取数据（假设drop.txt是DSH数据，DCQCN.txt是SIH数据）
try:
    dsh_x, dsh_y = read_data_file('DCQCN_fct.txt')
    irn_x, irn_y = read_data_file('IRN_fct.txt')
    sih_x, sih_y = read_data_file('LTFC_fct.txt')
except FileNotFoundError as e:
    print(f"错误：未找到文件 {e.filename}")
    exit()
except ValueError:
    print("错误：数据格式不正确，请确保每行有2个数值")
    exit()


# 绘制折线（精确匹配参考图样式）
ax.plot(dsh_x, dsh_y, 'o-', color="#CC2512", markersize=15,
        linewidth=3, label='PFC',
        markerfacecolor='white', markeredgewidth=4)

ax.plot(irn_x, irn_y, '*-', color="#1B0569", markersize=15,
        linewidth=3, label='IRN',
        markerfacecolor='white', markeredgewidth=4)

ax.plot(sih_x, sih_y, 'X-', color="#1B5031", markersize=15,
        linewidth=3, label='LTFC',
        markerfacecolor='white', markeredgewidth=4)

# 坐标轴设置
ax.set_xlabel('# of Workers', fontsize=24, fontweight='bold')
ax.set_ylabel('tail FCT slowdown', fontsize=24, fontweight='bold')
ax.set_xlim(7, 25)
ax.set_ylim(5,50)

# 刻度设置
ax.set_xticks([8,12,16,20,24])
ax.set_yticks([10, 20, 30, 40,50])
ax.tick_params(axis='both', which='major', labelsize=22)

for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('#000000')  # 纯黑色边框
    spine.set_linewidth(2.5)    # 加粗边框（默认1.0）
    
# 网格线
ax.grid(True, linestyle='--', linewidth=1.5, alpha=0.8, color="#918E8E")

# 重点：增大图例框设置
legend = ax.legend(
    loc='upper left',
    frameon=False,  # 取消边框
    fontsize=26,    # 保持大字体
    handlelength=1.5,  # 缩短标记线
    handleheight=1,    # 降低标记高度
    borderpad=0.5,     # 最小内边距
    labelspacing=0.3,  # 最小标签间距
    handletextpad=0.5, # 最小标记与文本间距
    borderaxespad=0.5  # 最小图例与坐标轴间距
)

# 设置图例框线宽
legend.get_frame().set_linewidth(1.5)

# 四边坐标轴可见
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('#999999')

plt.tight_layout()
plt.savefig('basic_googlenet_tail.png')  # 将图像保存为'loss_curves.png'
plt.savefig("basic_googlenet_tail.svg", dpi=600,format="svg")
plt.show()