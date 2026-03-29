"""
explore_energy_budget_propagation.py
------------------------------------
质疑点：sum(E) 是否“守恒”？ce_engine_v2 的规则是：每格能量 *λ 后再按
A/S/B 分到多个邻格，**未**做全局归一。因此每步总储量常数倍率约为
λ*(A+B+2S+对角项) 等，若 >1 则 sum(E) **指数增长**——这不是笔误，
而是与“概率归一化为 1”的教材薛定谔演化**不是同一对象**。

运行: python explore_energy_budget_propagation.py
输出: explore_energy_budget.png
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from ce_engine_v2 import propagate_double_slit

HEIGHT = 201
WIDTH = 400
A, S, B, LAM = 1.0, 0.30, 0.05, 0.92
SOURCE_X = 5
SOURCE_Y = HEIGHT // 2
BAR_X = 120
SLIT1_Y = HEIGHT // 2 - 22
SLIT2_Y = HEIGHT // 2 + 22
SLIT_W = 6
MAX_STEPS = 400

barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
barrier[:, BAR_X] = True
barrier[SLIT1_Y : SLIT1_Y + SLIT_W, BAR_X] = False
barrier[SLIT2_Y : SLIT2_Y + SLIT_W, BAR_X] = False

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1000.0

sums = []
for _ in range(MAX_STEPS):
    sums.append(float(np.sum(grid)))
    grid = propagate_double_slit(grid, barrier, A, S, B, LAM)

sums = np.array(sums)
rat = sums[1:] / (sums[:-1] + 1e-30)

print("=" * 60)
print("sum(E) 逐步记录（双缝，一步一调便于审计）")
print(f"初值 sum(E)0 = {sums[0]:.6g}")
print(f"终值 sum(E)  = {sums[-1]:.6g}")
print(f"总比值 sum_N/sum_0 = {sums[-1]/sums[0]:.6g}")
print(f"每步比值 median E_{{t+1}}/E_t = {np.median(rat):.6g}")
print(
    "说明: 当前内核下 sum(E) 常增长（分裂到多格 + λ）；"
    "若要与 |ψ|² 总量类比，需在每步后除以 sum(E) 或使用带归一化的引擎变体。"
)
print("=" * 60)

plt.figure(figsize=(9, 4))
plt.subplot(1, 2, 1)
plt.plot(sums, lw=2)
plt.xlabel("step")
plt.ylabel("sum(E)")
plt.title("Total grid sum vs step")
plt.grid(alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(rat, lw=1)
plt.xlabel("step")
plt.ylabel("sum(E)_{t+1} / sum(E)_t")
plt.title("Step-wise retention factor")
plt.grid(alpha=0.3)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_energy_budget.png")
plt.savefig(out, dpi=140)
print(f"Saved: {out}")
