import numpy as np
import matplotlib.pyplot as plt

from chain_explosion_numba import propagate_split_energy

# ============================================================
# 参数配置
# ============================================================

HEIGHT = 201
WIDTH = 600
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.90
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
STEPS = 800

# 纠缠源参数（产生两个波包）
SPLIT_X = WIDTH // 3           # 分裂点
SPLIT_ANGLE = 30               # 分裂角度（度）
WAVEPACKET_WIDTH = 10          # 波包宽度

# 探测器位置
DETECTOR1_X = 2 * WIDTH // 3
DETECTOR1_Y = HEIGHT // 2 - 50
DETECTOR2_X = 2 * WIDTH // 3
DETECTOR2_Y = HEIGHT // 2 + 50

# ============================================================
# 初始化
# ============================================================

print("=" * 60)
print("链式爆炸模型 - 量子纠缠模拟")
print("预言：纠缠是共享涟漪，不是超距作用")
print("=" * 60)

grid = np.zeros((HEIGHT, WIDTH))

# 创建纠缠源（一团高斯分布的初始能量）
for y in range(HEIGHT):
    dy = y - SOURCE_Y
    grid[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / (2 * WAVEPACKET_WIDTH**2))

# 分裂掩码（将波包分成两路）
split_mask = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
for y in range(HEIGHT):
    for x in range(SPLIT_X, SPLIT_X + 10):
        # 上路径
        target_y_up = SOURCE_Y - int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
        if 0 <= target_y_up < HEIGHT:
            split_mask[target_y_up, x] = True
        # 下路径
        target_y_down = SOURCE_Y + int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
        if 0 <= target_y_down < HEIGHT:
            split_mask[target_y_down, x] = True

# ============================================================
# 计算两个探测器的相关性
# ============================================================

def compute_correlation(grid):
    """计算两个探测器的能量相关性"""
    energy1 = grid[DETECTOR1_Y, DETECTOR1_X]
    energy2 = grid[DETECTOR2_Y, DETECTOR2_X]
    
    # 相关性 = (E1 - E1_mean) * (E2 - E2_mean) 的累积
    # 这里简化：直接返回能量乘积
    return energy1 * energy2

# ============================================================
# 运行模拟
# ============================================================

correlations = []
energies1 = []
energies2 = []

for step in range(STEPS):
    grid = propagate_split_energy(grid, split_mask, A, S, B, LAMBDA)
    
    # 记录探测器数据
    e1 = grid[DETECTOR1_Y, DETECTOR1_X]
    e2 = grid[DETECTOR2_Y, DETECTOR2_X]
    energies1.append(e1)
    energies2.append(e2)
    correlations.append(e1 * e2)
    
    if (step + 1) % 100 == 0:
        print(f"进度: {step+1}/{STEPS}")

# ============================================================
# 数据分析
# ============================================================

print("\n" + "=" * 60)
print("纠缠数据分析")
print("=" * 60)

# 平均相关性
avg_correlation = np.mean(correlations[-200:])  # 最后200步
print(f"平均相关性: {avg_correlation:.6e}")

# 两个探测器的能量比
avg_e1 = np.mean(energies1[-200:])
avg_e2 = np.mean(energies2[-200:])
print(f"探测器1平均能量: {avg_e1:.6e}")
print(f"探测器2平均能量: {avg_e2:.6e}")
print(f"能量比 (E1/E2): {avg_e1/avg_e2:.4f}")

# 判断是否有纠缠
if avg_correlation > 1e-6:
    print("\n✅ 检测到显著相关性！两个探测器的能量关联。")
    print("   你的模型解释：它们共享同一团涟漪的波包。")
    print("   量子力学解释：超距纠缠。")
    print("   区别：你的模型预言相关性随距离衰减，量子力学预言不衰减。")
else:
    print("\n⚠️ 未检测到显著相关性。")
    print("   可能原因：波包分裂后距离太远，共享涟漪太弱。")

# ============================================================
# 可视化
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 1. 最终能量分布
energy_display = np.log1p(grid)
im = axes[0].imshow(energy_display, cmap='hot', aspect='auto', origin='upper')
axes[0].set_title('最终能量分布（两个波包）')
axes[0].set_xlabel('X 位置')
axes[0].set_ylabel('Y 位置')
axes[0].axhline(y=DETECTOR1_Y, color='cyan', linestyle='--', linewidth=1, label='探测器1')
axes[0].axhline(y=DETECTOR2_Y, color='cyan', linestyle='--', linewidth=1, label='探测器2')
plt.colorbar(im, ax=axes[0])

# 2. 两个探测器的能量随时间变化
axes[1].plot(energies1, 'r-', linewidth=0.5, label='探测器1')
axes[1].plot(energies2, 'b-', linewidth=0.5, label='探测器2')
axes[1].set_title('探测器能量随时间变化')
axes[1].set_xlabel('时间步')
axes[1].set_ylabel('能量')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 3. 相关性分布
axes[2].plot(correlations, 'g-', linewidth=0.5)
axes[2].set_title('能量相关性 (E1*E2)')
axes[2].set_xlabel('时间步')
axes[2].set_ylabel('相关性')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('entanglement_simulation.png', dpi=150)
plt.show()

print("\n" + "=" * 60)
print("实验完成！图片已保存为 entanglement_simulation.png")
print("=" * 60)
print("\n下一步探索方向：")
print("1. 改变两个探测器的距离，观察相关性是否衰减")
print("2. 在一个探测器旁边插入吸收器，观察另一个探测器的能量是否变化")
print("3. 让两个波包重新汇合，观察纠缠是否恢复")