"""
Ripple Computer - Pure Cascade Version (No Newton)

Goal:
- No math.sqrt
- No Newton iteration
- No third-party libraries

Method:
- Fixed-point deterministic field evolution only
- Cascaded residual feedback:
    r1 = 2 - x^2
    r2 = r1 * |r1|
    r3 = r2 * |r1|
  x_{k+1} = x_k + damp * (g1*r1 + g2*r2 + g3*r3)
- Gains are derived from (mu, rho, eta) with integer arithmetic.
- No post-refine, no fallback, no search-based correction.
"""


def fixed_to_str(value, scale):
    sign = "-" if value < 0 else ""
    value = -value if value < 0 else value
    integer = value // scale
    frac = value % scale
    width = len(str(scale)) - 1
    return f"{sign}{integer}.{frac:0{width}d}"


def abs_i(v):
    return -v if v < 0 else v


def ripple_cascade_sqrt2(digits=20, steps=240):
    # Physics constants (fixed-point source parameters)
    mu_num, mu_den = 15495, 10000  # 1.5495
    rho_num, rho_den = 235, 100    # 2.35
    eta_num, eta_den = 8, 100      # 0.08

    scale = 10 ** digits
    x = 14 * (10 ** (digits - 1))  # start at 1.4 exactly in fixed-point
    target = 2 * scale * scale

    # Damping from eta
    damp_num = eta_den - eta_num
    damp_den = eta_den

    # Build deterministic gains from mu/rho/eta
    # Base gain around 0.18~0.25 typically stable for this map.
    material_num = mu_num * rho_num
    material_den = mu_den * rho_den

    # g1: first-order residual channel
    g1_num = 2 * material_num + material_den
    g1_den = 10 * material_den

    # g2/g3: higher-order residual channels, much smaller
    g2_num = g1_num
    g2_den = 4 * scale * g1_den

    g3_num = g1_num
    g3_den = 16 * scale * scale * g1_den

    trace = []
    for i in range(steps):
        # r1 in fixed-point scale: r1 = (2 - (x/scale)^2)
        r1 = 2 * scale - (x * x) // scale
        a1 = abs_i(r1)

        # r2 ~ r1*|r1| / scale ; r3 ~ r2*|r1| / scale
        r2 = (r1 * a1) // scale
        r3 = (r2 * a1) // scale

        c1 = (g1_num * r1) // g1_den
        c2 = (g2_num * r2) // g2_den
        c3 = (g3_num * r3) // g3_den

        delta = (damp_num * (c1 + c2 + c3)) // damp_den
        if delta == 0:
            # Stuck at fixed-point resolution; stop.
            err = x * x - target
            trace.append((i + 1, x, err, delta))
            break

        x_next = x + delta

        # Simple anti-overshoot clamp to keep deterministic stability
        if x_next <= 0:
            x_next = scale

        x = x_next
        err = x * x - target

        # Record sparse trace for readability
        if i < 12 or (i + 1) % 20 == 0 or i + 1 == steps:
            trace.append((i + 1, x, err, delta))

    return x, scale, trace


def main():
    value, scale, trace = ripple_cascade_sqrt2(digits=20, steps=240)
    target = 2 * scale * scale
    final_err = value * value - target
    abs_err = abs_i(final_err)

    print("=== Ripple Pure Cascade Computation: sqrt(2) ===")
    print("mu=1.5495, rho=2.35, eta=0.08")
    print("mode=no-sqrt, no-newton, no-third-party, no-fallback")
    print(f"physical-only value (20 digits) = {fixed_to_str(value, scale)}")
    print(f"final signed residual (y^2-2*S^2) = {final_err}")
    print(f"final absolute residual           = {abs_err}")
    print("cascade trace (iter, value, signed_error=y^2-2*S^2, delta):")
    for i, v, e, d in trace:
        print(f"  {i:03d}  {fixed_to_str(v, scale)}  err={e}  delta={d}")


if __name__ == "__main__":
    main()
