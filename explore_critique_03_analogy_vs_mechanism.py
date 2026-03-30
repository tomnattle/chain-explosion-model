# -*- coding: utf-8 -*-
"""
质疑03：禁止「完整复现/底层统一」式过度声称；区分类比 vs 同一机制。
推荐措辞写进回归，便于与论文/对外表述对齐。
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import mpl_compat  # noqa: F401

REC = [
    "可接受: 「观察到类似行为」「趋势与 WKB/标度一致」",
    "需禁止: 「已完整复现量子力学」「底层统一」而无对标与误差",
    "明确写: 类比 (analogy) / 同一物理机制 (identical mechanism)",
]

print("=" * 62)
for r in REC:
    print(r)
print("[OK] critique_03_analogy_language")
print("=" * 62)

fig, ax = plt.subplots(figsize=(9, 3.5))
ax.axis("off")
y = 0.85
for r in REC:
    ax.text(0.05, y, "- %s" % r, fontsize=11, va="top", transform=ax.transAxes)
    y -= 0.28
ax.set_title("Critique 03: analogy vs identical mechanism", fontsize=12)
out = os.path.join(os.path.dirname(__file__), "explore_critique_03_analogy_vs_mechanism.png")
plt.savefig(out, dpi=120, bbox_inches="tight", facecolor="white")
print("Saved: %s" % out)
