"""
explore_chsh_experiment_alignment.py
------------------------------------
实验级对齐入口（协议锁死 + 可审计）：

功能：
1) 读取真实事件 CSV（若未提供则用内置模拟事件）
2) 固定配对窗口做 coincidence pairing（不可事后调整）
3) 固定二值映射与统计流程，输出 E(a,b), E(a,b'), E(a',b), E(a',b'), S
4) 输出图：事件时间差分布 + 四组 E 柱状 + S 对比

CSV 最小字段（header）：
  side, t, setting, outcome
  - side: A or B
  - t: float 时间戳（同一单位）
  - setting: 0 或 1
  - outcome: -1 或 +1
"""

import csv
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

os.environ.setdefault("MPLBACKEND", "Agg")


def chsh(Eab, Eabp, Eapb, Eapbp):
    return Eab + Eabp + Eapb - Eapbp


def load_events_csv(path):
    A, B = [], []
    with open(path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        need = {"side", "t", "setting", "outcome"}
        if not need.issubset(set(rd.fieldnames or [])):
            raise ValueError("CSV 缺字段，需包含: side,t,setting,outcome")
        for row in rd:
            side = str(row["side"]).strip().upper()
            t = float(row["t"])
            s = int(row["setting"])
            o = int(row["outcome"])
            if s not in (0, 1):
                continue
            o = 1 if o >= 0 else -1
            if side == "A":
                A.append((t, s, o))
            elif side == "B":
                B.append((t, s, o))
    A.sort(key=lambda x: x[0])
    B.sort(key=lambda x: x[0])
    return A, B


def simulate_events(n=120000, seed=77):
    """
    无真实数据时的协议演示数据（局域模型）：
    每次 trial 生成 A/B 各一个事件，含抖动时间戳。
    """
    rng = np.random.default_rng(seed)
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    t0 = np.arange(n, dtype=np.float64)
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n)
    setA = rng.integers(0, 2, size=n)
    setB = rng.integers(0, 2, size=n)
    thA = np.where(setA == 0, a, ap)
    thB = np.where(setB == 0, b, bp)
    u = np.cos(lam - thA)
    v = np.cos(lam - thB)
    outA = np.where(u + 0.06 * rng.normal(size=n) >= 0.0, 1, -1)
    outB = np.where(v + 0.06 * rng.normal(size=n) >= 0.0, 1, -1)
    tA = t0 + 1.0 + 0.10 * rng.normal(size=n)
    tB = t0 + 1.0 + 0.10 * rng.normal(size=n)

    A = [(float(tA[i]), int(setA[i]), int(outA[i])) for i in range(n)]
    B = [(float(tB[i]), int(setB[i]), int(outB[i])) for i in range(n)]
    A.sort(key=lambda x: x[0])
    B.sort(key=lambda x: x[0])
    return A, B


def pair_events(A, B, window):
    """
    固定窗口配对：A 事件按时间扫描，给它找最近且未使用的 B 事件。
    """
    paired = []
    used_b = np.zeros(len(B), dtype=np.bool_)
    j = 0
    dt_list = []

    for ta, sa, oa in A:
        while j < len(B) and B[j][0] < ta - window:
            j += 1
        best_k = -1
        best_dt = None
        k = j
        while k < len(B) and B[k][0] <= ta + window:
            if not used_b[k]:
                dt = abs(B[k][0] - ta)
                if best_dt is None or dt < best_dt:
                    best_dt = dt
                    best_k = k
            k += 1
        if best_k >= 0:
            used_b[best_k] = True
            tb, sb, ob = B[best_k]
            paired.append((sa, sb, oa, ob))
            dt_list.append(tb - ta)

    return paired, np.asarray(dt_list, dtype=np.float64)


def compute_E_S(paired):
    if not paired:
        return None
    arr = np.asarray(paired, dtype=np.int64)
    sa = arr[:, 0]
    sb = arr[:, 1]
    oa = arr[:, 2]
    ob = arr[:, 3]
    ab = oa * ob

    def m(mask):
        if np.any(mask):
            return float(np.mean(ab[mask]))
        return 0.0

    Eab = m((sa == 0) & (sb == 0))
    Eabp = m((sa == 0) & (sb == 1))
    Eapb = m((sa == 1) & (sb == 0))
    Eapbp = m((sa == 1) & (sb == 1))
    S = float(chsh(Eab, Eabp, Eapb, Eapbp))
    return Eab, Eabp, Eapb, Eapbp, S


def main():
    parser = argparse.ArgumentParser(description="CHSH experiment alignment (locked protocol)")
    parser.add_argument("--events-csv", default="", help="真实事件 CSV 路径（可选）")
    parser.add_argument("--window", type=float, default=0.25, help="固定 coincidence 窗口")
    args = parser.parse_args()

    if args.events_csv:
        A, B = load_events_csv(args.events_csv)
        src = "real_csv"
    else:
        A, B = simulate_events()
        src = "simulated_fallback"

    paired, dt = pair_events(A, B, window=float(args.window))
    stats = compute_E_S(paired)
    if stats is None:
        raise RuntimeError("配对为空，请检查窗口或数据")
    Eab, Eabp, Eapb, Eapbp, S = stats

    print("CHSH experiment alignment (locked protocol)")
    print("source =", src)
    print("window =", float(args.window))
    print("pairs =", len(paired))
    print("E(a,b)=%.5f E(a,b')=%.5f E(a',b)=%.5f E(a',b')=%.5f" % (Eab, Eabp, Eapb, Eapbp))
    print("S = %.5f" % S)

    # plot
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    axes[0].hist(dt, bins=80, color="#58a6ff", alpha=0.9)
    axes[0].set_title("Paired time differences", color="white")
    axes[0].set_xlabel("t_B - t_A", color="#8b949e")
    axes[0].set_ylabel("count", color="#8b949e")
    axes[0].grid(True, alpha=0.2, color="#30363d")

    labels = ["ab", "ab'", "a'b", "a'b'"]
    vals = [Eab, Eabp, Eapb, Eapbp]
    axes[1].bar(np.arange(4), vals, color=["#58a6ff", "#7ee787", "#ffa657", "#d2a8ff"])
    axes[1].set_xticks(np.arange(4))
    axes[1].set_xticklabels(labels)
    axes[1].set_ylim(-1.05, 1.05)
    axes[1].set_title("E correlations", color="white")
    axes[1].grid(True, axis="y", alpha=0.2, color="#30363d")

    axes[2].bar([0], [S], color="#ffa657", width=0.5)
    axes[2].axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.5)
    axes[2].set_xlim(-0.8, 0.8)
    axes[2].set_ylim(min(-2.2, S - 0.2), max(2.2, S + 0.2))
    axes[2].set_xticks([0])
    axes[2].set_xticklabels(["S"])
    axes[2].set_title("CHSH S", color="white")
    axes[2].grid(True, axis="y", alpha=0.2, color="#30363d")
    axes[2].text(0.02, 0.95, "S=%.4f\npairs=%d\nsrc=%s" % (S, len(paired), src),
                 transform=axes[2].transAxes, va="top", ha="left", color="#c9d1d9", fontsize=9)

    out_png = "chsh_experiment_alignment.png"
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print("saved:", out_png)


if __name__ == "__main__":
    main()

