"""
Ripple Computer prototype:
- No math.sqrt / decimal / third-party libs
- Use a physics-inspired damped interference update to get an initial point
- Refine with pure integer fixed-point Newton iteration for sqrt(2)
"""


def fixed_to_str(value, scale):
    sign = "-" if value < 0 else ""
    value = -value if value < 0 else value
    integer = value // scale
    frac = value % scale
    width = len(str(scale)) - 1
    return f"{sign}{integer}.{frac:0{width}d}"


def interference_seed(mu_num=15495, mu_den=10000, eta_num=8, eta_den=100, steps=120):
    """
    Returns a fixed-point seed y ~= sqrt(2)*S, without using sqrt.
    Model:
        x_{k+1} = x_k + damp * (2 - x_k^2) / (2*x_k + rho)
    where damp=(1-eta), rho from mu and density mapping.
    """
    # Keep everything in fixed-point to avoid huge rational growth.
    seed_scale = 10 ** 8
    x = seed_scale  # 1.0

    damp_num = eta_den - eta_num  # 0.92 when eta=0.08
    damp_den = eta_den

    rho_num, rho_den = 235, 100
    # coupling ~= mu * rho
    coupling_scaled = (mu_num * rho_num * seed_scale) // (mu_den * rho_den)

    for _ in range(steps):
        # residual_scaled ~= (2 - (x/S)^2) * S
        residual_scaled = 2 * seed_scale - ((x * x) // seed_scale)

        # denominator_scaled ~= (2*x + coupling)
        denominator_scaled = 2 * x + coupling_scaled
        if denominator_scaled <= 0:
            denominator_scaled = seed_scale

        # delta_scaled ~= damp * residual / denominator, still in S scale
        delta_scaled = (
            damp_num * residual_scaled * seed_scale
        ) // (damp_den * denominator_scaled)

        x = x + delta_scaled

    return x, seed_scale


def sqrt2_fixed_point_20digits(seed_num, seed_den, digits=20, iters=14):
    """
    Pure fixed-point Newton:
      y_{n+1} = (y_n + floor(2*S^2 / y_n)) // 2
    with S=10^digits and y approximating sqrt(2)*S.
    """
    scale = 10 ** digits
    y = (seed_num * scale) // seed_den
    if y <= 0:
        y = scale

    target = 2 * scale * scale
    trace = []

    for i in range(iters):
        y_next = (y + (target // y)) // 2
        err = y_next * y_next - target
        trace.append((i + 1, y_next, err))
        if y_next == y:
            break
        y = y_next

    return y, trace, scale


def main():
    mu = "1.5495"
    rho = "2.35"
    eta = "0.08"

    seed_num, seed_den = interference_seed()
    value, trace, scale = sqrt2_fixed_point_20digits(seed_num, seed_den)

    print("=== Ripple Deterministic Computation: sqrt(2) ===")
    print(f"mu={mu}, rho={rho}, eta={eta}")
    print(f"interference seed (rational) = {seed_num}/{seed_den}")
    print(f"result (20 digits) = {fixed_to_str(value, scale)}")
    print("trace (iter, value, signed_error=y^2-2*S^2):")
    for i, v, e in trace:
        print(f"  {i:02d}  {fixed_to_str(v, scale)}  err={e}")


if __name__ == "__main__":
    main()
