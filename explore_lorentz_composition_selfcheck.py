"""
explore_lorentz_composition_selfcheck.py
----------------------------------------
质疑点 relativity_final.py：洛伦兹速度合成是外加公式还是由格点「推出」？
本脚本只做代数自洽性数值检验，与格点解耦——便于区分「演示」与「推导」。

检验:
  1) 爱因斯坦速度加法交换/接近结合（数值误差内）
  2) v=c 时在各惯性系公式下应保持 c（选取 c=1 单位制）

运行: python explore_lorentz_composition_selfcheck.py
失败时 exit 1，便于 CI / run_unified_suite 捕获。
"""
import sys

import numpy as np

C = 1.0


def add(u: float, v: float, c: float = C) -> float:
    """同向一维 Einstein 合成 u⊕v。"""
    return (u + v) / (1.0 + u * v / (c * c))


def inv_boost_velocity(v: float, V: float, c: float = C) -> float:
    """逆变换常用形式 v' = (v - V) / (1 - vV/c^2)。"""
    return (v - V) / (1.0 - v * V / (c * c))


def main():
    print("=" * 60)
    print("洛伦兹速度合成 — 代数自洽（与 relativity_final 演示分离）")
    # 交换
    a, b = 0.3, 0.4
    d = abs(add(a, b) - add(b, a))
    print(f"交换误差 |a⊕b - b⊕a| = {d:.3e}  (期望 0)")

    # 小结合链
    x = add(add(0.2, 0.2), 0.2)
    y = add(0.2, add(0.2, 0.2))
    print(f"结合链误差 ≈ {abs(x-y):.3e}")

    # c 不变（合成）
    vc = 0.99 * C
    w = add(vc, 0.2 * C)
    print(f"0.99c ⊕ 0.2c = {w:.6f} c  (< c)")

    # 逆变换：实验室见 v_lab=c，运动系 V=0.5，应得 v'=c
    vp = inv_boost_velocity(C, 0.5 * C)
    print(f"(v=c, V=0.5c) -> v' = {vp:.6f} c  (期望 1.0)")

    print("\n结论模板（可写进论文）:")
    print("  本仓库 relativity_final 使用 np.roll 演示局域最大位移 + 洛伦兹公式验算；")
    print("  该文件不声称从 shift 规则单独推出闵氏几何，只检验公式数值自洽。")
    print("=" * 60)

    ok = (
        d < 1e-9
        and abs(x - y) < 1e-9
        and abs(vp - C) < 1e-5
        and w < C
    )
    if ok:
        print("VERDICT: PASS (lorentz_algebra)")
    else:
        print(
            "VERDICT: FAIL (lorentz_algebra) — "
            f"commute={d:.3e}, assoc={abs(x-y):.3e}, v_prime={vp:.6f}, w_over_c={w/C:.6f}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
