"""
介质最小特征尺寸（启发式估算）

输入常数（与现有模拟一致，无量纲或约定单位）：
  mu = 1.5495   折射率 n 的取值
  rho = 2.35    相对密度（仅参与“结构冗余”尺度，见下文）
  eta = 0.08    损耗强度（无量纲，表示每经过一个“光学厚度”λ_med 的等效衰减比例）

说明：
  这不是严格 FDTD 推导，而是用三个数给出一个**可复核、可改假设**的最小尺度上界/下界组合。

重要区分（避免范畴错误）：
  - **工程光学模式**（本文件 `medium_scales`）：回答“按波长/损耗隐喻，块介质要多大才像样”，
    结果通常是微米–纳米级，和**光子器件**同量级。
  - **宇宙基底介质模式**（本体论）：若你认为“宇宙=离散介质”，其“元胞尺度”在现有物理学里
    **不能**由本项目的 mu,rho,eta 直接推出；需要额外公理把三者映射到基本长度（例如与 l_P、
    晶格常数、康普顿波长等挂钩）。否则会出现“明显太大/不对”的直觉——因为两种问题不是同一个问题。

主要量：
  1) λ_med = λ0 / mu           介质中波长尺度
  2) L_loss ≈ λ_med / eta      等效衰减特征长度（eta 越小，场可走越远）
  3) L_struct = rho * λ_med    密度越大，假设需要更多“材料周期”堆叠（启发式）

综合最小尺寸（保守取大）：
  L_min = max(λ_med, L_loss, L_struct)

依赖：仅标准库；不调用 sqrt / 第三方。

参考：普朗克长度取文献常用值（仅作数量级对比，不在此从 G,c,ℏ 重算）。
"""

from __future__ import annotations


# 三个常数（与项目其余脚本一致）
MU = 1.5495
RHO = 2.35
ETA = 0.08


def medium_scales(lambda0_m: float) -> dict[str, float]:
    """
    lambda0_m: 真空波长（米），例如 550e-9 表示绿光。
    返回各特征长度（米）。

    内部用「纳米整数 + 有理数 mu=15495/10000」避免浮点误差。
    """
    # 真空波长（nm，整数）
    lam0_nm = int(round(lambda0_m * 1e9))
    mu_num = 15495
    mu_den = 10000
    eta_num = 8
    eta_den = 100
    rho_num = 235
    rho_den = 100

    # λ_med(nm) = λ0 / mu
    lam_med_nm = (lam0_nm * mu_den) // mu_num

    # L_loss(nm) ≈ λ_med / eta
    l_loss_nm = (lam_med_nm * eta_den) // eta_num

    # L_struct(nm) = rho * λ_med
    l_struct_nm = (lam_med_nm * rho_num) // rho_den

    l_min_nm = max(lam_med_nm, l_loss_nm, l_struct_nm)

    def nm_to_m(nm: int) -> float:
        return nm * 1e-9

    return {
        "lambda_vacuum_m": lambda0_m,
        "lambda_medium_m": nm_to_m(lam_med_nm),
        "L_loss_m": nm_to_m(l_loss_nm),
        "L_struct_m": nm_to_m(l_struct_nm),
        "L_min_m": nm_to_m(l_min_nm),
    }


# 普朗克长度（米），数量级对比用；来源：CODATA 常用值约 1.616e-35 m
PLANCK_LENGTH_M = 1.616255e-35
# 典型固体原子间距量级（米），连续介质近似失效的粗下界之一
TYPICAL_ATOMIC_SPACING_M = 3e-10


def feasibility(l_min_m: float) -> str:
    """
    粗粒度可行性：与常见硅光子芯片尺度（毫米级）比较。
    """
    chip_m = 1e-3
    if l_min_m < chip_m:
        return "在毫米级芯片尺度内，该启发式最小特征长度远小于典型封装，**从尺度上可放置**（仍需工艺与耦合设计验证）。"
    return "启发式最小特征长度接近或超过毫米级，**单芯片集成可能偏紧**，需缩小工作波长或降低等效损耗假设。"


def print_cosmic_substrate_note(l_engineering_m: float) -> None:
    print()
    print("=== 若论「宇宙是介质」：与「最小单位」的关系 ===")
    print(
        "上面 L_min 是**工程光学隐喻**下的尺度，不是「时空基底元胞」尺度。"
        "若要把 μ,ρ,η 解释为宇宙介质，必须**另写映射公理**；仅凭当前三常数无法唯一确定普朗克尺度。"
    )
    print(f"数量级对照：工程 L_min ≈ {l_engineering_m:.3e} m")
    print(f"  典型原子间距 ~ {TYPICAL_ATOMIC_SPACING_M:.1e} m（固体离散性粗尺度）")
    print(f"  普朗克长度 l_P ~ {PLANCK_LENGTH_M:.3e} m（量子引力讨论用，非实验已证实格距）")
    if l_engineering_m > 0 and PLANCK_LENGTH_M > 0:
        ratio = l_engineering_m / PLANCK_LENGTH_M
        print(f"  比值 L_min / l_P ~ {ratio:.3e}（量级上相差极远，故二者不是同一概念）")


def main():
    # 默认：可见光中心约 550 nm
    lambda0_nm = 550.0
    lambda0_m = lambda0_nm * 1e-9

    s = medium_scales(lambda0_m)

    print("=== 介质最小特征尺寸（启发式）===")
    print(f"常数: mu={MU}, rho={RHO}, eta={ETA}")
    print(f"真空波长 λ0 = {lambda0_nm} nm")
    print(f"介质中波长尺度 λ_med ≈ {s['lambda_medium_m']*1e9:.3f} nm")
    print(f"损耗特征长度 L_loss ≈ {s['L_loss_m']*1e6:.3f} μm")
    print(f"密度冗余长度 L_struct = rho·λ_med ≈ {s['L_struct_m']*1e9:.3f} nm")
    print(f"综合保守最小尺度 L_min = max(...) ≈ {s['L_min_m']*1e6:.3f} μm")
    print()
    print("可行性（粗判）:", feasibility(s["L_min_m"]))
    print()
    print("能否做到：")
    print("- **数学/脚本层面**：能做到，本文件即给出可改假设下的数值。")
    print("- **工程/工艺层面**：需把 η 与真实吸收系数、Q 值、波导损耗关联后再判。")
    print_cosmic_substrate_note(s["L_min_m"])


if __name__ == "__main__":
    main()
