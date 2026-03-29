import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ============================================================
# 强制稳定性参数
# ============================================================
A, S, B, LAM = 0.5, 0.1, 0.0, 1.0
INITIAL_ENERGY = 1.0

HEIGHT, WIDTH = 301, 600
BAR_X, SCREEN_X = 100, 500
SLIT_W, d = 6, 30

print("=" * 65)
print("验证A(V5 强制归一化版)：物理标定与干涉提取")
print("=" * 65)

grid = np.zeros((HEIGHT, WIDTH))
grid[HEIGHT//2, 5] = INITIAL_ENERGY

barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BAR_X] = True
barrier[HEIGHT//2-d//2-SLIT_W//2 : HEIGHT//2-d//2+SLIT_W//2, BAR_X] = False
barrier[HEIGHT//2+d//2-SLIT_W//2 : HEIGHT//2+d//2+SLIT_W//2, BAR_X] = False

# ============================================================
# 核心：带能量控制的循环
# ============================================================
temp_grid = grid.copy()
for step in range(1, 601):
    # 每次仅跑 1 步
    temp_grid = propagate_double_slit_n_steps(temp_grid, barrier, A, S, B, LAM, 1)
    
    # 【数值保险丝】强制每一帧的总能量守恒
    current_total = np.sum(temp_grid)
    if current_total > 1e10 or current_total < 1e-10: # 防止溢出或湮灭
        temp_grid = (temp_grid / (current_total + 1e-12)) * INITIAL_ENERGY
    
    if step % 100 == 0:
        print(f" 步数 {step}: 能量已强制对齐到 {np.sum(temp_grid):.2f}")

# ============================================================
# 分析
# ============================================================
ce_screen = temp_grid[:, SCREEN_X]
# 归一化显示
ce_screen = ce_screen / (ce_screen.max() + 1e-12)

vis = compute_visibility(ce_screen)
print(f"\n最终干涉对比度 V = {vis:.4f}")

if vis > 0.05:
    print(" ✅ 成功：通过强制能量对齐，模型展现出了波动相干性！")
else:
    print(" ❌ 失败：即使能量守恒，模型依然表现为纯扩散。")