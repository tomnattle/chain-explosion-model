"""
explore_chsh_local_wave_closure_full.py
--------------------------------------
“更不 toy”的局域连续波 CHSH 闭环协议仿真（单文件可运行版）。

显式包含：
- 空间几何与有限传播速度（arrival time = distance / c）
- 设置时序（setting time），并强制局域生效：设置晚于到达则用上一状态
- 连续波局域响应（共享源相位/偏振角 lambda）
- 真实探测器要素：阈值、效率、暗噪声
- coincidence window（仅后筛选模式使用）

输出：
- chsh_local_wave_closure_full.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")


def sign_pm1(x):
    return np.where(x >= 0.0, 1.0, -1.0)


def chsh(Eab, Eabp, Eapb, Eapbp):
    return Eab + Eabp + Eapb - Eapbp


def detector_click_probability(intensity, eta_max, dark_rate, rng):
    """
    用最简单且稳定的模型把连续强度映射到点击概率：
      p = dark_rate + eta_max * intensity / (intensity + 1)
    """
    p = dark_rate + eta_max * intensity / (intensity + 1.0)
    p = np.clip(p, 0.0, 1.0)
    return rng.random(intensity.shape[0]) < p


def run_once(
    n_trials,
    threshold,
    coinc_window,
    seed,
    c_lattice=1.0,
    eta_a=0.85,
    eta_b=0.85,
    dark_rate=0.002,
    setting_jitter=0.25,
    arrival_jitter=0.12,
    readout_noise=0.06,
):
    rng = np.random.default_rng(seed)

    # CHSH canonical settings
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    # geometry (same source, two wings)
    src = np.array([0.0, 0.0])
    detA_pos = np.array([-14.0, 0.0])
    detB_pos = np.array([+15.0, 0.0])
    dA = float(np.linalg.norm(detA_pos - src))
    dB = float(np.linalg.norm(detB_pos - src))
    t_prop_A = dA / c_lattice
    t_prop_B = dB / c_lattice

    # trial clock
    t_emit = np.arange(n_trials, dtype=np.float64)

    # shared source variable (local hidden wave phase/polarization angle)
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)

    # random requested settings per trial
    reqA = rng.integers(0, 2, size=n_trials)  # 0:a, 1:a'
    reqB = rng.integers(0, 2, size=n_trials)  # 0:b, 1:b'

    # setting update times: around emission, can be late vs arrival
    t_set_A = t_emit + rng.normal(0.0, setting_jitter, size=n_trials)
    t_set_B = t_emit + rng.normal(0.0, setting_jitter, size=n_trials)

    # arrival times (finite speed + jitter)
    t_arr_A = t_emit + t_prop_A + rng.normal(0.0, arrival_jitter, size=n_trials)
    t_arr_B = t_emit + t_prop_B + rng.normal(0.0, arrival_jitter, size=n_trials)

    # locality rule: if setting not ready at arrival, detector uses previous stable setting
    effA = np.zeros(n_trials, dtype=np.int64)
    effB = np.zeros(n_trials, dtype=np.int64)
    prevA = 0
    prevB = 0
    lateA = np.zeros(n_trials, dtype=np.bool_)
    lateB = np.zeros(n_trials, dtype=np.bool_)

    for i in range(n_trials):
        if t_set_A[i] <= t_arr_A[i]:
            prevA = int(reqA[i])
        else:
            lateA[i] = True
        if t_set_B[i] <= t_arr_B[i]:
            prevB = int(reqB[i])
        else:
            lateB[i] = True
        effA[i] = prevA
        effB[i] = prevB

    thetaA = np.where(effA == 0, a, ap)
    thetaB = np.where(effB == 0, b, bp)

    # local continuous wave readout (projection + propagation phase)
    # propagation phase included but constant offsets don't create nonlocality
    phiA = lam - thetaA + 0.17 * dA
    phiB = lam - thetaB + 0.17 * dB
    u = np.cos(phiA)
    v = np.cos(phiB)

    # binary outcomes always defined (strict branch no discard)
    A_bin = sign_pm1(u + readout_noise * rng.normal(size=n_trials))
    B_bin = sign_pm1(v + readout_noise * rng.normal(size=n_trials))

    # detector click model (threshold + efficiency + dark count)
    IA = u * u
    IB = v * v
    # threshold gate first
    passA = IA >= threshold
    passB = IB >= threshold
    # then probabilistic detection
    detA = passA & detector_click_probability(IA, eta_a, dark_rate, rng)
    detB = passB & detector_click_probability(IB, eta_b, dark_rate, rng)

    # masks for four setting pairs under effective local settings
    m_ab = (effA == 0) & (effB == 0)
    m_abp = (effA == 0) & (effB == 1)
    m_apb = (effA == 1) & (effB == 0)
    m_apbp = (effA == 1) & (effB == 1)

    # strict mode: no postselection, missed detection mapped to -1
    A_strict = np.where(detA, A_bin, -1.0)
    B_strict = np.where(detB, B_bin, -1.0)
    ABs = A_strict * B_strict

    def mean_mask(arr, mask):
        if np.any(mask):
            return float(np.mean(arr[mask]))
        return 0.0

    Eab_s = mean_mask(ABs, m_ab)
    Eabp_s = mean_mask(ABs, m_abp)
    Eapb_s = mean_mask(ABs, m_apb)
    Eapbp_s = mean_mask(ABs, m_apbp)
    S_strict = float(chsh(Eab_s, Eabp_s, Eapb_s, Eapbp_s))

    # coincidence-postselected mode
    coinc = detA & detB & (np.abs(t_arr_A - t_arr_B) <= coinc_window)
    ABc = A_bin * B_bin

    def mean_post(mask):
        mm = mask & coinc
        if np.any(mm):
            return float(np.mean(ABc[mm]))
        return 0.0

    Eab_c = mean_post(m_ab)
    Eabp_c = mean_post(m_abp)
    Eapb_c = mean_post(m_apb)
    Eapbp_c = mean_post(m_apbp)
    S_post = float(chsh(Eab_c, Eabp_c, Eapb_c, Eapbp_c))

    return {
        "S_strict": S_strict,
        "S_post": S_post,
        "coinc_rate": float(np.mean(coinc)),
        "det_rate_A": float(np.mean(detA)),
        "det_rate_B": float(np.mean(detB)),
        "late_setting_rate": float(np.mean(lateA | lateB)),
    }


def main():
    # preregistered constants
    n_trials = 260000
    threshold_base = 0.22
    window_base = 0.28

    # scan axes
    thr_scan = np.linspace(0.08, 0.82, 16, dtype=np.float64)
    win_scan = np.array([0.05, 0.10, 0.16, 0.24, 0.36, 0.52, 0.75, 1.00], dtype=np.float64)

    # scan threshold at fixed window
    S_strict_thr, S_post_thr, coinc_thr = [], [], []
    for i, thr in enumerate(thr_scan):
        r = run_once(
            n_trials=n_trials,
            threshold=float(thr),
            coinc_window=window_base,
            seed=7000 + i,
        )
        S_strict_thr.append(r["S_strict"])
        S_post_thr.append(r["S_post"])
        coinc_thr.append(r["coinc_rate"])

    # scan window at fixed threshold
    S_strict_win, S_post_win, coinc_win = [], [], []
    for i, w in enumerate(win_scan):
        r = run_once(
            n_trials=n_trials,
            threshold=threshold_base,
            coinc_window=float(w),
            seed=8000 + i,
        )
        S_strict_win.append(r["S_strict"])
        S_post_win.append(r["S_post"])
        coinc_win.append(r["coinc_rate"])

    S_strict_thr = np.asarray(S_strict_thr)
    S_post_thr = np.asarray(S_post_thr)
    coinc_thr = np.asarray(coinc_thr)
    S_strict_win = np.asarray(S_strict_win)
    S_post_win = np.asarray(S_post_win)
    coinc_win = np.asarray(coinc_win)

    max_strict = float(max(np.max(S_strict_thr), np.max(S_strict_win)))
    max_post = float(max(np.max(S_post_thr), np.max(S_post_win)))
    gap = max_post - max_strict

    # single baseline point for textual audit
    base = run_once(
        n_trials=n_trials,
        threshold=threshold_base,
        coinc_window=window_base,
        seed=9001,
    )

    print("CHSH local-wave closure full audit")
    print("base: S_strict=%.5f, S_post=%.5f, coinc_rate=%.4f, late_setting=%.4f" % (
        base["S_strict"], base["S_post"], base["coinc_rate"], base["late_setting_rate"]
    ))
    print("scan max strict S = %.5f" % max_strict)
    print("scan max post S = %.5f" % max_post)
    print("scan gap(post-strict) = %.5f" % gap)

    # plot
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    ax = axes[0, 0]
    ax.plot(thr_scan, S_strict_thr, color="#58a6ff", linewidth=2, label="strict")
    ax.plot(thr_scan, S_post_thr, color="#ffa657", linewidth=2, label="coincidence_post")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH=2")
    ax.set_title("S vs detector threshold", color="white")
    ax.set_xlabel("threshold", color="#8b949e")
    ax.set_ylabel("S", color="#8b949e")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    ax = axes[0, 1]
    ax.plot(win_scan, S_strict_win, color="#58a6ff", linewidth=2, label="strict")
    ax.plot(win_scan, S_post_win, color="#ffa657", linewidth=2, label="coincidence_post")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH=2")
    ax.set_title("S vs coincidence window", color="white")
    ax.set_xlabel("window", color="#8b949e")
    ax.set_ylabel("S", color="#8b949e")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    ax = axes[1, 0]
    ax.plot(thr_scan, coinc_thr, color="#7ee787", linewidth=2, label="coinc_rate @fixed window")
    ax.plot(win_scan, coinc_win, color="#79c0ff", linewidth=2, label="coinc_rate @fixed threshold")
    ax.set_title("Coincidence rate", color="white")
    ax.set_xlabel("scan axis value", color="#8b949e")
    ax.set_ylabel("rate", color="#8b949e")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    ax = axes[1, 1]
    ax.axis("off")
    txt = (
        "Local-wave closure protocol (preregistered)\n"
        "-----------------------------------------\n"
        "n_trials = %d\n"
        "threshold_base = %.3f\n"
        "window_base = %.3f\n\n"
        "base S_strict = %.4f\n"
        "base S_post   = %.4f\n"
        "base coinc_rate = %.4f\n"
        "base late_setting = %.4f\n\n"
        "scan max strict S = %.4f\n"
        "scan max post S   = %.4f\n"
        "gap(post-strict)  = %.4f"
    ) % (
        n_trials,
        threshold_base,
        window_base,
        base["S_strict"],
        base["S_post"],
        base["coinc_rate"],
        base["late_setting_rate"],
        max_strict,
        max_post,
        gap,
    )
    ax.text(
        0.02,
        0.98,
        txt,
        va="top",
        ha="left",
        color="#c9d1d9",
        fontsize=10,
        family="monospace",
    )

    out_png = "chsh_local_wave_closure_full.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print("saved:", out_png)


if __name__ == "__main__":
    main()

