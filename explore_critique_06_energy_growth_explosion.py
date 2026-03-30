# -*- coding: utf-8 -*-
"""
质疑06：未全局归一时 sum(E) 可指数增长；不能美化为「相对论式守恒」。
记录 E_final/E0 与步间中位比，若非有限则 FAIL 子进程。
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import mpl_compat  # noqa: F401
from ce_engine_v2 import propagate_double_slit_n_steps

HEIGHT = 121
WIDTH = 260
A, S, B, LAM = 1.0, 0.28, 0.05, 0.96
SOURCE_X = 6
SOURCE_Y = HEIGHT // 2
BAR_X = 80
SLIT_W = 5
SLIT_GAP = 40
STEPS = 450

cy = SOURCE_Y
o1 = cy - SLIT_GAP // 2 - SLIT_W // 2
o2 = cy + SLIT_GAP // 2 - SLIT_W // 2

barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
barrier[:, BAR_X] = True
barrier[o1 : o1 + SLIT_W, BAR_X] = False
barrier[o2 : o2 + SLIT_W, BAR_X] = False

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1000.0
E0 = float(grid.sum())
ratios = []
cur = E0
for t in range(STEPS):
    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, 1)
    s = float(grid.sum())
    ratios.append(s / cur if cur > 0 else float("nan"))
    cur = s

E1 = float(grid.sum())
R = E1 / E0 if E0 > 0 else float("nan")
med_step = float(np.median(np.array(ratios[10:])))

print("=" * 62)
print("初 sum(E) = %.6g" % E0)
print("末 sum(E) = %.6g" % E1)
print("总能量比 R_E = E_final/E0 = %.6g" % R)
print("步间中位比 median(E_{t+1}/E_t) = %.4f" % med_step)
if not np.isfinite(E1) or not np.isfinite(R):
    print("[FAIL] energy non-finite")
    sys.exit(1)
if R > 1e100:
    print("[警告] R_E 天文量级: 非守恒, 非相对论守恒解释.")
else:
    print("[信息] R_E 虽未爆炸, 仍多 >1 (与 lam*分裂增益一致).")
print("[OK] critique_06_energy_growth")
print("=" * 62)

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.semilogy(np.arange(len(ratios)), ratios, "b-", lw=1)
ax.axhline(1.0, color="k", ls="--", alpha=0.4)
ax.set_xlabel("step")
ax.set_ylabel("E_{t+1}/E_t")
ax.set_title("Energy step ratio (no global renormalization)")
ax.grid(alpha=0.3)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_critique_06_energy_growth.png")
plt.savefig(out, dpi=120, bbox_inches="tight")
print("Saved: %s" % out)
