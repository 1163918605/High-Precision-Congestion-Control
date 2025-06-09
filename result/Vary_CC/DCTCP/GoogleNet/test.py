import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体支持（若需中文标签）
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False

# 创建图表和坐标轴
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
ax.set_facecolor('white')  # 白色背景

# 模拟数据（替换为实际数据）
categories = ['overall:Avg', '<100KB:Avg', '<100KB:99th', '>1MB:Avg']
lossless = [8000, 150, 9000, 3000]  # 浅绿色
lossy = [5000, 120, 6000, 2000]     # 蓝色
r_pfc = [3000, 100, 4000, 1500]     # 红色条纹

# 柱形图参数设置
bar_width = 0.25
indices = np.arange(len(categories))

# 绘制柱形图
bar1 = ax.bar(indices - bar_width, lossless, bar_width, 
              color='#90EE90', edgecolor='black', label='Lossless')
bar2 = ax.bar(indices, lossy, bar_width, 
              color='#1E90FF', edgecolor='black', label='Lossy')
bar3 = ax.bar(indices + bar_width, r_pfc, bar_width, 
              color='white', edgecolor='red', hatch='//', 
              linewidth=1.5, label='R-PFC')  # 红色斜线

# 设置对数坐标轴
ax.set_yscale('log')
ax.set_ylim(100, 10000)
ax.set_yticks([100, 1000, 10000])
ax.set_yticklabels(['$10^2$', '$10^3$', '$10^4$'])
ax.set_ylabel('FCT (μs)', fontsize=12)

# 设置横坐标
ax.set_xticks(indices)
ax.set_xticklabels(categories, fontsize=10)
ax.tick_params(axis='x', length=0)  # 去掉x轴刻度线

# 设置网格线
ax.grid(True, axis='y', linestyle='--', alpha=0.7, which='both')

# 添加图例 (右上角)
legend = ax.legend(loc='upper right', frameon=True, framealpha=1)
legend.get_frame().set_edgecolor('black')  # 黑色边框
legend.get_frame().set_linewidth(0.8)

# 添加数据标签（可选）
# for bars in [bar1, bar2, bar3]:
#     for bar in bars:
#         height = bar.get_height()
#         ax.annotate(f'{height}',
#             xy=(bar.get_x() + bar.get_width() / 2, height),
#             xytext=(0, 3), textcoords="offset points",
#             ha='center', va='bottom', fontsize=8)

# 调整布局
plt.tight_layout()
plt.savefig('fct_comparison.png', bbox_inches='tight')
plt.show()