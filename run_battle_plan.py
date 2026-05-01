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
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from repo_layout import find_script

REPO_ROOT = Path(__file__).resolve().parent


TARGETS = [
    {
        "script": "explore_chsh_strict_protocol.py",
        "must_contain": [
            "Strict CHSH protocol",
            "S = ",
            "saved: chsh_strict_protocol.png",
        ],
        "extract_regex": {
            "chsh_strict_S": r"S = ([0-9.+-]+)\s+\(",
        },
        "max_metrics": {
            "chsh_strict_S": 2.02,
        },
    },
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
    {
        "script": "explore_directionality_phase_diagram.py",
        "must_contain": [
            "Directionality phase diagram complete.",
            "corr(V, log10(D))",
            "saved: directionality_phase_diagram.png",
        ],
        "extract_regex": {
            "corr_V_logD": r"corr\(V, log10\(D\)\)\s*=\s*([0-9.+-]+)",
            "fit_rmse": r"rmse=([0-9.+-]+)",
        },
        "min_metrics": {
            "corr_V_logD": 0.45,
        },
    },
    {
        "script": "explore_chsh_strict_vs_postselected_compare.py",
        "must_contain": [
            "CHSH strict-vs-postselected compare complete.",
            "saved: chsh_strict_vs_postselected.png",
        ],
    },
    {
        "script": "explore_chsh_closure_protocol.py",
        "must_contain": [
            "CHSH closure-protocol audit",
            "preregistered verdict = PASS",
            "saved: chsh_closure_protocol.png",
        ],
        "extract_regex": {
            "closure_strict_max_S": r"strict max S = ([0-9.+-]+)",
            "closure_post_max_S": r"postselected max S = ([0-9.+-]+)",
            "closure_gap": r"gap\(post - strict\) = ([0-9.+-]+)",
        },
        "max_metrics": {
            "closure_strict_max_S": 2.02,
        },
    },
    {
        "script": "explore_chsh_local_wave_closure_full.py",
        "must_contain": [
            "CHSH local-wave closure full audit",
            "scan max strict S =",
            "scan max post S =",
            "saved: chsh_local_wave_closure_full.png",
        ],
        "extract_regex": {
            "full_scan_strict_max_S": r"scan max strict S = ([0-9.+-]+)",
            "full_scan_post_max_S": r"scan max post S = ([0-9.+-]+)",
            "full_scan_gap": r"scan gap\(post-strict\) = ([0-9.+-]+)",
        },
        "max_metrics": {
            "full_scan_strict_max_S": 2.02,
        },
    },
    {
        "script": "explore_threshold_detector_clicks.py",
        "must_contain": [
            "Threshold detector clicks experiment complete.",
            "pearson_r =",
            "saved: threshold_detector_clicks.png",
        ],
        "extract_regex": {
            "threshold_hit_rate": r"hit_rate = ([0-9.+-]+)",
            "threshold_pearson_r": r"pearson_r = ([0-9.+-]+)",
        },
        "min_metrics": {
            "threshold_pearson_r": 0.35,
        },
    },
]


def run_one(script_cfg):
    script = script_cfg["script"]
    script_path = find_script(REPO_ROOT, script)
    if not script_path.is_file():
        dt = 0.0
        return {
            "script": script,
            "ok": False,
            "return_code": 2,
            "elapsed_sec": dt,
            "extracted": {},
            "stdout_tail": "battle_plan: script not found -> %s" % script_path,
        }
    t0 = time.time()
    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")
    # 与 run_with_mpl_compat 一致：子脚本需导入仓库根目录下 ce_engine_v2 等模块
    _pp = str(REPO_ROOT)
    if env.get("PYTHONPATH"):
        env["PYTHONPATH"] = _pp + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = _pp
    p = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
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

    min_metrics = script_cfg.get("min_metrics", {})
    for mk, mv in min_metrics.items():
        got = extracted.get(mk)
        if got is None:
            ok = False
            continue
        try:
            if float(got) < float(mv):
                ok = False
        except Exception:
            ok = False
    max_metrics = script_cfg.get("max_metrics", {})
    for mk, mv in max_metrics.items():
        got = extracted.get(mk)
        if got is None:
            ok = False
            continue
        try:
            if float(got) > float(mv):
                ok = False
        except Exception:
            ok = False

    return {
        "script": script,
        "ok": ok,
        "return_code": p.returncode,
        "elapsed_sec": round(dt, 3),
        "extracted": extracted,
        "stdout_tail": "\n".join(out.splitlines()[-20:]),
    }


def _safe_read_image(path):
    """PNG 默认在仓库根（cwd）；否则尝试根目录与 scripts/explore/。"""
    p = Path(path)
    candidates = []
    if p.is_absolute():
        candidates.append(p)
    else:
        candidates.append(Path.cwd() / p)
        candidates.append(REPO_ROOT / p.name)
        candidates.append(REPO_ROOT / "scripts" / "explore" / p.name)
    for c in candidates:
        if c.is_file():
            try:
                return mpimg.imread(str(c))
            except Exception:
                return None
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
        ("chsh_strict_vs_postselected.png", "CHSH strict vs postselected"),
        ("chsh_closure_protocol.png", "CHSH closure protocol"),
        ("chsh_local_wave_closure_full.png", "CHSH local-wave closure full"),
        ("directional_emission_comparison.png", "Directional emission"),
        ("directional_double_slit_compare.png", "Directional double slit"),
        ("directionality_phase_diagram.png", "Directionality phase diagram"),
        ("threshold_detector_clicks.png", "Threshold detector clicks"),
        ("quantum_eraser_delayed_choice.png", "Quantum eraser"),
        ("bell_chsh_two_tracks.png", "Bell two tracks"),
        ("red_green_interference_analogy.png", "Red/green analogy"),
    ]

    for i, (fname, title) in enumerate(tiles[:5]):
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

