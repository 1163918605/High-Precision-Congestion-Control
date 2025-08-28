import matplotlib.pyplot as plt
import numpy as np

# 全局样式设置 - 增强可读性和视觉一致性
plt.style.use('default')
plt.rcParams.update({
    'font.family': 'Arial',
    'axes.edgecolor': '#000000',  # 改为纯黑边框
    'grid.color': '#CCCCCC',      # 加深网格线增强对比度
    'axes.labelpad': 12,
    'mathtext.default': 'regular'
})

# 创建图表
fig, ax = plt.subplots(figsize=(8, 6.5))

# 从txt文件读取数据
def read_data_file(filename):
    x, y = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():  # 跳过空行
                parts = line.strip().split()
                x.append(float(parts[0]))
                y.append(float(parts[1]))
    return np.array(x), np.array(y)

# 读取数据
try:
    dsh_x, dsh_y = read_data_file('table.txt')
    # irn_x, irn_y = read_data_file('IRN_fct.txt')
    # sih_x, sih_y = read_data_file('LTFC_fct.txt')
except FileNotFoundError as e:
    print(f"错误：未找到文件 {e.filename}")
    exit()
except ValueError:
    print("错误：数据格式不正确，请确保每行有2个数值")
    exit()

# 确保所有x值相同
# assert np.array_equal(dsh_x, irn_x) and np.array_equal(dsh_x, sih_x), "X值必须相同"

# 设置柱形图的宽度、位置和样式
bar_width = 0.6
x_positions = np.arange(len(dsh_x)) * 2.2  # 柱组间距

# 定义柱子样式
bar_styles = [
    {'color': "#5F9EA0", 'hatch': '....', 'label': 'LTFC'}, 
    {'color': "#CC2512", 'hatch': '////', 'label': 'PFC'},
    {'color': "#B0C4DE", 'hatch': 'xxxx', 'label': 'IRN'},
]

# 绘制柱形图
# ax.bar(x_positions - bar_width, sih_y, width=bar_width,
#        color=bar_styles[0]['color'],
#        hatch=bar_styles[0]['hatch'],
#        edgecolor='black',
#        linewidth=1.5,
#        label=bar_styles[0]['label'])

ax.bar(x_positions, dsh_y, width=bar_width,
       color=bar_styles[1]['color'],
       hatch=bar_styles[1]['hatch'],
       edgecolor='black',
       linewidth=1.5,
       label=bar_styles[1]['label'])

# ax.bar(x_positions + bar_width, irn_y, width=bar_width,
#        color=bar_styles[2]['color'],
#        hatch=bar_styles[2]['hatch'],
#        edgecolor='black',
#        linewidth=1.5,
#        label=bar_styles[2]['label'])

# ================== 主要修改部分 ==================
# 修改坐标轴标签和刻度格式
ax.set_xlabel('# of Workers', fontsize=28, fontweight='bold')
ax.set_ylabel('PFC Count', fontsize=28, fontweight='bold')
ax.set_xlim(1, 11)
ax.set_ylim(0,2500)

# 刻度设置
ax.set_xticks([2,4,6,8,10])
ax.set_yticks([0, 500, 1000, 1500, 2000, 2500])
ax.tick_params(axis='y', labelsize=22)

# 边框设置
ax.spines['top'].set_visible(True)
for spine in ax.spines.values():
    spine.set_color('#000000')
    spine.set_linewidth(2.5)

# 网格线设置
ax.grid(True, linestyle='--', linewidth=1.2, alpha=0.8, color="#918E8E", axis='y')

# 图例设置
legend = ax.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.2),
    ncol=3,
    frameon=False,
    fontsize=22,
    handleheight=1,
    handlelength=1,
    columnspacing=3,
    handletextpad=1,
    borderpad=1
)

# 调整布局
plt.subplots_adjust(top=0.7)
fig.tight_layout(rect=[0, 0, 1, 0.98])

plt.savefig('table.png', dpi=300)
plt.savefig("table.svg", dpi=600, format="svg")
plt.show()