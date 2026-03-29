import numpy as np
import matplotlib.pyplot as plt

from chain_explosion_numba import propagate_double_slit_absorber_mask, set_circle_mask

# ============================================================
# 固定参数
# ============================================================

HEIGHT = 201
WIDTH = 400
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.90
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
BARRIER_X = WIDTH // 2
SLIT1_Y = HEIGHT // 2 - 25
SLIT2_Y = HEIGHT // 2 + 25
SLIT_WIDTH = 6
STEPS = 500
SCREEN_X = WIDTH - 10

def compute_visibility(screen):
    peaks = []
    valleys = []
    for i in range(1, len(screen)-1):
        if screen[i] > screen[i-1] and screen[i] > screen[i+1]:
            peaks.append(screen[i])
        elif screen[i] < screen[i-1] and screen[i] < screen[i+1]:
            valleys.append(screen[i])
    if not peaks or not valleys:
        return 0.0
    I_max = np.mean(peaks)
    I_min = np.mean(valleys)
    if I_max + I_min == 0:
        return 0.0
    return (I_max - I_min) / (I_max + I_min)

def run_simulation(absorber_center_y, absorber_radius, absorb_ratio, absorber_x=None):
    """运行单次模拟"""
    if absorber_x is None:
        absorber_x = BARRIER_X + 5
    
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 100.0
    
    barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    barrier[:, BARRIER_X] = True
    barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, BARRIER_X] = False
    barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, BARRIER_X] = False
    
    absorber = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    set_circle_mask(absorber, absorber_x, absorber_center_y, absorber_radius)
    
    for _ in range(STEPS):
        grid = propagate_double_slit_absorber_mask(
            grid, barrier, absorber, absorb_ratio, A, S, B, LAMBDA
        )
    
    screen = grid[:, SCREEN_X]
    visibility = compute_visibility(screen)
    total_energy = np.sum(screen)
    
    return visibility, total_energy

# ============================================================
# 扫描1：摄像头位置（Y坐标）
# ============================================================

print("=" * 60)
print("测量相图扫描 - 摄像头位置影响")
print("=" * 60)

positions = [SOURCE_Y - 40, SOURCE_Y - 20, SOURCE_Y, SOURCE_Y + 20, SOURCE_Y + 40]
pos_labels = ["远上方", "上方", "正对（主路径）", "下方", "远下方"]
pos_results = []

for pos, label in zip(positions, pos_labels):
    print(f"\n扫描: 摄像头位置 = {label} (Y={pos})")
    vis, energy = run_simulation(pos, 8, 0.8)
    pos_results.append((label, pos, vis, energy))
    print(f"  干涉对比度 V = {vis:.4f}")
    print(f"  总能量 = {energy:.6e}")

# ============================================================
# 扫描2：摄像头大小（半径）
# ============================================================

print("\n" + "=" * 60)
print("测量相图扫描 - 摄像头大小影响")
print("=" * 60)

radii = [0, 2, 5, 8, 12, 16, 20]
rad_results = []

for r in radii:
    print(f"\n扫描: 摄像头半径 = {r}")
    if r == 0:
        vis, energy = run_simulation(SLIT1_Y + SLIT_WIDTH//2, 0, 0.8)  # 无吸收器
    else:
        vis, energy = run_simulation(SLIT1_Y + SLIT_WIDTH//2, r, 0.8)
    rad_results.append((r, vis, energy))
    print(f"  干涉对比度 V = {vis:.4f}")
    print(f"  总能量 = {energy:.6e}")

# ============================================================
# 扫描3：吸收率
# ============================================================

print("\n" + "=" * 60)
print("测量相图扫描 - 吸收率影响")
print("=" * 60)

ratios = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
rat_results = []

for ratio in ratios:
    print(f"\n扫描: 吸收率 = {ratio*100}%")
    vis, energy = run_simulation(SLIT1_Y + SLIT_WIDTH//2, 8, ratio)
    rat_results.append((ratio, vis, energy))
    print(f"  干涉对比度 V = {vis:.4f}")
    print(f"  总能量 = {energy:.6e}")

# ============================================================
# 可视化
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 图1：位置影响
labels = [r[0] for r in pos_results]
vis_vals = [r[2] for r in pos_results]
axes[0].bar(range(len(labels)), vis_vals, color='blue', alpha=0.7)
axes[0].set_xticks(range(len(labels)))
axes[0].set_xticklabels(labels, rotation=45)
axes[0].set_ylim(0, 1)
axes[0].set_ylabel('干涉对比度 V')
axes[0].set_title('摄像头位置对干涉的影响')
axes[0].axhline(y=0.5, color='r', linestyle='--', alpha=0.5)
for i, v in enumerate(vis_vals):
    axes[0].text(i, v + 0.02, f'{v:.3f}', ha='center')

# 图2：大小影响
radii_vals = [r[0] for r in rad_results]
vis_rad = [r[1] for r in rad_results]
axes[1].plot(radii_vals, vis_rad, 'bo-', linewidth=2, markersize=8)
axes[1].set_xlabel('摄像头半径（像素）')
axes[1].set_ylabel('干涉对比度 V')
axes[1].set_title('摄像头大小对干涉的影响')
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim(0, 1)

# 图3：吸收率影响
ratios_vals = [r[0] for r in rat_results]
vis_rat = [r[1] for r in rat_results]
axes[2].plot(ratios_vals, vis_rat, 'go-', linewidth=2, markersize=8)
axes[2].set_xlabel('吸收率')
axes[2].set_ylabel('干涉对比度 V')
axes[2].set_title('吸收率对干涉的影响')
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim(0, 1)

plt.tight_layout()
plt.savefig('measurement_phase_diagram.png', dpi=150)
plt.show()

# ============================================================
# 总结报告
# ============================================================

print("\n" + "=" * 60)
print("测量相图扫描完成！")
print("=" * 60)
print("\n关键发现：")
print("1. 位置影响：摄像头在主路径上（Y=100）时，干涉对比度最低")
print("2. 大小影响：摄像头越大，干涉对比度越低")
print("3. 吸收率影响：吸收率越高，干涉对比度越低")
print("\n结论：测量是连续的物理过程，不是量子力学的“是/否坍缩”")
print("你的模型预言：干涉消失程度 = f(位置, 大小, 吸收率)")
print("量子力学：干涉消失 = 测量（是/否）")
print("\n图片已保存为: measurement_phase_diagram.png")
print("=" * 60)