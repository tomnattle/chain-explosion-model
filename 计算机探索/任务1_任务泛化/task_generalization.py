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
    material_num = mu_num * mu_num * rho_den
    material_den = mu_den * mu_den * rho_num
    g1_num = 3 * material_num + material_den
    g1_den = 20 * material_den
    g2_num = g1_num
    g2_den = 6 * scale * g1_den
    g3_num = g1_num
    g3_den = 24 * scale * scale * g1_den
    return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den


def residual(task, x, scale, params):
    if task == "sqrt":
        # r = a - x^2
        a_scaled = params["a"] * scale
        return a_scaled - (x * x) // scale
    if task == "reciprocal":
        # r = 1 - b*x
        b = params["b"]
        return scale - b * x
    if task == "quadratic":
        # r = -(x^2 + b*x + c)
        b = params["b"]
        c = params["c"]
        poly = (x * x) // scale + b * x + c * scale
        return -poly
    raise ValueError(f"unknown task: {task}")


def run_task(task, params, seed_num, digits=20, steps=320):
    mu_num, mu_den = 15495, 10000
    rho_num, rho_den = 235, 100
    eta_num, eta_den = 8, 100

    scale = 10 ** digits
    x = seed_num * (10 ** (digits - 1))
    damp_num = eta_den - eta_num
    damp_den = eta_den
    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den = build_mapping_m2(
        mu_num, mu_den, rho_num, rho_den, scale
    )

    hist = [x]
    stop_reason = "max_steps"
    for _ in range(steps):
        r1 = residual(task, x, scale, params)
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
        hist.append(x_next)

        if delta == 0:
            stop_reason = "delta_zero"
            x = x_next
            break

        period = detect_cycle(hist, max_period=16)
        if period > 0:
            stop_reason = f"cycle_{period}"
            x = x_next
            break
        x = x_next

    final_res = residual(task, x, scale, params)
    return x, final_res, stop_reason, scale


def main():
    cases = [
        ("sqrt", {"a": 3}, 17, "sqrt(3)"),
        ("reciprocal", {"b": 7}, 2, "1/7"),
        ("quadratic", {"b": -5, "c": 6}, 26, "x^2-5x+6=0"),
    ]
    print("=== 任务泛化（纯级联，不作弊）===")
    for task, params, seed, label in cases:
        x, res, stop_reason, scale = run_task(task, params, seed_num=seed)
        print(
            f"{label:14s} | value={fixed_to_str(x, scale)} | "
            f"residual={res} | stop={stop_reason}"
        )


if __name__ == "__main__":
    main()
