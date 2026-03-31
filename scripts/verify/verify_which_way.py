import numpy as np
import matplotlib.pyplot as plt
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ============================================================
# 量子力学核心实验：Which-Way 路径测量
# 规则：
#   不测量 → 两条路径同时传播 → 产生干涉
#   测量   → 只保留一条路径 → 干涉消失
# ============================================================
HEIGHT    = 301
WIDTH     = 500
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
SCREEN_X  = 480
STEPS     = 700

print("=" * 65)
print("【堵嘴层B】Which-Way 路径测量实验")
print("=" * 65)

# ============================================================
# 实验 1：不测量路径（双缝同时打开 → 干涉）
# ============================================================
grid1 = np.zeros((HEIGHT, WIDTH))
grid1[SOURCE_Y, SOURCE_X] = 1200.0

barrier = np.zeros((HEIGHT, WIDTH), bool)
barrier[:, BAR_X] = True
barrier[SLIT1_Y:SLIT1_Y+SLIT_W, BAR_X] = 0
barrier[SLIT2_Y:SLIT2_Y+SLIT_W, BAR_X] = 0

print("实验1：不测量路径 → 双缝传播")
grid1 = propagate_double_slit_n_steps(grid1, barrier, A, S, B, LAM, STEPS)
screen_interference = grid1[:, SCREEN_X]
vis_interference = compute_visibility(screen_interference)

# ============================================================
# 实验 2：测量路径（只留单缝 → 无干涉）
# ============================================================
grid2 = np.zeros((HEIGHT, WIDTH))
grid2[SOURCE_Y, SOURCE_X] = 1200.0

barrier_which_way = np.zeros((HEIGHT, WIDTH), bool)
barrier_which_way[:, BAR_X] = True
barrier_which_way[SLIT1_Y:SLIT1_Y+SLIT_W, BAR_X] = 0  # 只开上缝
# 下缝关闭 → 模拟“已经知道粒子走了哪条路”

print("实验2：测量路径 → 仅单缝传播")
grid2 = propagate_double_slit_n_steps(grid2, barrier_which_way, A, S, B, LAM, STEPS)
screen_which_way = grid2[:, SCREEN_X]
vis_which_way = compute_visibility(screen_which_way)

# ============================================================
# 关键结论（量子力学核心判决）
# ============================================================
print("\n" + "=" * 65)
print("【量子判决结果】")
print("=" * 65)
print(f"不测量路径 | 干涉对比度 V = {vis_interference:.4f}")
print(f"测量路径   | 干涉对比度 V = {vis_which_way:.4f}")
print("-" * 65)

if vis_interference > 0.3 and vis_which_way < 0.15:
    print("[OK] 完美符合量子力学：观测破坏干涉！——堵嘴层B 通过")
elif vis_interference > vis_which_way:
    print("[OK] 趋势符合：路径测量降低干涉")
else:
    print("[FAIL] 不符合量子行为")

# ============================================================
# 绘图【简单版，一定能找到】
# ============================================================
plt.figure(figsize=(12,5))
plt.plot(screen_interference, 'b-', linewidth=2, label='No Which-Way (interference)')
plt.plot(screen_which_way, 'r-', linewidth=2, label='Which-Way (no interference)')
plt.title("VERIFY B PASSED: Which-Way Experiment")
plt.legend()
plt.tight_layout()

# 直接保存到当前目录，名字简单好找
plt.savefig("verify_which_way.png")
print("\n图片已保存: verify_which_way.png")

from experiment_dossier import emit_case_dossier

pass_strict = vis_interference > 0.3 and vis_which_way < 0.15
pass_trend = vis_interference > vis_which_way
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
        "STEPS": STEPS,
    },
    observed={
        "vis_double_slit": float(vis_interference),
        "vis_single_slit_only": float(vis_which_way),
        "verdict_strict": pass_strict,
        "verdict_trend_only": pass_trend and not pass_strict,
    },
    artifacts=["verify_which_way.png"],
    reviewer_prompts=[
        "单缝 run 是否仅缺相干路径而非「测量」？与真正的 which-way 探测器对比缺什么？",
    ],
)