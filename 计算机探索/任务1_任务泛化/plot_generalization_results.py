from matplotlib import pyplot as plt

from task_generalization import run_task


def main():
    cases = [
        ("sqrt", {"a": 3}, 17, "sqrt(3)"),
        ("reciprocal", {"b": 7}, 2, "1/7"),
        ("quadratic", {"b": -5, "c": 6}, 26, "x^2-5x+6=0"),
    ]

    labels = []
    values = []
    residual_digits = []

    for task, params, seed, label in cases:
        x, residual, _, scale = run_task(task, params, seed_num=seed)
        labels.append(label)
        values.append(x / scale)
        residual_digits.append(len(str(abs(residual))))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), dpi=140)
    axes[0].bar(labels, values, color=["#1f77b4", "#2ca02c", "#9467bd"])
    axes[0].set_title("Final Value by Task")
    axes[0].set_ylabel("value")
    axes[0].tick_params(axis="x", rotation=15)

    axes[1].bar(labels, residual_digits, color=["#ff7f0e", "#d62728", "#8c564b"])
    axes[1].set_title("Residual Magnitude (digits)")
    axes[1].set_ylabel("digits in |residual|")
    axes[1].tick_params(axis="x", rotation=15)

    fig.suptitle("Task Generalization Summary (No sqrt/Newton/Fallback)")
    plt.tight_layout(rect=[0, 0, 1, 0.94])

    out_path = "计算机探索/任务1_任务泛化/generalization_summary.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
