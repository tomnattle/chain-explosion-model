# -*- coding: utf-8 -*-
"""
质疑07：远场双缝 log-log 斜率期望约 -1；CE 网格常得偏离(如 ~-0.12)，须显式记录偏差。
（逻辑与 explore_fringe_spacing_vs_slit 一致，输出增加 reference 与 deviation.）
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import mpl_compat  # noqa: F401
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

HEIGHT = 301
WIDTH = 550
A, S, B, LAM = 1.0, 0.28, 0.05, 0.96
SOURCE_X = 8
SOURCE_Y = HEIGHT // 2
BAR_X = 150
SCREEN_X = WIDTH - 30
SLIT_W = 5
STEPS = 620
CENTER = SOURCE_Y
D_LIST = [36, 44, 52, 60, 68, 76]
REFERENCE_LOG_SLOPE = -1.0


def slit_rows_from_gap(d):
    half = d // 2
    y1c = CENTER - half
    y2c = CENTER + half
    o1 = y1c - SLIT_W // 2
    o2 = y2c - SLIT_W // 2
    return o1, o2


def dominant_peak_spacing(screen):
    sm = np.asarray(screen, dtype=np.float64)
    mx = float(sm.max())
    if mx < 1e-18:
        return float("nan")
    thr = 0.05 * mx
    idx = []
    for i in range(2, len(sm) - 2):
        if sm[i] > sm[i - 1] and sm[i] > sm[i + 1] and sm[i] >= thr:
            idx.append(i)
    if len(idx) >= 3:
        idx = np.array(idx, dtype=np.float64)
        gaps = np.diff(np.sort(idx))
        gaps = gaps[gaps > 2.0]
        if gaps.size >= 2:
            return float(np.median(gaps))
    s = sm - np.mean(sm)
    if np.sum(s ** 2) < 1e-20:
        return float("nan")
    w = np.hanning(len(s))
    spec = np.abs(np.fft.rfft(s * w))
    spec[0] = 0.0
    freqs = np.fft.rfftfreq(len(s), d=1.0)
    half = max(3, len(spec) // 2)
    best_k, best_m = -1, -1.0
    lo, hi = 4.0, 0.42 * len(s)
    for k in range(1, half):
        f = float(freqs[k])
        if f <= 1e-12:
            continue
        per = 1.0 / f
        if not (lo <= per <= hi):
            continue
        if spec[k] > best_m:
            best_m = spec[k]
            best_k = k
    if best_k < 0 or best_m <= 0:
        return float("nan")
    return 1.0 / float(freqs[best_k])


def run_one(d):
    o1, o2 = slit_rows_from_gap(d)
    barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    barrier[:, BAR_X] = True
    barrier[o1 : o1 + SLIT_W, BAR_X] = False
    barrier[o2 : o2 + SLIT_W, BAR_X] = False
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0
    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)
    screen = grid[:, SCREEN_X]
    return dominant_peak_spacing(screen), compute_visibility(screen)


spacings, ds = [], []
for d in D_LIST:
    sp, vis = run_one(d)
    spacings.append(sp)
    ds.append(float(d))
    print("d=%3d | spacing=%.3f | V=%.4f" % (d, sp, vis))

ds = np.array(ds)
sp = np.array(spacings)
valid = np.isfinite(sp) & (sp > 0) & (ds > 0)
if valid.sum() < 3:
    print("拟合点不足")
    from experiment_dossier import emit_case_dossier

    emit_case_dossier(
        __file__,
        constants={"D_LIST": D_LIST, "REFERENCE_LOG_SLOPE": REFERENCE_LOG_SLOPE},
        observed={
            "valid_fit_points": int(valid.sum()),
            "verdict": "insufficient_data_exit_2",
        },
        artifacts=[],
    )
    sys.exit(2)

logd = np.log(ds[valid])
logs = np.log(sp[valid])
coef = np.polyfit(logd, logs, 1)
fitted = float(coef[0])
dev = float(fitted - REFERENCE_LOG_SLOPE)

print("=" * 62)
print("标准远场 log-log 斜率期望 reference_log_slope = %.1f" % REFERENCE_LOG_SLOPE)
print("拟合斜率 fitted_log_slope = %.4f" % fitted)
print("偏差 deviation = fitted - reference = %.4f" % dev)
print("解读: |dev| 大说明条纹标度与教科书远场双缝尚未对齐, 非 runner 硬失败条件.")
print("[OK] critique_07_fringe_theory_gap")
print("=" * 62)

L = SCREEN_X - BAR_X
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(ds[valid], sp[valid], "bo-", lw=2)
ax[0].set_xlabel("d (px)")
ax[0].set_ylabel("Delta y")
ax[0].set_title("Fringe spacing vs d")
ax[0].grid(alpha=0.3)
ax[1].plot(logd, logs, "rs", ms=8)
xf = np.linspace(logd.min(), logd.max(), 40)
ax[1].plot(xf, np.polyval(coef, xf), "k--", lw=1)
ax[1].plot(xf, REFERENCE_LOG_SLOPE * xf + np.mean(logs - REFERENCE_LOG_SLOPE * logd), "g:", lw=1.5, label="ref -1")
ax[1].set_xlabel("log d")
ax[1].set_ylabel("log spacing")
ax[1].set_title("slope=%.3f vs ref -1" % fitted)
ax[1].legend(fontsize=8)
ax[1].grid(alpha=0.3)
plt.suptitle("Critique 07: theory gap (CE vs far-field -1)", y=1.02)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "explore_critique_07_fringe_theory_gap.png")
plt.savefig(out, dpi=120, bbox_inches="tight")
print("Saved: %s" % out)

from experiment_dossier import emit_case_dossier

emit_case_dossier(
    __file__,
    constants={
        "HEIGHT": HEIGHT,
        "WIDTH": WIDTH,
        "A": A,
        "S": S,
        "B": B,
        "LAM": LAM,
        "STEPS": STEPS,
        "SCREEN_X": SCREEN_X,
        "BAR_X": BAR_X,
        "D_LIST": D_LIST,
        "REFERENCE_LOG_SLOPE": REFERENCE_LOG_SLOPE,
    },
    observed={
        "fitted_log_slope": fitted,
        "deviation_from_reference": dev,
        "spacings": sp.tolist(),
        "d_values": ds.tolist(),
        "valid_points_used": int(valid.sum()),
        "marker": "[OK] critique_07_fringe_theory_gap",
    },
    artifacts=["explore_critique_07_fringe_theory_gap.png"],
    reviewer_prompts=[
        "dominant_peak_spacing 与 FFT 回退两种算法是否系统性偏斜 log-log 斜率？",
    ],
)
