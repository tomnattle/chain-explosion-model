import os

import numpy as np
import matplotlib.pyplot as plt

from chain_explosion_numba import propagate_double_slit_absorber_mask, set_circle_mask

# ============================================================
# 参数配置
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

# ========== 吸收器参数 ==========
ENABLE_ABSORBER = True          # 是否启用吸收器
ABSORBER_CENTER_X = BARRIER_X + 5   # 吸收器中心X（在缝后面）
ABSORBER_CENTER_Y = SLIT1_Y + SLIT_WIDTH // 2  # 吸收器中心Y（上缝位置）
ABSORBER_RADIUS = 10            # 吸收器半径（像素，覆盖多个格子）
ABSORB_RATIO = 0.8              # 吸收比例（0-1，1=完全吸收）

# ============================================================
# 初始化
# ============================================================

print("=" * 60)
print("链式爆炸模型 - 有限大小吸收器模拟（测量装置）")
print(f"参数: A={A}, S={S}, B={B}, λ={LAMBDA}")
print(f"双缝: 上缝Y={SLIT1_Y}, 下缝Y={SLIT2_Y}, 缝宽={SLIT_WIDTH}")
print(f"吸收器: 中心=({ABSORBER_CENTER_X},{ABSORBER_CENTER_Y}), 半径={ABSORBER_RADIUS}, 吸收比例={ABSORB_RATIO*100}%")
print("=" * 60)

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 100.0

# 挡板
barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BARRIER_X] = True
barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, BARRIER_X] = False
barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, BARRIER_X] = False

# 吸收器区域（圆形）
absorber = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
if ENABLE_ABSORBER:
    set_circle_mask(absorber, ABSORBER_CENTER_X, ABSORBER_CENTER_Y, ABSORBER_RADIUS)

# ============================================================
# 计算干涉对比度
# ============================================================

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

# ============================================================
# 运行模拟
# ============================================================

_ar = ABSORB_RATIO if ENABLE_ABSORBER else 0.0
for step in range(STEPS):
    grid = propagate_double_slit_absorber_mask(grid, barrier, absorber, _ar, A, S, B, LAMBDA)
    if (step + 1) % 100 == 0:
        print(f"进度: {step+1}/{STEPS}")

# 提取屏幕数据
screen = grid[:, SCREEN_X]

# ============================================================
# 数据分析
# ============================================================

total_energy = np.sum(screen)
peak_energy = np.max(screen)
mean_energy = np.mean(screen)
visibility = compute_visibility(screen)

print("\n" + "=" * 60)
print("屏幕能量统计")
print("=" * 60)
print(f"  总能量: {total_energy:.6e}")
print(f"  峰值能量: {peak_energy:.6e}")
print(f"  平均能量: {mean_energy:.6e}")
print(f"  干涉对比度 V = {visibility:.4f}")

# 找峰值
peaks = []
for y in range(1, HEIGHT-1):
    if screen[y] > screen[y-1] and screen[y] > screen[y+1] and screen[y] > mean_energy * 0.5:
        peaks.append((y, screen[y]))

print(f"\n检测到的峰值数量: {len(peaks)}")
if peaks:
    print("主峰列表 (Y, 能量):")
    for y, val in peaks[:10]:
        print(f"  Y={y:3d}, 能量={val:.6e}")

# 判断干涉是否被破坏
if visibility > 0.3:
    print("\n✅ 干涉条纹仍然明显（对比度 > 0.3）")
    print("   结论：有限大小吸收器未能完全破坏干涉。")
    print("   可能是因为吸收器只覆盖了部分区域，涟漪从周围绕过去了。")
elif visibility > 0.1:
    print("\n⚠️ 干涉条纹减弱（0.1 < 对比度 < 0.3）")
    print("   结论：吸收器部分破坏了干涉，但未完全消除。")
else:
    print("\n❌ 干涉条纹基本消失（对比度 < 0.1）")
    print("   结论：吸收器有效破坏了干涉，测量导致了坍缩。")

# ============================================================
# 可视化
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 1. 屏幕能量分布
axes[0].plot(screen, 'b-', linewidth=1)
axes[0].set_title(f'屏幕能量分布 (对比度={visibility:.3f})')
axes[0].set_xlabel('Y 位置')
axes[0].set_ylabel('能量')
axes[0].grid(True, alpha=0.3)

# 2. 最终能量分布热力图
energy_display = np.log1p(grid)
im = axes[1].imshow(energy_display, cmap='hot', aspect='auto', origin='upper')
axes[1].axvline(x=BARRIER_X, color='cyan', linestyle='--', linewidth=1, label='挡板')
if ENABLE_ABSORBER:
    # 画出吸收器圆形区域
    circle = plt.Circle((ABSORBER_CENTER_X, ABSORBER_CENTER_Y), ABSORBER_RADIUS, 
                         color='white', fill=False, linewidth=2, label='吸收器')
    axes[1].add_patch(circle)
axes[1].set_title('最终能量分布 (对数显示)')
axes[1].set_xlabel('X 位置')
axes[1].set_ylabel('Y 位置')
plt.colorbar(im, ax=axes[1], label='log(1+能量)')
axes[1].legend()

# 3. 吸收器附近的放大视图
zoom_y1 = max(0, ABSORBER_CENTER_Y - 40)
zoom_y2 = min(HEIGHT, ABSORBER_CENTER_Y + 40)
zoom_x1 = max(0, ABSORBER_CENTER_X - 40)
zoom_x2 = min(WIDTH, ABSORBER_CENTER_X + 40)
axes[2].imshow(np.log1p(grid[zoom_y1:zoom_y2, zoom_x1:zoom_x2]), cmap='hot', aspect='auto', origin='upper')
axes[2].set_title('吸收器附近放大视图')
axes[2].set_xlabel('X 位置')
axes[2].set_ylabel('Y 位置')

plt.tight_layout()
_out_png = os.path.join(os.path.dirname(__file__), "finite_absorber.png")
plt.savefig(_out_png, dpi=150)
print("Saved:", _out_png)
plt.show()

print("\n" + "=" * 60)
print("实验完成！图片已保存为", _out_png)
print("=" * 60)

# ============================================================
# 参数调整建议
# ============================================================

print("\n如果想进一步探索，可以修改以下参数：")
print("  ABSORBER_RADIUS: 吸收器大小（影响覆盖范围）")
print("  ABSORB_RATIO: 吸收比例（0-1）")
print("  ABSORBER_CENTER_X/Y: 吸收器位置（放在缝后面或别处）")
print("\n也可以禁用吸收器（ENABLE_ABSORBER=False）与有吸收的情况对比。")

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
        "ENABLE_ABSORBER": ENABLE_ABSORBER,
        "ABSORBER_RADIUS": ABSORBER_RADIUS,
        "ABSORB_RATIO": ABSORB_RATIO,
        "ABSORBER_CENTER_X": ABSORBER_CENTER_X,
        "ABSORBER_CENTER_Y": ABSORBER_CENTER_Y,
    },
    observed={
        "visibility_final": float(visibility),
        "grid_sum_final": float(np.sum(grid)),
    },
    artifacts=["finite_absorber.png"],
)