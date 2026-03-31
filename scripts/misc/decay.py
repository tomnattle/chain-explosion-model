import numpy as np
import matplotlib.pyplot as plt

SIZE = 800
grid = np.zeros(SIZE)
x0, sigma = 40,8
x = np.arange(SIZE)
grid = np.exp(-(x-x0)**2/(2*sigma**2))
grid /= np.sum(grid)

barrier_low, barrier_high = 120,160
screen_positions = [300,400,500,600,700]
visibilities = []

SPREAD = 0.12
DRIFT = 0.65
STEPS_PER_DIST = 150

for pos in screen_positions:
    g = grid.copy()
    steps = (pos - 40) * STEPS_PER_DIST // 100
    for _ in range(steps):
        new = g.copy()
        lap = np.roll(g,1)+np.roll(g,-1)-2*g
        new += SPREAD * lap
        shift = np.roll(g,1)
        new = DRIFT * shift + (1-DRIFT)*new
        new[0] = g[0]*(1-DRIFT)
        new /= np.sum(new)
        g = new
    vals = g[barrier_high:]
    vis = (vals.max() - vals.min()) / (vals.max() + vals.min() + 1e-10)
    visibilities.append(vis)

plt.figure(figsize=(10,6), dpi=120)
plt.plot([x-120 for x in screen_positions], visibilities, 'o-', linewidth=2)
plt.title("Interference Visibility Decay (Original Prediction)")
plt.xlabel("Distance from Slit")
plt.ylabel("Visibility V")
plt.grid(True)
plt.savefig("decay.png")
plt.show()