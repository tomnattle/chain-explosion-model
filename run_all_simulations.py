"""
依次运行仓库内全部 ce_*.py 仿真脚本，用于重新生成 PNG 并做冒烟验证。

用法（在仓库根目录）:
    python run_all_simulations.py

说明:
    - 设置 MPLBACKEND=Agg，避免 plt.show() 弹窗或阻塞。
    - Windows 下通过 cmd 先执行 chcp 65001，降低子进程打印 emoji 时的 GBK 编码错误。
    - 设置 PYTHONIOENCODING=utf-8 供子进程 stdio 参考。
    - ce_02 仅打印统计、默认不写图，仍会执行以验证 Numba 传播是否正常。
"""
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
MPL_LAUNCHER = REPO_ROOT / "run_with_mpl_compat.py"

# 按编号顺序，保证与实验递进一致
SCRIPTS = [
    "ce_00_double_slit_demo.py",
    "ce_01_visibility_vs_screen_distance.py",
    "ce_02_double_slit_screen_statistics.py",
    "ce_03_visibility_vs_side_coupling_S.py",
    "ce_04_measurement_absorption_at_slit.py",
    "ce_05_finite_absorber_detector.py",
    "ce_06_delayed_choice_absorber.py",
    "ce_07_measurement_phase_diagram_scan.py",
    "ce_08_entanglement_split_wavepackets.py",
    "ce_09_entanglement_with_phase_field.py",
    "ce_10_entanglement_distance_scan_numba.py",
]

EXPECTED_PNG = [
    "interference_decay.png",
    "V_vs_S.png",
    "measurement_effect.png",
    "finite_absorber.png",
    "delayed_choice.png",
    "measurement_phase_diagram.png",
    "entanglement_simulation.png",
    "entanglement_with_phase.png",
    "entanglement_scan_numba.png",
]


def _run_one_script(path, repo_root, env):
    """在仓库根目录执行单个脚本；Windows 使用 UTF-8 控制台代码页。"""
    path_s = str(path)
    exe = str(sys.executable)
    launch_s = str(MPL_LAUNCHER)
    use_launcher = MPL_LAUNCHER.is_file()
    if platform.system() == "Windows":
        # chcp 65001：避免 ce_* 中 print(✅) 等在默认 GBK 控制台下报错
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
        return subprocess.run(
            cmdline,
            cwd=str(repo_root),
            env=env,
            shell=True,
        )
    argv = [exe, launch_s, path_s] if use_launcher else [exe, path_s]
    return subprocess.run(argv, cwd=str(repo_root), env=env)


def main():
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    failures = []
    t0 = time.perf_counter()

    print(f"仓库根目录: {REPO_ROOT}")
    print(f"解释器: {sys.executable}")
    print(f"共 {len(SCRIPTS)} 个脚本，顺序执行。\n")

    for name in SCRIPTS:
        path = REPO_ROOT / name
        print("=" * 70)
        print(f">>> {name}")
        print("=" * 70, flush=True)

        if not path.is_file():
            print(f"缺失文件，跳过: {path}")
            failures.append((name, "file missing"))
            continue

        t_script = time.perf_counter()
        proc = _run_one_script(path, REPO_ROOT, env)
        elapsed = time.perf_counter() - t_script

        if proc.returncode != 0:
            print(f"\n[失败] {name} 退出码 {proc.returncode}，用时 {elapsed:.1f}s\n")
            failures.append((name, f"exit {proc.returncode}"))
        else:
            print(f"\n[通过] {name} 用时 {elapsed:.1f}s\n")

    total = time.perf_counter() - t0

    print("=" * 70)
    print("期望由脚本写入的 PNG（ce_02 不产生图）:")
    for png in EXPECTED_PNG:
        p = REPO_ROOT / png
        ok = p.is_file()
        print(f"  {'[有]' if ok else '[无]'} {png}")

    print("=" * 70)
    if failures:
        print(f"完成: {len(failures)}/{len(SCRIPTS)} 个失败，总用时 {total:.1f}s")
        for name, reason in failures:
            print(f"  - {name}: {reason}")
        return 1

    print(f"全部 {len(SCRIPTS)} 个脚本成功，总用时 {total:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
