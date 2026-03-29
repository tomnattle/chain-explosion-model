import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 参数配置
# ============================================================

HEIGHT = 201
WIDTH = 400
A = 1.0
S = 0.4
B = 0.05
LAMBDA = 0.90
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
BARRIER_X = WIDTH // 2
SLIT1_Y = HEIGHT // 2 - 25   # 上缝（将被吸收）
SLIT2_Y = HEIGHT // 2 + 25   # 下缝（参考）
SLIT_WIDTH = 6
STEPS = 500
SCREEN_X = WIDTH - 10

# 吸收参数
ABSORB_RATIO = 0.5   # 吸收比例（0=无吸收，1=完全吸收）

# ============================================================
# 传播函数（支持吸收）
# ============================================================

def propagate(grid, barrier, absorb_ratio):
    new_grid = np.zeros_like(grid)
    h, w = grid.shape
    for y in range(h):
        for x in range(w):
            energy = grid[y, x]
            if energy <= 0:
                continue
            
            # === 吸收器：在上缝右侧紧邻的格子处吸收能量 ===
            if absorb_ratio > 0:
                if x == BARRIER_X + 1 and (y >= SLIT1_Y and y < SLIT1_Y + SLIT_WIDTH):
                    energy *= (1 - absorb_ratio)
            
            energy *= LAMBDA
            
            # 主方向（右）
            if x + 1 < w and not barrier[y, x+1]:
                new_grid[y, x+1] += energy * A
            # 后方向（左）
            if x - 1 >= 0 and not barrier[y, x-1]:
                new_grid[y, x-1] += energy * B
            # 上下
            if y - 1 >= 0 and not barrier[y-1, x]:
                new_grid[y-1, x] += energy * S
            if y + 1 < h and not barrier[y+1, x]:
                new_grid[y+1, x] += energy * S
            # 对角（增强涟漪）
            if x-1>=0 and y-1>=0 and not barrier[y-1, x-1]:
                new_grid[y-1, x-1] += energy * S * 0.5
            if x+1<w and y-1>=0 and not barrier[y-1, x+1]:
                new_grid[y-1, x+1] += energy * S * 0.5
            if x-1>=0 and y+1<h and not barrier[y+1, x-1]:
                new_grid[y+1, x-1] += energy * S * 0.5
            if x+1<w and y+1<h and not barrier[y+1, x+1]:
                new_grid[y+1, x+1] += energy * S * 0.5
    return new_grid

# ============================================================
# 计算干涉对比度
# ============================================================

def compute_visibility(screen):
    peaks = []
    valleys = []
    for i in range(1, len(screen)-1):
        if screen[i] > screen[i-1] and screen[i] > screen[i+1]:
            peaks.append(screen[i])
        elif screen[i] < screen[i-1] and screen[i] < screen[i+1]:
            valleys.append(screen[i])
    if not peaks or not valleys:
        return 0.0
    I_max = np.mean(peaks)
    I_min = np.mean(valleys)
    if I_max + I_min == 0:
        return 0.0
    return (I_max - I_min) / (I_max + I_min)

# ============================================================
# 运行单次模拟
# ============================================================

def run_simulation(absorb_ratio, label):
    print(f"\n--- {label} (吸收比例={absorb_ratio*100}%) ---")
    
    # 初始化
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 100.0
    
    # 挡板
    barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
    barrier[:, BARRIER_X] = True
    barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, BARRIER_X] = False
    barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, BARRIER_X] = False
    
    # 传播
    for step in range(STEPS):
        grid = propagate(grid, barrier, absorb_ratio)
        if (step+1) % 100 == 0:
            print(f"  进度: {step+1}/{STEPS}")
    
    # 屏幕数据
    screen = grid[:, SCREEN_X]
    visibility = compute_visibility(screen)
    total_energy = np.sum(screen)
    peak_energy = np.max(screen)
    
    print(f"\n结果:")
    print(f"  干涉对比度 V = {visibility:.4f}")
    print(f"  总能量 = {total_energy:.6e}")
    print(f"  峰值能量 = {peak_energy:.6e}")
    
    return screen, visibility

# ============================================================
# 主程序：对比三种情况
# ============================================================

print("=" * 60)
print("测量模拟：吸收器对干涉条纹的影响")
print(f"固定参数: A={A}, S={S}, B={B}, λ={LAMBDA}")
print(f"吸收器位置: 上缝右侧，吸收比例 {ABSORB_RATIO*100}%")
print("=" * 60)

# 情况1：无吸收（标准双缝）
screen0, vis0 = run_simulation(0.0, "无吸收（标准双缝）")

# 情况2：有吸收（一个缝被部分吸收）
screen1, vis1 = run_simulation(ABSORB_RATIO, f"有吸收（吸收比例 {ABSORB_RATIO*100}%）")

# 情况3：完全吸收一个缝（相当于单缝）
screen2, vis2 = run_simulation(1.0, "完全吸收一个缝（等效单缝）")

# ============================================================
# 可视化对比
# ============================================================

plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(screen0, 'b-', linewidth=1)
plt.title(f'无吸收 (标准双缝) — 对比度 V = {vis0:.4f}')
plt.ylabel('能量')
plt.grid(True, alpha=0.3)

plt.subplot(3, 1, 2)
plt.plot(screen1, 'r-', linewidth=1)
plt.title(f'部分吸收 (上缝吸收 {ABSORB_RATIO*100}%) — 对比度 V = {vis1:.4f}')
plt.ylabel('能量')
plt.grid(True, alpha=0.3)

plt.subplot(3, 1, 3)
plt.plot(screen2, 'g-', linewidth=1)
plt.title(f'完全吸收一个缝 (等效单缝) — 对比度 V = {vis2:.4f}')
plt.xlabel('Y 位置（像素）')
plt.ylabel('能量')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('measurement_effect.png', dpi=150)
plt.show()

# ============================================================
# 结果分析
# ============================================================

print("\n" + "=" * 60)
print("实验结果分析")
print("=" * 60)
print(f"无吸收对比度:     {vis0:.4f}")
print(f"部分吸收对比度:   {vis1:.4f}")
print(f"完全吸收对比度:   {vis2:.4f}")

if vis1 < vis0:
    print("\n✅ 部分吸收导致干涉对比度下降！")
    print("   结论：测量（吸收能量）会改变光的传播状态。")
    print("   你的模型解释：吸收器吃掉了部分能量，破坏了完美的干涉叠加。")
    print("   量子力学解释：测量导致坍缩。但你的模型给出了物理机制（能量吸收）。")
else:
    print("\n⚠️ 部分吸收未导致对比度明显下降。")
    print("   可能需要调整吸收比例或参数。")

if vis2 < 0.05:
    print("\n✅ 完全吸收一个缝 → 干涉消失（单缝）。")
    print("   验证了：挡住一条路径，干涉消失。")
else:
    print("\n⚠️ 完全吸收一个缝后仍有干涉，检查代码。")

print("\n" + "=" * 60)
print("实验完成！图片已保存为 measurement_effect.png")
print("请将以上输出（包括对比度数值）反馈给我。")
print("=" * 60)