"""
run_battle_plan.py
------------------
One-command runner for current "battle plan" exploration scripts.

Runs selected scripts, prints compact status, and writes JSON summary:
  test_artifacts/battle_plan_summary.json
"""

import json
import os
import re
import subprocess
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


TARGETS = [
    {
        "script": "explore_directional_emission.py",
        "must_contain": [
            "Directional emission comparison complete.",
            "saved: directional_emission_comparison.png",
        ],
    },
    {
        "script": "explore_directional_double_slit_compare.py",
        "must_contain": [
            "Directional double-slit comparison complete.",
            "saved: directional_double_slit_compare.png",
        ],
        "extract_regex": {
            "V_near_isotropic": r"near-isotropic weights: .* V=([0-9.]+)",
            "V_directional": r"directional\s+weights: .* V=([0-9.]+)",
        },
    },
    {
        "script": "explore_quantum_eraser_delayed_choice.py",
        "must_contain": [
            "quantum eraser / delayed-choice toy",
            "saved: quantum_eraser_delayed_choice.png",
        ],
    },
    {
        "script": "explore_bell_chsh_two_tracks.py",
        "must_contain": [
            "S = ",
            "S_like = ",
            "已保存图像: bell_chsh_two_tracks.png",
            "已保存图像: red_green_interference_analogy.png",
        ],
        "extract_regex": {
            "S_strict": r"S = ([0-9.+-]+)\s+\(",
            "S_wave_like": r"S_like = ([0-9.+-]+)\s+\(",
        },
    },
]


def run_one(script_cfg):
    script = script_cfg["script"]
    t0 = time.time()
    p = subprocess.run(
        [sys.executable, script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    dt = time.time() - t0
    raw = p.stdout or b""
    if isinstance(raw, str):
        out = raw
    else:
        try:
            out = raw.decode("utf-8")
        except Exception:
            try:
                out = raw.decode("gbk")
            except Exception:
                out = raw.decode("utf-8", errors="replace")

    ok = p.returncode == 0
    for token in script_cfg.get("must_contain", []):
        if token not in out:
            ok = False
            break

    extracted = {}
    for k, pat in script_cfg.get("extract_regex", {}).items():
        m = re.search(pat, out)
        if m:
            try:
                extracted[k] = float(m.group(1))
            except ValueError:
                extracted[k] = m.group(1)

    return {
        "script": script,
        "ok": ok,
        "return_code": p.returncode,
        "elapsed_sec": round(dt, 3),
        "extracted": extracted,
        "stdout_tail": "\n".join(out.splitlines()[-20:]),
    }


def _safe_read_image(path):
    if not os.path.isfile(path):
        return None
    try:
        return mpimg.imread(path)
    except Exception:
        return None


def build_dashboard(results, out_png):
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes.flat:
        ax.set_facecolor("#0d1117")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    tiles = [
        ("directional_emission_comparison.png", "Directional emission"),
        ("directional_double_slit_compare.png", "Directional double slit"),
        ("quantum_eraser_delayed_choice.png", "Quantum eraser"),
        ("bell_chsh_two_tracks.png", "Bell two tracks"),
        ("red_green_interference_analogy.png", "Red/green analogy"),
    ]

    for i, (fname, title) in enumerate(tiles):
        ax = axes.flat[i]
        img = _safe_read_image(fname)
        if img is not None:
            ax.imshow(img)
        else:
            ax.text(
                0.5,
                0.5,
                "missing:\n%s" % fname,
                ha="center",
                va="center",
                color="#8b949e",
                fontsize=10,
            )
        ax.set_title(title, color="white", fontsize=10)

    # 最后一格：指标文本
    axm = axes.flat[5]
    axm.axis("off")
    lines = ["Battle Plan Metrics"]
    for row in results:
        if not row.get("ok", False):
            continue
        s = row.get("script", "")
        ext = row.get("extracted", {})
        if not ext:
            continue
        parts = ["%s=%s" % (k, v) for k, v in sorted(ext.items())]
        lines.append("- %s" % s)
        lines.append("  " + ", ".join(parts))
    if len(lines) == 1:
        lines.append("- no extracted metrics")
    axm.text(
        0.02,
        0.98,
        "\n".join(lines),
        va="top",
        ha="left",
        color="#c9d1d9",
        fontsize=10,
        family="monospace",
    )

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)


def main():
    os.makedirs("test_artifacts", exist_ok=True)
    started = time.strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for cfg in TARGETS:
        row = run_one(cfg)
        rows.append(row)
        status = "PASS" if row["ok"] else "FAIL"
        print(f"[{status}] {row['script']} ({row['elapsed_sec']}s)")
        if row["extracted"]:
            print("  metrics:", row["extracted"])

    all_ok = all(r["ok"] for r in rows)
    payload = {
        "started_at": started,
        "python": sys.version.split()[0],
        "all_ok": all_ok,
        "results": rows,
    }
    out_json = os.path.join("test_artifacts", "battle_plan_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    out_png = "battle_plan_dashboard.png"
    build_dashboard(rows, out_png)

    print("\nBattle plan run complete.")
    print("overall:", "PASS" if all_ok else "FAIL")
    print("summary:", out_json)
    print("dashboard:", out_png)

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

