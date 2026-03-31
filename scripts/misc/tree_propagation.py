"""
tree_double_slit_auto_screen.py

自动检测能量最远传播位置，显示屏幕能量分布。
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import deque

SQRT2 = 2 ** 0.5

def bfs_tree_propagation(
    source_y, source_x, initial_energy,
    A, S, B, lam, threshold,
    height, width,
    barrier_x, slits,
    max_steps=None,
    verbose=True
):
    # 挡板构建
    barrier = np.zeros((height, width), dtype=bool)
    barrier[:, barrier_x] = True
    for yc, w in slits:
        s = yc - w // 2
        barrier[s:s + w, barrier_x] = False

    energy = np.zeros((height, width), dtype=np.float64)
    fired = np.zeros((height, width), dtype=bool)
    generation = np.zeros((height, width), dtype=np.int32)

    if barrier[source_y, source_x]:
        raise ValueError("源点被挡板阻挡")

    energy[source_y, source_x] = initial_energy
    fired[source_y, source_x] = True
    generation[source_y, source_x] = 0
    queue = deque([(source_y, source_x)])

    lam_diag = lam ** SQRT2
    directions = [
        ( 0,  1, A,       lam),
        ( 0, -1, B,       lam),
        (-1,  0, S,       lam),
        ( 1,  0, S,       lam),
        (-1,  1, S * 0.5, lam_diag),
        (-1, -1, S * 0.5, lam_diag),
        ( 1,  1, S * 0.5, lam_diag),
        ( 1, -1, S * 0.5, lam_diag),
    ]

    steps = 0
    max_x_reached = source_x
    if verbose:
        print(f"初始总能量: {initial_energy:.6f}")
        print(f"衰减系数 lam={lam}  对角线衰减={lam_diag:.6f}")

    while queue and (max_steps is None or steps < max_steps):
        y, x = queue.popleft()
        e = energy[y, x]
        if e <= threshold:
            continue

        # 更新最大 x 坐标
        if x > max_x_reached:
            max_x_reached = x

        valid_dirs = []
        total_weight = 0.0
        for dy, dx, wgt, decay in directions:
            ny, nx = y + dy, x + dx
            if not (0 <= ny < height and 0 <= nx < width):
                continue
            if barrier[ny, nx]:
                continue
            if not fired[ny, nx]:
                valid_dirs.append((ny, nx, wgt, decay))
                total_weight += wgt

        if total_weight <= 0:
            continue

        for ny, nx, wgt, decay in valid_dirs:
            add = e * decay * (wgt / total_weight)
            if add > 0:
                energy[ny, nx] += add
                if not fired[ny, nx] and energy[ny, nx] > threshold:
                    fired[ny, nx] = True
                    generation[ny, nx] = generation[y, x] + 1
                    queue.append((ny, nx))

        energy[y, x] = 0.0
        steps += 1
        if verbose and steps % 500 == 0:
            total_e = np.sum(energy)
            print(f"  步数 {steps}: 总能量 = {total_e:.6f}, 队列长度 = {len(queue)}")

    total_energy_final = np.sum(energy)
    if verbose:
        print(f"\n传播完成，共 {steps} 步")
        print(f"最终总能量: {total_energy_final:.6f} / 初始 {initial_energy:.6f}")
        print(f"能量剩余比例: {total_energy_final / initial_energy * 100:.2f}%")
        print(f"能量最远到达 x 坐标: {max_x_reached}")

    return energy, generation, steps, barrier, max_x_reached


def main():
    # 网格与源点
    HEIGHT = 201
    WIDTH = 400
    SOURCE_X = 10
    SOURCE_Y = HEIGHT // 2
    INIT_ENERGY = 100.0

    # 传播参数
    A = 1.2
    S = 0.2
    B = 0.05
    LAM = 0.995
    THRESHOLD = 1e-7

    # 双缝参数
    BARRIER_X = 150
    SLIT_WIDTH = 8
    SLIT1_Y = HEIGHT // 2 - 30
    SLIT2_Y = HEIGHT // 2 + 30
    slits = [(SLIT1_Y, SLIT_WIDTH), (SLIT2_Y, SLIT_WIDTH)]

    print("=== 树状传播（能量包络）===")
    energy, generation, steps, barrier, max_x = bfs_tree_propagation(
        SOURCE_Y, SOURCE_X, INIT_ENERGY,
        A, S, B, LAM, THRESHOLD,
        HEIGHT, WIDTH,
        BARRIER_X, slits,
        max_steps=None,
        verbose=True,
    )

    total_energy = np.sum(energy)
    active_cells = np.sum(energy > 0)
    max_gen = np.max(generation)
    print(f"非零能量格子数: {active_cells}")
    print(f"最大传播代数: {max_gen}")

    # 自动设置屏幕位置：取最远 x 坐标附近，留一点边界
    screen_x = max_x - 10  # 留出一点余量，确保屏幕上有能量
    if screen_x < SOURCE_X + 5:
        screen_x = max_x
    screen = energy[:, screen_x]

    print(f"\n屏幕位置 x={screen_x}（最远 x={max_x}）")
    print(f"屏幕能量统计:")
    print(f"  总能量: {np.sum(screen):.6e}")
    print(f"  最大值: {np.max(screen):.6e}")
    print(f"  非零点数: {np.sum(screen > 0)}")
    nonzero = screen[screen > 0]
    if len(nonzero) > 0:
        print("  前10个非零值: ", nonzero[:10])

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 能量场
    ax1 = axes[0]
    eps = 1e-12
    im1 = ax1.imshow(
        energy + eps,
        cmap="hot",
        norm=plt.matplotlib.colors.LogNorm(vmin=eps, vmax=np.max(energy) if np.max(energy) > 0 else 1),
        aspect="auto",
        origin="upper",
    )
    ax1.axvline(x=BARRIER_X, color='cyan', linestyle='--', linewidth=1, label='barrier')
    ax1.axhline(y=SLIT1_Y, color='lime', linestyle=':', linewidth=1)
    ax1.axhline(y=SLIT2_Y, color='lime', linestyle=':', linewidth=1)
    ax1.axvline(x=screen_x, color='magenta', linestyle='-', linewidth=1, label='screen')
    fig.colorbar(im1, ax=ax1, label="Energy (LogNorm)")
    ax1.set_title(f"Tree propagation (λ={LAM})\nSteps={steps}, total energy={total_energy:.2f}")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.legend()

    # 屏幕能量
    ax2 = axes[1]
    ax2.plot(screen, 'b-', linewidth=1)
    ax2.set_xlabel("y")
    ax2.set_ylabel("Energy")
    ax2.set_title(f"Screen at x={screen_x}\nEnergy from two slits (no interference)")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("tree_double_slit_auto_screen.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()