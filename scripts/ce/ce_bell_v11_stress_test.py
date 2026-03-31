import numpy as np
from numba import jit
import matplotlib.pyplot as plt

# ============================================================
# V11 物理参数：引入熵与缺陷
# ============================================================
HEIGHT, WIDTH = 81, 300
A, S, B = 1.0, 0.4, 0.05
LAMBDA = 0.96
SOURCE_X, SOURCE_Y = 10, HEIGHT // 2
DETECTOR_X = 250
STEPS = 350

# 引入缺陷地图：模拟真实介质的不完美
DEFECT_MAP = np.random.rand(HEIGHT, WIDTH) > 0.05 # 5% 的格点是死的

@jit(nopython=True)
def propagate_v11(energy_grid, pol_grid, defect_map, noise_level, thres):
    h, w = energy_grid.shape
    new_e = np.zeros((h, w))
    new_p = np.zeros((h, w))
    
    # 增益与衰减常数
    GAIN, DAMP = 1.15, 0.4
    
    for y in range(h):
        for x in range(w):
            if not defect_map[y, x]: continue # 撞到缺陷，能量终止
            
            e = energy_grid[y, x]
            if e < 1e-10: continue
            
            # 引入热噪声：模拟不确定环境下的点火
            actual_e = e * (1.0 + np.random.randn() * noise_level)
            p = pol_grid[y, x]
            
            if actual_e > thres:
                e_active = actual_e * 0.96 * GAIN
            else:
                e_active = actual_e * 0.96 * DAMP
            
            # 确定性分配
            if x + 1 < w:
                new_e[y, x+1] += e_active * 1.0
                new_p[y, x+1] = p
            if y + 1 < h:
                new_e[y+1, x] += e_active * 0.4
                new_p[y+1, x] = p
            if y - 1 >= 0:
                new_e[y-1, x] += e_active * 0.4
                new_p[y-1, x] = p
                
    return new_e, new_p

def run_v11_sim(target_angle, noise, threshold):
    e_grid = np.zeros((HEIGHT, WIDTH))
    p_grid = np.zeros((HEIGHT, WIDTH))
    for y in range(HEIGHT):
        e_grid[y, SOURCE_X] = 100.0 * np.exp(-(y - SOURCE_Y)**2 / 30)
    
    for _ in range(STEPS):
        e_grid, p_grid = propagate_v11(e_grid, p_grid, DEFECT_MAP, noise, threshold)
    
    final_e = e_grid[SOURCE_Y, DETECTOR_X]
    final_p = p_grid[SOURCE_Y, DETECTOR_X]
    delta = np.radians(target_angle - final_p)
    return final_e * (np.cos(delta)**2)

# ============================================================
# 执行扫描：对比 纯净 vs 噪声 vs 极端环境
# ============================================================
angles = np.linspace(0, 90, 13)
noise_scenarios = [0.0, 0.05, 0.15] # 0%, 5%, 15% 的环境噪声

plt.figure(figsize=(10, 6))
for ns in noise_scenarios:
    print(f"Testing Noise Level: {ns*100}%...")
    curve = [run_v11_sim(ang, ns, 0.05) for ang in angles]
    curve = np.array(curve)
    if np.max(curve) > 0: curve /= np.max(curve)
    plt.plot(angles, curve, 'o-', label=f'Noise={ns*100}%')

plt.plot(angles, np.cos(np.radians(angles))**2, 'r--', label='Quantum (cos²θ)', alpha=0.7)
plt.title("V11 Stress Test: Robustness against Entropy & Defects")
plt.xlabel("Angle difference")
plt.ylabel("Correlation")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()