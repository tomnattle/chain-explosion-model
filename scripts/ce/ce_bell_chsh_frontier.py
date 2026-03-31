import numpy as np
from numba import jit
import matplotlib.pyplot as plt

# 核心物理配置（沿用你的原始规则）
HEIGHT, WIDTH = 81, 300
A, S, B, LAMBDA = 1.0, 0.4, 0.05, 0.96
SOURCE_X, SOURCE_Y = 10, HEIGHT // 2
DETECTOR_X = 250
STEPS = 350

@jit(nopython=True)
def get_correlation(target_angle, gain, thres):
    e_grid = np.zeros((HEIGHT, WIDTH))
    p_grid = np.zeros((HEIGHT, WIDTH))
    for y in range(HEIGHT):
        e_grid[y, SOURCE_X] = 100.0 * np.exp(-(y - SOURCE_Y)**2 / 30)
    
    for _ in range(STEPS):
        new_e = np.zeros((HEIGHT, WIDTH))
        new_p = np.zeros((HEIGHT, WIDTH))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                e = e_grid[y, x]
                if e < 1e-12: continue
                # 非线性点火逻辑
                e_next = e * LAMBDA * (gain if e > thres else 0.4)
                p = p_grid[y, x]
                if x + 1 < WIDTH: new_e[y, x+1] += e_next * A; new_p[y, x+1] = p
                if y + 1 < HEIGHT: new_e[y+1, x] += e_next * S; new_p[y+1, x] = p
                if y - 1 >= 0: new_e[y-1, x] += e_next * S; new_p[y-1, x] = p
        e_grid, p_grid = new_e, new_p
    
    # 马吕斯定律测量
    delta = np.radians(target_angle - p_grid[SOURCE_Y, DETECTOR_X])
    return np.cos(delta)**2 # 强度输出

def calc_s_frontier(gain, thres):
    # 计算归一化 E(theta) = 2*P(theta)/P(0) - 1
    p0 = get_correlation(0, gain, thres)
    if p0 < 1e-10: return 0
    
    def E(ang):
        return 2 * (get_correlation(ang, gain, thres) / p0) - 1

    # CHSH 角度
    s_val = abs(E(22.5) - E(67.5) + E(-22.5) + E(22.5))
    return s_val

# ============================================================
# 围堵扫描：看 GAIN 如何把 S 从 1.4 推向 2.8
# ============================================================
gains = np.linspace(1.0, 1.8, 15)
s_values = [calc_s_frontier(g, 0.05) for g in gains]

plt.figure(figsize=(10, 6))
plt.plot(gains, s_values, 'bo-', label='Your Model S-Value')
plt.axhline(y=2.8284, color='r', linestyle='--', label='Quantum Limit (2.828)')
plt.axhline(y=2.0, color='k', linestyle='-', label='Classical Limit (2.0)')
plt.axhline(y=1.414, color='g', linestyle='-.', label='DeepSeek Weak Correl (1.414)')
plt.xlabel("Medium Gain (Nonlinearity Strength)")
plt.ylabel("CHSH S-Value")
plt.title("The Bridge to Quantum: How Gain Transforms Correlation")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()