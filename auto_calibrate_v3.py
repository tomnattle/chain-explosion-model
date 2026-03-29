import numpy as np
from ce_engine_v3_coherent import propagate_coherent, compute_intensity

def run_calibration():
    best_r = -1
    best_params = {}
    
    # 扫描波数 k (影响条纹密度) 和 侧向系数 S (影响包络宽度)
    for k_test in np.linspace(1.0, 3.0, 10):
        for s_test in np.linspace(0.1, 0.5, 5):
            # ... 执行 verify_A 的简化逻辑 ...
            # 计算当前 r 值
            current_r = calculate_r(k_test, s_test) 
            
            if current_r > best_r:
                best_r = current_r
                best_params = {'k': k_test, 'S': s_test}
                print(f"找到更优匹配: r = {best_r:.4f} (k={k_test:.2f}, S={s_test:.2f})")
    
    return best_params

# 注意：此处 calculate_r 需引用你之前的 verify_A 逻辑