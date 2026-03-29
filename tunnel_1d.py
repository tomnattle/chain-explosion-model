import numpy as np
import matplotlib.pyplot as plt

# ==============================================
# 任务 1：量子隧穿 —— 局域扩散机制（无概率、无波函数）
# ==============================================

SIZE = 200
grid = np.zeros(SIZE)
grid[20:30] = 1.0   # 粒子源

# 势垒（传统物理认为无法穿过）
barrier_low = 80
barrier_high = 120
barrier = np.zeros(SIZE)
barrier[barrier_low:barrier_high] = 0.1  # 低透过区域

STEPS = 150
DRIFT = 1
SPREAD = 0.25

history = []

for step in range(STEPS):
    new = grid.copy()
    for i in range(1, SIZE-1):
        # 局域扩散（朴素物理）
        flow = (grid[i-1] + grid[i+1] - 2*grid[i]) * SPREAD
        new[i] += flow

        # 向右漂移
        if i < SIZE-2:
            move = grid[i] * 0.01 * DRIFT * barrier[i]
            new[i] -= move
            new[i+1] += move

    grid = new
    history.append(grid.copy())

# ==============================================
# 绘图：看到能量穿透壁垒
# ==============================================
plt.figure(figsize=(12,5))
plt.plot(history[0], label="initial")
plt.plot(history[40], label="step 40")
plt.plot(history[120], label="step 120")
plt.axvspan(barrier_low, barrier_high, alpha=0.2, color="red", label="barrier")
plt.title("Local Causal Tunneling (No Probability, No Quantum Magic)")
plt.legend()
plt.show()