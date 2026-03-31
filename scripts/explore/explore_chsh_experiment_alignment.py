"""
explore_chsh_experiment_alignment.py
------------------------------------
实验级对齐入口（预注册双协议 + 判据分离）：

1) 工程通过：数据加载、两协议配对、E/S 可算；可选与文献 S 量级比对。
2) 论点通过：同一批事件，strict 与 standard 仅按预注册 coincidence 窗不同；
   strict S <= thesis_gate.strict_max_S 且 standard S > thesis_gate.standard_min_S。

CSV 最小字段（header）：
  side, t, setting, outcome
"""

import argparse
import csv
import json
import os
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


def chsh(Eab, Eabp, Eapb, Eapbp):
    return Eab + Eabp + Eapb - Eapbp


def load_events_csv(path, fields):
    A, B = [], []
    with open(path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        need = {fields["side"], fields["time"], fields["setting"], fields["outcome"]}
        if not need.issubset(set(rd.fieldnames or [])):
            raise ValueError("CSV 缺字段，需包含映射字段: %s" % ",".join(sorted(need)))
        for row in rd:
            side = str(row[fields["side"]]).strip().upper()
            t = float(row[fields["time"]])
            s = int(row[fields["setting"]])
            o = int(row[fields["outcome"]])
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


def run_protocol(A, B, window: float, tag: str) -> Dict[str, Any]:
    paired, dt = pair_events(A, B, window=float(window))
    stats = compute_E_S(paired)
    row: Dict[str, Any] = {
        "tag": tag,
        "window": float(window),
        "pair_count": int(len(paired)),
    }
    if stats is None:
        row["S"] = None
        row["Eab"] = row["Eabp"] = row["Eapb"] = row["Eapbp"] = None
    else:
        Eab, Eabp, Eapb, Eapbp, S = stats
        row["Eab"] = Eab
        row["Eabp"] = Eabp
        row["Eapb"] = Eapb
        row["Eapbp"] = Eapbp
        row["S"] = S
    row["dt_list"] = dt
    return row


def evaluate_gates(
    strict: Dict[str, Any],
    standard: Dict[str, Any],
    eng: Dict[str, Any],
    thesis: Dict[str, Any],
) -> Tuple[bool, bool, List[str], List[str]]:
    eng_ok = True
    thesis_ok = True
    eng_reasons: List[str] = []
    thesis_reasons: List[str] = []

    min_pairs = int(eng.get("min_pairs_each_protocol", 0))
    for name, pr in ("strict", strict), ("standard", standard):
        pc = int(pr.get("pair_count") or 0)
        if pc < min_pairs:
            eng_ok = False
            eng_reasons.append("%s pair_count=%d < min_pairs=%d" % (name, pc, min_pairs))
        if pr.get("S") is None:
            eng_ok = False
            eng_reasons.append("%s S 不可算（配对为空）" % name)

    sv = eng.get("standard_vs_literature") or {}
    if sv.get("enabled") and standard.get("S") is not None:
        exp = float(sv.get("S_expected", 0.0))
        tol = float(sv.get("abs_tolerance", 0.0))
        Ss = float(standard["S"])
        if abs(Ss - exp) > tol:
            eng_ok = False
            eng_reasons.append(
                "standard S=%.5f 与文献 S_expected=%.5f 偏差 %.5f > tol=%.5f"
                % (Ss, exp, abs(Ss - exp), tol)
            )

    thesis_mode = str(thesis.get("mode", "full")).strip()
    smax = float(thesis.get("strict_max_S", 2.02))
    smin = float(thesis.get("standard_min_S", 2.0))
    req_fork = bool(thesis.get("require_standard_S_gt_strict_S", False))

    S_st = strict.get("S")
    S_sd = standard.get("S")
    if S_st is None or S_sd is None:
        thesis_ok = False
        thesis_reasons.append("missing S for strict or standard (no pairs)")
    else:
        S_st = float(S_st)
        S_sd = float(S_sd)
        if thesis_mode == "fork_only":
            if req_fork and not (S_sd > S_st + 1e-12):
                thesis_ok = False
                thesis_reasons.append(
                    "fork_only: standard S=%.6f not greater than strict S=%.6f"
                    % (S_sd, S_st)
                )
            elif thesis_ok:
                thesis_reasons.append(
                    "fork_only: S_strict=%.6f S_standard=%.6f (no strict_max/standard_min)"
                    % (S_st, S_sd)
                )
        else:
            if S_st > smax + 1e-12:
                thesis_ok = False
                thesis_reasons.append("strict S=%.6f > strict_max_S=%.6f" % (S_st, smax))
            if S_sd <= smin + 1e-12:
                thesis_ok = False
                thesis_reasons.append("standard S=%.6f <= standard_min_S=%.6f" % (S_sd, smin))
            if thesis_ok and req_fork and not (S_sd > S_st + 1e-12):
                thesis_ok = False
                thesis_reasons.append(
                    "standard S=%.6f not greater than strict S=%.6f (require_standard_S_gt_strict_S)"
                    % (S_sd, S_st)
                )
            if thesis_ok:
                thesis_reasons.append(
                    "thesis: same events, strict S=%.6f <= %.6f and standard S=%.6f > %.6f"
                    % (S_st, smax, S_sd, smin)
                )

    if eng_ok and not eng_reasons:
        eng_reasons.append("engineering gate: pair counts and S computable OK")
    if thesis_ok and len(thesis_reasons) == 0:
        thesis_reasons.append("thesis gate: fork inequalities satisfied")

    return eng_ok, thesis_ok, eng_reasons, thesis_reasons


def load_config(path: str) -> Dict[str, Any]:
    if not path or not os.path.isfile(path):
        return {}
    return json.loads(open(path, "r", encoding="utf-8").read())


def apply_style(ax):
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")


def main():
    parser = argparse.ArgumentParser(description="CHSH battle alignment (dual protocol, preregistered)")
    parser.add_argument("--events-csv", default="", help="真实事件 CSV（可选；缺省为内置模拟）")
    parser.add_argument("--config", default="configs/chsh_preregistered_config.json", help="预注册 JSON")
    parser.add_argument("--out-json", default="chsh_battle_result.json", help="判辞 JSON 路径")
    parser.add_argument("--out-png", default="chsh_experiment_alignment.png", help="图路径")
    parser.add_argument(
        "--window-strict",
        type=float,
        default=None,
        help="覆盖配置中 strict 窗口（仅调试；正式开盲应改 JSON）",
    )
    parser.add_argument(
        "--window-standard",
        type=float,
        default=None,
        help="覆盖配置中 standard 窗口（仅调试）",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    fields = {"side": "side", "time": "t", "setting": "setting", "outcome": "outcome"}
    pf = cfg.get("event_fields") or {}
    fields["side"] = pf.get("side", fields["side"])
    fields["time"] = pf.get("time", fields["time"])
    fields["setting"] = pf.get("setting", fields["setting"])
    fields["outcome"] = pf.get("outcome", fields["outcome"])

    if args.events_csv:
        A, B = load_events_csv(args.events_csv, fields)
        src = "real_csv"
        csv_path = os.path.abspath(args.events_csv)
    else:
        A, B = simulate_events()
        src = "simulated_fallback"
        csv_path = ""

    protocols = cfg.get("protocols")
    dual = isinstance(protocols, dict) and "strict" in protocols and "standard" in protocols

    if dual:
        w_s = float(protocols["strict"]["pairing"]["window"])
        w_std = float(protocols["standard"]["pairing"]["window"])
        if args.window_strict is not None:
            w_s = float(args.window_strict)
        if args.window_standard is not None:
            w_std = float(args.window_standard)
        strict_row = run_protocol(A, B, w_s, "strict")
        standard_row = run_protocol(A, B, w_std, "standard")
    else:
        leg = cfg.get("legacy_pairing") or cfg.get("pairing") or {}
        w = float(leg.get("window", 0.25))
        if args.window_standard is not None:
            w = float(args.window_standard)
        if args.window_strict is not None:
            w = float(args.window_strict)
        strict_row = run_protocol(A, B, w, "single_legacy")
        standard_row = dict(strict_row)
        standard_row["tag"] = "single_legacy"
        dual = False

    eng_gate = cfg.get("engineering_gate") or {}
    thesis_gate = cfg.get("thesis_gate") or {}

    strict_compact = {k: strict_row[k] for k in strict_row if k != "dt_list"}
    standard_compact = {k: standard_row[k] for k in standard_row if k != "dt_list"}

    eng_pass, thesis_pass, eng_rs, thesis_rs = evaluate_gates(
        strict_compact, standard_compact, eng_gate, thesis_gate
    )

    if not dual:
        thesis_pass = False
        thesis_rs = ["配置无 protocols.strict/standard 双协议块：论点门不适用（仅单协议运行）"]

    result: Dict[str, Any] = {
        "config_version": cfg.get("version", ""),
        "protocol_name": cfg.get("protocol_name", ""),
        "source": src,
        "events_csv": csv_path,
        "dual_protocol": dual,
        "engineering_pass": eng_pass,
        "thesis_pass": thesis_pass,
        "engineering_reasons": eng_rs,
        "thesis_reasons": thesis_rs,
        "strict": strict_compact,
        "standard": standard_compact,
        "gates": {
            "engineering_gate": eng_gate,
            "thesis_gate": thesis_gate,
        },
    }

    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("CHSH battle alignment (preregistered)")
    print("source =", src)
    print("dual_protocol =", dual)
    print("strict:  window=%.6f pairs=%d S=%s" % (
        strict_row["window"],
        strict_row["pair_count"],
        "None" if strict_row.get("S") is None else "%.6f" % strict_row["S"],
    ))
    print("standard: window=%.6f pairs=%d S=%s" % (
        standard_row["window"],
        standard_row["pair_count"],
        "None" if standard_row.get("S") is None else "%.6f" % standard_row["S"],
    ))
    print("engineering_pass =", eng_pass)
    print("thesis_pass =", thesis_pass)
    for r in eng_rs:
        print("  [engineering]", r)
    for r in thesis_rs:
        print("  [thesis]", r)
    print("saved:", args.out_json)

    # figure
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.0))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.ravel():
        apply_style(ax)

    dt_s = strict_row["dt_list"]
    dt_sd = standard_row["dt_list"]
    axes[0, 0].hist(dt_s, bins=80, color="#58a6ff", alpha=0.9)
    axes[0, 0].set_title("Paired dt (strict)", color="white")
    axes[0, 0].set_xlabel("t_B - t_A", color="#8b949e")
    axes[0, 0].grid(True, alpha=0.2, color="#30363d")

    axes[0, 1].hist(dt_sd, bins=80, color="#7ee787", alpha=0.9)
    axes[0, 1].set_title("Paired dt (standard)", color="white")
    axes[0, 1].set_xlabel("t_B - t_A", color="#8b949e")
    axes[0, 1].grid(True, alpha=0.2, color="#30363d")

    if standard_row.get("S") is not None:
        labels = ["ab", "ab'", "a'b", "a'b'"]
        vals = [
            standard_row["Eab"],
            standard_row["Eabp"],
            standard_row["Eapb"],
            standard_row["Eapbp"],
        ]
        axes[1, 0].bar(np.arange(4), vals, color=["#58a6ff", "#7ee787", "#ffa657", "#d2a8ff"])
        axes[1, 0].set_xticks(np.arange(4))
        axes[1, 0].set_xticklabels(labels)
        axes[1, 0].set_ylim(-1.05, 1.05)
        axes[1, 0].set_title("E (standard protocol)", color="white")
        axes[1, 0].grid(True, axis="y", alpha=0.2, color="#30363d")

    S_sm = standard_row.get("S")
    S_sv = strict_row.get("S")
    xs = [0, 1]
    ys = [
        float(S_sv) if S_sv is not None else float("nan"),
        float(S_sm) if S_sm is not None else float("nan"),
    ]
    axes[1, 1].bar(xs, ys, color=["#58a6ff", "#7ee787"], width=0.55)
    axes[1, 1].set_xticks(xs)
    axes[1, 1].set_xticklabels(["S strict", "S standard"])
    smax = float(thesis_gate.get("strict_max_S", 2.02))
    smin = float(thesis_gate.get("standard_min_S", 2.0))
    axes[1, 1].axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.2)
    axes[1, 1].axhline(smax, color="#ff7b72", linestyle=":", linewidth=1.2, label="strict max")
    axes[1, 1].axhline(smin, color="#ffa657", linestyle=":", linewidth=1.2, label="std min")
    ymax = 2.4
    ys_arr = np.asarray(ys, dtype=np.float64)
    if np.isfinite(ys_arr).any():
        ymax = max(ymax, float(np.nanmax(ys_arr)) + 0.15)
    axes[1, 1].set_ylim(-0.2, ymax)
    axes[1, 1].set_title("CHSH S fork (same events)", color="white")
    axes[1, 1].grid(True, axis="y", alpha=0.2, color="#30363d")
    verdict = "ENG=%s THESIS=%s" % (
        "PASS" if eng_pass else "FAIL",
        "PASS" if thesis_pass else "FAIL",
    )
    axes[1, 1].text(
        0.02,
        0.97,
        "%s\n%s" % (verdict, src),
        transform=axes[1, 1].transAxes,
        va="top",
        ha="left",
        color="#c9d1d9",
        fontsize=9,
    )

    plt.tight_layout()
    plt.savefig(args.out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print("saved:", args.out_png)


if __name__ == "__main__":
    main()
