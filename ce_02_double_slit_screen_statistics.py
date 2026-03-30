import numpy as np

from chain_explosion_numba import propagate_double_slit

# ============================================================
# 参数配置（你可以随意修改）
# ============================================================

HEIGHT = 201          # 网格高度（奇数，保证中心对称）
WIDTH = 400           # 网格宽度
A = 1.0               # 主方向强度
S = 0.4               # 侧向强度（调大以增强干涉）
B = 0.05              # 后向强度
LAMBDA = 0.90         # 能量衰减
SOURCE_X = 10         # 光源X坐标
SOURCE_Y = HEIGHT // 2
BARRIER_X = WIDTH // 2
SLIT1_Y = HEIGHT // 2 - 25
SLIT2_Y = HEIGHT // 2 + 25
SLIT_WIDTH = 6
STEPS = 500
SCREEN_X = WIDTH - 10 # 屏幕位置（右侧）

# ============================================================
# 初始化
# ============================================================

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 100.0

# 挡板
barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BARRIER_X] = True
barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, BARRIER_X] = False
barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, BARRIER_X] = False

# ============================================================
# 运行模拟
# ============================================================

print("=" * 60)
print("链式爆炸模型 - 双缝干涉实验")
print(f"参数: A={A}, S={S}, B={B}, λ={LAMBDA}")
print(f"双缝: 上缝Y={SLIT1_Y}, 下缝Y={SLIT2_Y}, 缝宽={SLIT_WIDTH}")
print(f"传播步数: {STEPS}, 屏幕X={SCREEN_X}")
print("=" * 60)

for step in range(STEPS):
    grid = propagate_double_slit(grid, barrier, A, S, B, LAMBDA)
    if (step + 1) % 100 == 0:
        print(f"进度: {step+1}/{STEPS}")

# 提取屏幕数据
screen = grid[:, SCREEN_X]

# ============================================================
# 数据分析与抽样（关键特征）
# ============================================================

# 1. 基础统计
total_energy = np.sum(screen)
peak_energy = np.max(screen)
mean_energy = np.mean(screen)
print(f"\n屏幕能量统计:")
print(f"  总能量: {total_energy:.4f}")
print(f"  峰值能量: {peak_energy:.4f}")
print(f"  平均能量: {mean_energy:.4f}")

# 2. 找所有峰值（局部最大值）
peaks = []
for y in range(1, HEIGHT-1):
    if screen[y] > screen[y-1] and screen[y] > screen[y+1] and screen[y] > mean_energy * 0.5:
        peaks.append((y, screen[y]))

print(f"\n检测到的主峰数量: {len(peaks)}")
if peaks:
    print("主峰列表 (Y, 能量):")
    for y, val in peaks:
        print(f"  Y={y:3d}, 能量={val:.4f}")

# 3. 计算干涉对比度（如果有多个峰）
if len(peaks) >= 2:
    # 取两个最高峰
    peaks_sorted = sorted(peaks, key=lambda x: x[1], reverse=True)
    top_two = peaks_sorted[:2]
    print(f"\n两个最高峰:")
    for y, val in top_two:
        print(f"  Y={y:3d}, 能量={val:.4f}")
    
    # 在两个主峰之间找谷值
    y1, y2 = sorted([top_two[0][0], top_two[1][0]])
    valley_energy = np.min(screen[y1:y2+1])
    valley_y = np.argmin(screen[y1:y2+1]) + y1
    print(f"\n两峰之间谷值: Y={valley_y:3d}, 能量={valley_energy:.4f}")
    
    # 对比度
    I_max = (top_two[0][1] + top_two[1][1]) / 2
    I_min = valley_energy
    visibility = (I_max - I_min) / (I_max + I_min) if I_max + I_min > 0 else 0
    print(f"\n干涉对比度 V = {visibility:.4f}")
    
    if visibility > 0.2:
        print("  ✅ 检测到明显干涉条纹")
    elif visibility > 0.05:
        print("  ⚠️ 检测到微弱干涉条纹")
    else:
        print("  ❌ 未检测到明显干涉条纹")
else:
    print("\n⚠️ 未检测到多个主峰，无法计算干涉对比度")
    visibility = 0

# 4. 检查对称性
center = HEIGHT // 2
left_energy = np.sum(screen[:center])
right_energy = np.sum(screen[center:])
symmetry_ratio = min(left_energy, right_energy) / max(left_energy, right_energy) if max(left_energy, right_energy) > 0 else 0
print(f"\n能量对称性 (左/右): {symmetry_ratio:.4f}")
if symmetry_ratio < 0.8:
    print("  ⚠️ 能量分布不对称（可能光源不在中心或参数非对称）")

# 5. 抽样数据（每隔N个点打印，便于AI分析）
sample_step = 10
print(f"\n屏幕能量抽样 (Y, 能量, 步长={sample_step}):")
for y in range(0, HEIGHT, sample_step):
    print(f"  Y={y:3d}: {screen[y]:.4f}")

# 6. 关键参数总结
print("\n" + "=" * 60)
print("实验总结:")
print(f"  传播距离: {SCREEN_X - BARRIER_X} 像素")
print(f"  总能量: {total_energy:.4f}")
print(f"  干涉对比度: {visibility:.4f}")
print("=" * 60)

import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 4))
plt.plot(screen, "b-", lw=1)
plt.xlabel("Y index")
plt.ylabel("Screen intensity")
plt.title("ce_02: screen column after propagation")
plt.grid(alpha=0.3)
_p = os.path.join(os.path.dirname(__file__), "ce_02_double_slit_screen_statistics.png")
plt.tight_layout()
plt.savefig(_p, dpi=120, bbox_inches="tight")
print("Saved:", _p)

from experiment_dossier import emit_case_dossier

emit_case_dossier(
    __file__,
    constants={
        "HEIGHT": HEIGHT,
        "WIDTH": WIDTH,
        "A": A,
        "S": S,
        "B": B,
        "LAMBDA": LAMBDA,
        "STEPS": STEPS,
        "SCREEN_X": SCREEN_X,
        "BARRIER_X": BARRIER_X,
        "SLIT_WIDTH": SLIT_WIDTH,
    },
    observed={
        "num_peaks_heuristic": len(peaks),
        "visibility_heuristic": float(visibility),
        "symmetry_ratio_LR": float(symmetry_ratio),
        "total_energy_on_screen_column": float(total_energy),
    },
    artifacts=["ce_02_double_slit_screen_statistics.png"],
    reviewer_prompts=[
        "峰检测阈值 mean*0.5 是否导致峰值数对噪声过敏？",
        "左右半屏能量比能否在严格镜像几何下仍偏离 1？原因是否为离散奇偶网格？",
    ],
)