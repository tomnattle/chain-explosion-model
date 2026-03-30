# -*- coding: utf-8 -*-
"""
质疑02：纠缠/坍缩叙事在 Bell-type 实验面前只能是工作假说或类比，不能直接当结论。
本脚本不跑满混沌 Bell 扫描，只把边界写死到回归输出。
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import mpl_compat  # noqa: F401

BOX = (
    "Bell / CHSH 实验：违反不等式支持量子相关，非定域；\n"
    "格点 toy 模型的「纠缠/坍缩」诠释必须与 CHSH 数值结果\n"
    "同批对照后才能升格为结论；否则仅限 working hypothesis.\n"
    "仓库内若有 ce_bell* 可作工程探针，但不可替代实验裁决."
)

print("=" * 62)
print(BOX.replace("\n", " "))
print("[OK] critique_02_bell_boundary")
print("=" * 62)

fig, ax = plt.subplots(figsize=(9, 4))
ax.axis("off")
ax.text(0.5, 0.5, BOX, fontsize=11, va="center", ha="center", ma="left", transform=ax.transAxes)
ax.set_title("Critique 02: Bell experiments vs narrative", fontsize=12)
out = os.path.join(os.path.dirname(__file__), "explore_critique_02_bell_hypothesis.png")
plt.savefig(out, dpi=120, bbox_inches="tight", facecolor="#f6f8fa")
print("Saved: %s" % out)
