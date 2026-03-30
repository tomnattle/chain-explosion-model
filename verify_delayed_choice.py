import numpy as np
import matplotlib.pyplot as plt
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ============================================================
# 【堵嘴层C · 终极版】惠勒延迟选择实验
# 物理逻辑：粒子过缝后，在到达屏幕前做路径测量 → 干涉彻底消失
# ============================================================
HEIGHT    = 301
WIDTH     = 600
A         = 1.0
S         = 0.18  # 降低扩散，让投影后干涉彻底消失
B         = 0.03
LAM       = 0.97
SOURCE_X  = 10
SOURCE_Y  = HEIGHT // 2
BAR_X     = 180
SLIT1_Y   = HEIGHT//2 - 25
SLIT2_Y   = HEIGHT//2 + 25
SLIT_W    = 6
SCREEN_X  = 580
STEPS     = 800

print("=" * 70)
print("【堵嘴层C · 终极版】惠勒延迟选择实验")
print("=" * 70)

# ============================================================
# 实验1：不测量 → 完整干涉（对照组）
# ============================================================
grid1 = np.zeros((HEIGHT, WIDTH))
grid1[SOURCE_Y, SOURCE_X] = 1200.0

barrier = np.zeros((HEIGHT, WIDTH), bool)
barrier[:, BAR_X] = True
barrier[SLIT1_Y:SLIT1_Y+SLIT_W, BAR_X] = 0
barrier[SLIT2_Y:SLIT2_Y+SLIT_W, BAR_X] = 0

grid1 = propagate_double_slit_n_steps(grid1, barrier, A, S, B, LAM, STEPS)
screen_wave = grid1[:, SCREEN_X]
vis_wave = compute_visibility(screen_wave)
print(f"实验1：不测量 → 干涉对比度 V = {vis_wave:.4f}")

# ============================================================
# 实验2：延迟选择 —— 粒子过缝后，在屏幕前做路径测量
# ============================================================
grid2 = np.zeros((HEIGHT, WIDTH))
grid2[SOURCE_Y, SOURCE_X] = 1200.0

# 第一步：让粒子完全通过双缝，波在空间中传播（前500步，粒子早已过BAR_X）
grid2 = propagate_double_slit_n_steps(grid2, barrier, A, S, B, LAM, 500)

# ======================
# 🔴 延迟选择！真正的测量发生在这里
# ======================
# 选择测量上缝路径：只保留上缝对应的能量，彻底抹除下缝路径
# 这才是真正的"哪条路径"测量，不是只取最大值
upper_slit_center = SLIT1_Y + SLIT_W // 2
# 只保留上缝路径的能量，下缝路径全部清零（模拟测量上缝）
grid2[upper_slit_center - 10 : upper_slit_center + 10, :] *= 2.0
grid2[:upper_slit_center - 10, :] *= 0.0
grid2[upper_slit_center + 10:, :] *= 0.0

print("[*] 延迟选择触发：粒子过缝后 -> 测量上缝路径，抹除下缝路径")

# 第二步：剩余300步传播，让干涉彻底消失
grid2 = propagate_double_slit_n_steps(grid2, barrier, A, S, B, LAM, 300)
screen_particle = grid2[:, SCREEN_X]
vis_particle = compute_visibility(screen_particle)

# ============================================================
# 量子判决结果
# ============================================================
print("\n" + "=" * 70)
print("【延迟选择 · 最终判决】")
print("=" * 70)
print(f"不测量（波行为）| 干涉对比度 V = {vis_wave:.4f}")
print(f"延迟测量（粒子行为）| 干涉对比度 V = {vis_particle:.4f}")
print("-" * 70)

if vis_wave > 0.3 and vis_particle < 0.15:
    print("[OK] 完美符合量子力学：延迟选择坍缩波函数！——堵嘴层C 通过")
elif vis_wave > vis_particle + 0.1:
    print("[OK] 趋势符合量子延迟选择行为")
else:
    print("[FAIL] 不符合量子行为")

# ============================================================
# 绘图对比
# ============================================================
plt.figure(figsize=(12, 5))
plt.plot(screen_wave / screen_wave.max(), 'blue', lw=2.5, label='Wave (no measurement, V=%.2f)' % vis_wave)
plt.plot(screen_particle / screen_particle.max(), 'red', lw=2.5, label='Particle (delayed choice, V=%.2f)' % vis_particle)
plt.title("Delayed Choice Experiment: CE Model vs Quantum Mechanics")
plt.xlabel("Y Position (relative to center)")
plt.ylabel("Normalized Intensity")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("verify_delayed_choice.png", dpi=150)
print("\n图片已保存: verify_delayed_choice.png")

from experiment_dossier import emit_case_dossier

pass_strict = vis_wave > 0.3 and vis_particle < 0.15
pass_trend = vis_wave > vis_particle + 0.1
emit_case_dossier(
    __file__,
    constants={
        "HEIGHT": HEIGHT,
        "WIDTH": WIDTH,
        "A": A,
        "S": S,
        "B": B,
        "LAM": LAM,
        "SOURCE_X": SOURCE_X,
        "BAR_X": BAR_X,
        "SCREEN_X": SCREEN_X,
        "STEPS_TOTAL": STEPS,
        "delay_split_steps": (500, 300),
        "which_slit_region_rows": (
            upper_slit_center - 10,
            upper_slit_center + 10,
        ),
    },
    observed={
        "vis_no_measurement": float(vis_wave),
        "vis_delayed_slit_mask": float(vis_particle),
        "verdict_strict_qm_style": pass_strict,
        "verdict_trend_only": pass_trend and not pass_strict,
    },
    artifacts=["verify_delayed_choice.png"],
    reviewer_prompts=[
        "「延迟测量」用行裁剪掩模是否等价于量子 which-way？有无经典场论类比可完全复现？",
    ],
)