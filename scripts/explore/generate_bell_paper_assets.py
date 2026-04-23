#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    src_nist = root / "artifacts" / "reports" / "chsh_battle_result_nist.json"
    src_sim = root / "artifacts" / "reports" / "chsh_battle_result.json"
    nist = load_json(src_nist)
    sim = load_json(src_sim)

    out_base = root / "papers" / "bell-audit-paper"
    out_fig = out_base / "figures"
    out_tab = out_base / "tables"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_tab.mkdir(parents=True, exist_ok=True)

    labels = ["NIST", "SimFallback"]
    s_strict = [nist["strict"]["S"], sim["strict"]["S"]]
    s_standard = [nist["standard"]["S"], sim["standard"]["S"]]
    pair_strict = [nist["strict"]["pair_count"], sim["strict"]["pair_count"]]
    pair_standard = [nist["standard"]["pair_count"], sim["standard"]["pair_count"]]

    x = np.arange(len(labels))
    w = 0.34

    # Figure 1: strict vs standard S
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.bar(x - w / 2, s_strict, width=w, label="strict S", color="#4e79a7")
    ax.bar(x + w / 2, s_standard, width=w, label="standard S", color="#f28e2b")
    ax.axhline(2.0, linestyle="--", linewidth=1.2, color="#666666", label="S=2 reference")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("S")
    ax.set_title("Strict vs Standard CHSH S")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_fig / "fig1_strict_vs_standard_s.png", dpi=180)
    plt.close(fig)

    # Figure 2: pair_count vs S (scatter)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.scatter(pair_strict, s_strict, s=80, marker="o", color="#4e79a7", label="strict")
    ax.scatter(pair_standard, s_standard, s=80, marker="s", color="#f28e2b", label="standard")
    for i, lab in enumerate(labels):
        ax.annotate(f"{lab}-strict", (pair_strict[i], s_strict[i]), textcoords="offset points", xytext=(6, 6), fontsize=8)
        ax.annotate(
            f"{lab}-standard",
            (pair_standard[i], s_standard[i]),
            textcoords="offset points",
            xytext=(6, -10),
            fontsize=8,
        )
    ax.set_xlabel("pair_count")
    ax.set_ylabel("S")
    ax.set_title("Pair Count vs S (Protocol Split)")
    ax.grid(alpha=0.25, linestyle="--")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_fig / "fig2_paircount_vs_s.png", dpi=180)
    plt.close(fig)

    # Figure 3: delta (standard - strict)
    delta = [s_standard[i] - s_strict[i] for i in range(len(labels))]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    bars = ax.bar(labels, delta, color=["#59a14f", "#e15759"])
    ax.axhline(0.0, linestyle="--", linewidth=1.0, color="#666666")
    ax.set_ylabel("Delta S (standard - strict)")
    ax.set_title("Protocol Delta Across Configurations")
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2.0, h, f"{h:.4f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_fig / "fig3_protocol_delta_s.png", dpi=180)
    plt.close(fig)

    table1 = [
        "# Table 1: Protocol Configuration Registry",
        "",
        "| config | source | strict_window | standard_window | strict_pair_count | standard_pair_count |",
        "|---|---|---:|---:|---:|---:|",
        (
            f"| NIST | {nist.get('source')} | {nist['strict']['window']} | {nist['standard']['window']} | "
            f"{nist['strict']['pair_count']} | {nist['standard']['pair_count']} |"
        ),
        (
            f"| SimFallback | {sim.get('source')} | {sim['strict']['window']} | {sim['standard']['window']} | "
            f"{sim['strict']['pair_count']} | {sim['standard']['pair_count']} |"
        ),
    ]
    (out_tab / "table1_protocol_registry.md").write_text("\n".join(table1), encoding="utf-8")

    table2 = [
        "# Table 2: Key CHSH Results and Gate Status",
        "",
        "| config | S_strict | S_standard | Delta(standard-strict) | engineering_pass | thesis_pass | thesis_reason |",
        "|---|---:|---:|---:|---|---|---|",
        (
            f"| NIST | {nist['strict']['S']:.6f} | {nist['standard']['S']:.6f} | "
            f"{(nist['standard']['S'] - nist['strict']['S']):.6f} | {nist.get('engineering_pass')} | "
            f"{nist.get('thesis_pass')} | {('; '.join(nist.get('thesis_reasons', [])))} |"
        ),
        (
            f"| SimFallback | {sim['strict']['S']:.6f} | {sim['standard']['S']:.6f} | "
            f"{(sim['standard']['S'] - sim['strict']['S']):.6f} | {sim.get('engineering_pass')} | "
            f"{sim.get('thesis_pass')} | {('; '.join(sim.get('thesis_reasons', [])))} |"
        ),
    ]
    (out_tab / "table2_key_results.md").write_text("\n".join(table2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
