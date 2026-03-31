"""
explore_bell_chsh_two_tracks.py
-------------------------------
双轨对照：
1) 严格 CHSH 轨（本地隐藏变量 + 二值输出 ±1 + 无后筛选）=> S <= 2
2) 经典波强度轨（连续场 + 投影 + 强度相关）=> 可接近 2*sqrt(2)

目的不是“否定贝尔数学”，而是把“问题定义不同”讲清楚：
- CHSH 上界约束的是特定假设组合；
- 改成连续波强度统计后，就不再是同一个不等式场景。
"""

import math
import os
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")


def chsh_S(Eab, Eabp, Eapb, Eapbp):
    # 标准 CHSH 组合之一
    return Eab + Eabp + Eapb - Eapbp


def run_strict_chsh_binary(n_samples=400000, seed=42):
    """
    严格 CHSH 轨：
    - 隐变量 lambda ~ U[0,2pi)
    - 本地响应 A(a,lambda), B(b,lambda) ∈ {+1,-1}
    - 无后筛选
    """
    rng = np.random.default_rng(seed)
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_samples)

    # CHSH 常用角度（弧度）
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    def A(theta, lamv):
        return np.where(np.cos(lamv - theta) >= 0.0, 1.0, -1.0)

    # 这里给 B 加一个 π/2 相位，故意制造相关结构；但仍是本地二值
    def B(theta, lamv):
        return np.where(np.cos(lamv - theta + np.pi / 2.0) >= 0.0, 1.0, -1.0)

    A_a = A(a, lam)
    A_ap = A(ap, lam)
    B_b = B(b, lam)
    B_bp = B(bp, lam)

    Eab = float(np.mean(A_a * B_b))
    Eabp = float(np.mean(A_a * B_bp))
    Eapb = float(np.mean(A_ap * B_b))
    Eapbp = float(np.mean(A_ap * B_bp))
    S = float(chsh_S(Eab, Eabp, Eapb, Eapbp))

    return {
        "Eab": Eab,
        "Eabp": Eabp,
        "Eapb": Eapb,
        "Eapbp": Eapbp,
        "S": S,
        "bound": 2.0,
        "note": "严格CHSH：二值±1、本地响应、无后筛选",
    }


def run_classical_wave_track():
    """
    经典波强度轨：
    用连续极化向量 e(λ)，通过偏振片角度做投影，
    再对输出强度做“中心化相关”。

    这个相关函数不等同于 CHSH 的二值相关 E=⟨A*B⟩(A,B∈±1)，
    因此数值可接近 2*sqrt(2)。
    """
    # 直接用解析相关 C(Δ)=cos(2Δ)
    def C(thetaA, thetaB):
        return math.cos(2.0 * (thetaA - thetaB))

    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    Cab = C(a, b)
    Cabp = C(a, bp)
    Capb = C(ap, b)
    Capbp = C(ap, bp)
    S = chsh_S(Cab, Cabp, Capb, Capbp)

    return {
        "Eab_like": Cab,
        "Eabp_like": Cabp,
        "Eapb_like": Capb,
        "Eapbp_like": Capbp,
        "S_like": float(S),
        "target": float(2.0 * math.sqrt(2.0)),
        "note": "经典波连续相关：不是二值CHSH E(±1,±1)",
    }


def build_angle_curve_points():
    # 扫描角差，画出两类相关函数曲线
    dtheta = np.linspace(-np.pi / 2, np.pi / 2, 300)

    # 严格二值本地模型对应的一种相关近似（符号比较模型）
    # 这里给出一条典型“分段线性”形状，和 cos(2Δ) 做直观对比。
    # E_bin(Δ) = 1 - 4|Δ|/pi (for |Δ|<=pi/2)
    E_bin = 1.0 - 4.0 * np.abs(dtheta) / np.pi

    # 连续波相关
    E_wave = np.cos(2.0 * dtheta)
    return dtheta, E_bin, E_wave


def save_comparison_figure(r1, r2, out_png="bell_chsh_two_tracks.png"):
    labels = ["(a,b)", "(a,b')", "(a',b)", "(a',b')"]
    strict_vals = [r1["Eab"], r1["Eabp"], r1["Eapb"], r1["Eapbp"]]
    wave_vals = [r2["Eab_like"], r2["Eabp_like"], r2["Eapb_like"], r2["Eapbp_like"]]

    dtheta, E_bin_curve, E_wave_curve = build_angle_curve_points()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    # 图1：角差-相关曲线
    axes[0].plot(dtheta, E_bin_curve, color="#58a6ff", linewidth=2, label="strict binary-local shape")
    axes[0].plot(dtheta, E_wave_curve, color="#ffa657", linewidth=2, label="wave continuous cos(2Δ)")
    axes[0].set_title("Correlation vs angle gap", color="white")
    axes[0].set_xlabel("Δθ (rad)", color="#8b949e")
    axes[0].set_ylabel("correlation", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")
    axes[0].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    # 图2：四组角度组合的柱状对比
    x = np.arange(len(labels))
    w = 0.36
    axes[1].bar(x - w / 2, strict_vals, width=w, color="#58a6ff", alpha=0.9, label="strict CHSH E")
    axes[1].bar(x + w / 2, wave_vals, width=w, color="#ffa657", alpha=0.9, label="wave C")
    axes[1].set_xticks(x, labels)
    axes[1].set_ylim(-1.1, 1.1)
    axes[1].set_title("Four setting correlations", color="white")
    axes[1].grid(True, axis="y", alpha=0.25, color="#30363d")
    axes[1].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    # 图3：S 总览
    s_labels = ["strict CHSH S", "wave-like S"]
    s_vals = [r1["S"], r2["S_like"]]
    s_colors = ["#58a6ff", "#ffa657"]
    axes[2].bar(np.arange(2), s_vals, color=s_colors, width=0.6, alpha=0.95)
    axes[2].axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5, label="CHSH bound = 2")
    axes[2].set_xticks(np.arange(2))
    axes[2].set_xticklabels(s_labels, rotation=10)
    axes[2].set_ylim(0.0, 3.0)
    axes[2].set_title("S comparison", color="white")
    axes[2].grid(True, axis="y", alpha=0.25, color="#30363d")
    axes[2].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"\n已保存图像: {out_png}")


def save_red_green_analogy_figure(out_png="red_green_interference_analogy.png", seed=7):
    """
    给非专业读者的“红/绿两路”直觉图：
    - 相干叠加：I = |u+v|^2  会出现细条纹（来自交叉项）
    - 可区分/不相干：I = |u|^2 + |v|^2  交叉项被抹掉 => 条纹消失/大幅减弱
    """
    rng = np.random.default_rng(seed)
    y = np.linspace(-1.0, 1.0, 900)

    # 两路“场”：同一个包络，但带不同相位/路径差
    env = np.exp(-(y / 0.55) ** 2)
    phase0 = 16.0 * np.pi * y
    dphi = 0.65 * np.pi + 0.15 * np.sin(2.5 * np.pi * y)
    # 加一点小扰动，避免过于理想
    jitter = 0.05 * rng.normal(size=y.shape)

    u = env * np.exp(1j * (phase0 + jitter))
    v = 0.92 * env * np.exp(1j * (phase0 + dphi - jitter))

    I_coh = np.abs(u + v) ** 2
    I_incoh = np.abs(u) ** 2 + np.abs(v) ** 2
    cross = I_coh - I_incoh  # = 2Re(u v*)

    # 归一化便于对比
    s = float(np.max(I_coh)) + 1e-18
    I_coh /= s
    I_incoh /= s
    cross /= s

    fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#30363d")

    axes[0].plot(y, I_coh, color="#ff7b72", linewidth=2.0, label="coherent: |u+v|^2  (有细条纹)")
    axes[0].plot(y, I_incoh, color="#7ee787", linewidth=2.0, label="distinguishable: |u|^2+|v|^2  (交叉项被抹掉)")
    axes[0].set_title("“红/绿两路”直觉：相干 vs 可区分", color="white")
    axes[0].set_ylabel("normalized intensity", color="#8b949e")
    axes[0].grid(True, alpha=0.25, color="#30363d")
    axes[0].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    axes[1].plot(y, cross, color="#58a6ff", linewidth=2.0, label="cross-term = |u+v|^2 - (|u|^2+|v|^2)")
    axes[1].axhline(0.0, color="#8b949e", linestyle="--", linewidth=1.2)
    axes[1].set_xlabel("screen coordinate (toy y)", color="#8b949e")
    axes[1].set_ylabel("cross-term", color="#8b949e")
    axes[1].grid(True, alpha=0.25, color="#30363d")
    axes[1].legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"已保存图像: {out_png}")


def main():
    print("=" * 72)
    print("Bell/CHSH 双轨对照（严格CHSH vs 经典波连续相关）")
    print("=" * 72)

    r1 = run_strict_chsh_binary(n_samples=500000, seed=42)
    print("\n[轨道1] 严格 CHSH（二值、本地、无后筛选）")
    print(f"E(a,b)   = {r1['Eab']:.4f}")
    print(f"E(a,b')  = {r1['Eabp']:.4f}")
    print(f"E(a',b)  = {r1['Eapb']:.4f}")
    print(f"E(a',b') = {r1['Eapbp']:.4f}")
    print(f"S = {r1['S']:.4f}  (理论上界 {r1['bound']:.1f})")
    print(f"说明: {r1['note']}")

    r2 = run_classical_wave_track()
    print("\n[轨道2] 经典波连续相关（投影强度/连续变量）")
    print(f"C(a,b)   = {r2['Eab_like']:.4f}")
    print(f"C(a,b')  = {r2['Eabp_like']:.4f}")
    print(f"C(a',b)  = {r2['Eapb_like']:.4f}")
    print(f"C(a',b') = {r2['Eapbp_like']:.4f}")
    print(f"S_like = {r2['S_like']:.4f}  (2*sqrt(2)={r2['target']:.4f})")
    print(f"说明: {r2['note']}")

    print("\n结论（朴素版）:")
    print("- CHSH <= 2 约束的是‘二值输出 + 本地隐藏变量 + 无后筛选’这一类模型。")
    print("- 连续波强度相关可以接近 2.828，但那已不是同一个CHSH统计对象。")
    print("- 所以不是数学错了，而是‘你在算不同问题’。")
    save_comparison_figure(r1, r2, out_png="bell_chsh_two_tracks.png")
    save_red_green_analogy_figure(out_png="red_green_interference_analogy.png")


if __name__ == "__main__":
    main()

