"""
Ripple phase-map scanner (pure cascade, no fallback).

Scan:
  mu  in [1.5, 1.6]
  rho in [2.3, 2.4]

Classify each sample:
  CONVERGED : close to sqrt(2) attractor
  CYCLIC    : detected periodic orbit
  DRIFTED   : neither converged nor cyclic
"""


def abs_i(v):
    return -v if v < 0 else v


def fixed_to_str(value, scale):
    sign = "-" if value < 0 else ""
    value = -value if value < 0 else value
    integer = value // scale
    frac = value % scale
    width = len(str(scale)) - 1
    return f"{sign}{integer}.{frac:0{width}d}"


def detect_cycle(values, max_period=16):
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


def build_mapping_m2(mu_num, mu_den, rho_num, rho_den, scale):
    # M2 nonlinear: mu^2 / rho
    material_num = mu_num * mu_num * rho_den
    material_den = mu_den * mu_den * rho_num
    g1_num = 3 * material_num + material_den
    g1_den = 20 * material_den
    g2_num = g1_num
    g2_den = 6 * scale * g1_den
    g3_num = g1_num
    g3_den = 24 * scale * scale * g1_den
    return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den


def run_point(mu_num, rho_num, digits=20, steps=260):
    mu_den = 10000
    rho_den = 1000
    eta_num, eta_den = 8, 100  # fixed eta=0.08

    scale = 10 ** digits
    target = 2 * scale * scale
    x = 14 * (10 ** (digits - 1))

    damp_num = eta_den - eta_num
    damp_den = eta_den
    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den = build_mapping_m2(
        mu_num, mu_den, rho_num, rho_den, scale
    )

    history = [x]
    cycle_period = 0
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

        cycle_period = detect_cycle(history, max_period=16)
        if cycle_period > 0:
            stop_reason = "cyclic"
            x = x_next
            break

        x = x_next

    final_err = x * x - target
    abs_err = abs_i(final_err)

    # threshold ~ 5e-19 in x-space (fixed-point digits=20)
    # compare squared residual directly in integer scale
    converged_threshold = 10 ** 22
    if abs_err <= converged_threshold:
        phase = "CONVERGED"
    elif stop_reason == "cyclic":
        phase = "CYCLIC"
    else:
        phase = "DRIFTED"

    return phase, x, abs_err, cycle_period


def main():
    # 11x11 grid with step 0.01 in both axes
    mu_values = [15000 + i * 100 for i in range(11)]   # 1.5000 .. 1.6000
    rho_values = [2300 + j * 10 for j in range(11)]    # 2.300 .. 2.400

    counts = {"CONVERGED": 0, "CYCLIC": 0, "DRIFTED": 0}
    records = []

    print("=== Ripple Phase Map Scan ===")
    print("mode: pure cascade only, no fallback")
    print("mapping: M2 nonlinear(mu^2/rho)")
    print("eta fixed at 0.08")
    print("grid: mu=[1.5,1.6], rho=[2.3,2.4], step=0.01")

    # header
    print("\nPhase map (rows=rho, cols=mu):")
    header = "rho\\mu " + " ".join([f"{m/10000:.2f}" for m in mu_values])
    print(header)

    for rho in rho_values:
        row_marks = []
        for mu in mu_values:
            phase, x, abs_err, cyc = run_point(mu, rho, digits=20, steps=260)
            counts[phase] += 1
            records.append((mu, rho, phase, x, abs_err, cyc))
            mark = "C" if phase == "CONVERGED" else ("Y" if phase == "CYCLIC" else "D")
            row_marks.append(mark)
        print(f"{rho/1000:.2f}   " + "   ".join(row_marks))

    print("\nLegend: C=CONVERGED, Y=CYCLIC, D=DRIFTED")
    total = len(records)
    print(
        f"Counts: CONVERGED={counts['CONVERGED']}, "
        f"CYCLIC={counts['CYCLIC']}, DRIFTED={counts['DRIFTED']}, total={total}"
    )

    # Print top 8 best converged points by residual
    best = [r for r in records if r[2] == "CONVERGED"]
    best.sort(key=lambda t: t[4])
    print("\nTop converged points (lowest abs residual):")
    for mu, rho, phase, x, abs_err, cyc in best[:8]:
        print(
            f"mu={mu/10000:.4f}, rho={rho/1000:.3f}, "
            f"value={fixed_to_str(x, 10**20)}, abs_err={abs_err}, cyc={cyc}"
        )


if __name__ == "__main__":
    main()
