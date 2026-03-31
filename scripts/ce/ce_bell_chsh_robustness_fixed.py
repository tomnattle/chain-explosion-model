import numpy as np
from numba import jit

# ============================================================
# 参数配置（完全来自你的模型）
# ============================================================

HEIGHT = 81
WIDTH = 300
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.96
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
STEPS = 350
DETECTOR_X = 250
SPLIT_X = WIDTH // 4
SPLIT_ANGLE = 8          # 分裂角度

# 非线性参数
THRESHOLD = 0.05
GAIN = 1.15
DAMP = 0.4
MAX_ENERGY = 1.0

# 噪声参数（高斯噪声的标准差，相对于能量最大值）
NOISE_LEVELS = [0.0, 0.022, 0.044, 0.067, 0.089, 0.111, 0.133, 0.156, 0.178, 0.20]

# ============================================================
# 初始化
# ============================================================

def init_grids():
    energy = np.zeros((HEIGHT, WIDTH))
    phase = np.zeros((HEIGHT, WIDTH))
    polarization = np.zeros((HEIGHT, WIDTH))
    for y in range(HEIGHT):
        dy = y - SOURCE_Y
        energy[y, SOURCE_X] = 100.0 * np.exp(-dy**2 / 30)
        polarization[y, SOURCE_X] = 0.0   # 初始偏振方向为0°
    return energy, phase, polarization

def create_split_mask():
    mask = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    for y in range(HEIGHT):
        for x in range(SPLIT_X, min(SPLIT_X + 20, WIDTH)):
            y_up = SOURCE_Y - int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
            y_down = SOURCE_Y + int((x - SPLIT_X) * np.tan(np.radians(SPLIT_ANGLE)))
            if 0 <= y_up < HEIGHT:
                mask[y_up, x] = True
            if 0 <= y_down < HEIGHT:
                mask[y_down, x] = True
    return mask

# ============================================================
# 传播函数（你的规则 + 可选的噪声）
# ============================================================

@jit(nopython=True)
def propagate(energy, phase, polarization, split_mask,
              lam, a_val, s_val, b_val,
              thresh, gain, damp, max_e, noise_std):
    h, w = energy.shape
    new_e = np.zeros((h, w))
    new_phase = np.zeros((h, w))
    new_pol = np.zeros((h, w))
    
    for y in range(h):
        for x in range(w):
            e = energy[y, x]
            if e < 1e-12:
                continue
            p = phase[y, x]
            pol = polarization[y, x]
            
            # 非线性阈值
            if e > thresh:
                e = e * lam * gain
            else:
                e = e * lam * damp
            
            if e > max_e:
                e = max_e
            
            # 加入噪声（在传播前）
            if noise_std > 0:
                # 简单的高斯噪声，不影响偏振方向
                noise = np.random.normal(0, noise_std)
                e = max(0.0, e + noise)
            
            # 分裂区域
            if split_mask[y, x]:
                if y - 1 >= 0 and x + 1 < w:
                    new_e[y-1, x+1] += e * a_val * 0.5
                    new_phase[y-1, x+1] = p
                    new_pol[y-1, x+1] = pol
                if y + 1 < h and x + 1 < w:
                    new_e[y+1, x+1] += e * a_val * 0.5
                    new_phase[y+1, x+1] = p
                    new_pol[y+1, x+1] = pol
            else:
                # 正常传播
                if x + 1 < w:
                    new_e[y, x+1] += e * a_val
                    new_phase[y, x+1] = p
                    new_pol[y, x+1] = pol
                if x - 1 >= 0:
                    new_e[y, x-1] += e * b_val
                    new_phase[y, x-1] = p
                    new_pol[y, x-1] = pol
                if y - 1 >= 0:
                    new_e[y-1, x] += e * s_val
                    new_phase[y-1, x] = p
                    new_pol[y-1, x] = pol
                if y + 1 < h:
                    new_e[y+1, x] += e * s_val
                    new_phase[y+1, x] = p
                    new_pol[y+1, x] = pol
                # 对角方向
                if x-1>=0 and y-1>=0:
                    new_e[y-1, x-1] += e * s_val * 0.5
                    new_phase[y-1, x-1] = p
                    new_pol[y-1, x-1] = pol
                if x+1<w and y-1>=0:
                    new_e[y-1, x+1] += e * s_val * 0.5
                    new_phase[y-1, x+1] = p
                    new_pol[y-1, x+1] = pol
                if x-1>=0 and y+1<h:
                    new_e[y+1, x-1] += e * s_val * 0.5
                    new_phase[y+1, x-1] = p
                    new_pol[y+1, x-1] = pol
                if x+1<w and y+1<h:
                    new_e[y+1, x+1] += e * s_val * 0.5
                    new_phase[y+1, x+1] = p
                    new_pol[y+1, x+1] = pol
    
    return new_e, new_phase, new_pol

# ============================================================
# 测量函数（马吕斯定律，无硬编码关联）
# ============================================================

def measure(energy, polarization, polarizer_angle):
    delta = abs(polarization - polarizer_angle)
    delta = min(delta, 180 - delta)
    transmission = np.cos(np.radians(delta)) ** 2
    return energy * transmission

# ============================================================
# 单次实验（返回符合计数）
# ============================================================

def run_experiment(angle_a, angle_b, noise_std):
    e_grid, p_grid, pol_grid = init_grids()
    split_mask = create_split_mask()
    
    det_y1 = SOURCE_Y - int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
    det_y2 = SOURCE_Y + int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
    
    if det_y1 < 0 or det_y1 >= HEIGHT or det_y2 < 0 or det_y2 >= HEIGHT:
        return 0.0
    
    for _ in range(STEPS):
        e_grid, p_grid, pol_grid = propagate(
            e_grid, p_grid, pol_grid, split_mask,
            LAMBDA, A, S, B, THRESHOLD, GAIN, DAMP, MAX_ENERGY, noise_std
        )
    
    e1 = e_grid[det_y1, DETECTOR_X]
    e2 = e_grid[det_y2, DETECTOR_X]
    pol1 = pol_grid[det_y1, DETECTOR_X]
    pol2 = pol_grid[det_y2, DETECTOR_X]
    
    m1 = measure(e1, pol1, angle_a)
    m2 = measure(e2, pol2, angle_b)
    
    return m1 * m2

# ============================================================
# 计算 CHSH S 值（带统计平均）
# ============================================================

def compute_chsh(noise_std, num_samples=10):
    """计算给定噪声水平下的平均 S 值（多次采样以平滑噪声）"""
    angles = {
        'a': 0,
        'a_prime': 45,
        'b': 22.5,
        'b_prime': 67.5
    }
    
    # 存储多次实验的关联值
    C_ab_list = []
    C_ab_prime_list = []
    C_a_prime_b_list = []
    C_a_prime_b_prime_list = []
    
    for _ in range(num_samples):
        C_ab = run_experiment(angles['a'], angles['b'], noise_std)
        C_ab_prime = run_experiment(angles['a'], angles['b_prime'], noise_std)
        C_a_prime_b = run_experiment(angles['a_prime'], angles['b'], noise_std)
        C_a_prime_b_prime = run_experiment(angles['a_prime'], angles['b_prime'], noise_std)
        
        if C_ab > 0:  # 只收集有效实验
            C_ab_list.append(C_ab)
            C_ab_prime_list.append(C_ab_prime)
            C_a_prime_b_list.append(C_a_prime_b)
            C_a_prime_b_prime_list.append(C_a_prime_b_prime)
    
    if not C_ab_list:
        return 0.0
    
    # 平均
    C_ab = np.mean(C_ab_list)
    C_ab_prime = np.mean(C_ab_prime_list)
    C_a_prime_b = np.mean(C_a_prime_b_list)
    C_a_prime_b_prime = np.mean(C_a_prime_b_prime_list)
    
    # 归一化
    norm = C_ab
    if norm <= 0:
        return 0.0
    
    E_ab = C_ab / norm
    E_ab_prime = C_ab_prime / norm
    E_a_prime_b = C_a_prime_b / norm
    E_a_prime_b_prime = C_a_prime_b_prime / norm
    
    S = abs(E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime)
    return S

# ============================================================
# 主程序：扫描噪声
# ============================================================

print("Noise %    | S Value    | Status")
print("-----------------------------------")

for noise in NOISE_LEVELS:
    s_val = compute_chsh(noise, num_samples=5)
    status = "VIOLATION" if s_val > 2.0 else "LOCAL"
    print(f"{noise*100:6.1f}% | {s_val:10.4f} | {status}")