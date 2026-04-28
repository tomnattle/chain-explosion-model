"""
Ripple phase map (color image) for multi-mapping and multi-seed.

Constraints:
- no sqrt
- no Newton
- no fallback refine
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
        label = "M1 linear(mu*rho)"
        return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den, label

    if mapping_id == 2:
        material_num = mu_num * mu_num * rho_den
        material_den = mu_den * mu_den * rho_num
        g1_num = 3 * material_num + material_den
        g1_den = 20 * material_den
        g2_num = g1_num
        g2_den = 6 * scale * g1_den
        g3_num = g1_num
        g3_den = 24 * scale * scale * g1_den
        label = "M2 nonlinear(mu^2/rho)"
        return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den, label

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
    label = "M3 reciprocal(mu/rho+rho/mu)"
    return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den, label


def run_point(mu_num, rho_num, mapping_id, seed_num, digits=20, steps=360):
    mu_den = 10000
    rho_den = 1000
    eta_num, eta_den = 8, 100

    scale = 10 ** digits
    target = 2 * scale * scale
    x = seed_num * (10 ** (digits - 1))

    damp_num = eta_den - eta_num
    damp_den = eta_den
    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den, _ = build_mapping(
        mapping_id, mu_num, mu_den, rho_num, rho_den, scale
    )

    history = [x]
    stop_reason = "max_steps"
    cycle_period = 0

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

        cycle_period = detect_cycle(history, max_period=24)
        if cycle_period > 0:
            stop_reason = f"cycle_{cycle_period}"
            x = x_next
            break

        x = x_next

    abs_err = abs_i(x * x - target)

    # 0=CONVERGED,1=NEAR_FIXED,2=CYCLIC,3=DRIFTED
    if abs_err <= 10 ** 18:
        return 0, abs_err, stop_reason
    if stop_reason.startswith("cycle_"):
        return 2, abs_err, stop_reason
    if stop_reason == "delta_zero":
        return 1, abs_err, stop_reason
    return 3, abs_err, stop_reason


def scan_grid(mapping_id, seed_num):
    mu_values = [13000 + i * 200 for i in range(26)]  # 1.30..1.80
    rho_values = [2000 + j * 40 for j in range(21)]   # 2.00..2.80

    grid = []
    counts = [0, 0, 0, 0]
    best_abs_err = None
    best_point = None

    for rho in rho_values:
        row = []
        for mu in mu_values:
            phase, abs_err, stop_reason = run_point(mu, rho, mapping_id, seed_num)
            row.append(phase)
            counts[phase] += 1
            if best_abs_err is None or abs_err < best_abs_err:
                best_abs_err = abs_err
                best_point = (mu, rho, abs_err, stop_reason)
        grid.append(row)

    return mu_values, rho_values, grid, counts, best_point


def main():
    mappings = [1, 2, 3]
    seeds = [12, 14, 16]  # 1.2, 1.4, 1.6

    cmap = ListedColormap(["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"])
    # CONVERGED, NEAR_FIXED, CYCLIC, DRIFTED

    fig, axes = plt.subplots(len(mappings), len(seeds), figsize=(15, 11), dpi=140)
    fig.suptitle(
        "Ripple Pure Cascade Phase Map (No sqrt/Newton/Fallback)\n"
        "green=CONVERGED, blue=NEAR_FIXED, orange=CYCLIC, red=DRIFTED",
        fontsize=11,
    )

    summary_lines = []
    for r, mapping_id in enumerate(mappings):
        for c, seed_num in enumerate(seeds):
            mu_values, rho_values, grid, counts, best_point = scan_grid(mapping_id, seed_num)
            ax = axes[r][c]
            im = ax.imshow(
                grid,
                cmap=cmap,
                vmin=0,
                vmax=3,
                origin="lower",
                aspect="auto",
                extent=[mu_values[0] / 10000, mu_values[-1] / 10000, rho_values[0] / 1000, rho_values[-1] / 1000],
            )
            ax.set_title(f"M{mapping_id}, seed={seed_num/10:.1f}", fontsize=9)
            ax.set_xlabel("mu")
            ax.set_ylabel("rho")

            total = sum(counts)
            summary_lines.append(
                f"M{mapping_id} seed={seed_num/10:.1f} | "
                f"C={counts[0]}/{total}, N={counts[1]}/{total}, Y={counts[2]}/{total}, D={counts[3]}/{total} | "
                f"best(mu={best_point[0]/10000:.2f},rho={best_point[1]/1000:.2f},err={best_point[2]},stop={best_point[3]})"
            )

    # Custom legend panel
    fig.text(0.01, 0.01, "\n".join(summary_lines), fontsize=8, family="monospace")
    plt.tight_layout(rect=[0.02, 0.07, 1, 0.94])

    out_path = f"{OUTPUT_DIR}/phase_map_multimapping.png"
    plt.savefig(out_path)
    print("Saved:", out_path)
    print("Legend: 0=CONVERGED, 1=NEAR_FIXED, 2=CYCLIC, 3=DRIFTED")
    for line in summary_lines:
        print(line)


if __name__ == "__main__":
    main()
