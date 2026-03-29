import numpy as np
from numba import jit
import matplotlib.pyplot as plt

# ============================================================
# 核心物理配置
# ============================================================
HEIGHT = 81
WIDTH = 300
A, S, B = 1.0, 0.4, 0.05    # 前向、侧向、后向传播系数
LAMBDA = 0.96               # 基础传播损耗
SOURCE_X, SOURCE_Y = 10, HEIGHT // 2
DETECTOR_X = 250            # 检测器位置
STEPS = 350                 # 确保波前能到达检测器

# ============================================================
# 初始化函数
# ============================================================
def init_experiment():
    energy_grid = np.zeros((HEIGHT, WIDTH))
    # 初始偏振设为 0° (A端的参考基准)
    pol_grid = np.zeros((HEIGHT, WIDTH)) 
    # 模拟一个具有高斯分布的初始波源
    for y in range(HEIGHT):
        dy = y - SOURCE_Y
        energy_grid[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / 30)
    return energy_grid, pol_grid

# ============================================================
# 传播引擎 (基于 DeepSeek 建议的局部非线性逻辑)
# ============================================================
@jit(nopython=True)
def propagate_v10(energy_grid, pol_grid, lam, a_v, s_v, b_v, thres, gain, damp):
    h, w = energy_grid.shape
    new_e = np.zeros((h, w))
    new_p = np.zeros((h, w))
    
    for y in range(h):
        for x in range(w):
            e = energy_grid[y, x]
            if e < 1e-10: continue
            
            p = pol_grid[y, x]
            
            # --- 局部非线性判断 ---
            # 只有能量超过阈值，介质才会“点火”产生增益
            if e > thres:
                e_active = e * lam * gain
            else:
                e_active = e * lam * damp
            
            # 能量与偏振的协同传播
            # 前向
            if x + 1 < w:
                new_e[y, x+1] += e_active * a_v
                new_p[y, x+1] = p
            # 侧向
            if y + 1 < h:
                new_e[y+1, x] += e_active * s_v
                new_p[y+1, x] = p
            if y - 1 >= 0:
                new_e[y-1, x] += e_active * s_v
                new_p[y-1, x] = p
            # 后向回火 (产生内部关联的关键)
            if x - 1 >= 0:
                new_e[y, x-1] += e_active * b_v
                new_p[y, x-1] = p
                
    return new_e, new_p

# ============================================================
# 模拟与测量
# ============================================================
def run_sim(target_angle, threshold):
    e_grid, p_grid = init_experiment()
    
    # 设定激活和熄灭的倍率
    GAIN, DAMP = 1.15, 0.4
    
    for _ in range(STEPS):
        e_grid, p_grid = propagate_v10(e_grid, p_grid, LAMBDA, A, S, B, threshold, GAIN, DAMP)
    
    # 在检测器位置读取能量和偏振
    final_e = e_grid[SOURCE_Y, DETECTOR_X]
    final_p = p_grid[SOURCE_Y, DETECTOR_X]
    
    # 偏振片测量：模拟 B 端测量角度与传播过来的偏振方向的相互作用
    delta = np.radians(target_angle - final_p)
    observed_intensity = final_e * (np.cos(delta)**2)
    return observed_intensity

# ============================================================
# 执行扫描与绘图
# ============================================================
angles = np.linspace(0, 90, 13)
thresholds = [0.005, 0.05, 0.2] # 扫描三个不同等级的“介质敏感度”

plt.figure(figsize=(10, 6))

for th in thresholds:
    print(f"Scanning with Threshold: {th}...")
    curve = []
    for ang in angles:
        val = run_sim(ang, th)
        curve.append(val)
    
    curve = np.array(curve)
    if np.max(curve) > 0:
        curve /= np.max(curve) # 归一化对比
        
    plt.plot(angles, curve, 'o-', label=f'Threshold={th}')

# 理论参考线
plt.plot(angles, np.cos(np.radians(angles))**2, 'r--', label='Quantum (cos²θ)', alpha=0.5)

plt.xlabel('Angle Difference (degrees)')
plt.ylabel('Normalized Correlation')
plt.title('V10: Emergent Correlation via Local Nonlinearity')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()