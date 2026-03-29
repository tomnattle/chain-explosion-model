import numpy as np
import matplotlib.pyplot as plt

from chain_explosion_numba import propagate_split_phase

# ============================================================
# 参数配置
# ============================================================

HEIGHT = 201
WIDTH = 800
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.95          # 衰减更慢，让光传更远
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
STEPS = 1200

# 纠缠源参数
SPLIT_X = WIDTH // 4
SPLIT_ANGLE = 20        # 分裂角度

# 探测器位置（拉远距离，测试衰减）
DETECTOR1_X = 3 * WIDTH // 4
DETECTOR1_Y = SOURCE_Y - 80
DETECTOR2_X = 3 * WIDTH // 4
DETECTOR2_Y = SOURCE_Y + 80

# ============================================================
# 初始化：能量 + 相位
# ============================================================

print("=" * 60)
print("链式爆炸模型 - 量子纠缠模拟（加入相位）")
print("预言：相位同步不随距离衰减，能量随距离衰减")
print("=" * 60)

# 能量网格
energy_grid = np.zeros((HEIGHT, WIDTH))
# 相位网格（-π 到 π）
phase_grid = np.zeros((HEIGHT, WIDTH))

# 初始波包（高斯分布，带相位）
for y in range(HEIGHT):
    dy = y - SOURCE_Y
    energy_grid[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / 100)
    phase_grid[y, SOURCE_X] = 0.0  # 初始相位为0

# 分裂掩码（将波包分成两路，并保持相位同步）
split_mask = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
for y in range(HEIGHT):
    for x in range(SPLIT_X, SPLIT_X + 20):
        # 上路径
        target_y_up = SOURCE_Y - int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
        if 0 <= target_y_up < HEIGHT:
            split_mask[target_y_up, x] = True
        # 下路径
        target_y_down = SOURCE_Y + int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
        if 0 <= target_y_down < HEIGHT:
            split_mask[target_y_down, x] = True

# ============================================================
# 计算相位相关性
# ============================================================

def compute_phase_correlation(phase_grid, y1, x1, y2, x2):
    """计算两个点的相位差（余弦相似度）"""
    phase1 = phase_grid[y1, x1]
    phase2 = phase_grid[y2, x2]
    return np.cos(phase1 - phase2)  # 1=同相，-1=反相，0=正交

# ============================================================
# 运行模拟
# ============================================================

energies1 = []
energies2 = []
phase_corrs = []

for step in range(STEPS):
    energy_grid, phase_grid = propagate_split_phase(
        energy_grid, phase_grid, split_mask, A, S, B, LAMBDA, False
    )
    
    # 记录探测器数据
    e1 = energy_grid[DETECTOR1_Y, DETECTOR1_X]
    e2 = energy_grid[DETECTOR2_Y, DETECTOR2_X]
    energies1.append(e1)
    energies2.append(e2)
    
    # 计算相位相关性
    corr = compute_phase_correlation(phase_grid, DETECTOR1_Y, DETECTOR1_X, DETECTOR2_Y, DETECTOR2_X)
    phase_corrs.append(corr)
    
    if (step + 1) % 200 == 0:
        print(f"进度: {step+1}/{STEPS}")

# ============================================================
# 数据分析
# ============================================================

print("\n" + "=" * 60)
print("纠缠数据分析（加入相位）")
print("=" * 60)

# 能量相关性
avg_e1 = np.mean(energies1[-200:])
avg_e2 = np.mean(energies2[-200:])
energy_ratio = avg_e1 / avg_e2 if avg_e2 > 0 else 0
print(f"探测器1平均能量: {avg_e1:.6e}")
print(f"探测器2平均能量: {avg_e2:.6e}")
print(f"能量比 (E1/E2): {energy_ratio:.4f}")

# 相位相关性
avg_phase_corr = np.mean(phase_corrs[-200:])
print(f"平均相位相关性: {avg_phase_corr:.4f} (1=完美同步)")

if avg_phase_corr > 0.9:
    print("\n✅ 相位高度相关！两个波包的相位同步。")
    print("   你的模型解释：纠缠是相位同步，不随距离衰减。")
    print("   能量随距离衰减，但相位保持。")
    print("   这兼容了量子力学实验（纠缠不衰减）和你的模型（能量衰减）。")
elif avg_phase_corr > 0.5:
    print("\n⚠️ 相位中度相关。")
else:
    print("\n❌ 相位相关性低。")

# ============================================================
# 可视化
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 1. 最终能量分布
im = axes[0,0].imshow(np.log1p(energy_grid), cmap='hot', aspect='auto', origin='upper')
axes[0,0].set_title('最终能量分布')
axes[0,0].axhline(y=DETECTOR1_Y, color='cyan', linestyle='--')
axes[0,0].axhline(y=DETECTOR2_Y, color='cyan', linestyle='--')
plt.colorbar(im, ax=axes[0,0])

# 2. 最终相位分布
im2 = axes[0,1].imshow(phase_grid, cmap='twilight', aspect='auto', origin='upper')
axes[0,1].set_title('最终相位分布')
plt.colorbar(im2, ax=axes[0,1])

# 3. 能量时间序列
axes[1,0].plot(energies1, 'r-', linewidth=0.5, label='探测器1')
axes[1,0].plot(energies2, 'b-', linewidth=0.5, label='探测器2')
axes[1,0].set_title('探测器能量随时间变化')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# 4. 相位相关性时间序列
axes[1,1].plot(phase_corrs, 'g-', linewidth=0.5)
axes[1,1].set_title('相位相关性 (cos(Δφ))')
axes[1,1].set_ylim(-1.1, 1.1)
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('entanglement_with_phase.png', dpi=150)
plt.show()

print("\n" + "=" * 60)
print("实验完成！图片已保存为 entanglement_with_phase.png")
print("=" * 60)
print("\n关键改进：")
print("1. 加入了相位（方向）维度")
print("2. 分裂时保持相位同步")
print("3. 预言：相位相关性不随距离衰减，能量随距离衰减")
print("\n这是你的模型兼容量子力学实验的关键：")
print("  - 能量衰减 → 可检验的新效应")
print("  - 相位保持 → 兼容现有纠缠实验")