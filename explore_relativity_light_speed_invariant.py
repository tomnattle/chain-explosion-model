# -*- coding: utf-8 -*-
"""
explore_relativity_light_speed_invariant.py
-------------------------------------------
质疑命题：教材里「光速与源速度无关」是公式层结论；本脚本**只做公式层数值自检**，
与 CE 格子传播**解耦**——避免把 relativity_final 里的 np.roll 玩具与 A/S/B 核混为一谈。

与 relativity_final.py 同款检验：v_model=c 时洛伦兹逆变 v' 应仍为 c（自然单位 c=1）。

运行: python explore_relativity_light_speed_invariant.py
输出: explore_relativity_light_speed_invariant.png

suite 解析行（勿改格式关键词）:
  洛伦兹逆变 v' = <float> c
  [OK] formula_layer v_prime_vs_c
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw

SIZE = 400
x = np.arange(SIZE)
x0, sigma = 50, 5
pulse = np.exp(-((x - x0) ** 2) / (2 * sigma**2))
pulse /= np.sum(pulse)

c = 1.0
STEPS = 200
history = []

for _ in range(STEPS):
    pulse = np.roll(pulse, int(c))
    pulse[0] = 0
    history.append(pulse.copy())


def com_ix(p):
    xx = np.arange(len(p), dtype=np.float64)
    s = np.sum(p)
    return float(np.sum(xx * p) / s) if s > 1e-15 else 0.0


com0 = com_ix(history[0])
com1 = com_ix(history[-1])
v_track = (com1 - com0) / STEPS
v_model = c
v_frame = 0.5 * c
v_transformed = (v_model - v_frame) / (1.0 - v_model * v_frame / c**2)

print("=" * 60)
print("公式层：局域 c 与洛伦兹逆变（与格子核分开叙述）")
print("质心跟踪 v_track = %.6f c（离散高斯会有小数噪声）" % v_track)
print("模型设定 v_model = %.6f c" % v_model)
# 下行供 run_unified_suite 正则解析（数字与 c 之间空一格）
print("洛伦兹逆变 v' = %.9f c" % v_transformed)
ok = abs(v_transformed - c) < 1e-9
if ok:
    print("[OK] formula_layer v_prime_vs_c")
else:
    print("[FAIL] formula_layer v_prime_vs_c")
print("=" * 60)

fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
ax.plot(history[0], label="t=0", lw=2)
ax.plot(history[100], label="t=100", lw=2)
ax.plot(history[-1], label="t=%d" % (len(history) - 1), lw=2)
ax.axvline(int(round(com0)), color="k", linestyle="--", alpha=0.4, label="COM t=0")
ax.set_xlabel("x")
ax.set_ylabel("normalized")
ax.set_title("Toy: np.roll pulse (formula check only; not ce_engine kernel)")
ax.grid(alpha=0.3)
legend_kw(ax, facecolor="white", labelcolor="black", fontsize=8)
plt.tight_layout()
out = os.path.join(
    os.path.dirname(__file__), "explore_relativity_light_speed_invariant.png"
)
plt.savefig(out, dpi=140)
print("Saved: %s" % out)

if not ok:
    sys.exit(1)
