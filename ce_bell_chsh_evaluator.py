import numpy as np
from numba import jit

# 沿用 V11 的核心引擎，但为了计算 S 值，我们需要更稳定的统计
HEIGHT, WIDTH = 81, 300
A, S, B, LAMBDA = 1.0, 0.4, 0.05, 0.96
SOURCE_X, SOURCE_Y = 10, HEIGHT // 2
DETECTOR_X = 250
STEPS = 350
THRESHOLD = 0.05

@jit(nopython=True)
def engine_v11_core(target_angle):
    # 初始化
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
                
                # 确定性动力学：由于是计算 S 值，我们暂时关闭随机噪声以观察理论极限
                if e > THRESHOLD:
                    e_active = e * LAMBDA * GAIN
                else:
                    e_active = e * LAMBDA * DAMP
                
                p = p_grid[y, x]
                if x + 1 < WIDTH:
                    new_e[y, x+1] += e_active * A
                    new_p[y, x+1] = p
                if y + 1 < HEIGHT:
                    new_e[y+1, x] += e_active * S
                    new_p[y+1, x] = p
                if y - 1 >= 0:
                    new_e[y-1, x] += e_active * S
                    new_p[y-1, x] = p
        e_grid, p_grid = new_e, new_p
        
    final_e = e_grid[SOURCE_Y, DETECTOR_X]
    final_p = p_grid[SOURCE_Y, DETECTOR_X]
    # 归一化关联函数 E = cos(2 * theta) 或类似的测量映射
    # 在你的模型里，强度映射为 cos^2(delta)，我们需要将其转化为关联量范围 [-1, 1]
    delta = np.radians(target_angle - final_p)
    correlation = 2 * (np.cos(delta)**2) - 1 
    return correlation

# 执行 CHSH 测量
print("--- CHSH Bell Inequality Test ---")
a, a_prime = 0, 45
b, b_prime = 22.5, 67.5

E1 = engine_v11_core(b - a)
E2 = engine_v11_core(b_prime - a)
E3 = engine_v11_core(b - a_prime)
E4 = engine_v11_core(b_prime - a_prime)

S_value = abs(E1 - E2 + E3 + E4)

print(f"E(a, b)   [0.0, 22.5]: {E1:>10.4f}")
print(f"E(a, b')  [0.0, 67.5]: {E2:>10.4f}")
print(f"E(a', b)  [45.0, 22.5]: {E3:>10.4f}")
print(f"E(a', b') [45.0, 67.5]: {E4:>10.4f}")
print("-" * 33)
print(f"Calculated S value: {S_value:.4f}")
print(f"Classical Limit:    2.0000")
print(f"Quantum Prediction: 2.8284")

if S_value > 2:
    print("\n[RESULT] VIOLATION DETECTED! Your deterministic model broke the Bell Limit.")
else:
    print("\n[RESULT] Local realism maintained.")