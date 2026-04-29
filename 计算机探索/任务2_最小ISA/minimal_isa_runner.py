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

    material_num = mu_num * rho_num
    material_den = mu_den * rho_den
    g1_num = 2 * material_num + material_den
    g1_den = 10 * material_den
    g2_num = g1_num
    g2_den = 4 * scale * g1_den
    g3_num = g1_num
    g3_den = 16 * scale * scale * g1_den
    return g1_num, g1_den, g2_num, g2_den, g3_num, g3_den


def residual(task, x, scale, params):
    if task == "sqrt":
        return params["a"] * scale - (x * x) // scale
    if task == "reciprocal":
        return scale - params["b"] * x
    raise ValueError("unsupported task")


def run_program(program):
    state = {
        "mu_num": 15495, "mu_den": 10000,
        "rho_num": 235, "rho_den": 100,
        "eta_num": 8, "eta_den": 100,
        "mapping_id": 2,
        "task": "sqrt",
        "params": {"a": 2},
        "seed_num": 14,
        "steps": 300,
        "digits": 20,
    }

    for inst in program:
        op = inst["op"]
        if op == "SET_CONST":
            state["mu_num"] = inst["mu_num"]
            state["mu_den"] = inst["mu_den"]
            state["rho_num"] = inst["rho_num"]
            state["rho_den"] = inst["rho_den"]
            state["eta_num"] = inst["eta_num"]
            state["eta_den"] = inst["eta_den"]
        elif op == "SET_MAPPING":
            state["mapping_id"] = inst["mapping_id"]
        elif op == "SET_TASK":
            state["task"] = inst["task"]
            state["params"] = inst["params"]
        elif op == "SET_SEED":
            state["seed_num"] = inst["seed_num"]
        elif op == "RUN":
            state["steps"] = inst["steps"]
            state["digits"] = inst["digits"]
        else:
            raise ValueError(f"unknown op: {op}")

    scale = 10 ** state["digits"]
    x = state["seed_num"] * (10 ** (state["digits"] - 1))
    damp_num = state["eta_den"] - state["eta_num"]
    damp_den = state["eta_den"]
    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den = build_mapping(
        state["mapping_id"],
        state["mu_num"], state["mu_den"],
        state["rho_num"], state["rho_den"], scale
    )

    stop = "max_steps"
    for _ in range(state["steps"]):
        r1 = residual(state["task"], x, scale, state["params"])
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
        if delta == 0:
            stop = "delta_zero"
            x = x_next
            break
        x = x_next

    final_res = residual(state["task"], x, scale, state["params"])
    return x, final_res, stop, scale, state


def main():
    program = [
        {"op": "SET_CONST", "mu_num": 15495, "mu_den": 10000, "rho_num": 235, "rho_den": 100, "eta_num": 8, "eta_den": 100},
        {"op": "SET_MAPPING", "mapping_id": 2},
        {"op": "SET_TASK", "task": "sqrt", "params": {"a": 3}},
        {"op": "SET_SEED", "seed_num": 17},
        {"op": "RUN", "steps": 320, "digits": 20},
    ]
    x, final_res, stop, scale, state = run_program(program)
    print("=== 最小ISA执行结果 ===")
    print(f"task={state['task']} params={state['params']} mapping=M{state['mapping_id']}")
    print(f"value={fixed_to_str(x, scale)} residual={final_res} stop={stop}")


if __name__ == "__main__":
    main()
