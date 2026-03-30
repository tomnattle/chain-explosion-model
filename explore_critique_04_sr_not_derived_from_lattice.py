# -*- coding: utf-8 -*-
"""
质疑04：np.roll + 洛伦兹公式验算 = 外部公式一致性演示；
真正「从格点因果结构推出闵氏几何+洛伦兹群」本仓库未声称完成。
并列打印：ce_engine 因果前缘速度 vs 公式层 v'（仅对照，非推导链）。
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import mpl_compat  # noqa: F401
from ce_engine_v2 import propagate_double_slit_n_steps

HEIGHT = 101
WIDTH = 200
A, S, B, LAM = 1.0, 0.12, 0.01, 0.97
SOURCE_X = 5
SOURCE_Y = HEIGHT // 2
STEPS = 60
THRESH = 1e-10

barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1.0
front = []
for t in range(STEPS + 1):
    col_max = grid.max(axis=0)
    hit = np.where(col_max > THRESH)[0]
    xr = int(hit.max()) if hit.size else SOURCE_X
    front.append(xr)
    if t < STEPS:
        grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, 1)
front = np.array(front, dtype=np.float64)
v_grid = float(np.median(np.diff(front[5:])))

c = 1.0
v_model = c
v_frame = 0.5 * c
v_prime = (v_model - v_frame) / (1.0 - v_model * v_frame / c**2)

print("=" * 62)
print("格点层: dx/dt 中位数(右向前缘) = %.4f 格/步" % v_grid)
print("公式层: 逆变后 v' = %.6f c (演示用, 非从本核推导)" % v_prime)
print("命题: 闵氏度规/洛伦兹群在此脚本中未由离散更新规则唯一推出。")
print("[OK] critique_04_sr_not_derived")
print("=" * 62)

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(front, "b.-")
ax.set_xlabel("step")
ax.set_ylabel("rightmost active x")
ax.set_title("Causal front (CE) vs Lorentz formula (text layer) — not a derivation")
ax.grid(alpha=0.25)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_critique_04_sr_not_derived.png")
plt.savefig(out, dpi=120, bbox_inches="tight")
print("Saved: %s" % out)
