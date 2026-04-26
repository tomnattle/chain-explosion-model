#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    in_path = Path("artifacts/ripple_quantum_tests_v3_derived/RIPPLE_QUANTUM_TESTS_V3_RESULTS.json")
    out_dir = Path("artifacts/ripple_quantum_tests_v3_derived")
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(in_path.read_text(encoding="utf-8"))
    rows = {r["name"]: r for r in data["results"]}
    mri = rows["mri_larmor"]
    clock = rows["atomic_clock_modes"]

    lines = [
        "# v3 未闭环原因诊断（derived）",
        "",
        "本报告只基于 `constant_mode=derived` 结果。",
        "",
        "## MRI 未闭环原因",
        "",
        f"- shape_pass: `{mri['shape_pass']}`",
        f"- constant_pass: `{mri['constant_pass']}`",
        f"- final_pass: `{mri['final_pass']}`",
        f"- 诊断信息: `{mri['note']}`",
        "",
        "判定：当前主要问题不是曲线形状，而是关键常数（gamma）没有由模型参数推导到容差范围内。",
        "",
        "## 原子钟未闭环原因",
        "",
        f"- shape_pass: `{clock['shape_pass']}`",
        f"- constant_pass: `{clock['constant_pass']}`",
        f"- final_pass: `{clock['final_pass']}`",
        f"- 诊断信息: `{clock['note']}`",
        "",
        "判定：原子钟同时存在形状与常数两层差距；当前 cavity 参数映射尚不足以稳定复现实测目标中心频率。",
        "",
        "## 下一步任务（只做 derived）",
        "",
        "1. MRI：对 `(mu, kappa, rho, eta)` 进行受限扫描，最小化 `gamma_rel_err`；",
        "2. 原子钟：对 `(length_m, wave_speed_m_s, mode_index)` 做物理可行约束扫描，最小化 `center_err_hz` 与形状误差；",
        "3. 新结论仅以 `final_pass` 报告，禁止单独引用 `shape_pass`。",
    ]
    (out_dir / "RIPPLE_QUANTUM_TESTS_V3_OPEN_LOOPS.zh.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V3_OPEN_LOOPS.zh.md")


if __name__ == "__main__":
    main()
