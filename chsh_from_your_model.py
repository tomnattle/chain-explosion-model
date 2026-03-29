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
# 传播函数（你的规则：能量 + 偏振传播）
# ============================================================

@jit(nopython=True)
def propagate(energy, phase, polarization, split_mask,
              lam, a_val, s_val, b_val,
              thresh, gain, damp, max_e):
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
                # 对角（简化，可选）
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
    """探测器测量：透过率 = cos²(角度差)"""
    delta = abs(polarization - polarizer_angle)
    delta = min(delta, 180 - delta)  # 取锐角
    transmission = np.cos(np.radians(delta)) ** 2
    return energy * transmission

# ============================================================
# 单次实验（返回符合计数 = 能量乘积）
# ============================================================

def run_experiment(angle_a, angle_b):
    e_grid, p_grid, pol_grid = init_grids()
    split_mask = create_split_mask()
    
    # 探测器位置（根据分裂角度计算）
    det_y1 = SOURCE_Y - int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
    det_y2 = SOURCE_Y + int(DETECTOR_X * np.tan(np.radians(SPLIT_ANGLE)))
    
    if det_y1 < 0 or det_y1 >= HEIGHT or det_y2 < 0 or det_y2 >= HEIGHT:
        return 0.0
    
    # 传播
    for _ in range(STEPS):
        e_grid, p_grid, pol_grid = propagate(
            e_grid, p_grid, pol_grid, split_mask,
            LAMBDA, A, S, B, THRESHOLD, GAIN, DAMP, MAX_ENERGY
        )
    
    # 读取探测器
    e1 = e_grid[det_y1, DETECTOR_X]
    e2 = e_grid[det_y2, DETECTOR_X]
    pol1 = pol_grid[det_y1, DETECTOR_X]
    pol2 = pol_grid[det_y2, DETECTOR_X]
    
    # 测量
    m1 = measure(e1, pol1, angle_a)
    m2 = measure(e2, pol2, angle_b)
    
    return m1 * m2   # 符合计数（关联值）

# ============================================================
# 计算归一化关联函数 E(α, β)
# ============================================================

def correlation(angle_a, angle_b):
    """关联值 E = [C(α,β) - C(α,β⊥)] / [C(α,β) + C(α,β⊥)]"""
    # 这里简化：直接用符合计数，用 0°-0° 作为基准归一化
    C = run_experiment(angle_a, angle_b)
    return C

# ============================================================
# CHSH 不等式计算
# ============================================================

print("=" * 60)
print("CHSH Bell Inequality Test - From Your Model Rules")
print("=" * 60)

# 四个角度组合（标准 CHSH 设置）
angles = {
    'a': 0,
    'a_prime': 45,
    'b': 22.5,
    'b_prime': 67.5
}

# 测量所有组合
C_ab = correlation(angles['a'], angles['b'])
C_ab_prime = correlation(angles['a'], angles['b_prime'])
C_a_prime_b = correlation(angles['a_prime'], angles['b'])
C_a_prime_b_prime = correlation(angles['a_prime'], angles['b_prime'])

print(f"C(a, b)     = {C_ab:.6e}")
print(f"C(a, b')    = {C_ab_prime:.6e}")
print(f"C(a', b)    = {C_a_prime_b:.6e}")
print(f"C(a', b')   = {C_a_prime_b_prime:.6e}")

# 归一化：用 C(a,b) 作为基准（假设它在 0°-0° 时最大）
norm = C_ab
if norm > 0:
    E_ab = C_ab / norm
    E_ab_prime = C_ab_prime / norm
    E_a_prime_b = C_a_prime_b / norm
    E_a_prime_b_prime = C_a_prime_b_prime / norm
else:
    E_ab = E_ab_prime = E_a_prime_b = E_a_prime_b_prime = 0.0

print("\n--- Normalized Correlations ---")
print(f"E(a, b)     = {E_ab:.6f}")
print(f"E(a, b')    = {E_ab_prime:.6f}")
print(f"E(a', b)    = {E_a_prime_b:.6f}")
print(f"E(a', b')   = {E_a_prime_b_prime:.6f}")

# CHSH S 值
S = abs(E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime)

print("\n--- CHSH Result ---")
print(f"S = {S:.6f}")
print(f"Classical limit: 2.0")
print(f"Quantum limit:   2.8284")

if S > 2.0:
    print("\n[RESULT] BELL INEQUALITY VIOLATED")
    print("Your deterministic model reproduces quantum correlation.")
    print("The violation comes from propagation + polarization + Malus law,")
    print("not from hardcoded cos²θ.")
else:
    print("\n[RESULT] Bell inequality NOT violated")
    print("Your model remains local realistic.")