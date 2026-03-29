import numpy as np
from numba import jit

@jit(nopython=True)
def propagate_coherent(U, barrier, A, S, LAM, k):
    """
    复数相干传播引擎 (V3)
    U: 复数阵列 np.complex128
    k: 波数 (2*pi/lambda)，控制条纹间距
    """
    h, w = U.shape
    new_U = np.zeros_like(U)
    
    # 距离因子（格点间距假设为1）
    dist_diag = np.sqrt(2)
    
    for y in range(h):
        for x in range(w):
            if barrier[y, x] or np.abs(U[y, x]) < 1e-10:
                continue
            
            val = U[y, x] * LAM
            
            # 正向传播 (exp(i*k*r) 赋予物理相位)
            if x + 1 < w:
                new_U[y, x+1] += val * A * np.exp(1j * k)
            
            # 侧向传播
            if y + 1 < h:
                new_U[y+1, x] += val * S * np.exp(1j * k)
            if y - 1 >= 0:
                new_U[y-1, x] += val * S * np.exp(1j * k)
                
            # 对角传播 (纠正之前的几何畸变)
            if x + 1 < w and y + 1 < h:
                new_U[y+1, x+1] += val * S * 0.5 * np.exp(1j * k * dist_diag)
            if x + 1 < w and y - 1 >= 0:
                new_U[y-1, x+1] += val * S * 0.5 * np.exp(1j * k * dist_diag)
                
    return new_U

def compute_intensity(U):
    """强度 = |U|^2"""
    return np.abs(U)**2