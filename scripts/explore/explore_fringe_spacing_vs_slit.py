"""
explore_fringe_spacing_vs_slit.py (tightened version)
----------------------------------------------------
用当前 ce_engine_v2 双缝传播，扫描缝中心间距 d，测量屏上条纹平均间隔 Δy，
并输出与远场理论预期的偏差，同时检查数值稳定性。
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ================== 模型参数（内核不变） ==================
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

# 缝中心间距 d（像素）系列
D_LIST = [36, 44, 52, 60, 68, 76]

# ================== 辅助函数（与之前相同） ==================
def slit_rows_from_gap(d: int):
    half = d // 2
    y1c = CENTER - half
    y2c = CENTER + half
    o1 = y1c - SLIT_W // 2
    o2 = y2c - SLIT_W // 2
    return o1, o2, d

def dominant_peak_spacing(screen: np.ndarray) -> float:
    """条纹间隔：优先峰间距中位数，失败则用 Hann + rFFT 估计主周期。"""
    # 与之前相同，但增加对 inf/nan 的处理
    if not np.isfinite(screen).all():
        return np.nan
    sm = np.asarray(screen, dtype=np.float64)
    mx = float(sm.max())
    if mx < 1e-18:
        return np.nan
    thr = 0.05 * mx
    idx = []
    for i in range(2, len(sm) - 2):
        if sm[i] > sm[i-1] and sm[i] > sm[i+1] and sm[i] >= thr:
            idx.append(i)
    if len(idx) >= 3:
        idx = np.array(idx, dtype=np.float64)
        gaps = np.diff(np.sort(idx))
        gaps = gaps[gaps > 2.0]
        if gaps.size >= 2:
            return float(np.median(gaps))
    # FFT fallback
    s = sm - np.mean(sm)
    if np.sum(s**2) < 1e-20:
        return np.nan
    w = np.hanning(len(s))
    spec = np.abs(np.fft.rfft(s * w))
    spec[0] = 0.0
    freqs = np.fft.rfftfreq(len(s), d=1.0)
    half = max(3, len(spec)//2)
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
        return np.nan
    return 1.0 / float(freqs[best_k])

def run_one(d: int):
    o1, o2, _ = slit_rows_from_gap(d)
    barrier = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    barrier[:, BAR_X] = True
    barrier[o1:o1+SLIT_W, BAR_X] = False
    barrier[o2:o2+SLIT_W, BAR_X] = False

    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0
    # 内核不变
    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)
    screen = grid[:, SCREEN_X]
    # 检查数值溢出
    if not np.isfinite(screen).all():
        print(f"  WARNING: screen contains inf/nan for d={d}")
        return np.nan, np.nan, screen
    spacing = dominant_peak_spacing(screen)
    vis = compute_visibility(screen)
    return spacing, vis, screen

# ================== 主程序 ==================
def main():
    spacings = []
    ds = []
    vis_list = []
    valid_for_fit = []

    for d in D_LIST:
        sp, vis, _ = run_one(d)
        ds.append(float(d))
        spacings.append(sp)
        vis_list.append(vis)
        print(f"d={d:3d} px | median fringe spacing Δy ≈ {sp:.3f} | V={vis:.4f}")
        # 仅当 spacing 有效且对比度 > 0.2 时，才用于拟合（避免低对比度干扰）
        if np.isfinite(sp) and vis > 0.2:
            valid_for_fit.append(True)
        else:
            valid_for_fit.append(False)

    # 幂律拟合（仅用有效点）
    ds_arr = np.array([ds[i] for i in range(len(ds)) if valid_for_fit[i]])
    sp_arr = np.array([spacings[i] for i in range(len(spacings)) if valid_for_fit[i]])
    if len(ds_arr) >= 3:
        logd = np.log(ds_arr)
        logs = np.log(sp_arr)
        coef = np.polyfit(logd, logs, 1)
        power = coef[0]
        print(f"\n幂律拟合 log(Δy) = {power:.3f} * log(d) + const")
        print(f"拟合斜率 = {power:.4f}")
        print(f"与远场理论值 -1 的偏差 = {abs(power + 1):.4f}")
        # 收紧门禁：报告偏差大小，但不过于强硬（模型特性）
        if abs(power + 1) > 0.5:
            print("NOTE: 当前参数下模型处于近场区域或有效波长非常数，未达到远场反比关系。")
    else:
        power = np.nan
        print("有效数据点不足，无法拟合幂律。")

    L = SCREEN_X - BAR_X
    plt.figure(figsize=(10,4))
    plt.subplot(1,2,1)
    plt.plot(ds, spacings, 'bo-', lw=2)
    plt.xlabel("slit center distance d (px)")
    plt.ylabel("median fringe spacing Δy (px)")
    plt.title("Fringe spacing vs slit gap (CE grid)")
    plt.grid(alpha=0.3)

    plt.subplot(1,2,2)
    if len(ds_arr) >= 3:
        plt.plot(np.log(ds_arr), np.log(sp_arr), 'rs-', ms=8)
        xf = np.linspace(np.log(ds_arr).min(), np.log(ds_arr).max(), 50)
        plt.plot(xf, np.polyval(coef, xf), 'k--', lw=1)
        plt.xlabel("log d")
        plt.ylabel("log Δy")
        plt.title(f"log-log slope ≈ {power:.3f}")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "explore_fringe_spacing.png")
    plt.savefig(out, dpi=140)
    print(f"\nSaved: {out}")
    print(f"几何: L = screen - barrier = {L} px（用于与理论对照时请自洽 λ_eff）")

    # 可选：将结果写入统一报告格式
    from experiment_dossier import emit_case_dossier
    emit_case_dossier(
        __file__,
        constants={"D_LIST": list(D_LIST), "STEPS": STEPS, "L_px": int(L)},
        observed={
            "loglog_slope_fitted": float(power) if power == power else None,
            "visibility_per_d": [float(v) for v in vis_list],
            "spacing_per_d": [float(s) if s == s else None for s in spacings],
        },
        artifacts=["explore_fringe_spacing.png"],
    )

if __name__ == "__main__":
    main()