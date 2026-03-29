import numpy as np
from numba import jit

@jit(nopython=True)
def propagate_linear(energy_grid, phase_grid, polarization_grid, split_mask,
                     lambda_val, A_val, S_val, B_val):
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
            energy *= lambda_val
            
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

# 参数
HEIGHT, WIDTH = 101, 400
A, S, B = 1.0, 0.4, 0.05
LAMBDA = 0.99
SOURCE_X, SOURCE_Y = 10, HEIGHT//2
SPLIT_ANGLE = 8
SPLIT_X = WIDTH // 4
DETECTOR_X = 250
STEPS = 800

# 初始化
energy_grid = np.zeros((HEIGHT, WIDTH))
phase_grid = np.zeros((HEIGHT, WIDTH))
polarization_grid = np.zeros((HEIGHT, WIDTH))
for y in range(HEIGHT):
    dy = y - SOURCE_Y
    energy_grid[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / 50)

# 分裂掩码
split_mask = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
for y in range(HEIGHT):
    for x in range(SPLIT_X, min(SPLIT_X + 20, WIDTH)):
        target_y_up = SOURCE_Y - int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
        if 0 <= target_y_up < HEIGHT:
            split_mask[target_y_up, x] = True
        target_y_down = SOURCE_Y + int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
        if 0 <= target_y_down < HEIGHT:
            split_mask[target_y_down, x] = True

# 传播
for step in range(STEPS):
    energy_grid, phase_grid, polarization_grid = propagate_linear(
        energy_grid, phase_grid, polarization_grid, split_mask,
        LAMBDA, A, S, B
    )
    if step % 100 == 0:
        print(f"Step {step}, total energy: {np.sum(energy_grid):.6e}")

# 探测器位置
detector_y1 = SOURCE_Y - int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
detector_y2 = SOURCE_Y + int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
print(f"Detector Y1={detector_y1}, Y2={detector_y2}")

if 0 <= detector_y1 < HEIGHT and 0 <= detector_y2 < HEIGHT:
    e1 = energy_grid[detector_y1, DETECTOR_X]
    e2 = energy_grid[detector_y2, DETECTOR_X]
    print(f"e1={e1:.6e}, e2={e2:.6e}")
else:
    print("Detector out of bounds!")