# -*- coding: utf-8 -*-
"""
explore_double_slit_mirror_parity.py
------------------------------------
质疑命题：几何与源关于中心水平轴镜像对称时，屏上强度 I(y) 应近似满足 I(y)≈I(2y0-y)。
标量 CE 核如果意外带「手征」或数值偏置，残差会偏大。

度量（相对 L1 残差）:
  相对不对称度 asym = sum_y |I(y)-I_mirror(y)| / (sum_y I(y) + eps)

运行: python explore_double_slit_mirror_parity.py
输出: explore_double_slit_mirror_parity.png

suite 解析:
  相对不对称度 asym = <float>
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import propagate_double_slit_n_steps

HEIGHT = 201
WIDTH = 400
A, S, B, LAM = 1.0, 0.30, 0.05, 0.90
SOURCE_X = 5
SOURCE_Y = HEIGHT // 2
BAR_X = 150
SLIT_W = 6
SCREEN_X = WIDTH - 15
STEPS = 500

cy = HEIGHT // 2
d_half = 25
slit1_y0 = cy - d_half - SLIT_W // 2
slit2_y0 = cy + d_half - SLIT_W // 2

barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
barrier[:, BAR_X] = True
barrier[slit1_y0 : slit1_y0 + SLIT_W, BAR_X] = False
barrier[slit2_y0 : slit2_y0 + SLIT_W, BAR_X] = False

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1000.0

grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)

I = grid[:, SCREEN_X].astype(np.float64)
total = I.sum()
if total < 1e-12:
    print("无能量到屏")
    sys.exit(2)

Im = I[::-1]
num = np.sum(np.abs(I - Im))
den = total + 1e-15
asym = float(num / den)
if np.std(I) > 1e-15:
    r_m = float(np.corrcoef(I, Im)[0, 1])
else:
    r_m = 1.0

print("=" * 60)
print("质疑向：双缝几何镜像对称 → 屏强度镜像残差（宇称/后向耦合探针）")
print("相对不对称度 asym = %.6f" % asym)
print("镜像皮尔逊 r_mirror = %.6f" % r_m)
print(
    "解读: A/B/S 核在 B>0 时一般不保证关于缝中心的严格 y-镜面对称；"
    "asym 偏大可能是可测后果，未必是几何画错。"
)
print("=" * 60)

fig, ax = plt.subplots(figsize=(8, 4))
y = np.arange(HEIGHT) - SOURCE_Y
ax.plot(y, I / (I.max() + 1e-15), label="I(y)", lw=1.5)
ax.plot(y, Im / (Im.max() + 1e-15), "--", label="I_mirr(y)", lw=1.5, alpha=0.8)
ax.set_xlabel("y relative to source row")
ax.set_ylabel("normalized")
ax.set_title("Mirror parity check @ screen x=%d" % SCREEN_X)
ax.grid(alpha=0.25)
legend_kw(ax, facecolor="white", labelcolor="black", fontsize=9)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_double_slit_mirror_parity.png")
plt.savefig(out, dpi=140)
print("Saved: %s" % out)
