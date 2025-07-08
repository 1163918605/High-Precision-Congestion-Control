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

# 创建图表 - 增加高度以容纳上方图例
fig, ax = plt.subplots(figsize=(8, 6.5))  # 增加高度为7.0

# 从txt文件读取数据
def read_data_file(filename):
    x, y1, y2 = [], [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():  # 跳过空行
                parts = line.strip().split()
                x.append(float(parts[0]))
                y1.append(float(parts[1]))  # 柱状图数据
                y2.append(float(parts[2]))   # 折线图数据
    return np.array(x), np.array(y1), np.array(y2)

# 读取数据
try:
    dsh_x, dsh_y, dsh_line = read_data_file('DropResNet.txt')
    irn_x, irn_y, irn_line = read_data_file('Drop.txt')
except FileNotFoundError as e:
    print(f"错误：未找到文件 {e.filename}")
    exit()
except ValueError:
    print("错误：数据格式不正确，请确保每行有3个数值")
    exit()

# 确保所有x值相同
assert np.array_equal(dsh_x, irn_x), "X值必须相同"

# 设置柱形图的宽度、位置和样式
bar_width = 0.8  # 加宽柱子
x_positions = np.arange(len(dsh_x)) * 2.2  # 柱组间距

# 定义柱子样式 - 精确匹配图片效果
bar_styles = [
    {'color': "#CC2512", 'hatch': '////', 'label': 'ResNet50 (avg)'},  # 红色斜纹
    {'color': "#B0C4DE", 'hatch': 'xxxx', 'label': 'GoogleNet (avg)'},  # 深蓝色实心
]

# 绘制柱形图
bars1 = ax.bar(x_positions - bar_width/2, dsh_y, width=bar_width,
       color=bar_styles[0]['color'],
       hatch=bar_styles[0]['hatch'],
       edgecolor='black',
       linewidth=1.5,
       label=bar_styles[0]['label'])

bars2 = ax.bar(x_positions + bar_width/2, irn_y, width=bar_width,
       color=bar_styles[1]['color'],
       hatch=bar_styles[1]['hatch'],
       edgecolor='black',
       linewidth=1.5,
       label=bar_styles[1]['label'])

# 创建第二个y轴用于折线图
ax2 = ax.twinx()

# 绘制折线图
line1, = ax2.plot(x_positions, dsh_line, color='#2E8B57', marker='o', 
                 markersize=10, linewidth=3, linestyle='-', label='PFC (line)')
line2, = ax2.plot(x_positions, irn_line, color='#8A2BE2', marker='s', 
                 markersize=10, linewidth=3, linestyle='--', label='IRN (line)')

# 设置第二个y轴的范围和刻度
ax2.set_ylim(0, 16)
ax2.set_yticks([0,4,8,12,16])
ax2.tick_params(axis='y', labelsize=22)

# 坐标轴设置
ax.set_xlabel('# of Workers', fontsize=24, fontweight='bold')
ax.set_ylabel('Loss Ratio(%)', fontsize=24, fontweight='bold')
# ax2.set_ylabel('Additional Metric', fontsize=24, fontweight='bold')
ax.set_xlim(-1, len(dsh_x)*2.2 - 1.2)
ax.set_ylim(0, 16)  # 精确匹配图片的纵轴范围

# 设置x轴刻度位置和标签
ax.set_xticks(x_positions)
ax.set_xticklabels(dsh_x.astype(int), fontsize=22)

# Y轴刻度设置 - 匹配图片刻度
ax.set_yticks([0,4,8,12,16])
ax.tick_params(axis='y', labelsize=22)

# 边框设置 - 显示上边框
ax.spines['top'].set_visible(True)
for spine in ax.spines.values():
    spine.set_color('#000000')
    spine.set_linewidth(2.5)

# 网格线 - 仅显示水平网格线
ax.grid(True, linestyle='--', linewidth=1.2, alpha=0.8, color="#918E8E", axis='y')
# ax.axhline(y=10, color='red', linestyle='--', linewidth=2, alpha=0.9)
# 合并图例
lines = [bars1, bars2, line1, line2]
labels = [bar_styles[0]['label'], bar_styles[1]['label'], 'ResNet50 (max)', 'GoogleNet (max)']
legend = ax.legend(
    lines, labels,
    loc='upper center',            # 定位基准点为上方中心
    bbox_to_anchor=(0.5, 1.4),     # x=0.5表示居中, y=1.2表示在图表区域上方
    ncol=2,                        # 改为2列布局
    frameon=False,                 # 无边框
    fontsize=24,                   # 字体大小
    handleheight=1,              # 图例项高度
    handlelength=1,              # 图例项长度
    columnspacing=1,             # 列间距
    handletextpad=0.5,             # 图标与文本间距
    borderpad=1               # 内部边距
)

# 精确调整图表布局 - 增加顶部空间
plt.subplots_adjust(top=0.6)  # 为图例留出足够空间

# 添加标题空间以确保不遮挡
fig.tight_layout(rect=[0, 0, 1, 0.98])  # 图表区域占整体高度的92%

plt.savefig('basic_drop.png', dpi=300)
plt.savefig("basic_drop.svg", dpi=600, format="svg")
plt.show()