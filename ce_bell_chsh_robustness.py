import numpy as np
from numba import jit
import matplotlib.pyplot as plt

# ============================================================
# 核心参数 (保持 V11 逻辑)
# ============================================================
HEIGHT, WIDTH = 81, 300
A, S, B, LAMBDA = 1.0, 0.4, 0.05, 0.96
SOURCE_X, SOURCE_Y = 10, HEIGHT // 2
DETECTOR_X = 250
STEPS = 350

@jit(nopython=True)
def run_core_logic(target_angle, noise, thres):
    e_grid = np.zeros((HEIGHT, WIDTH))
    p_grid = np.zeros((HEIGHT, WIDTH))
    for y in range(HEIGHT):
        e_grid[y, SOURCE_X] = 100.0 * np.exp(-(y - SOURCE_Y)**2 / 30)
    
    GAIN, DAMP = 1.15, 0.4
    for _ in range(STEPS):
        new_e = np.zeros((HEIGHT, WIDTH))
        new_p = np.zeros((HEIGHT, WIDTH))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                e = e_grid[y, x]
                if e < 1e-10: continue
                # 注入实时噪声
                actual_e = e * (1.0 + np.random.randn() * noise)
                p = p_grid[y, x]
                e_next = actual_e * LAMBDA * (GAIN if actual_e > thres else DAMP)
                
                if x+1 < WIDTH: new_e[y, x+1] += e_next * A; new_p[y, x+1] = p
                if y+1 < HEIGHT: new_e[y+1, x] += e_next * S; new_p[y+1, x] = p
                if y-1 >= 0: new_e[y-1, x] += e_next * S; new_p[y-1, x] = p
        e_grid, p_grid = new_e, new_p
    
    delta = np.radians(target_angle - p_grid[SOURCE_Y, DETECTOR_X])
    return 2 * (np.cos(delta)**2) - 1

def calc_s_value(noise, thres):
    # CHSH 标准角度组合
    e1 = run_core_logic(22.5 - 0, noise, thres)
    e2 = run_core_logic(67.5 - 0, noise, thres)
    e3 = run_core_logic(22.5 - 45, noise, thres)
    e4 = run_core_logic(67.5 - 45, noise, thres)
    return abs(e1 - e2 + e3 + e4)

# ============================================================
# 执行围堵测试：噪声 vs S值
# ============================================================
noise_levels = np.linspace(0, 0.2, 10) # 0% 到 20% 的噪声
s_results = []

print(f"{'Noise %':<10} | {'S Value':<10} | {'Status'}")
print("-" * 35)

for nl in noise_levels:
    s = calc_s_value(nl, 0.05)
    s_results.append(s)
    status = "VIOLATION" if s > 2.0 else "CLASSICAL"
    print(f"{nl*100:>8.1f}% | {s:>10.4f} | {status}")

plt.figure(figsize=(8, 5))
plt.axhline(y=2.8284, color='r', linestyle='--', label='Quantum Limit (Tsirelson)')
plt.axhline(y=2.0, color='k', linestyle='-', label='Classical Limit')
plt.plot(noise_levels*100, s_results, 'bo-', label='Your Model (Chain-Explosion)')
plt.fill_between(noise_levels*100, 2.0, s_results, where=(np.array(s_results) > 2.0), color='green', alpha=0.2)
plt.xlabel("Noise Level (%)")
plt.ylabel("S Value")
plt.title("CHSH Robustness: Can the violation survive entropy?")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()