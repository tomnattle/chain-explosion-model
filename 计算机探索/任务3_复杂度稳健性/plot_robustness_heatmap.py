import csv
from collections import defaultdict

from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap


def main():
    in_csv = "计算机探索/任务3_复杂度稳健性/robustness_results.csv"
    out_png = "计算机探索/任务3_复杂度稳健性/robustness_heatmap.png"

    rows = []
    with open(in_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    noise_values = sorted({int(r["noise_ppm"]) for r in rows})
    eta_values = sorted({int(r["eta_num"]) for r in rows})

    phase_score = {"CONVERGED": 3, "CYCLIC": 2, "DRIFTED": 1}
    agg = defaultdict(list)
    for r in rows:
        key = (int(r["eta_num"]), int(r["noise_ppm"]))
        agg[key].append(phase_score[r["phase"]])

    grid = []
    for eta in eta_values:
        line = []
        for noise in noise_values:
            vals = agg[(eta, noise)]
            avg = sum(vals) / len(vals) if vals else 0
            # map to 0..2 for color bins
            if avg >= 2.5:
                line.append(2)  # mostly converged
            elif avg >= 1.5:
                line.append(1)  # mixed/cyclic
            else:
                line.append(0)  # mostly drifted
        grid.append(line)

    cmap = ListedColormap(["#d62728", "#ff7f0e", "#2ca02c"])
    plt.figure(figsize=(6, 4), dpi=150)
    plt.imshow(
        grid,
        cmap=cmap,
        origin="lower",
        aspect="auto",
        extent=[noise_values[0], noise_values[-1], eta_values[0], eta_values[-1]],
        vmin=0,
        vmax=2,
    )
    plt.title("Robustness Heatmap (eta vs noise)")
    plt.xlabel("noise_ppm")
    plt.ylabel("eta_num")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    print("Saved:", out_png)


if __name__ == "__main__":
    main()
