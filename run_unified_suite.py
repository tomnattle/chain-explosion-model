"""
统一入口：按组运行 CE 仿真 / 验证与发现 / 探索脚本，并输出明确的 PASS 或 FAIL 及原因。

设计态度（自检）：
  - 子进程 returncode==0 不代表物理正确；本脚本对若干脚本尝试解析 stdout 做额外门禁。
  - 门禁阈值可能被参数漂移打破；失败时请先看「原因」再决定是否改模型或放宽 --relaxed。
  - 探索类脚本部分是「记录现象」而非教科书定理；门禁只做空值/一致性 sanity check。

用法（仓库根目录）:
    python run_unified_suite.py              # 全部组
    python run_unified_suite.py -g verify    # 仅验证+发现（6 个）
    python run_unified_suite.py -g explore
    python run_unified_suite.py -g ce
    python run_unified_suite.py -g extended  # 额外 verify_*（若存在）
    python run_unified_suite.py --dry-run
    python run_unified_suite.py --relaxed    # 降低相关系数/幂律门禁

环境:
  - 强制 MPLBACKEND=Agg，避免阻塞。
  - Windows 下用 chcp 65001 启动子进程，减少控制台编码问题。

兼容: 避免 from __future__ import annotations，以支持 Python 3.6。
"""
import argparse
import os
import platform
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent
# 子进程先加载 mpl_compat，避免 Agg 下中文缺字形刷 RuntimeWarning
MPL_LAUNCHER = REPO_ROOT / "run_with_mpl_compat.py"

# ---------------------------------------------------------------------------
# 子进程
# ---------------------------------------------------------------------------


def _child_env() -> dict:
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    return env


def _decode_out(b: Optional[bytes]) -> str:
    if not b:
        return ""
    return b.decode("utf-8", errors="replace")


def run_script(repo: Path, script_name: str, env: dict) -> Tuple[int, str, str]:
    path = repo / script_name
    exe = sys.executable
    path_s = str(path)
    use_launcher = MPL_LAUNCHER.is_file()
    launch_s = str(MPL_LAUNCHER)
    if platform.system() == "Windows":
        if use_launcher:
            cmdline = 'chcp 65001 >nul && "{}" "{}" "{}"'.format(
                exe,
                launch_s.replace('"', '\\"'),
                path_s.replace('"', '\\"'),
            )
        else:
            cmdline = 'chcp 65001 >nul && "{}" "{}"'.format(
                exe, path_s.replace('"', '\\"')
            )
        p = subprocess.run(
            cmdline,
            cwd=str(repo),
            env=env,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return p.returncode, _decode_out(p.stdout), _decode_out(p.stderr)
    argv = [exe, launch_s, path_s] if use_launcher else [exe, path_s]
    p = subprocess.run(
        argv,
        cwd=str(repo),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return p.returncode, _decode_out(p.stdout), _decode_out(p.stderr)


# ---------------------------------------------------------------------------
# 从 stdout 抽取度量
# ---------------------------------------------------------------------------


def _f(x: str) -> float:
    return float(x.strip())


def parse_pearson_r_verify_a(text: str) -> Optional[float]:
    m = re.search(r"与夫琅禾费公式的皮尔逊相关系数:\s*r\s*=\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_pearson_r_verify_b(text: str) -> Optional[float]:
    m = re.search(r"蒙特卡洛\s+皮尔逊相关系数:\s*r\s*=\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_alpha_verify_c(text: str) -> Optional[float]:
    m = re.search(r"幂律指数\s*α\s*=\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_discover_d_vis(text: str) -> Tuple[Optional[float], Optional[float]]:
    a = re.search(r"初始对比度:\s+V\s*=\s*([0-9.eE+-]+)", text)
    b = re.search(r"末端对比度:\s+V\s*=\s*([0-9.eE+-]+)", text)
    return (
        _f(a.group(1)) if a else None,
        _f(b.group(1)) if b else None,
    )


def parse_discover_e_verdict(text: str) -> Optional[str]:
    for line in text.splitlines():
        if line.strip().startswith("[OK]") or line.strip().startswith("[警告]"):
            return line.strip()
    return None


def parse_lorentz(text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    c = re.search(r"\|a⊕b\s*-\s*b⊕a\|\s*=\s*([0-9.eE+-]+)", text)
    a = re.search(r"结合链误差\s*≈\s*([0-9.eE+-]+)", text)
    vp = re.search(r"->\s*v'\s*=\s*([0-9.eE+-]+)\s*c", text)
    return (
        _f(c.group(1)) if c else None,
        _f(a.group(1)) if a else None,
        _f(vp.group(1)) if vp else None,
    )


def parse_median_intensity_ratio(text: str) -> Optional[float]:
    m = re.search(r"median\(loss/base\)\s*=\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_median_energy_step_ratio(text: str) -> Optional[float]:
    m = re.search(r"median\s+E_\{t\+1\}/E_t\s*=\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_causal_dx_median(text: str) -> Optional[float]:
    m = re.search(r"dx/dt\s*中位数.*?≈\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_fringe_slope(text: str) -> Optional[float]:
    m = re.search(r"拟合斜率\s*=\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# 校验器：返回 (是否通过, 原因一行)
# ---------------------------------------------------------------------------

Validator = Callable[[str, Path, bool], Tuple[bool, str]]


def check_png_exists(text: str, repo: Path, png: Optional[str], relaxed: bool) -> Tuple[bool, str]:
    if not png:
        return True, "(无期望 PNG)"
    p = repo / png
    if p.is_file():
        return True, f"PNG 已生成: {png}"
    return False, f"缺失输出文件: {png}"


def make_default(png: Optional[str]) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        return check_png_exists(text, repo, png, relaxed)

    return _v


def validate_pearson(script_hint: str, parser: Callable[[str], Optional[float]], png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        r = parser(text)
        if r is None:
            return False, f"无法从 stdout 解析皮尔逊 r（{script_hint}），输出可能改版"
        lo = 0.70 if relaxed else 0.90
        if r < lo:
            return (
                False,
                f"r={r:.4f} < 门禁 {lo:.2f}（{'relaxed' if relaxed else 'strict'}）；"
                f"相关系数不足，优先怀疑参数/网格/解析失败",
            )
        return True, f"r={r:.4f} >= {lo:.2f}"

    return _v


def validate_uncertainty_alpha(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        a = parse_alpha_verify_c(text)
        if a is None:
            return False, "无法解析幂律指数 α（verify_C 输出改版？）"
        dev = abs(a - (-1.0))
        lo = 0.6 if relaxed else 0.3
        if dev > lo:
            return (
                False,
                f"α={a:.4f}，与理论 -1 偏差 |Δα|={dev:.3f} > 允许 {lo:.2f}",
            )
        return True, f"α={a:.4f}，|Δα|={dev:.3f} <= {lo:.2f}"

    return _v


def validate_discover_d(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        v0, v1 = parse_discover_d_vis(text)
        if v0 is None or v1 is None:
            return False, "无法解析初始/末端对比度（discover_D 改版？）"
        if v0 <= v1 + 1e-6:
            return (
                False,
                f"对比度未随距离下降（V初={v0:.4f}, V末={v1:.4f}）；"
                f"与脚本叙事不符，怀疑参数或可见度计算",
            )
        return True, f"V: {v0:.4f} -> {v1:.4f}（衰减方向正确）"

    return _v


def validate_discover_e(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        line = parse_discover_e_verdict(text)
        if line is None:
            return False, "未找到 [OK]/[警告] 判语（discover_E 改版？）"
        if line.startswith("[警告]"):
            return False, f"阈值判语: {line}"
        if line.startswith("[OK]"):
            return True, line
        return False, f"未识别判语: {line}"

    return _v


def validate_discover_f(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        m = re.search(r"最优S/A\s*=\s*([0-9.eE+-]+)", text)
        if not m:
            return True, "未解析最优 S/A（仅 smoke）；PNG 已生成"
        r = _f(m.group(1))
        if not (r > 0.0) or not (r < 1.0 + 1e6):
            return False, f"最优 S/A={r} 非有限正数？"
        return True, f"最优 S/A={r:.6f}（探索项，无语义阈值）"

    return _v


def validate_lorentz() -> Validator:
    """无 PNG；仅数值代数自洽。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        c, assoc, vp = parse_lorentz(text)
        if c is None or assoc is None or vp is None:
            return False, "无法解析洛伦兹自检数值（输出改版？）"
        if c > 1e-9 or assoc > 1e-9:
            return (
                False,
                f"交换/结合误差过大: commute={c:.3e}, assoc={assoc:.3e}",
            )
        if abs(vp - 1.0) > 1e-5:
            return False, f"v' 应≈1，得 {vp:.6f}"
        return True, f"commute={c:.3e}, assoc={assoc:.3e}, v'={vp:.6f}"

    return _v


def validate_visibility_loss(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        ratio = parse_median_intensity_ratio(text)
        if ratio is None:
            return False, "无法解析 median(loss/base)（脚本改版？）"
        if ratio >= 1.0 - 1e-6:
            return (
                False,
                f"median(loss/base)={ratio:.6f} 应明显 <1；"
                f"均匀损耗未压低总强度，怀疑未应用 loss 或步数/η 异常",
            )
        return (
            True,
            f"强度比={ratio:.4f}<1（V 对全局标度不变是预期；见脚本说明）",
        )

    return _v


def validate_energy_budget(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        med = parse_median_energy_step_ratio(text)
        if med is None:
            return False, "无法解析 median E_{t+1}/E_t"
        if med <= 1.0:
            return (
                False,
                f"步间中位比={med:.6g}；当前 ce_engine_v2 文档预期常>1（总量增长）。"
                f"若已改内核或归一化，请更新门禁或脚本说明",
            )
        return (
            True,
            f"步间中位比={med:.4f}>1（与「未全局归一、sum(E) 常增长」一致；非守恒检验）",
        )

    return _v


def validate_causal_front(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        dx = parse_causal_dx_median(text)
        if dx is None:
            return False, "无法解析 dx/dt 中位数"
        if not (0.85 <= dx <= 1.15):
            return (
                False,
                f"dx/dt 中位数={dx:.4f} 超出 [0.85,1.15]；怀疑传播核或步进定义变更",
            )
        return True, f"dx/dt 中位数={dx:.4f}（因果前缘 ~1 格/步）"

    return _v


def validate_fringe_spacing(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        slope = parse_fringe_slope(text)
        if slope is None or not (slope == slope):
            return False, "无法解析拟合斜率或 NaN"
        notes = []
        if slope > -0.2:
            notes.append(
                f"斜率={slope:.3f} 与远场 Δy∝1/d（期望约 -1）偏离大；"
                f"可能是离散/近场/有效波长定义，非 runner 硬失败条件"
            )
        msg = "；".join(notes) if notes else f"log-log 斜率={slope:.4f}"
        return True, msg

    return _v


# ---------------------------------------------------------------------------
# 任务表
# ---------------------------------------------------------------------------


@dataclass
class Job:
    script: str
    group: str
    title: str
    expect_png: Optional[str]
    validate: Validator


def build_jobs() -> List[Job]:
    return [
        Job(
            "ce_00_double_slit_demo.py",
            "ce",
            "CE-00 双缝演示",
            None,
            make_default(None),
        ),
        Job(
            "ce_01_visibility_vs_screen_distance.py",
            "ce",
            "CE-01 对比度-屏距",
            None,
            make_default(None),
        ),
        Job(
            "ce_02_double_slit_screen_statistics.py",
            "ce",
            "CE-02 屏上统计",
            None,
            make_default(None),
        ),
        Job(
            "ce_03_visibility_vs_side_coupling_S.py",
            "ce",
            "CE-03 V vs S",
            "V_vs_S.png",
            make_default("V_vs_S.png"),
        ),
        Job(
            "ce_04_measurement_absorption_at_slit.py",
            "ce",
            "CE-04 缝口吸收",
            "measurement_effect.png",
            make_default("measurement_effect.png"),
        ),
        Job(
            "ce_05_finite_absorber_detector.py",
            "ce",
            "CE-05 有限吸收体",
            "finite_absorber.png",
            make_default("finite_absorber.png"),
        ),
        Job(
            "ce_06_delayed_choice_absorber.py",
            "ce",
            "CE-06 延迟选择",
            "delayed_choice.png",
            make_default("delayed_choice.png"),
        ),
        Job(
            "ce_07_measurement_phase_diagram_scan.py",
            "ce",
            "CE-07 测量相图",
            "measurement_phase_diagram.png",
            make_default("measurement_phase_diagram.png"),
        ),
        Job(
            "ce_08_entanglement_split_wavepackets.py",
            "ce",
            "CE-08 纠缠分包",
            "entanglement_simulation.png",
            make_default("entanglement_simulation.png"),
        ),
        Job(
            "ce_09_entanglement_with_phase_field.py",
            "ce",
            "CE-09 相位场纠缠",
            "entanglement_with_phase.png",
            make_default("entanglement_with_phase.png"),
        ),
        Job(
            "ce_10_entanglement_distance_scan_numba.py",
            "ce",
            "CE-10 距离扫描(Numba)",
            "entanglement_scan_numba.png",
            make_default("entanglement_scan_numba.png"),
        ),
        Job(
            "verify_A_fraunhofer.py",
            "verify",
            "验证A 夫琅禾费",
            "verify_A_fraunhofer.png",
            validate_pearson("verify_A", parse_pearson_r_verify_a, "verify_A_fraunhofer.png"),
        ),
        Job(
            "verify_B_born_rule.py",
            "verify",
            "验证B 波恩规则",
            "verify_B_born_rule.png",
            validate_pearson("verify_B", parse_pearson_r_verify_b, "verify_B_born_rule.png"),
        ),
        Job(
            "verify_C_uncertainty.py",
            "verify",
            "验证C 不确定性",
            "verify_C_uncertainty.png",
            validate_uncertainty_alpha("verify_C_uncertainty.png"),
        ),
        Job(
            "discover_D_visibility_decay.py",
            "verify",
            "发现D 对比度衰减",
            "discover_D_visibility_decay.png",
            validate_discover_d("discover_D_visibility_decay.png"),
        ),
        Job(
            "discover_E_measurement_continuity.py",
            "verify",
            "发现E 测量连续性",
            "discover_E_measurement_continuity.png",
            validate_discover_e("discover_E_measurement_continuity.png"),
        ),
        Job(
            "discover_F_coupling_constant.py",
            "verify",
            "发现F 耦合常数",
            "discover_F_coupling_constant.png",
            validate_discover_f("discover_F_coupling_constant.png"),
        ),
        Job(
            "explore_lorentz_composition_selfcheck.py",
            "explore",
            "探索 洛伦兹代数自检",
            None,
            validate_lorentz(),
        ),
        Job(
            "explore_visibility_ce_vs_uniform_loss.py",
            "explore",
            "探索 均匀损耗 vs V",
            "explore_visibility_loss_compare.png",
            validate_visibility_loss("explore_visibility_loss_compare.png"),
        ),
        Job(
            "explore_energy_budget_propagation.py",
            "explore",
            "探索 能量预算 sum(E)",
            "explore_energy_budget.png",
            validate_energy_budget("explore_energy_budget.png"),
        ),
        Job(
            "explore_causal_front_2d.py",
            "explore",
            "探索 因果前缘 2D",
            "explore_causal_front.png",
            validate_causal_front("explore_causal_front.png"),
        ),
        Job(
            "explore_fringe_spacing_vs_slit_gap.py",
            "explore",
            "探索 条纹间隔 vs 缝距",
            "explore_fringe_spacing.png",
            validate_fringe_spacing("explore_fringe_spacing.png"),
        ),
        Job(
            "verify_D_interference_decay.py",
            "extended",
            "验证D 干涉衰减",
            "verify_D_interference_decay.png",
            make_default("verify_D_interference_decay.png"),
        ),
        Job(
            "verify_C_delayed_choice.py",
            "extended",
            "验证C 延迟选择",
            "verify_C_delayed_choice.png",
            make_default("verify_C_delayed_choice.png"),
        ),
        Job(
            "verify_B_which_way.py",
            "extended",
            "验证B Which-way",
            "verify_B_which_way.png",
            make_default("verify_B_which_way.png"),
        ),
    ]


def _print_job_header(n: int, total: int, job: Job) -> None:
    print()
    print("=" * 72)
    print(f"[{n}/{total}] ({job.group}) {job.title}")
    print(f"  脚本: {job.script}")
    print("=" * 72, flush=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CE 仓库统一回归入口（含门禁与原因）")
    parser.add_argument(
        "-g",
        "--group",
        choices=("all", "ce", "verify", "explore", "extended"),
        default="all",
        help="all=ce+verify+explore；extended=额外 verify_*（可与 all 同用请分次运行）",
    )
    parser.add_argument(
        "--relaxed",
        action="store_true",
        help="放宽 verify A/B 的 r 与 verify C 的 α 门禁",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅列出将运行的任务",
    )
    args = parser.parse_args(argv)

    all_jobs = build_jobs()
    groups: List[str]
    if args.group == "all":
        groups = ["ce", "verify", "explore"]
    else:
        groups = [args.group]

    jobs = [j for j in all_jobs if j.group in groups]
    env = _child_env()

    print("仓库:", REPO_ROOT)
    print("解释器:", sys.executable)
    print("组:", ", ".join(groups))
    print("门禁:", "relaxed" if args.relaxed else "strict")

    if args.dry_run:
        for i, j in enumerate(jobs, 1):
            png = j.expect_png or "(无)"
            print(f"  {i:3d}. [{j.group}] {j.script} -> {png}")
        print(f"\n共 {len(jobs)} 项（dry-run）")
        return 0

    results: List[Tuple[Job, str, str, str]] = []
    failed = 0
    t0 = time.perf_counter()

    for i, job in enumerate(jobs, 1):
        _print_job_header(i, len(jobs), job)
        path = REPO_ROOT / job.script
        if not path.is_file():
            print("[FAIL] 未找到脚本文件")
            print(f"  原因: 路径不存在 -> {path}")
            results.append((job, "FAIL", "missing_file", str(path)))
            failed += 1
            continue

        t1 = time.perf_counter()
        rc, out, err = run_script(REPO_ROOT, job.script, env)
        elapsed = time.perf_counter() - t1

        if rc != 0:
            print(f"[FAIL] 子进程 exit={rc}，用时 {elapsed:.1f}s")
            print(f"  原因: 运行异常终止（非零退出码）")
            tail = (err or out or "").strip().splitlines()
            for line in tail[-5:]:
                print(f"  stderr/stdout 尾部: {line}")
            results.append((job, "FAIL", f"exit_{rc}", ""))
            failed += 1
            continue

        ok, reason = job.validate(out, REPO_ROOT, args.relaxed)
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{status}] 用时 {elapsed:.1f}s")
        print(f"  依据: {reason}")
        if err.strip():
            print(f"  注意: 子进程 stderr 非空（前 3 行）")
            for line in err.strip().splitlines()[:3]:
                print(f"    {line}")
        results.append((job, status, reason, ""))

    total = time.perf_counter() - t0

    print()
    print("=" * 72)
    print("汇总（逐项 PASS/FAIL + 原因）")
    print("=" * 72)
    for job, status, reason, extra in results:
        flag = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"{flag} [{job.group:8s}] {job.script}")
        print(f"         {reason}")
        if extra:
            print(f"         {extra}")

    print("-" * 72)
    print(
        f"合计: {len(jobs) - failed}/{len(jobs)} 通过，"
        f"{failed} 未通过，总用时 {total:.1f}s"
    )
    if failed:
        print("最终: SUITE_FAIL（存在 FAIL 项，退出码 1）")
        return 1
    print("最终: SUITE_PASS（退出码 0）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
