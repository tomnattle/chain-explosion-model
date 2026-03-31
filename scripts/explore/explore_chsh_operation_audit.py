"""
explore_chsh_operation_audit.py
--------------------------------
CHSH 操作等价审计（重点排查“超 2”来自哪里）：

同一组设置角度（a,a',b,b'），对每个隐变量 lambda 生成局域连续信号，
再用阈值探测规则把信号变成离散输出，并可选后筛选（丢弃探测失败事件）。

两种模式：
  Mode A: no_postselection
    - 若某侧未探测，将其输出直接映射为 -1（避免样本偏置）
  Mode B: postselection
    - 只用同时探测成功的事件计算相关（公平采样漏洞的典型来源）

输出：
  - chsh_operation_audit.png
  - 控制台打印：最大 S 与对应效率 eta
"""

import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")


def compute_chsh_from_E(Eab, Eabp, Eapb, Eapbp):
    # S = E(a,b) + E(a,b') + E(a',b) - E(a',b')
    return Eab + Eabp + Eapb - Eapbp


def local_sign(x):
    # sign(0) 取 +1，避免全 0 均值带来的数值奇异
    return np.where(x >= 0.0, 1.0, -1.0)


def run_modes(a, ap, b, bp, n_samples, theta_list, noise_sigma, seed):
    rng = np.random.default_rng(seed)
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_samples)

    def signals(thetaA, thetaB):
        # 局域连续“振幅”：cos(λ-θ)
        u = np.cos(lam - thetaA)
        v = np.cos(lam - thetaB)
        # 强度：cos^2
        IU = u * u
        IV = v * v
        return u, v, IU, IV

    results = []

    for thr in theta_list:
        # thr 是强度阈值（0~1）
        Eb = {}

        for name, thA, thB in [
            ("a_b", a, b),
            ("a_bp", a, bp),
            ("ap_b", ap, b),
            ("ap_bp", ap, bp),
        ]:
            u, v, IU, IV = signals(thA, thB)
            # 加噪声：探测器噪声进入探测判据
            if noise_sigma > 0:
                nu = noise_sigma * rng.normal(size=n_samples)
                nv = noise_sigma * rng.normal(size=n_samples)
            else:
                nu = 0.0
                nv = 0.0

            detA = (IU + nu) >= thr
            detB = (IV + nv) >= thr

            A_out = local_sign(u)
            B_out = local_sign(v)

            # Mode A: no_postselection -> 未探测输出固定为 -1
            A_A = np.where(detA, A_out, -1.0)
            B_A = np.where(detB, B_out, -1.0)
            E_A = float(np.mean(A_A * B_A))

            # Mode B: postselection -> 只用同时探测事件
            both = detA & detB
            eta = float(np.mean(both))
            if np.any(both):
                E_B = float(np.mean(A_out[both] * B_out[both]))
            else:
                E_B = 0.0
            Eb[name] = (E_A, E_B, eta)

        S_A = compute_chsh_from_E(Eb["a_b"][0], Eb["a_bp"][0], Eb["ap_b"][0], Eb["ap_bp"][0])
        S_B = compute_chsh_from_E(Eb["a_b"][1], Eb["a_bp"][1], Eb["ap_b"][1], Eb["ap_bp"][1])
        # eta 取四组里最大重叠效率的中值，作为画图横轴（粗略）
        etas = [Eb[k][2] for k in Eb]
        eta_eff = float(np.median(etas))

        results.append((thr, eta_eff, S_A, S_B))

    return results


def main():
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    n_samples = 250000
    seed = 123

    # 探测器噪声（越大越“像真实实验”，但也会变弱）
    noise_sigma = 0.05

    # 阈值扫：从容易探测到严格探测
    theta_list = np.linspace(0.05, 0.95, 30, dtype=np.float64)

    results = run_modes(a, ap, b, bp, n_samples, theta_list, noise_sigma, seed)

    thr_arr = np.array([r[0] for r in results], dtype=np.float64)
    eta_arr = np.array([r[1] for r in results], dtype=np.float64)
    S_A_arr = np.array([r[2] for r in results], dtype=np.float64)
    S_B_arr = np.array([r[3] for r in results], dtype=np.float64)

    max_idx_A = int(np.argmax(S_A_arr))
    max_idx_B = int(np.argmax(S_B_arr))

    print("CHSH operation audit (local continuous signals + threshold detection)")
    print("settings: a=0, a'=pi/4, b=pi/8, b'=-pi/8")
    print("n_samples =", n_samples, "noise_sigma =", noise_sigma)
    print("no_postselection: max S =", float(S_A_arr[max_idx_A]), "at eta~", float(eta_arr[max_idx_A]))
    print("postselection:   max S =", float(S_B_arr[max_idx_B]), "at eta~", float(eta_arr[max_idx_B]))

    # 作图
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 5.2))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")

    ax.plot(eta_arr, S_A_arr, color="#58a6ff", linewidth=2, label="no_postselection (map miss->-1)")
    ax.plot(eta_arr, S_B_arr, color="#ffa657", linewidth=2, label="postselection (keep only both-detected)")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH bound = 2")

    ax.set_xlabel("detection efficiency eta (approx)", color="#8b949e")
    ax.set_ylabel("S value", color="#8b949e")
    ax.set_title("Where does 'super-2' come from?", color="white")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    out_png = "chsh_operation_audit.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)

    print("saved:", out_png)


if __name__ == "__main__":
    main()

