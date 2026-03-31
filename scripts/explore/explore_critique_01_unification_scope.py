# -*- coding: utf-8 -*-
"""
质疑01（学术表述边界）：「统一 QM 与相对论」在现行标准下需可审计对标。
输出：清单图 + 固定标记行供 run_unified_suite 解析。
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import mpl_compat  # noqa: F401

LINES = [
    "不能仅凭叙事宣称「统一」；须给出：",
    "1) 物理量：哪些可观测量被计算/测量；",
    "2) 定理：对标哪条教科书定理（编号/假设）；",
    "3) 误差：与实验或解析的差及不确定度；",
    "4) 自由度：可调参数个数、是否过拟合；",
    "5) 若缺任一项 → 宜表述为类比/趋势，而非「已统一」.",
]

print("=" * 62)
for s in LINES:
    print(s)
print("[OK] critique_01_unification_scope")
print("=" * 62)

fig, ax = plt.subplots(figsize=(10, 5))
ax.axis("off")
y = 0.92
for s in LINES:
    ax.text(0.04, y, s, fontsize=11, va="top", transform=ax.transAxes)
    y -= 0.14
ax.set_title("Critique 01: scope for claiming unification", fontsize=12)
out = os.path.join(os.path.dirname(__file__), "explore_critique_01_unification_scope.png")
plt.savefig(out, dpi=120, bbox_inches="tight", facecolor="white")
print("Saved: %s" % out)

from experiment_dossier import emit_case_dossier

emit_case_dossier(
    __file__,
    constants={"lines_in_figure": len(LINES)},
    observed={"checklist_items_printed": len(LINES)},
    artifacts=["explore_critique_01_unification_scope.png"],
)
