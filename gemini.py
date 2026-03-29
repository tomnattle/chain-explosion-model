import numpy as np
from numba import jit
import time

# ============================================================
# 你的核心 A-S-B 链式内核
# ============================================================
@jit(nopython=True)
def step_explosion(grid, A, S, B, lam):
    h, w = grid.shape
    new_grid = np.zeros((h, w))
    for y in range(h):
        for x in range(w):
            e = grid[y, x]
            if e < 1e-8: continue
            
            e_next = e * lam
            # 链式传播
            if x + 1 < w: new_grid[y, x + 1] += e_next * A # 前
            if x - 1 >= 0: new_grid[y, x - 1] += e_next * B # 后 (回火关键)
            if y + 1 < h: new_grid[y + 1, x] += e_next * S # 侧
            if y - 1 >= 0: new_grid[y - 1, x] += e_next * S # 侧
    return new_grid

# ============================================================
# 实验主循环
# ============================================================
def run_monitored_experiment(feedback_strength=0.2):
    H, W = 51, 201
    grid = np.zeros((H, W))
    
    # 初始化源头
    mid_y, mid_x = H // 2, W // 2
    grid[mid_y, mid_x] = 1000.0
    
    A, S, B, LAMBDA = 1.0, 0.3, feedback_strength, 0.95
    
    print(f"{'Step':<6} | {'Source_E':<12} | {'A_End_E':<12} | {'B_End_E':<12} | {'Event'}")
    print("-" * 70)

    for step in range(1, 301):
        grid = step_explosion(grid, A, S, B, LAMBDA)
        
        # 监测点能量
        e_source = grid[mid_y, mid_x]
        e_a = np.sum(grid[:, :mid_x-20]) # A端区域
        e_b = np.sum(grid[:, mid_x+20:]) # B端区域
        
        event = ""
        # 模拟 A 端测量事件：在第 100 步“吃掉”A端所有能量
        if step == 100:
            grid[:, :mid_x-10] = 0.0
            event = "<<< A-OBSERVED (Energy Eaten) >>>"
        
        # 关键日志：每 20 步或在事件发生后输出
        if step % 20 == 0 or (100 < step < 110):
            print(f"{step:<6} | {e_source:<12.4f} | {e_a:<12.4f} | {e_b:<12.4f} | {event}")

# 运行测试
run_monitored_experiment(feedback_strength=0.15) # B=0.15 模拟较强的反馈