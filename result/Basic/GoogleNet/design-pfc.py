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
                y.append(float(parts[1]))
    print(np.array(x))
    print(np.array(y))
    return np.array(x), np.array(y)

# 读取数据（假设drop.txt是DSH数据，DCQCN.txt是SIH数据）
try:
    dsh_x, dsh_y = read_data_file('PFC-design.txt')
    sih_x, sih_y = read_data_file('PFC-LTFC.txt')
    sxx_x, sxx_y = read_data_file('PFC-incast.txt')
except FileNotFoundError as e:
    print(f"错误：未找到文件 {e.filename}")
    exit()
except ValueError:
    print("错误：数据格式不正确，请确保每行有2个数值")
    exit()

# 绘制折线（精确匹配参考图样式）

ax.plot(sxx_x, sxx_y, '*-', color="#251774", markersize=15,
        linewidth=3, label='PFC with DT',
        markerfacecolor='white', markeredgewidth=4,
        zorder=3)  # 增加zorder使折线在顶层

ax.plot(dsh_x, dsh_y, 'o-', color="#CC2512", markersize=15,
        linewidth=3, label='LTFC with DT',
        markerfacecolor='white', markeredgewidth=4,
        zorder=3)  # 增加zorder使折线在顶层

ax.plot(sih_x, sih_y, 'X-', color="#1B5031", markersize=15,
        linewidth=3, label='LTFC with LABM',
        markerfacecolor='white', markeredgewidth=4,
        zorder=3)  # 增加zorder使折线在顶层

# 坐标轴设置
ax.set_xlabel('# of Workers', fontsize=28, fontweight='bold')
ax.set_ylabel('PFC Count', fontsize=28, fontweight='bold')
ax.set_xlim(7, 25)
ax.set_ylim(0,3000)

# 刻度设置
ax.set_xticks([8,12,16,20,24])
ax.set_yticks([0, 500, 1000, 1500, 2000, 2500, 3000])
ax.tick_params(axis='both', which='major', labelsize=28)

# 网格线（确保在最底层）
ax.grid(True, linestyle='--', linewidth=1.5, alpha=0.8, color="#918E8E", zorder=0)

# 坐标轴边框设置（中间层）
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('#000000')
    spine.set_linewidth(3)
    spine.set_zorder(1)  # 将坐标轴放到中间层

# 图例设置
legend = ax.legend(
    loc='upper left',
    frameon=False,
    fontsize=26,
    handlelength=1.5,
    handleheight=1,
    borderpad=0.5,
    labelspacing=0.3,
    handletextpad=0.5,
    borderaxespad=0.5
)

plt.tight_layout()
plt.savefig('design-pfc.png')
plt.savefig("design-pfc.svg", dpi=600, format="svg")
plt.show()