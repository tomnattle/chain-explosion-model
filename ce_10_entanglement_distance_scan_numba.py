import numpy as np
import matplotlib.pyplot as plt
from numba import jit
import time

# ============================================================
# 参数配置
# ============================================================

HEIGHT = 101
WIDTH = 400
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.95
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
STEPS = 800
SPLIT_X = WIDTH // 4
SPLIT_ANGLE = 15
DETECTOR_DISTANCES = [150, 250, 350]

# ============================================================
# Numba加速的传播函数（关键优化）
# ============================================================

@jit(nopython=True)
def propagate_numba(energy_grid, phase_grid, split_mask, lambda_val, A_val, S_val, B_val):
    """单步传播 - 使用numba加速"""
    h, w = energy_grid.shape
    new_energy = np.zeros((h, w))
    new_phase = np.zeros((h, w))
    
    for y in range(h):
        for x in range(w):
            energy = energy_grid[y, x]
            if energy <= 0:
                continue
            
            phase = phase_grid[y, x]
            energy *= lambda_val
            
            # 分裂区域
            if split_mask[y, x]:
                # 上方向
                if y - 1 >= 0 and x + 1 < w:
                    new_energy[y-1, x+1] += energy * A_val * 0.5
                    new_phase[y-1, x+1] = phase
                # 下方向
                if y + 1 < h and x + 1 < w:
                    new_energy[y+1, x+1] += energy * A_val * 0.5
                    new_phase[y+1, x+1] = phase
            else:
                # 正常传播
                if x + 1 < w:
                    new_energy[y, x+1] += energy * A_val
                    new_phase[y, x+1] = phase
                if x - 1 >= 0:
                    new_energy[y, x-1] += energy * B_val
                    new_phase[y, x-1] = phase
                if y - 1 >= 0:
                    new_energy[y-1, x] += energy * S_val
                    new_phase[y-1, x] = phase
                if y + 1 < h:
                    new_energy[y+1, x] += energy * S_val
                    new_phase[y+1, x] = phase
                # 对角方向
                if x-1>=0 and y-1>=0:
                    new_energy[y-1, x-1] += energy * S_val * 0.5
                    new_phase[y-1, x-1] = phase
                if x+1<w and y-1>=0:
                    new_energy[y-1, x+1] += energy * S_val * 0.5
                    new_phase[y-1, x+1] = phase
                if x-1>=0 and y+1<h:
                    new_energy[y+1, x-1] += energy * S_val * 0.5
                    new_phase[y+1, x-1] = phase
                if x+1<w and y+1<h:
                    new_energy[y+1, x+1] += energy * S_val * 0.5
                    new_phase[y+1, x+1] = phase
    
    # 归一化
    total = np.sum(new_energy)
    if total > 1e-9:
        new_energy /= total
    
    return new_energy, new_phase

# ============================================================
# 初始化函数（不需要加速）
# ============================================================

def init_grids():
    energy_grid = np.zeros((HEIGHT, WIDTH))
    phase_grid = np.zeros((HEIGHT, WIDTH))
    for y in range(HEIGHT):
        dy = y - SOURCE_Y
        energy_grid[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / 50)
    return energy_grid, phase_grid

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
# 单次模拟
# ============================================================

def run_simulation(detector_x, detector_y1, detector_y2):
    energy_grid, phase_grid = init_grids()
    split_mask = create_split_mask()
    
    energies1, energies2, phases1, phases2 = [], [], [], []
    
    for step in range(STEPS):
        energy_grid, phase_grid = propagate_numba(
            energy_grid, phase_grid, split_mask, LAMBDA, A, S, B
        )
        
        energies1.append(energy_grid[detector_y1, detector_x])
        energies2.append(energy_grid[detector_y2, detector_x])
        phases1.append(phase_grid[detector_y1, detector_x])
        phases2.append(phase_grid[detector_y2, detector_x])
        
        if (step + 1) % 200 == 0:
            print(f"    Step {step+1}/{STEPS}")
    
    avg_e1 = np.mean(energies1[-200:])
    avg_e2 = np.mean(energies2[-200:])
    avg_p1 = np.mean(phases1[-200:])
    avg_p2 = np.mean(phases2[-200:])
    phase_corr = np.cos(avg_p1 - avg_p2)
    
    return avg_e1, avg_e2, phase_corr

# ============================================================
# 主程序
# ============================================================

print("=" * 70)
print("Chain Explosion Model - Entanglement Scan (Numba Accelerated)")
print(f"Grid: {HEIGHT}x{WIDTH}, Steps: {STEPS}")
print(f"Parameters: A={A}, S={S}, B={B}, Lambda={LAMBDA}")
print("=" * 70)

results = []

for dist in DETECTOR_DISTANCES:
    print(f"\n>>> Testing distance: X={dist}")
    
    detector_y1 = SOURCE_Y - int(dist * np.tan(np.radians(SPLIT_ANGLE)))
    detector_y2 = SOURCE_Y + int(dist * np.tan(np.radians(SPLIT_ANGLE)))
    
    if detector_y1 < 0 or detector_y1 >= HEIGHT or detector_y2 < 0 or detector_y2 >= HEIGHT:
        print(f"  Skip: out of bounds (y1={detector_y1}, y2={detector_y2})")
        continue
    
    print(f"  Detector1 Y={detector_y1}, Detector2 Y={detector_y2}")
    
    start = time.time()
    e1, e2, phase_corr = run_simulation(dist, detector_y1, detector_y2)
    elapsed = time.time() - start
    
    results.append({
        'distance': dist,
        'e1': e1,
        'e2': e2,
        'phase_corr': phase_corr
    })
    
    print(f"  Detector1 energy: {e1:.6e}")
    print(f"  Detector2 energy: {e2:.6e}")
    print(f"  Phase correlation: {phase_corr:.6f}")
    print(f"  Time: {elapsed:.1f}s")

# ============================================================
# 可视化
# ============================================================

if results:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    distances = [r['distance'] for r in results]
    e1_vals = [r['e1'] for r in results]
    e2_vals = [r['e2'] for r in results]
    phase_vals = [r['phase_corr'] for r in results]
    
    axes[0].plot(distances, e1_vals, 'ro-', label='Detector 1')
    axes[0].plot(distances, e2_vals, 'bo-', label='Detector 2')
    axes[0].set_xlabel('Distance')
    axes[0].set_ylabel('Energy')
    axes[0].set_title('Energy Decay')
    axes[0].legend()
    axes[0].grid(True)
    
    axes[1].plot(distances, phase_vals, 'go-')
    axes[1].set_xlabel('Distance')
    axes[1].set_ylabel('Phase Correlation')
    axes[1].set_title('Phase Correlation')
    axes[1].set_ylim(-0.1, 1.1)
    axes[1].grid(True)
    
    if len(results) >= 2:
        decay = (results[0]['e1'] - results[-1]['e1']) / results[0]['e1']
        axes[2].bar(['Decay'], [decay])
        axes[2].set_ylabel('Energy Decay Ratio')
        axes[2].set_title(f'Decay: {decay*100:.1f}%')
    
    plt.tight_layout()
    plt.savefig('entanglement_scan_numba.png', dpi=150)
    plt.show()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Energy decay: {(results[0]['e1'] - results[-1]['e1'])/results[0]['e1']*100:.1f}%")
    print(f"Phase correlation stable: {abs(results[-1]['phase_corr'] - results[0]['phase_corr']):.6f}")