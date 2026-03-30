# -*- coding: utf-8 -*-
"""
质疑05：干涉/可见度随距离的衰减可被「简单全局均匀损耗」大量模仿；
需报告「轨迹相似度」以量化不可替代性缺口。
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import mpl_compat  # noqa: F401
from ce_engine_v2 import propagate_double_slit, compute_visibility

HEIGHT = 301
WIDTH = 800
A, S, B, LAM = 1.0, 0.25, 0.04, 0.95
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
BAR_X = 180
SLIT1_Y = HEIGHT // 2 - 25
SLIT2_Y = HEIGHT // 2 + 25
SLIT_W = 6
STEPS_PER_100PX = 150
screen_x_list = [300, 400, 500, 600, 700]
ETA = 0.008


def build_barrier():
    b = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    b[:, BAR_X] = True
    b[SLIT1_Y : SLIT1_Y + SLIT_W, BAR_X] = False
    b[SLIT2_Y : SLIT2_Y + SLIT_W, BAR_X] = False
    return b


def run_vis(apply_loss):
    barrier = build_barrier()
    vis = []
    for sx in screen_x_list:
        steps = max(20, (sx - SOURCE_X) * STEPS_PER_100PX // 100)
        grid = np.zeros((HEIGHT, WIDTH))
        grid[SOURCE_Y, SOURCE_X] = 1200.0
        for _ in range(steps):
            grid = propagate_double_slit(grid, barrier, A, S, B, LAM)
            if apply_loss:
                grid *= 1.0 - ETA
        vis.append(compute_visibility(grid[:, sx]))
    return np.array(vis, dtype=np.float64)


v0 = run_vis(False)
v1 = run_vis(True)
if np.std(v0) > 1e-12 and np.std(v1) > 1e-12:
    r_v = float(np.corrcoef(v0, v1)[0, 1])
else:
    r_v = float("nan")
rmse = float(np.sqrt(np.mean((v0 - v1) ** 2)))

print("=" * 62)
print("可见度 V(L): CE 纯传播 vs CE+全局均匀损耗 (每步 eta=%.4f)" % ETA)
print("V 轨迹皮尔逊 r_V_ce_vs_uniform = %.4f" % r_v)
print("RMSE(V|base - V|loss) = %.4f" % rmse)
print("解读: r_V 越接近 1，则「仅靠 V」越难区分机理；需用 sum(I) 等额外量。")
print("[OK] critique_05_decay_nonuniqueness")
print("=" * 62)

dist = np.array([x - BAR_X for x in screen_x_list], dtype=np.float64)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(dist, v0, "b-o", label="CE only")
ax.plot(dist, v1, "r--s", label="CE + uniform loss")
ax.set_xlabel("L (px)")
ax.set_ylabel("V")
ax.set_title("Nonuniqueness: similar V decay channels")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_critique_05_decay_nonuniqueness.png")
plt.savefig(out, dpi=120, bbox_inches="tight")
print("Saved: %s" % out)
