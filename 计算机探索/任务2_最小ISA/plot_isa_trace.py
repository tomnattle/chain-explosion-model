from matplotlib import pyplot as plt

from minimal_isa_runner import abs_i, build_mapping, residual


def run_program_with_trace(program):
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

    scale = 10 ** state["digits"]
    x = state["seed_num"] * (10 ** (state["digits"] - 1))
    damp_num = state["eta_den"] - state["eta_num"]
    damp_den = state["eta_den"]
    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den = build_mapping(
        state["mapping_id"], state["mu_num"], state["mu_den"], state["rho_num"], state["rho_den"], scale
    )

    trace_x = [x / scale]
    trace_res = [abs_i(residual(state["task"], x, scale, state["params"]))]
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
        x = x_next
        trace_x.append(x / scale)
        trace_res.append(abs_i(residual(state["task"], x, scale, state["params"])))
        if delta == 0:
            break
    return trace_x, trace_res, state


def main():
    program = [
        {"op": "SET_CONST", "mu_num": 15495, "mu_den": 10000, "rho_num": 235, "rho_den": 100, "eta_num": 8, "eta_den": 100},
        {"op": "SET_MAPPING", "mapping_id": 2},
        {"op": "SET_TASK", "task": "sqrt", "params": {"a": 3}},
        {"op": "SET_SEED", "seed_num": 17},
        {"op": "RUN", "steps": 320, "digits": 20},
    ]
    trace_x, trace_res, state = run_program_with_trace(program)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), dpi=140)
    axes[0].plot(trace_x, color="#1f77b4")
    axes[0].set_title("ISA Execution: value trajectory")
    axes[0].set_xlabel("step")
    axes[0].set_ylabel("x")

    axes[1].plot([len(str(r)) for r in trace_res], color="#d62728")
    axes[1].set_title("ISA Execution: residual magnitude")
    axes[1].set_xlabel("step")
    axes[1].set_ylabel("digits in |residual|")

    fig.suptitle(f"Minimal ISA Trace (task={state['task']}, mapping=M{state['mapping_id']})")
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out_path = "计算机探索/任务2_最小ISA/isa_trace.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
