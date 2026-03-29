import numpy as np
import matplotlib.pyplot as plt

SIZE = 300
grid = np.zeros(SIZE)
x0, sigma = 40, 8
x = np.arange(SIZE)
grid = np.exp(-(x - x0)**2 / (2 * sigma**2))
grid /= np.sum(grid)

barrier_low, barrier_high = 120, 160
barrier_height = 0.3
barrier_mask = np.zeros(SIZE, dtype=bool)
barrier_mask[barrier_low:barrier_high] = True

STEPS = 400
SPREAD = 0.1
DRIFT = 0.6
history = []

for step in range(STEPS):
    new = grid.copy()
    laplacian = np.roll(grid, 1) + np.roll(grid, -1) - 2 * grid
    new += SPREAD * laplacian
    shift = np.roll(grid, 1)
    new = DRIFT * shift + (1 - DRIFT) * new
    new[0] = grid[0] * (1 - DRIFT)
    new[barrier_mask] *= (1 - barrier_height * 0.3)
    new /= np.sum(new)
    grid = new
    history.append(grid.copy())

final = history[-1]
transmitted = np.sum(final[barrier_high:])
reflected = np.sum(final[:barrier_low])
T = transmitted / (transmitted + reflected)

plt.figure(figsize=(14,6), dpi=120)
plt.plot(history[0], label="Initial")
plt.plot(history[150], label="Step 150")
plt.plot(history[-1], label=f"Final T={T:.3f}")
plt.axvspan(barrier_low, barrier_high, alpha=0.2, color='red')
plt.title("Local Causal Tunneling")
plt.legend()
plt.savefig("tunnel.png")
plt.show()