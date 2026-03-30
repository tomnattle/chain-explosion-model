import numpy as np
import matplotlib.pyplot as plt
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ============================================================
# 【发现层 · 验证D】干涉对比度随传播距离衰减（原创预言）
# 标准量子力学：干涉对比度不随距离衰减
# CE模型预言：干涉对比度随传播距离（屏幕位置）逐渐降低
# ============================================================
HEIGHT    = 301
WIDTH     = 800
A         = 1.0
S         = 0.25
B         = 0.04
LAM       = 0.95
SOURCE_X  = 10
SOURCE_Y  = HEIGHT // 2
BAR_X     = 180
SLIT1_Y   = HEIGHT//2 - 25
SLIT2_Y   = HEIGHT//2 + 25
SLIT_W    = 6
STEPS_PER_100PX = 150  # 每100像素对应150步传播

# 不同屏幕位置（距离双缝的距离）
screen_x_list = [300, 400, 500, 600, 700]
vis_list = []

print("=" * 70)
print("【发现层D】干涉对比度随传播距离衰减（CE模型原创预言）")
print("=" * 70)

# 初始化壁垒（双缝）
barrier = np.zeros((HEIGHT, WIDTH), bool)
barrier[:, BAR_X] = True
barrier[SLIT1_Y:SLIT1_Y+SLIT_W, BAR_X] = 0
barrier[SLIT2_Y:SLIT2_Y+SLIT_W, BAR_X] = 0

for screen_x in screen_x_list:
    # 计算对应传播步数
    steps = (screen_x - SOURCE_X) * STEPS_PER_100PX // 100
    # 初始化网格
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1200.0
    # 传播
    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, steps)
    # 读取屏幕信号
    screen = grid[:, screen_x]
    # 计算干涉对比度
    vis = compute_visibility(screen)
    vis_list.append(vis)
    print(f"屏幕位置 x={screen_x} | 距离双缝 L={screen_x-BAR_X} | 干涉对比度 V={vis:.4f}")

# ============================================================
# 绘图：干涉对比度 vs 传播距离
# ============================================================
distance_list = [x - BAR_X for x in screen_x_list]
plt.figure(figsize=(10, 6))
plt.plot(distance_list, vis_list, 'bo-', linewidth=2.5, markersize=8, label='CE Model Prediction')
plt.axhline(y=1.0, color='r', linestyle='--', label='Standard Quantum Mechanics (V=1.0)')
plt.title("Interference Visibility vs Propagation Distance\nCE Model Original Prediction", fontsize=14)
plt.xlabel("Distance from Double Slit (pixels)", fontsize=12)
plt.ylabel("Interference Visibility V", fontsize=12)
plt.legend(fontsize=12)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("verify_interference_decay.png", dpi=150)
print("\n图片已保存: verify_interference_decay.png")

# ============================================================
# 总结报告
# ============================================================
print("\n" + "=" * 70)
print("【发现层D 总结】")
print("=" * 70)
print("CE模型原创预言：干涉对比度随传播距离逐渐衰减")
print("标准量子力学预言：干涉对比度不随距离衰减（恒为1.0）")
print("-" * 70)
print("实验可检验性：可通过双缝干涉实验，测量不同距离屏幕的干涉对比度")
print("若实验观测到衰减，则CE模型被验证，量子力学基础理论需修正")
print("=" * 70)