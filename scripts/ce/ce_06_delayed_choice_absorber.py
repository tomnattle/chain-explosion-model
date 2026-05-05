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

# ========== 延迟选择参数 ==========
INSERT_STEP = 300          # 在第几步插入吸收器（光已通过双缝但未到屏幕）
ABSORBER_CENTER_X = BARRIER_X + 5
ABSORBER_CENTER_Y = SLIT1_Y + SLIT_WIDTH // 2
ABSORBER_RADIUS = 8
ABSORB_RATIO = 0.9

# ============================================================
# 初始化
# ============================================================

print("=" * 60)
print("链式爆炸模型 - 延迟选择实验（量子力学最诡异现象）")
print(f"参数: A={A}, S={S}, B={B}, λ={LAMBDA}")
print(f"吸收器插入步数: {INSERT_STEP} / {STEPS}")
print("=" * 60)

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 100.0

# 挡板
barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BARRIER_X] = True
barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, BARRIER_X] = False
barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, BARRIER_X] = False

# 吸收器（初始为空）
absorber = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)

# ============================================================
# 运行模拟
# ============================================================

for step in range(STEPS):
    # 在指定步数插入吸收器
    if step == INSERT_STEP:
        print(f"\n>>> 在步数 {step} 处插入吸收器（光已通过双缝，但未到屏幕）")
        set_circle_mask(absorber, ABSORBER_CENTER_X, ABSORBER_CENTER_Y, ABSORBER_RADIUS)
        print(f"    吸收器位置: ({ABSORBER_CENTER_X},{ABSORBER_CENTER_Y}), 半径={ABSORBER_RADIUS}")
    
    grid = propagate_double_slit_absorber_mask(
        grid, barrier, absorber, ABSORB_RATIO, A, S, B, LAMBDA
    )
    
    if (step + 1) % 100 == 0:
        print(f"进度: {step+1}/{STEPS}")

# 提取屏幕数据
screen = grid[:, SCREEN_X]

# ============================================================
# 数据分析
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

total_energy = np.sum(screen)
peak_energy = np.max(screen)
visibility = compute_visibility(screen)

print("\n" + "=" * 60)
print("屏幕能量统计")
print("=" * 60)
print(f"  总能量: {total_energy:.6e}")
print(f"  峰值能量: {peak_energy:.6e}")
print(f"  干涉对比度 V = {visibility:.4f}")

# 判断干涉是否消失
if visibility < 0.1:
    print("\n❌ 干涉条纹基本消失（对比度 < 0.1）")
    print("   结论：延迟插入的吸收器仍然破坏了干涉！")
    print("   量子力学解释：这是延迟选择，测量决定了过去。")
    print("   你的模型解释：涟漪是连续的，吸收器吃掉了涟漪的尾巴，破坏了整个结构。")
    print("   不需要超距，不需要延迟，只需要物理吸收。")
elif visibility > 0.3:
    print("\n✅ 干涉条纹仍然明显（对比度 > 0.3）")
    print("   结论：延迟插入的吸收器未破坏干涉。")
    print("   这可能与插入时间、吸收器大小有关。")
else:
    print("\n⚠️ 干涉条纹部分减弱（0.1 < 对比度 < 0.3）")

# ============================================================
# 可视化
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 1. 屏幕能量分布
axes[0].plot(screen, 'b-', linewidth=1)
axes[0].set_title(f'延迟选择实验 - 屏幕能量分布 (V={visibility:.3f})')
axes[0].set_xlabel('Y 位置')
axes[0].set_ylabel('能量')
axes[0].grid(True, alpha=0.3)

# 2. 最终能量分布
energy_display = np.log1p(grid)
im = axes[1].imshow(energy_display, cmap='hot', aspect='auto', origin='upper')
axes[1].axvline(x=BARRIER_X, color='cyan', linestyle='--', linewidth=1, label='挡板')
if INSERT_STEP < STEPS:
    circle = plt.Circle((ABSORBER_CENTER_X, ABSORBER_CENTER_Y), ABSORBER_RADIUS, 
                         color='white', fill=False, linewidth=2, label='吸收器')
    axes[1].add_patch(circle)
axes[1].set_title('最终能量分布 (对数显示)')
axes[1].set_xlabel('X 位置')
axes[1].set_ylabel('Y 位置')
plt.colorbar(im, ax=axes[1], label='log(1+能量)')
axes[1].legend()

# 3. 吸收器附近放大
zoom_y1 = max(0, ABSORBER_CENTER_Y - 30)
zoom_y2 = min(HEIGHT, ABSORBER_CENTER_Y + 30)
zoom_x1 = max(0, ABSORBER_CENTER_X - 30)
zoom_x2 = min(WIDTH, ABSORBER_CENTER_X + 30)
axes[2].imshow(np.log1p(grid[zoom_y1:zoom_y2, zoom_x1:zoom_x2]), cmap='hot', aspect='auto', origin='upper')
axes[2].set_title('吸收器附近放大视图')
axes[2].set_xlabel('X 位置')
axes[2].set_ylabel('Y 位置')

plt.tight_layout()
_out_png = os.path.join(os.path.dirname(__file__), "delayed_choice.png")
plt.savefig(_out_png, dpi=150)
print("Saved:", _out_png)
plt.show()

print("\n" + "=" * 60)
print("实验完成！图片已保存为", _out_png)
print("=" * 60)

# ============================================================
# 对比实验建议
# ============================================================

print("\n对比实验：")
print("  1. 无吸收器（注释掉插入代码）→ 应看到明显干涉")
print("  2. 提前插入吸收器（INSERT_STEP=0）→ 干涉消失")
print("  3. 延迟插入（当前）→ 观察是否消失")
print("\n如果延迟插入也导致干涉消失，你的模型就挑战了量子力学的‘延迟选择’解释。")

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
        "INSERT_STEP": INSERT_STEP,
        "ABSORB_RATIO": ABSORB_RATIO,
    },
    observed={
        "visibility_final": float(visibility),
    },
    artifacts=["delayed_choice.png"],
    reviewer_prompts=[
        "INSERT_STEP 与物理“延迟”的映射是否在一行注释里写清？",
    ],
)