import csv
import random


def abs_i(v):
    return -v if v < 0 else v


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


def run_once(mu_num, rho_num, eta_num, seed_num, noise_ppm=0, steps=320, digits=20):
    mu_den = 10000
    rho_den = 100
    eta_den = 100
    scale = 10 ** digits
    target = 2 * scale * scale
    x = seed_num * (10 ** (digits - 1))

    g1_num, g1_den, g2_num, g2_den, g3_num, g3_den = build_mapping_m2(
        mu_num, mu_den, rho_num, rho_den, scale
    )
    damp_num = eta_den - eta_num
    damp_den = eta_den

    hist = [x]
    stop_reason = "max_steps"
    step_used = 0

    for i in range(steps):
        r1 = 2 * scale - (x * x) // scale
        if noise_ppm > 0:
            jitter = random.randint(-noise_ppm, noise_ppm)
            r1 = r1 + (r1 * jitter) // 1_000_000
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
        step_used = i + 1

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

    abs_err = abs_i(x * x - target)
    if abs_err <= 10 ** 18:
        phase = "CONVERGED"
    elif stop_reason.startswith("cycle_"):
        phase = "CYCLIC"
    else:
        phase = "DRIFTED"
    return phase, abs_err, step_used, stop_reason


def main():
    random.seed(42)
    out_csv = "计算机探索/任务3_复杂度稳健性/robustness_results.csv"
    rows = []

    mu_candidates = [15480, 15495, 15510]   # around 1.5495
    rho_candidates = [234, 235, 236]        # around 2.35
    eta_candidates = [7, 8, 9]              # around 0.08
    seed_candidates = [12, 14, 16]
    noise_candidates = [0, 200, 500]        # ppm

    for mu in mu_candidates:
        for rho in rho_candidates:
            for eta in eta_candidates:
                for seed in seed_candidates:
                    for noise_ppm in noise_candidates:
                        phase, abs_err, steps, stop = run_once(
                            mu_num=mu, rho_num=rho, eta_num=eta,
                            seed_num=seed, noise_ppm=noise_ppm
                        )
                        rows.append([mu, rho, eta, seed, noise_ppm, phase, abs_err, steps, stop])

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mu_num", "rho_num", "eta_num", "seed_num", "noise_ppm", "phase", "abs_err", "steps", "stop_reason"])
        w.writerows(rows)

    total = len(rows)
    conv = sum(1 for r in rows if r[5] == "CONVERGED")
    cyc = sum(1 for r in rows if r[5] == "CYCLIC")
    drf = sum(1 for r in rows if r[5] == "DRIFTED")
    avg_steps = sum(r[7] for r in rows) / total

    print("=== 复杂度与稳健性基准 ===")
    print(f"total={total} CONVERGED={conv} CYCLIC={cyc} DRIFTED={drf}")
    print(f"avg_steps={avg_steps:.2f}")
    print(f"saved_csv={out_csv}")


if __name__ == "__main__":
    main()
