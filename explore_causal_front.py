"""
explore_causal_front.py
-----------------------
無障礙 2D 點源：右向「因果前」最遠到達列 x_max(step)。
用於把「局域最大推進」說成可測的量，而非口號。

运行: python explore_causal_front.py
输出: explore_causal_front.png
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from ce_engine_v2 import propagate_double_slit_n_steps

HEIGHT = 151
WIDTH = 320
A, S, B, LAM = 1.0, 0.12, 0.01, 0.97
SOURCE_X = 8
SOURCE_Y = HEIGHT // 2
STEPS = 120
THRESH = 1e-8

# 无边栏：全程可穿行
barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1.0

front = []
total_e = []
for t in range(STEPS + 1):
    col_max = grid.max(axis=0)
    hit = np.where(col_max > THRESH)[0]
    x_right = int(hit.max()) if hit.size else SOURCE_X
    front.append(x_right)
    total_e.append(float(grid.sum()))
    if t < STEPS:
        grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, 1)

front = np.array(front, dtype=np.float64)
vel = np.diff(front)
print("=" * 60)
print("无障碍点源：右边界最远激活列 x_right(t)")
print(f"dx/dt 中位数（格/步）≈ {np.median(vel):.4f}  (纯 +x 理论上限受 A 分配与对角项影响)")
print(f"首末 x_right: {front[0]:.0f} -> {front[-1]:.0f}  over {STEPS} steps")
print(f"sum(E) 初末: {total_e[0]:.6g} -> {total_e[-1]:.6g} (lam={LAM})")
print(
    "注意: 本引擎未全局归一，能量分裂到多格常使 sum(E) 猛增；"
    "本脚本只看因果前缘 x_right(t)，勿把 sum(E) 当概率守恒。"
)
print("=" * 60)

plt.figure(figsize=(8, 4))
plt.plot(front, "b.-", lw=2)
plt.xlabel("step t")
plt.ylabel("rightmost active column index")
plt.title("Causal front (max x with E>thresh)")
plt.grid(alpha=0.3)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_causal_front.png")
plt.savefig(out, dpi=140)
print(f"Saved: {out}")
