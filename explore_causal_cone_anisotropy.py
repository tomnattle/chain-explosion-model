# -*- coding: utf-8 -*-
"""
explore_causal_cone_anisotropy.py
--------------------------------
质疑命题（盲人摸象里的「边界打卡」）：
  连续狭义相对论里，惯性系下光锥对称；你叙事里「c = 局域最大传播」在具体 CE 核心里
  是否各向同性？

测量（无挡板点源）：
  - R_plus:  沿 +x 最远超前缘的曼哈顿步数近似（用最右激活列 - x0）。
  - R_diag:  同时看 |dx|+|dy|意义下的「远角」——用激活格点到源点的 L1 距离最大值。
  - 打印 各向异性比 R_diag / (R_plus + eps) 及若干步后的采样。

失败语义：无。只记录现象；若比显著偏离 1，说明「不能把当前格子核直接等同于
  洛伦兹群的 SO(3) 截面」，公式层与网格层要分层叙述。

运行: python explore_causal_cone_anisotropy.py
输出: explore_causal_cone_anisotropy.png
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import propagate_double_slit_n_steps

HEIGHT = 151
WIDTH = 320
A, S, B, LAM = 1.0, 0.12, 0.01, 0.97
SOURCE_X = 8
SOURCE_Y = HEIGHT // 2
STEPS = 120
THRESH = 1e-10

barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)

grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1.0

rplus_hist = []
rdiag_hist = []
rat_hist = []

for t in range(STEPS + 1):
    ys, xs = np.where(grid > THRESH)
    if xs.size == 0:
        rplus = 0.0
        rdiag = 0.0
    else:
        rplus = float(np.max(xs) - SOURCE_X)
        l1 = np.abs(xs - SOURCE_X) + np.abs(ys - SOURCE_Y)
        rdiag = float(np.max(l1))
    rplus_hist.append(rplus)
    rdiag_hist.append(rdiag)
    rat_hist.append(rdiag / (rplus + 0.5))

    if t < STEPS:
        grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, 1)

rplus_hist = np.array(rplus_hist, dtype=np.float64)
rdiag_hist = np.array(rdiag_hist, dtype=np.float64)
rat_hist = np.array(rat_hist, dtype=np.float64)
vr = np.diff(rplus_hist)
vd = np.diff(rdiag_hist)

print("=" * 62)
print("质疑向：CE 内核因果前缘各向异性（对「光锥各向同性」的对照）")
print("R_plus = max(x)-x0  (右向前走); R_L1_max = max |dx|+|dy| (角向+轴向混合)")
print("各向异性比 median(R_L1_max / (R_plus+0.5)) = %.4f" % np.median(rat_hist[10:]))
print("dR_plus/dt 中位数 = %.4f 格/步" % np.median(vr[5:]))
print("dR_L1_max/dt 中位数 = %.4f 格/步" % np.median(vd[5:]))
print(
    "解读: 比≈1 不保证洛伦兹群成立；比明显偏离 1 则说明离散邻居权重≠各向同性度规。"
)
print("=" * 62)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(rplus_hist, label="R_plus (max x - x0)", lw=2)
ax.plot(rdiag_hist, label="R_L1_max", lw=2)
ax.set_xlabel("step")
ax.set_ylabel("reach (cells)")
ax.set_title("Causal reach: cardinal vs L1-max (anisotropy probe)")
ax.grid(alpha=0.25)
legend_kw(ax, facecolor="white", labelcolor="black", fontsize=9)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_causal_cone_anisotropy.png")
plt.savefig(out, dpi=140)
print("Saved: %s" % out)

from experiment_dossier import emit_case_dossier

emit_case_dossier(
    __file__,
    constants={"HEIGHT": HEIGHT, "WIDTH": WIDTH, "A": A, "S": S, "B": B, "LAM": LAM, "STEPS": STEPS},
    observed={
        "median_anisotropy_ratio_R_L1_over_Rplus": float(np.median(rat_hist[10:])),
        "median_dRplus_dt": float(np.median(vr[5:])),
        "median_dR_L1_dt": float(np.median(vd[5:])),
    },
    artifacts=["explore_causal_cone_anisotropy.png"],
)
