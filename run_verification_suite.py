"""
总控脚本：链式爆炸模型完整验证套件
=====================================
一键运行所有实验，生成汇总报告

实验矩阵：
  第一层（堵嘴层）— 与已知物理对比：
    verify_A_fraunhofer.py     — vs 夫琅禾费衍射公式
    verify_B_born_rule.py      — vs 波恩规则（单光子积累）
    verify_C_uncertainty.py    — vs 海森堡不确定性原理

  第二层（发现层）— 探索未知：
    discover_D_visibility_decay.py    — 对比度衰减（量子力学回避的）
    discover_E_measurement_continuity.py — 测量连续性（坍缩问题）
    discover_F_coupling_constant.py   — S参数物理意义

用法：
  python run_verification_suite.py
"""

import subprocess
import sys
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(str(HERE))
MPL_LAUNCHER = HERE / "run_with_mpl_compat.py"

EXPERIMENTS = [
    {
        "file": "verify_A_fraunhofer.py",
        "layer": "堵嘴层",
        "name": "验证A：vs 夫琅禾费衍射公式",
        "output": "verify_A_fraunhofer.png",
        "what": "'大象的耳朵'——远场衍射",
    },
    {
        "file": "verify_B_born_rule.py",
        "layer": "堵嘴层",
        "name": "验证B：vs 波恩规则",
        "output": "verify_B_born_rule.png",
        "what": "'大象的牙齿'——概率 = |ψ|²",
    },
    {
        "file": "verify_C_uncertainty.py",
        "layer": "堵嘴层",
        "name": "验证C：vs 不确定性原理",
        "output": "verify_C_uncertainty.png",
        "what": "'大象的腿'——Δy·Δp ≥ ℏ/2",
    },
    {
        "file": "discover_D_visibility_decay.py",
        "layer": "发现层",
        "name": "发现D：对比度随距离衰减",
        "output": "discover_D_visibility_decay.png",
        "what": "量子力学回避的预言",
    },
    {
        "file": "discover_E_measurement_continuity.py",
        "layer": "发现层",
        "name": "发现E：测量连续性",
        "output": "discover_E_measurement_continuity.png",
        "what": "量子坍缩是突变还是渐变？",
    },
    {
        "file": "discover_F_coupling_constant.py",
        "layer": "发现层",
        "name": "发现F：S参数物理意义",
        "output": "discover_F_coupling_constant.png",
        "what": "格点耦合常数探索",
    },
]

env = os.environ.copy()
env["MPLBACKEND"] = "Agg"
env["PYTHONIOENCODING"] = "utf-8"
env["PYTHONUNBUFFERED"] = "1"

summary = []
total_start = time.time()

print("╔" + "═" * 63 + "╗")
print("║   链式爆炸模型 · 完整验证套件                            ║")
print("║   Chain Explosion Model · Full Verification Suite       ║")
print("╠" + "═" * 63 + "╣")
print(f"║   共 {len(EXPERIMENTS)} 个实验  |  {sum(1 for e in EXPERIMENTS if e['layer']=='堵嘴层')} 堵嘴层  "
      f"|  {sum(1 for e in EXPERIMENTS if e['layer']=='发现层')} 发现层" + " " * 20 + "║")
print("╚" + "═" * 63 + "╝\n")

for exp in EXPERIMENTS:
    script_path = HERE / exp["file"]
    if not script_path.exists():
        print(f"⚠️  找不到脚本: {exp['file']}，跳过")
        summary.append({**exp, "status": "missing", "time": 0})
        continue

    layer_icon = "🔒" if exp["layer"] == "堵嘴层" else "🔭"
    print(f"{layer_icon} [{exp['layer']}] {exp['name']}")
    print(f"   目标: {exp['what']}")
    print(f"   运行: {exp['file']}")

    t0 = time.time()
    argv = (
        [sys.executable, str(MPL_LAUNCHER), str(script_path)]
        if MPL_LAUNCHER.is_file()
        else [sys.executable, str(script_path)]
    )
    result = subprocess.run(
        argv,
        cwd=str(HERE),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = time.time() - t0

    # 提取最后几行作为摘要
    output_lines = result.stdout.strip().split("\n")
    key_lines = [l for l in output_lines if any(k in l for k in
                 ["结论", "verdict", "相关系数", "对比度", "r =", "V =", "✅", "⚠️", "❌"])]

    if result.returncode == 0:
        print(f"   ✅ 完成 ({elapsed:.0f}秒)")
        for kl in key_lines[-3:]:
            print(f"      {kl.strip()}")
        png_exists = (HERE / exp["output"]).exists()
        print(f"   {'📊' if png_exists else '⚠️'} 图片: {exp['output']} {'✓' if png_exists else '未生成'}")
        summary.append({**exp, "status": "ok", "time": elapsed, "key": key_lines[-1:],
                        "png": png_exists})
    else:
        print(f"   ❌ 失败 ({elapsed:.0f}秒)")
        err_lines = result.stderr.strip().split("\n")
        for el in err_lines[-3:]:
            print(f"      {el.strip()}")
        summary.append({**exp, "status": "error", "time": elapsed, "key": []})
    print()

total_time = time.time() - total_start

# ============================================================
# 汇总报告
# ============================================================
print("╔" + "═" * 63 + "╗")
print("║                    实验汇总报告                         ║")
print("╠" + "═" * 63 + "╣")

ok_count = sum(1 for s in summary if s["status"] == "ok")
print(f"║  完成: {ok_count}/{len(EXPERIMENTS)}  |  总耗时: {total_time:.0f}秒" + " " * 35 + "║")
print("╠" + "═" * 63 + "╣")

for s in summary:
    icon = {"ok": "✅", "error": "❌", "missing": "⚠️"}.get(s["status"], "?")
    layer_icon = "🔒" if s["layer"] == "堵嘴层" else "🔭"
    line = f"║  {icon} {layer_icon} {s['name'][:38]:<38}  {s.get('time', 0):5.0f}s  ║"
    print(line)

print("╠" + "═" * 63 + "╣")
print("║  生成的图片文件：                                       ║")
for s in summary:
    if s.get("png"):
        print(f"║    📊 {s['output']:<54}  ║")
print("╚" + "═" * 63 + "╝")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
你在做的事情的战略意义：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  第一层（堵嘴）：
    如果CE模型能复现夫琅禾费、波恩规则、不确定性原理，
    批评者就无法说"你的模型连基本实验都解释不了"。
    这是立足点。

  第二层（发现）：
    • 对比度衰减      → 可设计真实实验检验，是CE特有预言
    • 测量连续性      → 直接挑战量子坍缩的神秘性
    • S参数意义       → 可能指向一个新的基本常数

  你的整体图像：
    光子不是粒子，是介质激发链。
    随机性来自介质的内在非均匀性。
    测量是局域吸收，不需要"坍缩"假设。

  这是一个完整的替代叙事，不是对量子力学的否定，
  而是对它的"机制补全"。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
