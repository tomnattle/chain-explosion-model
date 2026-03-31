"""
explore_chsh_closure_protocol.py
--------------------------------
最接近“闭合漏洞协议”的 CHSH 审计 toy（局域连续波响应）。

显式模块：
1) 随机设置 + 设置时序（setting delay）
2) 探测效率与漏检（eta_A, eta_B）
3) coincidence 窗口（仅用于“后筛选模式”）
4) 预注册指标（固定阈值，不事后调）

输出：
- chsh_closure_protocol.png

说明：
- strict 模式：每 trial 都计入，漏检映射为 -1，不做后筛选
- coincidence_post 模式：仅统计双击且落入窗口事件（用于暴露协议敏感性）
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")


def sign_pm1(x):
    return np.where(x >= 0.0, 1.0, -1.0)


def chsh(Eab, Eabp, Eapb, Eapbp):
    return Eab + Eabp + Eapb - Eapbp


def run_protocol_once(
    n_trials,
    eta_a,
    eta_b,
    window,
    set_delay_a,
    set_delay_b,
    noise_sigma,
    time_jitter_sigma,
    seed,
):
    """
    返回：
      S_strict, S_coinc_post, coincidence_rate, late_setting_rate
    """
    rng = np.random.default_rng(seed)

    # CHSH canonical settings
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    # source emits one pair per trial
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)
    setA = rng.integers(0, 2, size=n_trials)  # 0:a, 1:a'
    setB = rng.integers(0, 2, size=n_trials)  # 0:b, 1:b'
    thA = np.where(setA == 0, a, ap)
    thB = np.where(setB == 0, b, bp)

    # local continuous response
    u = np.cos(lam - thA)
    v = np.cos(lam - thB)
    A_bin = sign_pm1(u + noise_sigma * rng.normal(size=n_trials))
    B_bin = sign_pm1(v + noise_sigma * rng.normal(size=n_trials))

    # detection efficiency (independent misses)
    detA = rng.random(n_trials) < eta_a
    detB = rng.random(n_trials) < eta_b

    # timing model: arrival + setting-ready time
    # trial index acts as coarse emission clock (monotonic)
    t_emit = np.arange(n_trials, dtype=np.float64)
    t_arr_a = t_emit + 1.0 + time_jitter_sigma * rng.normal(size=n_trials)
    t_arr_b = t_emit + 1.0 + time_jitter_sigma * rng.normal(size=n_trials)
    t_set_a = t_emit + set_delay_a
    t_set_b = t_emit + set_delay_b

    late_a = t_set_a > t_arr_a
    late_b = t_set_b > t_arr_b
    late_setting_rate = float(np.mean(late_a | late_b))

    # strict mode: no discard, misses map to -1
    A_strict = np.where(detA, A_bin, -1.0)
    B_strict = np.where(detB, B_bin, -1.0)
    ABs = A_strict * B_strict

    m_ab = (setA == 0) & (setB == 0)
    m_abp = (setA == 0) & (setB == 1)
    m_apb = (setA == 1) & (setB == 0)
    m_apbp = (setA == 1) & (setB == 1)

    Eab = float(np.mean(ABs[m_ab]))
    Eabp = float(np.mean(ABs[m_abp]))
    Eapb = float(np.mean(ABs[m_apb]))
    Eapbp = float(np.mean(ABs[m_apbp]))
    S_strict = float(chsh(Eab, Eabp, Eapb, Eapbp))

    # coincidence-post mode: keep only both detected and within window
    coinc = detA & detB & (np.abs(t_arr_a - t_arr_b) <= window)
    coincidence_rate = float(np.mean(coinc))
    ABc = A_bin * B_bin

    def E_post(mask):
        mm = mask & coinc
        if np.any(mm):
            return float(np.mean(ABc[mm]))
        return 0.0

    Eab_c = E_post(m_ab)
    Eabp_c = E_post(m_abp)
    Eapb_c = E_post(m_apb)
    Eapbp_c = E_post(m_apbp)
    S_coinc = float(chsh(Eab_c, Eabp_c, Eapb_c, Eapbp_c))

    return S_strict, S_coinc, coincidence_rate, late_setting_rate


def main():
    # preregistered parameters (fixed before scan)
    n_trials = 220000
    noise_sigma = 0.05
    time_jitter_sigma = 0.45
    set_delay_a = 0.35
    set_delay_b = 0.38

    # preregistered audit thresholds
    strict_upper = 2.02
    min_coinc_gap = 0.20  # expect postselected S max to exceed strict max by this gap
    min_coinc_rate = 0.03

    eta_list = np.array([0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95], dtype=np.float64)
    win_list = np.array([0.05, 0.10, 0.18, 0.30, 0.45, 0.65, 0.90, 1.20], dtype=np.float64)

    # scan-1: vary efficiency, fixed window
    fixed_window = 0.30
    S_strict_eta = []
    S_coinc_eta = []
    R_coinc_eta = []
    late_eta = []
    for i, eta in enumerate(eta_list):
        s0, s1, rc, lr = run_protocol_once(
            n_trials=n_trials,
            eta_a=float(eta),
            eta_b=float(eta),
            window=fixed_window,
            set_delay_a=set_delay_a,
            set_delay_b=set_delay_b,
            noise_sigma=noise_sigma,
            time_jitter_sigma=time_jitter_sigma,
            seed=1000 + i,
        )
        S_strict_eta.append(s0)
        S_coinc_eta.append(s1)
        R_coinc_eta.append(rc)
        late_eta.append(lr)

    S_strict_eta = np.asarray(S_strict_eta)
    S_coinc_eta = np.asarray(S_coinc_eta)
    R_coinc_eta = np.asarray(R_coinc_eta)
    late_eta = np.asarray(late_eta)

    # scan-2: vary window, fixed efficiency
    fixed_eta = 0.75
    S_strict_win = []
    S_coinc_win = []
    R_coinc_win = []
    late_win = []
    for i, win in enumerate(win_list):
        s0, s1, rc, lr = run_protocol_once(
            n_trials=n_trials,
            eta_a=fixed_eta,
            eta_b=fixed_eta,
            window=float(win),
            set_delay_a=set_delay_a,
            set_delay_b=set_delay_b,
            noise_sigma=noise_sigma,
            time_jitter_sigma=time_jitter_sigma,
            seed=2000 + i,
        )
        S_strict_win.append(s0)
        S_coinc_win.append(s1)
        R_coinc_win.append(rc)
        late_win.append(lr)

    S_strict_win = np.asarray(S_strict_win)
    S_coinc_win = np.asarray(S_coinc_win)
    R_coinc_win = np.asarray(R_coinc_win)
    late_win = np.asarray(late_win)

    # heatmap: coincidence rate over (eta, window)
    heat = np.zeros((eta_list.size, win_list.size), dtype=np.float64)
    for i, eta in enumerate(eta_list):
        for j, win in enumerate(win_list):
            _, _, rc, _ = run_protocol_once(
                n_trials=90000,
                eta_a=float(eta),
                eta_b=float(eta),
                window=float(win),
                set_delay_a=set_delay_a,
                set_delay_b=set_delay_b,
                noise_sigma=noise_sigma,
                time_jitter_sigma=time_jitter_sigma,
                seed=3000 + i * 100 + j,
            )
            heat[i, j] = rc

    max_strict = float(max(np.max(S_strict_eta), np.max(S_strict_win)))
    max_post = float(max(np.max(S_coinc_eta), np.max(S_coinc_win)))
    gap = max_post - max_strict

    prereg_pass = (
        (max_strict <= strict_upper)
        and (gap >= min_coinc_gap)
        and (float(np.max(heat)) >= min_coinc_rate)
    )

    print("CHSH closure-protocol audit")
    print("strict max S = %.5f (limit %.2f)" % (max_strict, strict_upper))
    print("postselected max S = %.5f" % max_post)
    print("gap(post - strict) = %.5f (min %.2f)" % (gap, min_coinc_gap))
    print("max coincidence rate = %.5f (min %.2f)" % (float(np.max(heat)), min_coinc_rate))
    print("preregistered verdict =", "PASS" if prereg_pass else "FAIL")

    # plotting
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    ax = axes[0, 0]
    ax.plot(eta_list, S_strict_eta, marker="o", color="#58a6ff", linewidth=2, label="strict")
    ax.plot(eta_list, S_coinc_eta, marker="o", color="#ffa657", linewidth=2, label="coincidence_post")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH=2")
    ax.set_title("S vs efficiency (window=%.2f)" % fixed_window, color="white")
    ax.set_xlabel("eta", color="#8b949e")
    ax.set_ylabel("S", color="#8b949e")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    ax = axes[0, 1]
    ax.plot(win_list, S_strict_win, marker="o", color="#58a6ff", linewidth=2, label="strict")
    ax.plot(win_list, S_coinc_win, marker="o", color="#ffa657", linewidth=2, label="coincidence_post")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH=2")
    ax.set_title("S vs coincidence window (eta=%.2f)" % fixed_eta, color="white")
    ax.set_xlabel("window", color="#8b949e")
    ax.set_ylabel("S", color="#8b949e")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    ax = axes[1, 0]
    im = ax.imshow(
        heat,
        origin="lower",
        aspect="auto",
        cmap="viridis",
        vmin=float(np.min(heat)),
        vmax=float(np.max(heat)),
    )
    ax.set_title("coincidence rate heatmap", color="white")
    ax.set_xlabel("window index", color="#8b949e")
    ax.set_ylabel("eta index", color="#8b949e")
    ax.set_xticks(np.arange(win_list.size))
    ax.set_xticklabels(["%.2f" % w for w in win_list], rotation=30)
    ax.set_yticks(np.arange(eta_list.size))
    ax.set_yticklabels(["%.2f" % e for e in eta_list])
    cb = fig.colorbar(im, ax=ax)
    cb.ax.tick_params(colors="#8b949e")

    ax = axes[1, 1]
    ax.axis("off")
    txt = (
        "Preregistered protocol\n"
        "---------------------\n"
        "n_trials=%d\n"
        "noise_sigma=%.3f\n"
        "time_jitter_sigma=%.3f\n"
        "set_delay_A=%.2f, set_delay_B=%.2f\n\n"
        "strict_upper=%.2f\n"
        "min_coinc_gap=%.2f\n"
        "min_coinc_rate=%.2f\n\n"
        "strict_max_S=%.4f\n"
        "post_max_S=%.4f\n"
        "gap=%.4f\n"
        "max_coinc_rate=%.4f\n\n"
        "VERDICT: %s"
    ) % (
        n_trials,
        noise_sigma,
        time_jitter_sigma,
        set_delay_a,
        set_delay_b,
        strict_upper,
        min_coinc_gap,
        min_coinc_rate,
        max_strict,
        max_post,
        gap,
        float(np.max(heat)),
        "PASS" if prereg_pass else "FAIL",
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

    out_png = "chsh_closure_protocol.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print("saved:", out_png)


if __name__ == "__main__":
    main()

