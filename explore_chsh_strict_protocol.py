"""
explore_chsh_strict_protocol.py
-------------------------------
最严 CHSH 协议（锁死争议项）：
1) 输出固定二值 ±1
2) 严格事件配对（每个 trial 恰好贡献一个 A 与一个 B）
3) 无后筛选（任何 trial 都计入统计）
4) 设置独立随机（a/a' 与 b/b' 均独立伯努利采样）
5) 局域响应：A 仅依赖 (lambda, setting_A)，B 仅依赖 (lambda, setting_B)

模型：
- 连续局域场响应 u=cos(lambda-theta)，v=cos(lambda-theta)
- 二值读出 sign(u+noise), sign(v+noise)
- 不允许按探测成功与否筛样本

输出：
- chsh_strict_protocol.png
- 控制台打印 S、各 E 值、统计误差估计
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")


def sign_pm1(x):
    return np.where(x >= 0.0, 1.0, -1.0)


def chsh(Eab, Eabp, Eapb, Eapbp):
    return Eab + Eabp + Eapb - Eapbp


def run_strict(n_trials=400000, noise_sigma=0.05, seed=2026):
    rng = np.random.default_rng(seed)

    # CHSH canonical angles
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    # hidden variable, independent settings
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)
    setA = rng.integers(0, 2, size=n_trials)   # 0->a, 1->a'
    setB = rng.integers(0, 2, size=n_trials)   # 0->b, 1->b'

    thetaA = np.where(setA == 0, a, ap)
    thetaB = np.where(setB == 0, b, bp)

    u = np.cos(lam - thetaA)
    v = np.cos(lam - thetaB)

    # fixed binary output for every event (no discard)
    nA = noise_sigma * rng.normal(size=n_trials)
    nB = noise_sigma * rng.normal(size=n_trials)
    Aout = sign_pm1(u + nA)
    Bout = sign_pm1(v + nB)

    AB = Aout * Bout

    m_ab = (setA == 0) & (setB == 0)
    m_abp = (setA == 0) & (setB == 1)
    m_apb = (setA == 1) & (setB == 0)
    m_apbp = (setA == 1) & (setB == 1)

    Eab = float(np.mean(AB[m_ab]))
    Eabp = float(np.mean(AB[m_abp]))
    Eapb = float(np.mean(AB[m_apb]))
    Eapbp = float(np.mean(AB[m_apbp]))
    S = float(chsh(Eab, Eabp, Eapb, Eapbp))

    # rough sigma_S from Bernoulli variance in each subgroup
    def se(mask):
        x = AB[mask]
        n = max(1, x.size)
        v = float(np.var(x))
        return np.sqrt(v / n)

    se_S = float(np.sqrt(se(m_ab) ** 2 + se(m_abp) ** 2 + se(m_apb) ** 2 + se(m_apbp) ** 2))
    return {
        "Eab": Eab,
        "Eabp": Eabp,
        "Eapb": Eapb,
        "Eapbp": Eapbp,
        "S": S,
        "se_S": se_S,
        "counts": [int(np.sum(m_ab)), int(np.sum(m_abp)), int(np.sum(m_apb)), int(np.sum(m_apbp))],
    }


def main():
    # single strict run
    r = run_strict(n_trials=500000, noise_sigma=0.05, seed=2026)
    print("Strict CHSH protocol (no postselection, binary outputs, local response)")
    print("counts (ab,ab',a'b,a'b') =", r["counts"])
    print("E(a,b)   = %.5f" % r["Eab"])
    print("E(a,b')  = %.5f" % r["Eabp"])
    print("E(a',b)  = %.5f" % r["Eapb"])
    print("E(a',b') = %.5f" % r["Eapbp"])
    print("S = %.5f  (95%% CI approx: %.5f ~ %.5f)" % (r["S"], r["S"] - 1.96 * r["se_S"], r["S"] + 1.96 * r["se_S"]))

    # robustness scan vs noise
    sigmas = np.array([0.0, 0.02, 0.05, 0.08, 0.12, 0.18], dtype=np.float64)
    Svals = []
    lo = []
    hi = []
    for i, s in enumerate(sigmas):
        rr = run_strict(n_trials=220000, noise_sigma=float(s), seed=2026 + i)
        Svals.append(rr["S"])
        lo.append(rr["S"] - 1.96 * rr["se_S"])
        hi.append(rr["S"] + 1.96 * rr["se_S"])
        print("noise=%.3f -> S=%.5f" % (s, rr["S"]))

    Svals = np.asarray(Svals)
    lo = np.asarray(lo)
    hi = np.asarray(hi)

    fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.0))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")

    ax.plot(sigmas, Svals, marker="o", color="#58a6ff", linewidth=2, label="strict protocol S")
    ax.fill_between(sigmas, lo, hi, color="#58a6ff", alpha=0.18, label="95% CI approx")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH bound = 2")
    ax.axhline(-2.0, color="#8b949e", linestyle="--", linewidth=1.0, alpha=0.5)
    ax.set_xlabel("detector additive noise sigma", color="#8b949e")
    ax.set_ylabel("S", color="#8b949e")
    ax.set_title("Strict CHSH protocol audit", color="white")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    out_png = "chsh_strict_protocol.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print("saved:", out_png)


if __name__ == "__main__":
    main()

