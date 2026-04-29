"""
Paper-style plots for ripple phase analysis (pure cascade only).

Outputs:
  1) phase_map_m1_oscillation.png
  2) residual_map_m2_m3.png
"""

from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap

OUTPUT_DIR = "计算机探索/figures"


def abs_i(v):
    return -v if v < 0 else v


def detect_cycle(values, max_period=24):
    if len(values) < 2 * max_period + 2:
        return 0
    tail = values[-(2 * max_period + 2):]
    for p in range(1, max_period + 1):
        ok = True
        for i in range(1, p + 1):
            if tail[-i] != tail[-i - p]:
                ok = False
                break
        if ok:
            return p
    return 0


def build_mapping(mapping_id, mu_num, mu_den, rho_num, rho_den, scale):
    if mapping_id == 1:
        material_num = mu_num * rho_num
        material_den = mu_den * rho_den
        g1_num = 2 * material_num + material_den
        g1_den = 10 * material_den
        g2_num = g1_num
        g2_den = 4 * scale * g1_den
        g3_num = g1_num
        g3_den = 16 * scale * scale * g1_den
        return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den

    if mapping_id == 2:
        material_num = mu_num * mu_num * rho_den
        material_den = mu_den * mu_den * rho_num
        g1_num = 3 * material_num + material_den
        g1_den = 20 * material_den
        g2_num = g1_num
        g2_den = 6 * scale * g1_den
        g3_num = g1_num
        g3_den = 24 * scale * scale * g1_den
        return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den

    left_num = mu_num * rho_den
    left_den = mu_den * rho_num
    right_num = rho_num * mu_den
    right_den = rho_den * mu_num
    mix_num = left_num * right_den + right_num * left_den
    mix_den = left_den * right_den
    g1_num = mix_num
    g1_den = 16 * mix_den
    g2_num = g1_num
    g2_den = 8 * scale * g1_den
    g3_num = g1_num
    g3_den = 32 * scale * scale * g1_den
    return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den


def run_point(mu_num, rho_num, mapping_id, seed_num, digits=20, steps=360):
    mu_den = 10000
    rho_den = 1000
    eta_num, eta_den = 8, 100

    scale = 10 ** digits
    target = 2 * scale * scale
    x = seed_num * (10 ** (digits - 1))

    damp_num = eta_den - eta_num
    damp_den = eta_den
    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den = build_mapping(
        mapping_id, mu_num, mu_den, rho_num, rho_den, scale
    )

    history = [x]
    stop_reason = "max_steps"

    for _ in range(steps):
        r1 = 2 * scale - (x * x) // scale
        a1 = abs_i(r1)
        r2 = (r1 * a1) // scale
        r3 = (r2 * a1) // scale

        c1 = (g1_num * r1) // g1_den
        c2 = (g2_num * r2) // g2_den
        c3 = (g3_num * r3) // g3_den
        delta = (damp_num * (c1 + c2 + c3)) // damp_den

        x_next = x + delta
        if x_next <= 0:
            x_next = scale

        history.append(x_next)

        if delta == 0:
            stop_reason = "delta_zero"
            x = x_next
            break

        period = detect_cycle(history, max_period=24)
        if period > 0:
            stop_reason = f"cycle_{period}"
            x = x_next
            break

        x = x_next

    abs_err = abs_i(x * x - target)

    # 0=CONVERGED,1=NEAR_FIXED,2=CYCLIC,3=DRIFTED
    if abs_err <= 10 ** 18:
        phase = 0
    elif stop_reason.startswith("cycle_"):
        phase = 2
    elif stop_reason == "delta_zero":
        phase = 1
    else:
        phase = 3
    return phase, abs_err


def grid_ranges():
    mu_values = [13000 + i * 200 for i in range(26)]  # 1.30..1.80
    rho_values = [2000 + j * 40 for j in range(21)]   # 2.00..2.80
    return mu_values, rho_values


def plot_m1_phase(seed_num=14):
    mu_values, rho_values = grid_ranges()
    phase_grid = []
    for rho in rho_values:
        row = []
        for mu in mu_values:
            phase, _ = run_point(mu, rho, mapping_id=1, seed_num=seed_num)
            row.append(phase)
        phase_grid.append(row)

    cmap = ListedColormap(["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"])
    plt.figure(figsize=(8, 5), dpi=150)
    plt.imshow(
        phase_grid,
        cmap=cmap,
        vmin=0,
        vmax=3,
        origin="lower",
        aspect="auto",
        extent=[mu_values[0] / 10000, mu_values[-1] / 10000, rho_values[0] / 1000, rho_values[-1] / 1000],
    )
    plt.title("M1 Phase Regions (seed=1.4)\nGreen=CONVERGED Blue=NEAR_FIXED Orange=CYCLIC Red=DRIFTED")
    plt.xlabel("mu")
    plt.ylabel("rho")
    out_path = f"{OUTPUT_DIR}/phase_map_m1_oscillation.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_m2_m3_residual(seed_num=14):
    mu_values, rho_values = grid_ranges()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=150)
    for idx, mapping_id in enumerate((2, 3)):
        residual_grid = []
        for rho in rho_values:
            row = []
            for mu in mu_values:
                _, abs_err = run_point(mu, rho, mapping_id=mapping_id, seed_num=seed_num)
                # log10-like compression using digit length
                row.append(len(str(abs_err)))
            residual_grid.append(row)

        im = axes[idx].imshow(
            residual_grid,
            cmap="viridis",
            origin="lower",
            aspect="auto",
            extent=[mu_values[0] / 10000, mu_values[-1] / 10000, rho_values[0] / 1000, rho_values[-1] / 1000],
        )
        axes[idx].set_title(f"M{mapping_id} residual magnitude (seed=1.4)")
        axes[idx].set_xlabel("mu")
        axes[idx].set_ylabel("rho")
        cbar = fig.colorbar(im, ax=axes[idx])
        cbar.set_label("digits in abs_err (smaller is better)")

    fig.suptitle("Residual Gradient Maps (pure cascade, no fallback)")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = f"{OUTPUT_DIR}/residual_map_m2_m3.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def main():
    p1 = plot_m1_phase(seed_num=14)
    p2 = plot_m2_m3_residual(seed_num=14)
    print("Saved:", p1)
    print("Saved:", p2)


if __name__ == "__main__":
    main()
