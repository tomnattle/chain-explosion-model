import numpy as np
from numba import jit
import matplotlib.pyplot as plt

@jit(nopython=True)
def propagate_v3_fast(U, barrier, a_val, s_val, lam, k):
    h, w = U.shape
    new_U = np.zeros(U.shape, dtype=np.complex128)
    p_step = np.exp(1j * k)
    
    for y in range(h):
        for x in range(w):
            u_val = U[y, x]
            if np.abs(u_val) < 1e-10 or barrier[y, x]:
                continue
            
            # 极简传播：去掉所有非线性干扰，回归纯粹相干叠加
            val = u_val * lam
            if x + 1 < w:
                new_U[y, x+1] += val * a_val * p_step
            if y + 1 < h:
                new_U[y+1, x] += val * s_val * p_step
            if y - 1 >= 0:
                new_U[y-1, x] += val * s_val * p_step
    return new_U

def run_hyper_test():
    H, W = 151, 200 # 缩小画布，提高分辨率密度
    U = np.zeros((H, W), dtype=np.complex128)
    U[H//2, 2] = 100.0 + 0j
    
    barrier = np.zeros((H, W), dtype=np.bool_)
    bar_x = 30 # 极短距离，保持相干性
    barrier[:, bar_x] = True
    d, slit_w = 12, 2 # 紧凑型双缝
    barrier[H//2 - d//2 : H//2 - d//2 + slit_w, bar_x] = False
    barrier[H//2 + d//2 : H//2 + d//2 + slit_w, bar_x] = False
    
    # 参数硬核校准：K=0.8 (长波长), S=0.6 (大角度衍射)
    A, S, LAM, K = 1.0, 0.6, 1.0, 0.8
    
    print("执行高精度相干演化...")
    for _ in range(120): # 减少步数，防止波形塌缩
        U = propagate_v3_fast(U, barrier, A, S, LAM, K)
    
    # 在屏后不远处采样
    screen_x = bar_x + 50
    screen = np.abs(U[:, screen_x])**2
    if screen.max() == 0: return 0, np.zeros(H), np.zeros(H)
    screen /= screen.max()
    
    # 理论拟合
    y = np.arange(H) - H//2
    dist = screen_x - bar_x
    theta = np.arctan2(y, dist)
    wl = 2 * np.pi / K
    theory = (np.cos(np.pi * d * np.sin(theta) / wl)**2) * \
             (np.sinc(slit_w * np.sin(theta) / wl)**2)
    theory /= theory.max()
    
    r = np.corrcoef(screen, theory)[0, 1]
    return r, screen, theory, H//2

if __name__ == "__main__":
    r, ce, th, mid = run_hyper_test()
    print(f"\n突围结果皮尔逊相关系数 r = {r:.4f}")
    
    plt.figure(figsize=(8, 4))
    plt.plot(ce[mid-40:mid+40], label="CE Model (Sub-section)")
    plt.plot(th[mid-40:mid+40], '--', label="Fraunhofer Theory")
    plt.title(f"Hyper Precision Test: r={r:.4f}")
    plt.legend()
    plt.show()