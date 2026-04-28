"""
Ripple Computer - Pure Cascade Diagnostics (No Fallback)

Purpose:
- Keep pure physical-style evolution (no sqrt/newton/search refinement)
- Compare 3 gain-mapping formulas from (mu, rho, eta)
- Detect convergence / periodic orbit / drift using full-step traces
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


def build_mapping(mapping_id, mu_num, mu_den, rho_num, rho_den, scale):
    """
    Returns:
      (g1_num, g1_den, g2_num, g2_den, g3_num, g3_den, label)
    """
    # eta is handled as damping outside
    if mapping_id == 1:
        # linear blend: close to prior version
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
        # inverse-density emphasis: mu^2 / rho
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

    # mapping_id == 3:
    # reciprocal mix: mu/rho + rho/mu, then softened
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
    label = "M3 reciprocal(mu/rho + rho/mu)"
    return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den, label


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


def run_pure_cascade(mapping_id, digits=20, steps=320):
    mu_num, mu_den = 15495, 10000  # 1.5495
    rho_num, rho_den = 235, 100    # 2.35
    eta_num, eta_den = 8, 100      # 0.08

    scale = 10 ** digits
    target = 2 * scale * scale
    x = 14 * (10 ** (digits - 1))  # 1.4 seed

    damp_num = eta_den - eta_num
    damp_den = eta_den

    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den, label = build_mapping(
        mapping_id, mu_num, mu_den, rho_num, rho_den, scale
    )

    all_x = [x]
    trace = []
    cycle_period = 0
    stop_reason = "max_steps"

    for i in range(steps):
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

        err = x_next * x_next - target
        trace.append((i + 1, x_next, err, delta))
        all_x.append(x_next)

        if delta == 0:
            stop_reason = "delta_zero"
            x = x_next
            break

        cycle_period = detect_cycle(all_x, max_period=16)
        if cycle_period > 0:
            stop_reason = f"cycle_{cycle_period}"
            x = x_next
            break

        x = x_next

    final_err = x * x - target
    final_abs_err = abs_i(final_err)

    return {
        "mapping_id": mapping_id,
        "label": label,
        "value": x,
        "scale": scale,
        "final_err": final_err,
        "final_abs_err": final_abs_err,
        "stop_reason": stop_reason,
        "cycle_period": cycle_period,
        "trace": trace,
    }


def main():
    print("=== Ripple Pure Cascade Diagnostics ===")
    print("constraints: no-sqrt, no-newton, no-third-party, no-fallback")
    print("constants: mu=1.5495, rho=2.35, eta=0.08")

    results = []
    for mapping_id in (1, 2, 3):
        results.append(run_pure_cascade(mapping_id, digits=20, steps=320))

    print("\n--- Summary ---")
    for r in results:
        print(
            f"[{r['mapping_id']}] {r['label']} | value={fixed_to_str(r['value'], r['scale'])} "
            f"| abs_err={r['final_abs_err']} | stop={r['stop_reason']}"
        )

    # Print compact traces for each mapping
    for r in results:
        print(f"\n--- Trace Mapping {r['mapping_id']}: {r['label']} ---")
        tr = r["trace"]
        for i, v, e, d in tr:
            if i <= 12 or i % 25 == 0 or i == len(tr):
                print(
                    f"  {i:03d}  {fixed_to_str(v, r['scale'])}  "
                    f"err={e}  delta={d}"
                )


if __name__ == "__main__":
    main()
