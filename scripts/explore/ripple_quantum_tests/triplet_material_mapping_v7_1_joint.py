"""
v7.1 joint structured mapping — GPU-accelerated rewrite
使用 PyTorch 向量化，彻底消灭三重嵌套 Python 循环。

加速原理：
- 将 mu/rho/eta 网格预先展开为张量 (mu_steps * rho_steps * eta_steps, 3)
- 每个数据点的目标函数对全部候选点同时计算（纯张量运算）
- 支持 AMD GPU (ROCm) / NVIDIA GPU (CUDA) / CPU 自动选择
- 批量处理多个数据点以摊薄 GPU 调度开销

依赖: pip install torch  (ROCm 版本见: https://pytorch.org/get-started/locally/)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import torch


def apply_profile(cfg: "Cfg", profile: str) -> "Cfg":
    """
    预设配置：
    - robust: 优先极端样本与单调性门禁
    - si_priority: 优先 core4 中 si 的 n_mae
    """
    if profile == "robust":
        cfg.fit_iters = 12
        cfg.w_eta_floor = 0.5
        cfg.w_eta_target = 0.2
        cfg.w_eta_target_lowk_boost = 1.0
        cfg.w_eta_abs_very_lowk = 0.0
        cfg.auto_select_tilt = True
        cfg.force_bias_only_materials = ()
        cfg.force_tilt_materials = ("metalx", "gaas", "highnlowk", "midkcurve")
        cfg.eta_max_overrides = {"gaas": 2.5, "metalx": 2.8, "highnlowk": 3.9}
        return cfg
    if profile == "si_priority":
        cfg.fit_iters = 12
        cfg.w_eta_floor = 0.5
        cfg.w_eta_target = 0.2
        cfg.w_eta_target_lowk_boost = 1.0
        cfg.w_eta_abs_very_lowk = 0.0
        # 关闭强制 tilt，优先让 si 保持原始结构拟合
        cfg.auto_select_tilt = False
        cfg.force_bias_only_materials = ()
        cfg.force_tilt_materials = ()
        cfg.eta_max_overrides = {"gaas": 2.5, "metalx": 2.8, "highnlowk": 3.9}
        return cfg
    raise SystemExit(f"unknown --profile: {profile}")


# ─── 配置 ─────────────────────────────────────────────────────────────────────

@dataclass
class Cfg:
    eta_ref: float = 0.08
    distance_unit_to_m: float = 1e-6
    eta_min: float = 0.0
    eta_max: float = 1.0
    eta_max_cap: float = 2.0
    eta_steps: int = 61
    mu_min: float = 0.2
    mu_max: float = 40.0
    mu_steps: int = 121
    rho_min: float = 0.2
    rho_max: float = 30.0
    rho_steps: int = 121
    # model coefficients
    a0: float = 0.95
    a1: float = 0.45
    a2: float = 0.02
    a3: float = 0.16
    a4: float = 0.02
    a5: float = 0.18
    a6: float = 0.22
    # losses
    w_n: float = 1.0
    w_eta_target: float = 0.2
    # 对低 k 材料增强 eta_target 约束（1.0 表示关闭增强）
    w_eta_target_lowk_boost: float = 1.0
    eta_target_lowk_threshold: float = 1e-3
    # 超低 k 下对 eta 绝对值加软惩罚（0.0 表示关闭）
    w_eta_abs_very_lowk: float = 0.0
    eta_abs_very_lowk_threshold: float = 5e-4
    w_smooth_mu: float = 0.2
    w_smooth_rho: float = 0.2
    w_smooth_eta: float = 1.0
    w_eta_floor: float = 0.5
    # 外层迭代次数（每轮一次正向扫描 + bias 更新；见 --bidirectional）
    fit_iters: int = 12
    # 每轮是否在正扫后再做一次反扫（对 si/sio2/kdemo 往往有益，强色散 GaAs 类可能略损 n_mae）
    bidirectional: bool = False
    w_eta_lowk_shape: float = 1.0
    lowk_k_threshold: float = 1e-5
    lowk_eta_base: float = 0.003
    lowk_eta_span: float = 0.045
    eta_max_overrides: dict[str, float] | None = None
    # 自动在 bias-only 与 bias+tilt*x 间择优（按材料内 n_mae）
    auto_select_tilt: bool = True
    # 对这些材料强制 bias-only（优先级最高，用于保护已表现稳定的材料）
    force_bias_only_materials: tuple[str, ...] = ()
    # 对这些材料始终启用 affine tilt（优先于 auto_select_tilt）
    force_tilt_materials: tuple[str, ...] = ("metalx", "gaas", "highnlowk", "midkcurve")

    # ── GPU 专属 ──────────────────────────────────────────────────────────────
    # 同时处理多少个数据点（增大可提升 GPU 利用率，但会占更多显存）
    batch_size: int = 64
    # float32 精度（GPU 默认）；改为 torch.float64 可提升精度但速度减半
    dtype: torch.dtype = torch.float32


# ─── 工具函数（与原版一致）────────────────────────────────────────────────────

def load_rows(path: Path, material: str) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({
                "material": material,
                "wavelength_nm": float(row["wavelength_nm"]),
                "n_ref": float(row["n_ref"]),
                "k_ref": float(row.get("k_ref", "0") or 0.0),
            })
    rows.sort(key=lambda x: x["wavelength_nm"])
    if not rows:
        return rows
    w0 = rows[len(rows) // 2]["wavelength_nm"]
    for row in rows:
        row["x"] = (float(row["wavelength_nm"]) - w0) / max(float(w0), 1e-9)
    return rows


def eta_target(k_ref: float, wavelength_nm: float, cfg: Cfg) -> float:
    wl_m = max(wavelength_nm * 1e-9, 1e-18)
    alpha_i = 4.0 * math.pi * max(k_ref, 0.0) / wl_m
    return 0.5 * alpha_i * cfg.distance_unit_to_m


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    q_clip = min(max(q, 0.0), 1.0)
    idx = q_clip * (len(ordered) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return ordered[lo]
    w = idx - lo
    return ordered[lo] * (1.0 - w) + ordered[hi] * w


def eta_max_for_material(rows: list[dict], cfg: Cfg) -> float:
    material = str(rows[0]["material"]).strip().lower() if rows else ""
    if cfg.eta_max_overrides and material in cfg.eta_max_overrides:
        ov = float(cfg.eta_max_overrides[material])
        # 允许单材料 override 高于全局 eta_max_cap（用于强吸收极端样例，避免 eta_target 被全局上限夹扁）
        upper = max(cfg.eta_max_cap, ov)
        return min(max(ov, cfg.eta_min), upper)
    targets = [eta_target(float(r["k_ref"]), float(r["wavelength_nm"]), cfg) for r in rows]
    p90 = percentile(targets, 0.90)
    auto_cap = max(cfg.eta_max, p90 * 1.20)
    return min(max(auto_cap, cfg.eta_min), cfg.eta_max_cap)


def eta_floor_weight_by_k(k_ref: float, cfg: Cfg) -> float:
    k = max(k_ref, 0.0)
    if k <= 1e-5:   scale = 0.15
    elif k <= 1e-4: scale = 0.35
    elif k <= 1e-3: scale = 0.70
    elif k <= 1e-2: scale = 1.10
    elif k <= 5e-2: scale = 1.70
    else:            scale = 2.40
    return cfg.w_eta_floor * scale


def lowk_shape_target(k_ref: float, k_min: float, k_max: float, cfg: Cfg) -> float:
    if k_max <= k_min + 1e-18:
        return cfg.lowk_eta_base
    t = (max(k_ref, k_min) - k_min) / (k_max - k_min)
    return cfg.lowk_eta_base + cfg.lowk_eta_span * min(max(t, 0.0), 1.0)


# ─── GPU 核心：预构建网格 ──────────────────────────────────────────────────────

def build_grid(cfg: Cfg, eta_max_material: float, device: torch.device) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    返回三个形状均为 (G,) 的 1-D 张量，G = mu_steps * rho_steps * eta_steps。
    meshgrid 展开后每行对应一个候选 (mu, rho, eta) 组合。
    """
    mu_1d  = torch.linspace(cfg.mu_min,  cfg.mu_max,  cfg.mu_steps,  dtype=cfg.dtype, device=device)
    rho_1d = torch.linspace(cfg.rho_min, cfg.rho_max, cfg.rho_steps, dtype=cfg.dtype, device=device)
    eta_1d = torch.linspace(cfg.eta_min, eta_max_material, cfg.eta_steps, dtype=cfg.dtype, device=device)

    mu_g, rho_g, eta_g = torch.meshgrid(mu_1d, rho_1d, eta_1d, indexing="ij")
    return mu_g.reshape(-1), rho_g.reshape(-1), eta_g.reshape(-1)


def n_model_vec(mu: torch.Tensor, rho: torch.Tensor, eta: torch.Tensor,
                x: torch.Tensor, k: torch.Tensor, bias: float, tilt: float, cfg: Cfg) -> torch.Tensor:
    """
    向量化版 n_model。
    mu/rho/eta : (G,)   网格候选点
    x/k        : (B,)   数据点（通过广播与网格交叉）
    返回        : (B, G)
    """
    # 广播: (B,1) op (1,G) -> (B,G)
    mu_  = mu.unsqueeze(0)        # (1, G)
    rho_ = rho.unsqueeze(0)
    eta_ = eta.unsqueeze(0)
    x_   = x.unsqueeze(1)         # (B, 1)
    k_   = k.unsqueeze(1)

    base     = cfg.a0 + cfg.a1 * torch.log1p(mu_.clamp(min=1e-12))
    curve    = cfg.a2 * rho_ * (x_ ** 2)
    coupling = cfg.a3 * torch.sqrt((mu_ * rho_).clamp(min=1e-12))
    eta_term = cfg.a4 * (eta_ - cfg.eta_ref)
    k_term   = cfg.a5 * torch.log1p(k_.clamp(min=0.0) * 300.0) * eta_
    k_pow    = cfg.a6 * (k_.clamp(min=0.0) ** 0.35) * (0.3 + eta_)
    tilt_term = tilt * x_
    return base + curve + coupling + eta_term + k_term + k_pow + tilt_term + bias


def objective_batch(
    mu_g: torch.Tensor, rho_g: torch.Tensor, eta_g: torch.Tensor,
    x_b: torch.Tensor, k_b: torch.Tensor,
    n_ref_b: torch.Tensor, eta_target_b: torch.Tensor,
    prev_mu: torch.Tensor | None, prev_rho: torch.Tensor | None, prev_eta: torch.Tensor | None,
    next_mu: torch.Tensor | None, next_rho: torch.Tensor | None, next_eta: torch.Tensor | None,
    is_lowk: bool, lowk_min: float, lowk_max: float,
    cfg: Cfg, bias: float, tilt: float,
) -> torch.Tensor:
    """
    返回 (B, G) 目标函数值张量。
    """
    n_hat = n_model_vec(mu_g, rho_g, eta_g, x_b, k_b, bias, tilt, cfg)  # (B, G)

    obj = cfg.w_n * (n_hat - n_ref_b.unsqueeze(1)) ** 2
    # 低 k 下增强 eta_target 约束，防止 eta 在弱吸收数据上退化为无信息常数
    lowk_mask = (k_b <= cfg.eta_target_lowk_threshold).to(cfg.dtype)
    w_eta_row = cfg.w_eta_target * (1.0 + lowk_mask * (cfg.w_eta_target_lowk_boost - 1.0))
    obj = obj + w_eta_row.unsqueeze(1) * (eta_g.unsqueeze(0) - eta_target_b.unsqueeze(1)) ** 2

    # low-k shape
    if is_lowk:
        k_np = k_b.cpu().float().numpy()
        eta_shapes = torch.tensor(
            [lowk_shape_target(float(k), lowk_min, lowk_max, cfg) for k in k_np],
            dtype=cfg.dtype, device=mu_g.device
        )  # (B,)
        obj = obj + cfg.w_eta_lowk_shape * (eta_g.unsqueeze(0) - eta_shapes.unsqueeze(1)) ** 2

    # eta floor penalty（逐行，因为每行 k 不同）
    k_np = k_b.cpu().float().numpy()
    for bi, k_val in enumerate(k_np):
        k_val = float(k_val)
        if k_val > 0:
            eta_floor = max(0.02, min(0.25, 0.05 + 2.5 * k_val))
            w_floor   = eta_floor_weight_by_k(k_val, cfg)
            below     = (eta_g < eta_floor).float()
            obj[bi]   = obj[bi] + w_floor * below * (eta_floor - eta_g) ** 2
            if k_val <= cfg.eta_abs_very_lowk_threshold:
                obj[bi] = obj[bi] + cfg.w_eta_abs_very_lowk * (eta_g ** 2)

    # 平滑项（利用已选出的前/后邻居，形状 (B,)）
    for prev_val, w, grid in [
        (prev_mu,  cfg.w_smooth_mu,  mu_g),
        (prev_rho, cfg.w_smooth_rho, rho_g),
        (prev_eta, cfg.w_smooth_eta, eta_g),
    ]:
        if prev_val is not None:
            obj = obj + w * (grid.unsqueeze(0) - prev_val.unsqueeze(1)) ** 2
    for nxt_val, w, grid in [
        (next_mu,  cfg.w_smooth_mu,  mu_g),
        (next_rho, cfg.w_smooth_rho, rho_g),
        (next_eta, cfg.w_smooth_eta, eta_g),
    ]:
        if nxt_val is not None:
            obj = obj + w * (grid.unsqueeze(0) - nxt_val.unsqueeze(1)) ** 2

    return obj  # (B, G)


def _sweep_update_points(
    indices: range,
    mu_g: torch.Tensor,
    rho_g: torch.Tensor,
    eta_g: torch.Tensor,
    x_all: torch.Tensor,
    k_all: torch.Tensor,
    n_ref_all: torch.Tensor,
    eta_target_all: torch.Tensor,
    mu_fit_all: torch.Tensor,
    rho_fit_all: torch.Tensor,
    eta_fit_all: torch.Tensor,
    is_lowk: bool,
    lowk_min: float,
    lowk_max: float,
    cfg: Cfg,
    bias: float,
    tilt: float,
    N: int,
) -> None:
    """对给定下标序列做一次 Gauss-Seidel 更新（就地写 mu/rho/eta_fit）。"""
    for i in indices:
        prev_mu  = mu_fit_all[i - 1 : i] if i > 0 else None
        prev_rho = rho_fit_all[i - 1 : i] if i > 0 else None
        prev_eta = eta_fit_all[i - 1 : i] if i > 0 else None
        nxt_mu   = mu_fit_all[i + 1 : i + 2] if i < N - 1 else None
        nxt_rho  = rho_fit_all[i + 1 : i + 2] if i < N - 1 else None
        nxt_eta  = eta_fit_all[i + 1 : i + 2] if i < N - 1 else None

        obj = objective_batch(
            mu_g,
            rho_g,
            eta_g,
            x_all[i : i + 1],
            k_all[i : i + 1],
            n_ref_all[i : i + 1],
            eta_target_all[i : i + 1],
            prev_mu,
            prev_rho,
            prev_eta,
            nxt_mu,
            nxt_rho,
            nxt_eta,
            is_lowk,
            lowk_min,
            lowk_max,
            cfg,
            bias,
            tilt,
        )
        best_idx = obj[0].argmin()
        mu_fit_all[i] = mu_g[best_idx]
        rho_fit_all[i] = rho_g[best_idx]
        eta_fit_all[i] = eta_g[best_idx]


# ─── 每种材料的拟合主循环 ─────────────────────────────────────────────────────

def fit_one_material(rows: list[dict], cfg: Cfg, device: torch.device) -> list[dict]:
    material_name = str(rows[0]["material"]).strip().lower() if rows else ""
    eta_max_mat = eta_max_for_material(rows, cfg)
    mu_g, rho_g, eta_g = build_grid(cfg, eta_max_mat, device)

    k_values   = [max(float(r["k_ref"]), 0.0) for r in rows]
    k_nonzero  = [k for k in k_values if k > 0.0]
    is_lowk    = bool(k_nonzero) and max(k_nonzero) <= cfg.lowk_k_threshold
    lowk_min   = min(k_nonzero) if k_nonzero else 0.0
    lowk_max   = max(k_nonzero) if k_nonzero else 0.0

    # 初始化 fit_rows
    fit_rows = []
    for r in rows:
        et = min(max(eta_target(float(r["k_ref"]), float(r["wavelength_nm"]), cfg),
                     cfg.eta_min), eta_max_mat)
        fit_rows.append({**r, "eta_target": et, "mu_fit": 3.0, "rho_fit": 3.0, "eta_fit": et})

    N = len(fit_rows)
    material_bias = 0.0
    material_tilt = 0.0

    # 把全部数据打包为张量（一次性传 GPU）
    x_all         = torch.tensor([float(r["x"])          for r in fit_rows], dtype=cfg.dtype, device=device)
    k_all         = torch.tensor([float(r["k_ref"])       for r in fit_rows], dtype=cfg.dtype, device=device)
    n_ref_all     = torch.tensor([float(r["n_ref"])       for r in fit_rows], dtype=cfg.dtype, device=device)
    eta_target_all= torch.tensor([float(r["eta_target"])  for r in fit_rows], dtype=cfg.dtype, device=device)

    mu_fit_all  = torch.full((N,), 3.0, dtype=cfg.dtype, device=device)
    rho_fit_all = torch.full((N,), 3.0, dtype=cfg.dtype, device=device)
    eta_fit_all = eta_target_all.clone()

    for _ in range(cfg.fit_iters):
        _sweep_update_points(
            range(N),
            mu_g,
            rho_g,
            eta_g,
            x_all,
            k_all,
            n_ref_all,
            eta_target_all,
            mu_fit_all,
            rho_fit_all,
            eta_fit_all,
            is_lowk,
            lowk_min,
            lowk_max,
            cfg,
            material_bias,
            material_tilt,
            N,
        )
        if cfg.bidirectional:
            _sweep_update_points(
                range(N - 1, -1, -1),
                mu_g,
                rho_g,
                eta_g,
                x_all,
                k_all,
                n_ref_all,
                eta_target_all,
                mu_fit_all,
                rho_fit_all,
                eta_fit_all,
                is_lowk,
                lowk_min,
                lowk_max,
                cfg,
                material_bias,
                material_tilt,
                N,
            )

        # 更新 n_model 的材料级修正：在 bias-only 与 bias+tilt*x 间自动择优
        n_base_all = _n_model_elementwise(mu_fit_all, rho_fit_all, eta_fit_all, x_all, k_all, cfg)
        bias_only, tilt_zero = _solve_bias_only(n_ref_all, n_base_all)
        n_bias_only = n_base_all + bias_only + tilt_zero * x_all
        mae_bias_only = float((n_bias_only - n_ref_all).abs().mean().cpu())

        aff_bias, aff_tilt = _solve_affine_correction(n_ref_all, n_base_all, x_all)
        n_aff = n_base_all + aff_bias + aff_tilt * x_all
        mae_aff = float((n_aff - n_ref_all).abs().mean().cpu())

        force_bias_only = material_name in {m.strip().lower() for m in cfg.force_bias_only_materials}
        force_tilt = material_name in {m.strip().lower() for m in cfg.force_tilt_materials}
        if force_bias_only:
            material_bias, material_tilt = bias_only, tilt_zero
            n_model_all = n_bias_only
        elif force_tilt or (cfg.auto_select_tilt and mae_aff <= mae_bias_only):
            material_bias, material_tilt = aff_bias, aff_tilt
            n_model_all = n_aff
        else:
            material_bias, material_tilt = bias_only, tilt_zero
            n_model_all = n_bias_only

        n_err_all = n_model_all - n_ref_all

    # 写回 Python list
    mu_cpu  = mu_fit_all.cpu().tolist()
    rho_cpu = rho_fit_all.cpu().tolist()
    eta_cpu = eta_fit_all.cpu().tolist()
    nm_cpu  = n_model_all.cpu().tolist()
    ne_cpu  = n_err_all.cpu().tolist()

    for i, r in enumerate(fit_rows):
        r["mu_fit"]        = mu_cpu[i]
        r["rho_fit"]       = rho_cpu[i]
        r["eta_fit"]       = eta_cpu[i]
        r["n_model"]       = nm_cpu[i]
        r["n_err"]         = ne_cpu[i]
        r["material_bias"] = material_bias
        r["material_tilt"] = material_tilt

    return fit_rows


def _n_model_elementwise(
    mu: torch.Tensor,
    rho: torch.Tensor,
    eta: torch.Tensor,
    x: torch.Tensor,
    k: torch.Tensor,
    cfg: Cfg,
) -> torch.Tensor:
    """逐元素版本，所有输入均 (N,)，输出 (N,)。"""
    base     = cfg.a0 + cfg.a1 * torch.log1p(mu.clamp(min=1e-12))
    curve    = cfg.a2 * rho * x ** 2
    coupling = cfg.a3 * torch.sqrt((mu * rho).clamp(min=1e-12))
    eta_term = cfg.a4 * (eta - cfg.eta_ref)
    k_term   = cfg.a5 * torch.log1p(k.clamp(min=0.0) * 300.0) * eta
    k_pow    = cfg.a6 * (k.clamp(min=0.0) ** 0.35) * (0.3 + eta)
    return base + curve + coupling + eta_term + k_term + k_pow


def _solve_affine_correction(
    n_ref: torch.Tensor,
    n_base: torch.Tensor,
    x: torch.Tensor,
) -> tuple[float, float]:
    """
    对 n_ref - n_base 拟合 affine: bias + tilt*x（最小二乘闭式解）。
    """
    y = n_ref - n_base
    x_mean = x.mean()
    y_mean = y.mean()
    x_center = x - x_mean
    y_center = y - y_mean
    var_x = (x_center * x_center).mean()
    if float(var_x.abs().cpu()) <= 1e-18:
        tilt = 0.0
    else:
        tilt = float(((x_center * y_center).mean() / var_x).cpu())
    bias = float((y_mean - tilt * x_mean).cpu())
    return bias, tilt


def _solve_bias_only(n_ref: torch.Tensor, n_base: torch.Tensor) -> tuple[float, float]:
    """仅拟合材料级 bias，tilt 固定为 0。"""
    bias = float((n_ref - n_base).mean().cpu())
    return bias, 0.0


# ─── I/O ─────────────────────────────────────────────────────────────────────

def write_csv(path: Path, rows: list[dict]) -> None:
    keys = ["material", "wavelength_nm", "n_ref", "k_ref", "eta_target",
            "mu_fit", "rho_fit", "eta_fit", "material_bias", "material_tilt", "n_model", "n_err"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})


# ─── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", nargs="+", required=True, help="format: material=path.csv")
    p.add_argument("--out-dir", default="artifacts/ripple_triplet_material_mapping_v7_1_joint")
    p.add_argument(
        "--device",
        default="auto",
        help="auto | dml | cpu | cuda | cuda:0  (AMD Windows 推荐 dml)",
    )
    p.add_argument(
        "--fit-iters",
        type=int,
        default=None,
        help="覆盖 Cfg.fit_iters；默认见 Cfg",
    )
    p.add_argument(
        "--bidirectional",
        action="store_true",
        help="每轮在正扫后再反扫一次（改善部分材料的 η 轨迹，GaAs 类可能略增 n_mae）",
    )
    p.add_argument(
        "--profile",
        default="robust",
        choices=["robust", "si_priority"],
        help="内置参数预设：robust（默认）或 si_priority",
    )
    p.add_argument("--w-eta-target", type=float, default=None, help="覆盖 Cfg.w_eta_target")
    p.add_argument("--w-smooth-eta", type=float, default=None, help="覆盖 Cfg.w_smooth_eta")
    p.add_argument("--w-eta-floor", type=float, default=None, help="覆盖 Cfg.w_eta_floor")
    p.add_argument("--w-eta-lowk-shape", type=float, default=None, help="覆盖 Cfg.w_eta_lowk_shape")
    p.add_argument("--eta-steps", type=int, default=None, help="覆盖 Cfg.eta_steps")
    p.add_argument(
        "--eta-max-override",
        action="append",
        default=[],
        metavar="MAT=MAX",
        help="追加单种材料的 eta 上界覆盖（可多次）。例：--eta-max-override metalx=2.8",
    )
    a = p.parse_args()

    # ── 设备选择 ──────────────────────────────────────────────────────────────
    device_name = "CPU"
    if a.device == "auto":
        # AMD on Windows: prefer DirectML first
        try:
            import torch_directml

            device = torch_directml.device()
            device_name = "DirectML"
        except Exception:
            if torch.cuda.is_available():
                device = torch.device("cuda")
                device_name = torch.cuda.get_device_name(device)
            else:
                device = torch.device("cpu")
                print("[warn] GPU 不可用，使用 CPU")
    elif a.device == "dml":
        import torch_directml

        device = torch_directml.device()
        device_name = "DirectML"
    else:
        device = torch.device(a.device)
        if getattr(device, "type", "") == "cuda":
            device_name = torch.cuda.get_device_name(device)
    print(f"[device] {device} ({device_name})")

    cfg = apply_profile(Cfg(), a.profile)
    eta_max_overrides: dict[str, float] = dict(cfg.eta_max_overrides or {})
    for item in a.eta_max_override:
        if "=" not in item:
            raise SystemExit(f"invalid --eta-max-override (expected MAT=MAX): {item!r}")
        mat, vmax = item.split("=", 1)
        eta_max_overrides[mat.strip().lower()] = float(vmax)
    cfg.eta_max_overrides = eta_max_overrides
    if a.fit_iters is not None:
        if a.fit_iters < 1:
            raise SystemExit("--fit-iters must be >= 1")
        cfg.fit_iters = a.fit_iters
    if a.eta_steps is not None:
        if a.eta_steps < 3:
            raise SystemExit("--eta-steps must be >= 3")
        cfg.eta_steps = a.eta_steps
    if a.bidirectional:
        cfg.bidirectional = True
    if a.w_eta_target is not None:
        cfg.w_eta_target = float(a.w_eta_target)
    if a.w_smooth_eta is not None:
        cfg.w_smooth_eta = float(a.w_smooth_eta)
    if a.w_eta_floor is not None:
        cfg.w_eta_floor = float(a.w_eta_floor)
    if a.w_eta_lowk_shape is not None:
        cfg.w_eta_lowk_shape = float(a.w_eta_lowk_shape)
    all_rows: list[dict] = []
    mats_summary = []

    for item in a.input:
        material, path = item.split("=", 1)
        rows     = load_rows(Path(path), material)
        fit_rows = fit_one_material(rows, cfg, device)
        all_rows.extend(fit_rows)
        mae = sum(abs(float(r["n_err"])) for r in fit_rows) / max(len(fit_rows), 1)
        mats_summary.append({
            "material":  material,
            "rows":      len(fit_rows),
            "n_mae":     mae,
            "mu_mean":   sum(float(r["mu_fit"]) for r in fit_rows) / max(len(fit_rows), 1),
            "rho_mean":  sum(float(r["rho_fit"]) for r in fit_rows) / max(len(fit_rows), 1),
            "eta_mean":  sum(float(r["eta_fit"]) for r in fit_rows) / max(len(fit_rows), 1),
        })

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.csv", all_rows)
    cfg_dict = asdict(cfg)
    if "dtype" in cfg_dict:
        cfg_dict["dtype"] = str(cfg_dict["dtype"])
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": cfg_dict,
        "materials": mats_summary,
        "rows": all_rows,
    }
    (out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = ["# Triplet Material Mapping v7.1 Joint (GPU build)", ""]
    for m in mats_summary:
        lines.append(
            f"- {m['material']}: rows={m['rows']}, n_mae={m['n_mae']:.6e}, "
            f"mu_mean={m['mu_mean']:.6f}, rho_mean={m['rho_mean']:.6f}, eta_mean={m['eta_mean']:.6f}"
        )
    (out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())