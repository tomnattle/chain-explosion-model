"""
统一入口：按组运行 CE 仿真 / 验证与发现 / 探索脚本，并输出明确的 PASS 或 FAIL 及原因。

设计态度（自检）：
  - 子进程 returncode==0 不代表物理正确；本脚本对若干脚本尝试解析 stdout 做额外门禁。
  - 门禁阈值可能被参数漂移打破；失败时请先看「原因」再决定是否改模型或放宽 --relaxed。
  - 默认 strict：`explore_fringe_spacing_vs_slit.py` 外均需实质 PNG（字节数+方差）、更严的数值带；`--relaxed` 略放宽若干 explore/critique/verify 阈值。
  - 探索类脚本部分是「记录现象」而非教科书定理；门禁只做空值/一致性 sanity check。
  - 不包含 verify_A_fraunhofer：离散链式传播与连续夫琅禾费解析式不对等，用皮尔逊 r 做硬门禁易误判（类「拿错尺子」）。
  - verify_uncertainty：记录拟合指数 alpha，不设与 -1 硬比；discover_measurement_continuity：[警告] 仍为探索软通过。
  - 新增 explore 质疑项：因果锥各向异性、公式层光速不变（与格子核分开）、双缝镜像宇称残差。
  - critique 组：7 条「对外表述/机理边界」回归；默认 all 已包含 critique。
    其对 PNG 做非空/对比度检查，并对可量化脚本设可复现数值公差（漂移即 FAIL）。
  - 与 critique 同批收紧的 explore 质疑 3 条：因果锥各向异性比、双缝镜像宇称（公式层光速不变已硬比）。

用法（仓库根目录）:
    python run_unified_suite.py              # ce+verify+explore+critique；默认写入 test_artifacts/ 并更新 README 动态区块
    python run_unified_suite.py --no-artifacts
    python run_unified_suite.py --no-readme-patch
    python run_unified_suite.py -g verify    # 仅验证+发现（5 个）
    python run_unified_suite.py -g explore
    python run_unified_suite.py -g critique # 仅 7 条质疑脚本
    python run_unified_suite.py -g ce
    python run_unified_suite.py -g extended  # 额外 verify_*（若存在）
    python run_unified_suite.py -g research  # 仅 run_battle_plan.py 聚合门禁
    python run_unified_suite.py --with-battle-plan  # 在当前组之外追加 research 门禁
    python run_unified_suite.py --dry-run
    python run_unified_suite.py --relaxed    # 放宽 Born r、discover_E([警告]可过)、PNG 尺寸/对比度下限及若干 critique/explore 数值带

环境:
  - 强制 MPLBACKEND=Agg，避免阻塞。
  - Windows 下用 chcp 65001 启动子进程，减少控制台编码问题。

兼容: 避免 from __future__ import annotations，以支持 Python 3.6。
"""
import argparse
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import matplotlib.image as mpimg
import numpy as np

from repo_layout import find_generated_output, find_script
import suite_artifacts as sa
from experiment_dossier import dossier_fields_for_readme

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
    path = find_script(repo, script_name)
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


def parse_pearson_r_verify_b(text: str) -> Optional[float]:
    m = re.search(r"蒙特卡洛\s+皮尔逊相关系数:\s*r\s*=\s*([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_hit_rate_verify_b(text: str) -> Optional[float]:
    """
    解析 stdout 里的命中率：
      击中屏幕: {hits:,} / {N_PHOTONS:,} ({hit_rate*100:.1f}%)
    返回命中率 hit_rate（0~1）。
    """
    m = re.search(
        r"击中屏幕:\s*([0-9,]+)\s*/\s*([0-9,]+)\s*\(([0-9.+-eE]+)%\)",
        text,
    )
    if not m:
        return None
    hits_s, total_s, pct_s = m.group(1), m.group(2), m.group(3)
    try:
        hits = int(hits_s.replace(",", ""))
        total = int(total_s.replace(",", ""))
    except Exception:
        return None
    if total <= 0:
        return None
    hit_rate = hits / total
    # 允许百分比解析偏差，但用 hits/total 作为主要来源
    return hit_rate


def parse_visibility_mc_verify_b(text: str) -> Optional[float]:
    m = re.search(r"蒙特卡洛对比度 V\s*=\s*([0-9.eE+-]+)", text)
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
    """匹配 explore_fringe_spacing_vs_slit  stdout；亦可从 dossier JSON 回退解析。"""
    m = re.search(r"拟合斜率\s*=\s*([0-9.eE+-]+)", text)
    if m:
        return _f(m.group(1))
    m2 = re.search(r'"loglog_slope_fitted"\s*:\s*([0-9.eE+-]+)', text)
    return _f(m2.group(1)) if m2 else None


def parse_causal_aniso_ratio(text: str) -> Optional[float]:
    m = re.search(
        r"各向异性比 median\(R_L1_max / \(R_plus\+0\.5\)\) = ([0-9.eE+-]+)",
        text,
    )
    return _f(m.group(1)) if m else None


def parse_relativity_v_prime(text: str) -> Optional[float]:
    m = re.search(r"洛伦兹逆变 v'\s*=\s*([0-9.eE+-]+)\s*c", text)
    return _f(m.group(1)) if m else None


def parse_mirror_asym(text: str) -> Optional[float]:
    m = re.search(r"相对不对称度 asym = ([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_mirror_corrcoef(text: str) -> Optional[float]:
    m = re.search(r"镜像皮尔逊 r_mirror = ([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_decay_nonuniqueness_rv(text: str) -> Optional[float]:
    m = re.search(r"V 轨迹皮尔逊 r_V_ce_vs_uniform = ([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_energy_ratio_RE(text: str) -> Optional[float]:
    m = re.search(r"总能量比 R_E = E_final/E0 = ([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_fitted_log_slope_critique(text: str) -> Optional[float]:
    m = re.search(r"拟合斜率 fitted_log_slope = ([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


def parse_critique04_v_grid(text: str) -> Optional[float]:
    m = re.search(r"右向前缘\) = ([0-9.eE+-]+)\s*格/步", text)
    return _f(m.group(1)) if m else None


def parse_critique04_v_prime(text: str) -> Optional[float]:
    m = re.search(r"逆变后 v' = ([0-9.eE+-]+)\s*c", text)
    return _f(m.group(1)) if m else None


def parse_critique06_median_Eratio(text: str) -> Optional[float]:
    m = re.search(r"median\(E_\{t\+1\}/E_t\) = ([0-9.eE+-]+)", text)
    return _f(m.group(1)) if m else None


# critique_07：远场连续近似下 reference=-1；本仓库 CE v2 在此脚本固定参数下可复现斜率约 -0.12。
CRITIQUE07_FITTED_LOG_SLOPE_GOLD = -0.1181
CRITIQUE07_FITTED_TOL = 0.032

# explore_causal_cone_anisotropy：曼哈顿前缘 vs L1 前缘中位比（4/3 邻域类离散常见值）。
CAUSAL_ANISO_RATIO_GOLD = 1.3333
CAUSAL_ANISO_RATIO_TOL = 0.045

# explore_double_slit_mirror_parity：B>0 时残差为主；与当前内核参数对齐的回归带。
MIRROR_ASYM_LO, MIRROR_ASYM_HI = 0.24, 0.40
MIRROR_R_LO, MIRROR_R_HI = 0.89, 0.95

# CE / verify 类：实质 PNG 下限（strict）；relaxed 用较宽一档。
CE_PNG_MIN_BYTES_STRICT = 9000
CE_PNG_MIN_STD_STRICT = 0.018
CE_PNG_MIN_BYTES_RELAXED = 5200
CE_PNG_MIN_STD_RELAXED = 0.011


# ---------------------------------------------------------------------------
# 校验器：返回 (是否通过, 原因一行)
# ---------------------------------------------------------------------------

Validator = Callable[[str, Path, bool], Tuple[bool, str]]


def check_png_exists(text: str, repo: Path, png: Optional[str], relaxed: bool) -> Tuple[bool, str]:
    if not png:
        return True, "(无期望 PNG)"
    p = find_generated_output(repo, png)
    if p.is_file():
        return True, f"PNG 已生成: {png}"
    return False, f"缺失输出文件: {png}"


def assert_png_substantive(repo: Path, png: str, min_bytes: int = 3500, min_std: float = 0.006) -> Tuple[bool, str]:
    """拒绝过小或近乎常数的 PNG（防空白/损坏输出）。"""
    p = find_generated_output(repo, png)
    if not p.is_file():
        return False, "缺失 PNG: %s" % png
    n = p.stat().st_size
    if n < min_bytes:
        return False, "PNG 过小(%d B)；疑似未正常绘图" % n
    try:
        img = np.asarray(mpimg.imread(str(p)), dtype=np.float64)
    except Exception as exc:
        return False, "无法读取 PNG(%s): %s" % (png, exc)
    if img.ndim == 3:
        tile = img[..., : min(3, img.shape[-1])]
    else:
        tile = img
    std = float(np.std(tile))
    if not math.isfinite(std) or std < min_std:
        return False, "PNG 像素对比度过低(std=%.6g)；疑似空白" % std
    return True, "PNG OK(size=%dB, std=%.4f)" % (n, std)


def make_default(png: Optional[str]) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        return check_png_exists(text, repo, png, relaxed)

    return _v


def make_ce_substantive_png(png: Optional[str]) -> Validator:
    """CE / extended verify_*：须非空白、有足够对比度的 PNG。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        if not png:
            return True, "(无期望 PNG)"
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        return assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)

    return _v


def validate_pearson(script_hint: str, parser: Callable[[str], Optional[float]], png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        r = parser(text)
        if r is None:
            return False, f"无法从 stdout 解析皮尔逊 r（{script_hint}），输出可能改版"
        # strict 高于旧版 0.90；略低于 0.965 以容纳 born MC 涨落（~0.93 仍应稳定通过）
        lo = 0.85 if relaxed else 0.93
        if r < lo:
            return (
                False,
                f"r={r:.4f} < 门禁 {lo:.3f}（{'relaxed' if relaxed else 'strict'}）；"
                f"相关系数不足，优先怀疑参数/网格/解析失败",
            )
        return True, f"{msg_s}；r={r:.4f} >= {lo:.3f}"

    return _v


def validate_verify_born_rule(png: str) -> Validator:
    """
    堵住 born rule 的“擦线通过”口子：
      除了皮尔逊 r，还要求 MC 命中率 hit_rate 和 MC 可见度 V 也达到阈值。
    """

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png

        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s

        r = parse_pearson_r_verify_b(text)
        if r is None:
            return False, "无法解析皮尔逊 r（verify_born_rule 输出改版？）"

        vis_mc = parse_visibility_mc_verify_b(text)
        if vis_mc is None:
            return False, "无法解析蒙特卡洛对比度 V（verify_born_rule 输出改版？）"

        hit_rate = parse_hit_rate_verify_b(text)
        if hit_rate is None:
            return False, "无法解析击中率 hit_rate（verify_born_rule 输出改版？）"

        # 阈值：strict 用本仓库当前设定下的稳定量级做底线，避免未来“噪声擦线”。
        r_lo = 0.85 if relaxed else 0.93
        hit_lo = 0.02 if relaxed else 0.035
        vis_lo = 0.08 if relaxed else 0.14

        if r < r_lo:
            return False, f"r={r:.4f} < 门禁 {r_lo:.3f}（strict/relaxed 不通过）"
        if hit_rate < hit_lo:
            return (
                False,
                f"hit_rate={hit_rate:.4f} < 门禁 {hit_lo:.3f}（统计量不足，易误判）",
            )
        if vis_mc < vis_lo:
            return (
                False,
                f"V_mc={vis_mc:.4f} < 门禁 {vis_lo:.3f}（MC 条纹对比度不够）",
            )

        return (
            True,
            f"{msg_s}；r={r:.4f}>= {r_lo:.3f}, hit_rate={hit_rate:.4f}>= {hit_lo:.3f}, V_mc={vis_mc:.4f}>= {vis_lo:.3f}",
        )

    return _v


def validate_verify_uncertainty_phenomenon(png: str) -> Validator:
    """verify_uncertainty：现象记录；解析 α 但不与 -1 硬比。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        a = parse_alpha_verify_c(text)
        if a is None:
            return False, "无法解析幂律指数 α（verify_uncertainty 输出改版？）"
        if not math.isfinite(a) or abs(a) > 6.0:
            return False, f"α={a} 非有限或超出合理现象范围（|α|≤6）"
        dev = abs(a - (-1.0))
        return (
            True,
            f"{msg_s}；alpha={a:.4f}，|Δalpha|={dev:.3f}（不与 -1 硬比；见脚本）",
        )

    return _v


def validate_discover_d(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        v0, v1 = parse_discover_d_vis(text)
        if v0 is None or v1 is None:
            return False, "无法解析初始/末端对比度（discover_visibility_decay 改版？）"
        if v0 <= v1 + 1e-6:
            return (
                False,
                f"对比度未随距离下降（V初={v0:.4f}, V末={v1:.4f}）；"
                f"与脚本叙事不符，怀疑参数或可见度计算",
            )
        rel_drop = (v0 - v1) / max(v0, 1e-9)
        min_rel = 0.012 if relaxed else 0.028
        if rel_drop < min_rel:
            return (
                False,
                "相对降幅 %.4f < 门禁 %.4f（V初=%.4f,V末=%.4f）；衰减过弱"
                % (rel_drop, min_rel, v0, v1),
            )
        return True, f"{msg_s}；V: {v0:.4f}->{v1:.4f}（降幅≈{100*rel_drop:.1f}%）"

    return _v


def validate_discover_e(png: str) -> Validator:
    """discover_E：strict 要求 [OK]；relaxed 仍允许 [警告]（可见度算法敏感）。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        line = parse_discover_e_verdict(text)
        if line is None:
            return False, "未找到 [OK]/[警告] 判语（discover_measurement_continuity 改版？）"
        if line.startswith("[警告]"):
            if relaxed:
                return True, f"{msg_s}；relaxed 通过: {line[:120]}..."
            return (
                False,
                "strict 要求 [OK]；当前为 [警告]（可加 --relaxed 或调脚本尖峰阈）",
            )
        if line.startswith("[OK]"):
            return True, f"{msg_s}；{line[:160]}"
        return False, f"未识别判语: {line}"

    return _v


def validate_discover_f(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        m = re.search(r"最优S/A\s*=\s*([0-9.eE+-]+)", text)
        if not m:
            return False, "未解析最优 S/A（discover_coupling_constant 须打印最终数值）"
        r = _f(m.group(1))
        if not (r > 0.0) or not (r < 1.0 + 1e6):
            return False, f"最优 S/A={r} 非有限正数？"
        return True, f"{msg_s}；最优 S/A={r:.6f}"

    return _v


def validate_lorentz() -> Validator:
    """无 PNG；仅数值代数自洽。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        c, assoc, vp = parse_lorentz(text)
        if c is None or assoc is None or vp is None:
            return False, "无法解析洛伦兹自检数值（输出改版？）"
        lim_c = 5e-9 if relaxed else 8e-12
        lim_vp = 3e-5 if relaxed else 5e-7
        if c > lim_c or assoc > lim_c:
            return (
                False,
                f"交换/结合误差过大: commute={c:.3e}, assoc={assoc:.3e}（阈≈{lim_c:.1e}）",
            )
        if abs(vp - 1.0) > lim_vp:
            return False, f"v' 应≈1，得 {vp:.9f}（|Δ|≤{lim_vp:.1e}）"
        return True, f"commute={c:.3e}, assoc={assoc:.3e}, v'={vp:.9f}"

    return _v


def validate_lorentz_with_png(png: str) -> Validator:
    """洛伦兹数值门禁 + 归档用 PNG 须存在且非空白。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        inner = validate_lorentz()
        ok2, msg2 = inner(text, repo, relaxed)
        if not ok2:
            return False, msg2
        return True, "%s；%s" % (msg_s, msg2)

    return _v


def validate_visibility_loss(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        ratio = parse_median_intensity_ratio(text)
        if ratio is None:
            return False, "无法解析 median(loss/base)（脚本改版？）"
        cap = 0.992 if relaxed else 0.975
        if ratio >= cap:
            return (
                False,
                f"median(loss/base)={ratio:.6f} 应 < {cap:.3f}；"
                f"均匀损耗未足够压低总强度",
            )
        return (
            True,
            f"{msg_s}；强度比={ratio:.4f}（V 对全局标度不变是预期）",
        )

    return _v


def validate_energy_budget(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        med = parse_median_energy_step_ratio(text)
        if med is None:
            return False, "无法解析 median E_{t+1}/E_t"
        floor = 1.004 if relaxed else 1.018
        if med <= floor:
            return (
                False,
                f"步间中位比={med:.6g}；应 > {floor:.3f}（未归一核总量增长须可分辨）",
            )
        return (
            True,
            f"{msg_s}；步间中位比={med:.4f}>1",
        )

    return _v


def validate_causal_front(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        dx = parse_causal_dx_median(text)
        if dx is None:
            return False, "无法解析 dx/dt 中位数"
        lo, hi = (0.88, 1.12) if relaxed else (0.94, 1.06)
        if not (lo <= dx <= hi):
            return (
                False,
                f"dx/dt 中位数={dx:.4f} 超出 [{lo:.2f},{hi:.2f}]",
            )
        return True, f"{msg_s}；dx/dt 中位数={dx:.4f}"

    return _v


def validate_causal_anisotropy_probe(png: str) -> Validator:
    """CE 因果前缘 L1 vs 轴向比须落在离散核可复现带内。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        tol = CAUSAL_ANISO_RATIO_TOL * (1.12 if relaxed else 1.0)
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        r = parse_causal_aniso_ratio(text)
        if r is None or not math.isfinite(r):
            return False, "无法解析各向异性比（脚本改版？）"
        dev = abs(r - CAUSAL_ANISO_RATIO_GOLD)
        if dev > tol:
            return (
                False,
                "median(R_L1/R_plus+)=%.4f 偏离 GOLD %.4f 超过 %.3f"
                % (r, CAUSAL_ANISO_RATIO_GOLD, tol),
            )
        return True, "%s；ratio=%.4f≈%.4f" % (msg_s, r, CAUSAL_ANISO_RATIO_GOLD)

    return _v


def validate_relativity_formula_layer(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        vp = parse_relativity_v_prime(text)
        if vp is None:
            return False, "无法解析洛伦兹逆变 v'（输出改版？）"
        if abs(vp - 1.0) > 1e-6:
            return False, "v'=%.9f c 应≈1（公式层数字异常）" % vp
        if "[OK] formula_layer v_prime_vs_c" not in text:
            return False, "缺少 [OK] formula_layer v_prime_vs_c"
        return True, "%s；v'=%.9fc" % (msg_s, vp)

    return _v


def validate_critique_doc_png(png: str, ok_line: str) -> Validator:
    """叙事类质疑：须生成非空 PNG，且 stdout 含固定 [OK] 行。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        if ok_line not in text:
            return False, "缺少标记行: %s" % ok_line
        return True, "%s；%s" % (msg_s, ok_line)

    return _v


def validate_critique_04_sr_boundary(png: str) -> Validator:
    """质疑04：格点因果前缘 ~1 格/步 + 公式层 v'≈c；PNG 非空。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        if "[OK] critique_04_sr_not_derived" not in text:
            return False, "缺少 critique_04 标记"
        vg = parse_critique04_v_grid(text)
        vp = parse_critique04_v_prime(text)
        if vg is None or vp is None:
            return False, "无法解析格点 v_grid 或公式层 v'（输出改版？）"
        v_lo, v_hi = (0.90, 1.10) if relaxed else (0.96, 1.04)
        if not (v_lo <= vg <= v_hi):
            return False, "格点 dx/dt 中位数=%.4f 超出 [%.2f,%.2f]" % (vg, v_lo, v_hi)
        vp_lim = 2e-5 if relaxed else 6e-7
        if abs(vp - 1.0) > vp_lim:
            return False, "公式层 v'=%.9f c 应≈1（|Δ|≤%.1e）" % (vp, vp_lim)
        return True, "%s；v_grid=%.4f, v'=%.9fc" % (msg_s, vg, vp)

    return _v


def validate_critique_05_with_rv(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        lo_r = 0.988 if relaxed else 0.998
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        if "[OK] critique_05_decay_nonuniqueness" not in text:
            return False, "缺少 critique_05 标记"
        rv = parse_decay_nonuniqueness_rv(text)
        if rv is None or not math.isfinite(rv):
            return False, "无法解析 r_V_ce_vs_uniform 或非有限"
        if rv < lo_r:
            return (
                False,
                "r_V=%.4f < %.4f；V 轨迹与均匀损耗应高度同向（难区分通道）"
                % (rv, lo_r),
            )
        return True, "%s；r_V=%.4f（≥%.3f）" % (msg_s, rv, lo_r)

    return _v


def validate_critique_06_energy(png: str) -> Validator:
    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        if "[OK] critique_06_energy_growth" not in text:
            return False, "缺少 critique_06 标记"
        r = parse_energy_ratio_RE(text)
        if r is None:
            return False, "无法解析 R_E"
        if not math.isfinite(r):
            return False, "R_E 非有限"
        med = parse_critique06_median_Eratio(text)
        if med is None or not math.isfinite(med):
            return False, "无法解析步间中位比"
        r_floor = 1e35 if relaxed else 1e115
        if r < r_floor:
            return (
                False,
                "R_E=%.4g 应 ≥1e%.0f量级（非守恒增长）；低于门禁可能是核/步数变更"
                % (r, math.log10(r_floor)),
            )
        med_min = 1.006 if relaxed else 1.014
        if med <= med_min:
            return (
                False,
                "步间中位比=%.4f 应 > %.3f（总量增长须清晰）" % (med, med_min),
            )
        return True, "%s；R_E=%.3g，median(Et+1/Et)=%.4f" % (msg_s, r, med)

    return _v


def validate_critique_07_fringe(png: str) -> Validator:
    """可复现斜率相对 GOLD 回归；不声称已对齐远场 −1。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        tol = CRITIQUE07_FITTED_TOL * (1.35 if relaxed else 1.0)
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        if "[OK] critique_07_fringe_theory_gap" not in text:
            return False, "缺少 critique_07 标记"
        ft = parse_fitted_log_slope_critique(text)
        if ft is None or not math.isfinite(ft):
            return False, "无法解析 fitted_log_slope"
        dev_g = abs(ft - CRITIQUE07_FITTED_LOG_SLOPE_GOLD)
        if dev_g > tol:
            return (
                False,
                "fitted_log_slope=%.4f 偏离本仓库 GOLD %.4f 超过 %.3f；"
                "若有意改核或参数，请更新 CRITIQUE07_* 常量"
                % (ft, CRITIQUE07_FITTED_LOG_SLOPE_GOLD, tol),
            )
        return (
            True,
            "%s；slope=%.4f≈GOLD(%.4f±%.3f)；|与远场-1|=%.3f"
            % (
                msg_s,
                ft,
                CRITIQUE07_FITTED_LOG_SLOPE_GOLD,
                tol,
                abs(ft - (-1.0)),
            ),
        )

    return _v


def validate_double_slit_mirror_parity(png: str) -> Validator:
    """对称破缺残差量级须与当前内核参数可复现（非要求 asym→0）。"""

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        ok_png, msg_png = check_png_exists(text, repo, png, relaxed)
        if not ok_png:
            return False, msg_png
        mb = CE_PNG_MIN_BYTES_RELAXED if relaxed else CE_PNG_MIN_BYTES_STRICT
        ms = CE_PNG_MIN_STD_RELAXED if relaxed else CE_PNG_MIN_STD_STRICT
        ok_s, msg_s = assert_png_substantive(repo, png, min_bytes=mb, min_std=ms)
        if not ok_s:
            return False, msg_s
        a = parse_mirror_asym(text)
        rm = parse_mirror_corrcoef(text)
        if a is None or rm is None:
            return False, "无法解析 asym 或 r_mirror（脚本改版？）"
        if relaxed:
            alo, ahi = MIRROR_ASYM_LO - 0.05, MIRROR_ASYM_HI + 0.05
            rlo, rhi = MIRROR_R_LO - 0.04, MIRROR_R_HI + 0.03
        else:
            alo, ahi = MIRROR_ASYM_LO, MIRROR_ASYM_HI
            rlo, rhi = MIRROR_R_LO, MIRROR_R_HI
        if not (alo <= a <= ahi):
            return False, "asym=%.4f 不在回归带 [%.2f,%.2f]" % (a, alo, ahi)
        if not (rlo <= rm <= rhi):
            return False, "r_mirror=%.4f 不在回归带 [%.2f,%.2f]" % (rm, rlo, rhi)
        return True, "%s；asym=%.4f, r_mirror=%.4f" % (msg_s, a, rm)

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


def validate_battle_plan_summary(json_relpath: str) -> Validator:
    """
    research 门禁：运行 run_battle_plan.py 后，要求 summary JSON 存在且 all_ok=true。
    """

    def _v(text: str, repo: Path, relaxed: bool) -> Tuple[bool, str]:
        p = repo / json_relpath
        if not p.is_file():
            return False, f"缺失 battle plan 汇总: {json_relpath}"
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            return False, f"无法解析 battle plan 汇总 JSON: {exc}"
        all_ok = bool(payload.get("all_ok", False))
        rows = payload.get("results", [])
        n = len(rows) if isinstance(rows, list) else 0
        if not all_ok:
            return False, f"battle plan all_ok=false（results={n}）"
        ok_png, msg_png = assert_png_substantive(
            repo, "battle_plan_dashboard.png", min_bytes=8000, min_std=0.01
        )
        if not ok_png:
            return False, f"battle plan summary OK but dashboard invalid: {msg_png}"
        return True, f"battle plan PASS（results={n}；{msg_png}）"

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
            "ce_00_double_slit_demo.png",
            make_ce_substantive_png("ce_00_double_slit_demo.png"),
        ),
        Job(
            "ce_01_visibility_vs_screen_distance.py",
            "ce",
            "CE-01 对比度-屏距",
            "interference_decay.png",
            make_ce_substantive_png("interference_decay.png"),
        ),
        Job(
            "ce_02_double_slit_screen_statistics.py",
            "ce",
            "CE-02 屏上统计",
            "ce_02_double_slit_screen_statistics.png",
            make_ce_substantive_png("ce_02_double_slit_screen_statistics.png"),
        ),
        Job(
            "ce_03_visibility_vs_side_coupling_S.py",
            "ce",
            "CE-03 V vs S",
            "V_vs_S.png",
            make_ce_substantive_png("V_vs_S.png"),
        ),
        Job(
            "ce_04_measurement_absorption_at_slit.py",
            "ce",
            "CE-04 缝口吸收",
            "measurement_effect.png",
            make_ce_substantive_png("measurement_effect.png"),
        ),
        Job(
            "ce_05_finite_absorber_detector.py",
            "ce",
            "CE-05 有限吸收体",
            "finite_absorber.png",
            make_ce_substantive_png("finite_absorber.png"),
        ),
        Job(
            "ce_06_delayed_choice_absorber.py",
            "ce",
            "CE-06 延迟选择",
            "delayed_choice.png",
            make_ce_substantive_png("delayed_choice.png"),
        ),
        Job(
            "ce_07_measurement_phase_diagram_scan.py",
            "ce",
            "CE-07 测量相图",
            "measurement_phase_diagram.png",
            make_ce_substantive_png("measurement_phase_diagram.png"),
        ),
        Job(
            "ce_08_entanglement_split_wavepackets.py",
            "ce",
            "CE-08 纠缠分包",
            "entanglement_simulation.png",
            make_ce_substantive_png("entanglement_simulation.png"),
        ),
        Job(
            "ce_09_entanglement_with_phase_field.py",
            "ce",
            "CE-09 相位场纠缠",
            "entanglement_with_phase.png",
            make_ce_substantive_png("entanglement_with_phase.png"),
        ),
        Job(
            "ce_10_entanglement_distance_scan.py",
            "ce",
            "CE-10 纠缠距离扫描",
            "ce_10_entanglement_scan.png",
            make_ce_substantive_png("ce_10_entanglement_scan.png"),
        ),
        Job(
            "verify_born_rule.py",
            "verify",
            "验证 波恩规则",
            "verify_born_rule.png",
            validate_verify_born_rule("verify_born_rule.png"),
        ),
        Job(
            "verify_uncertainty.py",
            "verify",
            "验证 不确定性(现象记录)",
            "verify_uncertainty.png",
            validate_verify_uncertainty_phenomenon("verify_uncertainty.png"),
        ),
        Job(
            "discover_visibility_decay.py",
            "verify",
            "发现 对比度衰减",
            "discover_visibility_decay.png",
            validate_discover_d("discover_visibility_decay.png"),
        ),
        Job(
            "discover_measurement_continuity.py",
            "verify",
            "发现 测量连续性",
            "discover_measurement_continuity.png",
            validate_discover_e("discover_measurement_continuity.png"),
        ),
        Job(
            "discover_coupling_constant.py",
            "verify",
            "发现 耦合常数",
            "discover_coupling_constant.png",
            validate_discover_f("discover_coupling_constant.png"),
        ),
        Job(
            "explore_lorentz_selfcheck.py",
            "explore",
            "探索 洛伦兹代数自检",
            "explore_lorentz_selfcheck.png",
            validate_lorentz_with_png("explore_lorentz_selfcheck.png"),
        ),
        Job(
            "explore_visibility_vs_uniform_loss.py",
            "explore",
            "探索 均匀损耗 vs V",
            "explore_visibility_loss_compare.png",
            validate_visibility_loss("explore_visibility_loss_compare.png"),
        ),
        Job(
            "explore_energy_budget.py",
            "explore",
            "探索 能量预算 sum(E)",
            "explore_energy_budget.png",
            validate_energy_budget("explore_energy_budget.png"),
        ),
        Job(
            "explore_causal_front.py",
            "explore",
            "探索 因果前缘 2D",
            "explore_causal_front.png",
            validate_causal_front("explore_causal_front.png"),
        ),
        Job(
            "explore_fringe_spacing_vs_slit.py",
            "explore",
            "探索 条纹间隔 vs 缝距",
            "explore_fringe_spacing.png",
            validate_fringe_spacing("explore_fringe_spacing.png"),
        ),
        Job(
            "explore_causal_cone_anisotropy.py",
            "explore",
            "质疑 因果锥各向异性",
            "explore_causal_cone_anisotropy.png",
            validate_causal_anisotropy_probe("explore_causal_cone_anisotropy.png"),
        ),
        Job(
            "explore_relativity_light_speed_invariant.py",
            "explore",
            "质疑 公式层光速不变自检",
            "explore_relativity_light_speed_invariant.png",
            validate_relativity_formula_layer("explore_relativity_light_speed_invariant.png"),
        ),
        Job(
            "explore_double_slit_mirror_parity.py",
            "explore",
            "质疑 双缝镜像宇称残差",
            "explore_double_slit_mirror_parity.png",
            validate_double_slit_mirror_parity("explore_double_slit_mirror_parity.png"),
        ),
        Job(
            "explore_critique_01_unification_scope.py",
            "critique",
            "质疑01 统一宣称须可审计",
            "explore_critique_01_unification_scope.png",
            validate_critique_doc_png(
                "explore_critique_01_unification_scope.png",
                "[OK] critique_01_unification_scope",
            ),
        ),
        Job(
            "explore_critique_02_bell_hypothesis_boundary.py",
            "critique",
            "质疑02 Bell/坍缩仅为假说边界",
            "explore_critique_02_bell_hypothesis.png",
            validate_critique_doc_png(
                "explore_critique_02_bell_hypothesis.png",
                "[OK] critique_02_bell_boundary",
            ),
        ),
        Job(
            "explore_critique_03_analogy_vs_mechanism.py",
            "critique",
            "质疑03 类比 vs 同一机制措辞",
            "explore_critique_03_analogy_vs_mechanism.png",
            validate_critique_doc_png(
                "explore_critique_03_analogy_vs_mechanism.png",
                "[OK] critique_03_analogy_language",
            ),
        ),
        Job(
            "explore_critique_04_sr_not_derived_from_lattice.py",
            "critique",
            "质疑04 SR 非从格点推导",
            "explore_critique_04_sr_not_derived.png",
            validate_critique_04_sr_boundary("explore_critique_04_sr_not_derived.png"),
        ),
        Job(
            "explore_critique_05_decay_nonuniqueness.py",
            "critique",
            "质疑05 干涉衰减非唯一",
            "explore_critique_05_decay_nonuniqueness.png",
            validate_critique_05_with_rv("explore_critique_05_decay_nonuniqueness.png"),
        ),
        Job(
            "explore_critique_06_energy_growth_explosion.py",
            "critique",
            "质疑06 能量增长非相对论守恒",
            "explore_critique_06_energy_growth.png",
            validate_critique_06_energy("explore_critique_06_energy_growth.png"),
        ),
        Job(
            "explore_critique_07_fringe_spacing_theory_gap.py",
            "critique",
            "质疑07 条纹斜率与远场-1偏差",
            "explore_critique_07_fringe_theory_gap.png",
            validate_critique_07_fringe("explore_critique_07_fringe_theory_gap.png"),
        ),
        Job(
            "verify_interference_decay.py",
            "extended",
            "验证 干涉衰减",
            "verify_interference_decay.png",
            make_ce_substantive_png("verify_interference_decay.png"),
        ),
        Job(
            "verify_delayed_choice.py",
            "extended",
            "验证 延迟选择",
            "verify_delayed_choice.png",
            make_ce_substantive_png("verify_delayed_choice.png"),
        ),
        Job(
            "verify_which_way.py",
            "extended",
            "验证 Which-way",
            "verify_which_way.png",
            make_ce_substantive_png("verify_which_way.png"),
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
        choices=("all", "ce", "verify", "explore", "critique", "extended", "research"),
        default="all",
        help="all=ce+verify+explore+critique；extended=额外 verify_*；research=战斗路线聚合",
    )
    parser.add_argument(
        "--relaxed",
        action="store_true",
        help="放宽 verify B 的 r；另放宽 critique05/06/07、因果锥比、镜像宇称回归带",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅列出将运行的任务",
    )
    parser.add_argument(
        "--no-artifacts",
        action="store_true",
        help="不写 test_artifacts/ 与 README 替换块",
    )
    parser.add_argument(
        "--no-readme-patch",
        action="store_true",
        help="仍写 JSON/figures，但不改 README.md（可配合 --no-artifacts 无效）",
    )
    parser.add_argument(
        "--with-battle-plan",
        action="store_true",
        help="在当前组之外追加 run_battle_plan.py 研究门禁（读取 battle_plan_summary.json）",
    )
    args = parser.parse_args(argv)

    all_jobs = build_jobs()
    groups: List[str]
    if args.group == "all":
        groups = ["ce", "verify", "explore", "critique"]
    else:
        groups = [args.group]

    jobs = [j for j in all_jobs if j.group in groups]
    if args.group == "research" or args.with_battle_plan:
        jobs.append(
            Job(
                "run_battle_plan.py",
                "research",
                "战斗路线聚合回归",
                "battle_plan_dashboard.png",
                validate_battle_plan_summary("test_artifacts/battle_plan_summary.json"),
            )
        )
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
    report_rows: List[dict] = []
    artifact_root = None
    figures_dir = None
    if not args.no_artifacts:
        artifact_root, figures_dir = sa.ensure_dirs(REPO_ROOT)

    failed = 0
    t0 = time.perf_counter()

    for i, job in enumerate(jobs, 1):
        _print_job_header(i, len(jobs), job)
        path = find_script(REPO_ROOT, job.script)
        if not path.is_file():
            print("[FAIL] 未找到脚本文件")
            print(f"  原因: 路径不存在 -> {path}")
            results.append((job, "FAIL", "missing_file", str(path)))
            failed += 1
            report_rows.append(
                dict(
                    dossier_fields_for_readme(job.script),
                    **{
                        "script": job.script,
                        "group": job.group,
                        "title": job.title,
                        "status": "FAIL",
                        "reason": "missing_file -> %s" % path,
                        "stdout_tail": "",
                        "archived_figure": None,
                    },
                )
            )
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
            report_rows.append(
                dict(
                    dossier_fields_for_readme(job.script),
                    **{
                        "script": job.script,
                        "group": job.group,
                        "title": job.title,
                        "status": "FAIL",
                        "reason": "exit_%d" % rc,
                        "stdout_tail": "\n".join(
                            ((out or "") + "\n" + (err or "")).strip().splitlines()[-20:]
                        ),
                        "archived_figure": None,
                    },
                )
            )
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

        stdout_tail = "\n".join((out or "").strip().splitlines()[-20:])
        archived = None
        if not args.no_artifacts and figures_dir is not None and job.expect_png:
            archived = sa.archive_job_figure(
                REPO_ROOT, figures_dir, job.group, job.script, job.expect_png
            )
        report_rows.append(
            dict(
                dossier_fields_for_readme(job.script),
                **{
                    "script": job.script,
                    "group": job.group,
                    "title": job.title,
                    "expect_png": job.expect_png,
                    "status": status,
                    "reason": reason,
                    "elapsed_s": round(elapsed, 3),
                    "stdout_tail": stdout_tail,
                    "archived_figure": archived,
                },
            )
        )

    total = time.perf_counter() - t0

    if not args.no_artifacts and artifact_root is not None:
        payload = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "suite_pass": failed == 0,
            "elapsed_s": round(total, 3),
            "groups_ran": groups,
            "relaxed": args.relaxed,
            "rows": report_rows,
        }
        sa.write_report_json(artifact_root / "suite_report.json", payload)
        md_block = sa.build_markdown(report_rows, failed == 0, total)
        (artifact_root / "README_TEST_REPORT.md").write_text(
            md_block, encoding="utf-8"
        )
        if not args.no_readme_patch:
            sa.patch_readme(REPO_ROOT / "README.md", md_block)
        print()
        print("已写入: test_artifacts/figures/, suite_report.json, README_TEST_REPORT.md", flush=True)
        if not args.no_readme_patch:
            print("已更新: README.md 中 SUITE_ARTIFACTS 区块", flush=True)

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
