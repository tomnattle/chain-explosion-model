"""
explore_chsh_strict_vs_postselected_compare.py
----------------------------------------------
同图对照：
  strict protocol (no postselection, binary outputs)  vs
  postselected protocol (keep only both-detected)
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")


def sign_pm1(x):
    return np.where(x >= 0.0, 1.0, -1.0)


def chsh(Eab, Eabp, Eapb, Eapbp):
    return Eab + Eabp + Eapb - Eapbp


def run_strict_once(n_trials=220000, noise_sigma=0.05, seed=1001):
    rng = np.random.default_rng(seed)
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)
    setA = rng.integers(0, 2, size=n_trials)
    setB = rng.integers(0, 2, size=n_trials)
    thA = np.where(setA == 0, a, ap)
    thB = np.where(setB == 0, b, bp)
    u = np.cos(lam - thA)
    v = np.cos(lam - thB)
    A = sign_pm1(u + noise_sigma * rng.normal(size=n_trials))
    B = sign_pm1(v + noise_sigma * rng.normal(size=n_trials))
    AB = A * B
    m_ab = (setA == 0) & (setB == 0)
    m_abp = (setA == 0) & (setB == 1)
    m_apb = (setA == 1) & (setB == 0)
    m_apbp = (setA == 1) & (setB == 1)
    return float(
        chsh(np.mean(AB[m_ab]), np.mean(AB[m_abp]), np.mean(AB[m_apb]), np.mean(AB[m_apbp]))
    )


def run_postselected_curve(thr_list, n_samples=200000, noise_sigma=0.05, seed=2002):
    rng = np.random.default_rng(seed)
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_samples)

    def one_E(thA, thB, thr):
        u = np.cos(lam - thA)
        v = np.cos(lam - thB)
        IU = u * u + noise_sigma * rng.normal(size=n_samples)
        IV = v * v + noise_sigma * rng.normal(size=n_samples)
        detA = IU >= thr
        detB = IV >= thr
        both = detA & detB
        eta = float(np.mean(both))
        if np.any(both):
            E = float(np.mean(sign_pm1(u[both]) * sign_pm1(v[both])))
        else:
            E = 0.0
        return E, eta

    etas, Ss = [], []
    for thr in thr_list:
        Eab, eta1 = one_E(a, b, thr)
        Eabp, eta2 = one_E(a, bp, thr)
        Eapb, eta3 = one_E(ap, b, thr)
        Eapbp, eta4 = one_E(ap, bp, thr)
        Ss.append(float(chsh(Eab, Eabp, Eapb, Eapbp)))
        etas.append(float(np.median([eta1, eta2, eta3, eta4])))
    return np.asarray(etas), np.asarray(Ss)


def main():
    # strict curve vs noise
    sigmas = np.array([0.0, 0.02, 0.05, 0.08, 0.12, 0.18], dtype=np.float64)
    S_strict = np.array([run_strict_once(noise_sigma=float(s), seed=1001 + i) for i, s in enumerate(sigmas)])

    # postselected curve vs eta(threshold)
    thr_list = np.linspace(0.05, 0.95, 28, dtype=np.float64)
    eta_ps, S_ps = run_postselected_curve(thr_list, n_samples=220000, noise_sigma=0.05, seed=2002)

    print("CHSH strict-vs-postselected compare complete.")
    print("strict S range: [%.4f, %.4f]" % (float(np.min(S_strict)), float(np.max(S_strict))))
    print("postselected max S: %.4f" % float(np.max(S_ps)))

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    axes[0].plot(sigmas, S_strict, marker="o", color="#58a6ff", linewidth=2, label="strict protocol")
    axes[0].axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH=2")
    axes[0].set_xlabel("noise sigma", color="#8b949e")
    axes[0].set_ylabel("S", color="#8b949e")
    axes[0].set_title("Strict protocol (no postselection)", color="white")
    axes[0].grid(True, alpha=0.25, color="#30363d")
    axes[0].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    axes[1].plot(eta_ps, S_ps, color="#ffa657", linewidth=2, label="postselected")
    axes[1].axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH=2")
    axes[1].set_xlabel("eta (approx)", color="#8b949e")
    axes[1].set_ylabel("S", color="#8b949e")
    axes[1].set_title("Postselected protocol", color="white")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    out_png = "chsh_strict_vs_postselected.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print("saved:", out_png)


if __name__ == "__main__":
    main()

