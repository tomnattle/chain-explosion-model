# -*- coding: utf-8 -*-
"""
verify_uncertainty.py
单缝缝宽 vs 屏上展宽（不确定性叙事的「现象记录」）
====================================================
标准 QM 常写成 Δy·Δp_y ~ 单缝角尺度 ~ λ/a（展宽 ~ 1/a）。

本脚本使用的信道：
  - ce_engine_v2.propagate_double_slit_n_steps：非负实能量、局域分裂规则（A/S/B/λ），
    与 ce_*.py 主线一致。
  - 说明：ce_engine_v2.propagate_with_real_phase 在当前「先穿过竖直栅栏缝」几何下，
    易出现相干相消、归一化后远屏可忽略，不适合作稳定拟合；若将来为单缝给出专用相干步进，
    可再对接。

可观测量：
  - 缝宽 a（格点）；屏上强度二矩 σ_y；σ_θ = atan(σ_y / L)，L 为缝到屏的格距。

拟合 log σ_θ vs log a 得幂律指数 α。离散标量扩散信道**不承诺**教科书 −1 幂律；
run_unified_suite 中本项**仅要求 PNG + 打印 α**，不设与 -1 的硬门禁。
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import propagate_double_slit_n_steps

HEIGHT = 401
WIDTH = 400
A = 1.0
S = 0.30
B = 0.05
LAM = 0.92
SOURCE_X = 5
SOURCE_Y = HEIGHT // 2
BAR_X = 150
SCREEN_X = WIDTH - 20
STEPS = 600

SLIT_WIDTHS = [2, 4, 6, 8, 12, 16, 24, 32]

print("=" * 65)
print("验证C：单缝缝宽 vs 屏上角展宽（标量能量信道，现象记录）")
print("扫描缝宽: %s 格点" % (SLIT_WIDTHS,))
print("=" * 65)

results = []

for slit_w in SLIT_WIDTHS:
    slit_y_center = HEIGHT // 2
    slit_y0 = slit_y_center - slit_w // 2
    slit_y1 = slit_y0 + slit_w

    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0

    barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    barrier[:, BAR_X] = True
    barrier[slit_y0:slit_y1, BAR_X] = False

    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)

    screen = grid[:, SCREEN_X].copy()
    total = screen.sum()

    if total < 1e-6:
        print("  缝宽=%d: 无能量到屏，跳过" % slit_w)
        continue

    y_positions = np.arange(HEIGHT, dtype=np.float64)
    mean_y = np.sum(y_positions * screen) / total
    sigma_y = np.sqrt(np.sum((y_positions - mean_y) ** 2 * screen) / total)

    L = float(SCREEN_X - BAR_X)
    sigma_theta = np.arctan(sigma_y / L)

    results.append(
        {
            "slit_w": slit_w,
            "sigma_screen": sigma_y,
            "sigma_theta_deg": np.degrees(sigma_theta),
            "screen": screen.copy(),
            "total": total,
        }
    )

    print(
        "  缝宽=%2d  sigma_y=%.1f px  sigma_theta=%.2f deg  能量=%.1f"
        % (slit_w, sigma_y, np.degrees(sigma_theta), total)
    )

if len(results) < 2:
    raise SystemExit("数据点不足，无法拟合（请检查参数/几何）")

widths = np.array([r["slit_w"] for r in results], dtype=float)
sigmas = np.array([r["sigma_theta_deg"] for r in results], dtype=float)

log_w = np.log(widths)
log_s = np.log(sigmas + 1e-9)
coeffs = np.polyfit(log_w, log_s, 1)
alpha_fit = float(coeffs[0])

print("\n幂律指数 α = %.4f" % alpha_fit)
print("拟合: sigma_theta 比例于 a^%.3f" % alpha_fit)
print(
    "偏差 |alpha - (-1)| = %.3f（仅为对照；本信道不设硬阈）"
    % abs(alpha_fit - (-1.0))
)

theory_const = float(np.mean(np.log(sigmas + 1e-9) - (-1.0) * log_w))

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.patch.set_facecolor("#0d1117")
for ax in axes.flat:
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values():
        spine.set_color("#30363d")

y_axis = np.arange(HEIGHT) - SOURCE_Y
cmap = plt.cm.plasma
colors = [cmap(i / len(results)) for i in range(len(results))]

ax = axes[0][0]
for i, r in enumerate(results):
    s = r["screen"]
    ax.plot(
        y_axis,
        s / (s.max() + 1e-9),
        color=colors[i],
        linewidth=1.2,
        alpha=0.85,
        label="a=%d" % r["slit_w"],
    )
ax.set_title("各缝宽的屏上强度", color="white", fontsize=11)
ax.set_xlabel("Y（相对中心）", color="#8b949e")
ax.set_ylabel("归一强度", color="#8b949e")
legend_kw(ax, facecolor="#161b22", fontsize=7, ncol=2, loc="upper right")
ax.grid(True, alpha=0.15, color="#30363d")

ax = axes[0][1]
ax.scatter(widths, sigmas, color="#58a6ff", s=80, zorder=5)
w_fit = np.linspace(widths.min(), widths.max(), 100)
s_fit = np.exp(np.polyval(coeffs, np.log(w_fit)))
ax.plot(
    w_fit,
    s_fit,
    color="#f78166",
    linestyle="--",
    linewidth=2,
    label="fit alpha=%.2f" % alpha_fit,
)
ax.set_title("sigma_theta vs 缝宽 a", color="white", fontsize=11)
ax.set_xlabel("a（格点）", color="#8b949e")
ax.set_ylabel("sigma_theta (deg)", color="#8b949e")
legend_kw(ax, facecolor="#161b22")
ax.grid(True, alpha=0.15, color="#30363d")

ax = axes[1][0]
ax.scatter(log_w, log_s, color="#58a6ff", s=80, zorder=5, label="CE data")
ax.plot(
    log_w,
    np.polyval(coeffs, log_w),
    color="#f78166",
    linestyle="--",
    linewidth=2,
    label="fit alpha=%.2f" % alpha_fit,
)
ax.plot(
    log_w,
    -1.0 * log_w + theory_const,
    color="#3fb950",
    linestyle=":",
    linewidth=2,
    label="reference alpha=-1",
)
ax.set_title("log-log", color="white", fontsize=11)
ax.set_xlabel("log(a)", color="#8b949e")
ax.set_ylabel("log(sigma_theta)", color="#8b949e")
legend_kw(ax, facecolor="#161b22")
ax.grid(True, alpha=0.15, color="#30363d")

ax = axes[1][1]
uncertainty_products = widths * sigmas
ax.scatter(widths, uncertainty_products, color="#ffa657", s=80, zorder=5)
mean_product = np.mean(uncertainty_products)
ax.axhline(
    mean_product,
    color="#f78166",
    linestyle="--",
    linewidth=2,
    label="mean a*sigma=%.2f" % mean_product,
)
ax.set_title("a * sigma_theta", color="white", fontsize=11)
ax.set_xlabel("a", color="#8b949e")
ax.set_ylabel("a * sigma_theta", color="#8b949e")
std_product = np.std(uncertainty_products)
ax.text(
    0.05,
    0.95,
    "CV = %.3f" % (std_product / (mean_product + 1e-12),),
    transform=ax.transAxes,
    color="white",
    fontsize=10,
    va="top",
    bbox=dict(boxstyle="round", facecolor="#161b22", alpha=0.8),
)
legend_kw(ax, facecolor="#161b22")
ax.grid(True, alpha=0.15, color="#30363d")

plt.suptitle(
    "验证C：缝宽 vs 展宽（现象记录，alpha=%.3f）" % alpha_fit,
    color="white",
    fontsize=13,
)
plt.tight_layout()
plt.savefig("verify_uncertainty.png", dpi=150, bbox_inches="tight", facecolor="#0d1117")
print("\n图片已保存: verify_uncertainty.png")
print("=" * 65)
