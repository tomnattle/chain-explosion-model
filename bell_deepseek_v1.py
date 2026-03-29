import numpy as np
from numba import jit
import matplotlib.pyplot as plt

# ============================================================
# 参数配置
# ============================================================

HEIGHT = 101
WIDTH = 400
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.98         # 衰减稍慢
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
STEPS = 600
SPLIT_X = WIDTH // 4
SPLIT_ANGLE = 8
DETECTOR_X = 250

# 非线性阈值参数（带饱和）
THRESHOLD = 0.01
GAIN = 1.05
DAMP = 0.8
MAX_ENERGY = 1.0      # 能量上限（饱和）

# ============================================================
# 初始化
# ============================================================

def init_grids():
    energy_grid = np.zeros((HEIGHT, WIDTH))
    phase_grid = np.zeros((HEIGHT, WIDTH))
    polarization_grid = np.zeros((HEIGHT, WIDTH))
    
    for y in range(HEIGHT):
        dy = y - SOURCE_Y
        energy_grid[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / 50)
        polarization_grid[y, SOURCE_X] = 0.0
    
    return energy_grid, phase_grid, polarization_grid

def create_split_mask():
    split_mask = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    for y in range(HEIGHT):
        for x in range(SPLIT_X, min(SPLIT_X + 20, WIDTH)):
            target_y_up = SOURCE_Y - int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
            if 0 <= target_y_up < HEIGHT:
                split_mask[target_y_up, x] = True
            target_y_down = SOURCE_Y + int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
            if 0 <= target_y_down < HEIGHT:
                split_mask[target_y_down, x] = True
    return split_mask

# ============================================================
# 传播函数（带能量饱和）
# ============================================================

@jit(nopython=True)
def propagate_numba_saturated(energy_grid, phase_grid, polarization_grid, split_mask,
                               lambda_val, A_val, S_val, B_val,
                               threshold, gain, damp, max_energy):
    h, w = energy_grid.shape
    new_energy = np.zeros((h, w))
    new_phase = np.zeros((h, w))
    new_polarization = np.zeros((h, w))
    
    for y in range(h):
        for x in range(w):
            energy = energy_grid[y, x]
            if energy <= 1e-12:
                continue
            
            phase = phase_grid[y, x]
            pol = polarization_grid[y, x]
            
            # 非线性阈值 + 饱和
            if energy > threshold:
                energy = energy * lambda_val * gain
            else:
                energy = energy * lambda_val * damp
            
            # 饱和钳制
            if energy > max_energy:
                energy = max_energy
            
            # 分裂区域处理
            if split_mask[y, x]:
                if y - 1 >= 0 and x + 1 < w:
                    new_energy[y-1, x+1] += energy * A_val * 0.5
                    new_phase[y-1, x+1] = phase
                    new_polarization[y-1, x+1] = pol
                if y + 1 < h and x + 1 < w:
                    new_energy[y+1, x+1] += energy * A_val * 0.5
                    new_phase[y+1, x+1] = phase
                    new_polarization[y+1, x+1] = pol
            else:
                if x + 1 < w:
                    new_energy[y, x+1] += energy * A_val
                    new_phase[y, x+1] = phase
                    new_polarization[y, x+1] = pol
                if x - 1 >= 0:
                    new_energy[y, x-1] += energy * B_val
                    new_phase[y, x-1] = phase
                    new_polarization[y, x-1] = pol
                if y - 1 >= 0:
                    new_energy[y-1, x] += energy * S_val
                    new_phase[y-1, x] = phase
                    new_polarization[y-1, x] = pol
                if y + 1 < h:
                    new_energy[y+1, x] += energy * S_val
                    new_phase[y+1, x] = phase
                    new_polarization[y+1, x] = pol
                # 对角方向
                if x-1>=0 and y-1>=0:
                    new_energy[y-1, x-1] += energy * S_val * 0.5
                    new_phase[y-1, x-1] = phase
                    new_polarization[y-1, x-1] = pol
                if x+1<w and y-1>=0:
                    new_energy[y-1, x+1] += energy * S_val * 0.5
                    new_phase[y-1, x+1] = phase
                    new_polarization[y-1, x+1] = pol
                if x-1>=0 and y+1<h:
                    new_energy[y+1, x-1] += energy * S_val * 0.5
                    new_phase[y+1, x-1] = phase
                    new_polarization[y+1, x-1] = pol
                if x+1<w and y+1<h:
                    new_energy[y+1, x+1] += energy * S_val * 0.5
                    new_phase[y+1, x+1] = phase
                    new_polarization[y+1, x+1] = pol
    
    return new_energy, new_phase, new_polarization

# ============================================================
# 测量函数
# ============================================================

def measure_with_polarizer(energy, polarization, polarizer_angle):
    delta = abs(polarization - polarizer_angle)
    delta = min(delta, 180 - delta)
    transmission = np.cos(np.radians(delta))**2
    return energy * transmission

# ============================================================
# 单次模拟
# ============================================================

def run_saturated_simulation(angle1, angle2):
    energy_grid, phase_grid, polarization_grid = init_grids()
    split_mask = create_split_mask()
    
    detector_y1 = SOURCE_Y - int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
    detector_y2 = SOURCE_Y + int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
    
    if detector_y1 < 0 or detector_y1 >= HEIGHT or detector_y2 < 0 or detector_y2 >= HEIGHT:
        return 0.0
    
    for step in range(STEPS):
        energy_grid, phase_grid, polarization_grid = propagate_numba_saturated(
            energy_grid, phase_grid, polarization_grid, split_mask,
            LAMBDA, A, S, B, THRESHOLD, GAIN, DAMP, MAX_ENERGY
        )
        if step % 100 == 0:
            total = np.sum(energy_grid)
            print(f"Step {step}, total energy: {total:.6e}")
    
    e1 = energy_grid[detector_y1, DETECTOR_X]
    e2 = energy_grid[detector_y2, DETECTOR_X]
    p1 = polarization_grid[detector_y1, DETECTOR_X]
    p2 = polarization_grid[detector_y2, DETECTOR_X]
    
    m1 = measure_with_polarizer(e1, p1, angle1)
    m2 = measure_with_polarizer(e2, p2, angle2)
    
    return m1 * m2

# ============================================================
# 主程序
# ============================================================

angles = np.linspace(0, 90, 10)
results = []

print("Running Bell test with energy saturation...")
for ang in angles:
    corr = run_saturated_simulation(0, ang)
    results.append(corr)
    print(f"Angle {ang:.1f}° -> Correlation: {corr:.6e}")

# 归一化
results = np.array(results)
if results[0] > 0:
    results = results / results[0]

# 量子力学曲线
qm_curve = np.cos(np.radians(angles))**2

plt.figure(figsize=(8, 6))
plt.plot(angles, results, 'bo-', label='Your Model (Saturated)')
plt.plot(angles, qm_curve, 'r--', label='Quantum Mechanics (cos²θ)')
plt.xlabel('Polarizer Angle Difference (degrees)')
plt.ylabel('Normalized Correlation')
plt.title('Bell Test: Nonlinear Saturated Model')
plt.legend()
plt.grid(True)
plt.savefig('bell_test_saturated.png', dpi=150)
plt.show()