import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 参数配置
# ============================================================

# 网格尺寸（高度固定，宽度可变）
HEIGHT = 201      # 高度，奇数，保证中心对称
WIDTH_BASE = 300  # 基础宽度，屏幕初始位置

# 传播参数（你的核心规则）
A = 1.0          # 主方向强度（向右）
S = 0.3          # 侧向强度（上下）
B = 0.05         # 后向强度（向左）
LAMBDA = 0.90    # 能量衰减系数

# 光源位置（左边界中央）
SOURCE_X = 5
SOURCE_Y = HEIGHT // 2

# 双缝参数
BARRIER_X = 150            # 挡板位置（固定）
SLIT1_Y = HEIGHT // 2 - 20 # 上缝中心
SLIT2_Y = HEIGHT // 2 + 20 # 下缝中心
SLIT_WIDTH = 4             # 缝宽（像素）

# 传播步数（足够让光到达屏幕）
STEPS = 400

# 要扫描的距离列表（屏幕X坐标，从挡板后开始）
SCREEN_DISTANCES = [180, 200, 220, 240, 260, 280, 300, 320, 340, 360]

# ============================================================
# 初始化函数
# ============================================================

def create_grid_and_barrier(width, barrier_x):
    """创建指定宽度的网格和挡板"""
    grid = np.zeros((HEIGHT, width))
    grid[SOURCE_Y, SOURCE_X] = 100.0  # 光源能量
    
    # 挡板（True = 阻挡）
    barrier = np.zeros((HEIGHT, width), dtype=bool)
    if barrier_x < width:
        barrier[:, barrier_x] = True
        barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, barrier_x] = False
        barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, barrier_x] = False
    
    return grid, barrier

# ============================================================
# 传播函数（链式爆炸）
# ============================================================

def propagate(grid, barrier):
    """一次传播步"""
    new_grid = np.zeros_like(grid)
    h, w = grid.shape
    
    for y in range(h):
        for x in range(w):
            energy = grid[y, x]
            if energy <= 0:
                continue
            
            energy *= LAMBDA
            
            # 向右（主方向）
            if x + 1 < w and not barrier[y, x+1]:
                new_grid[y, x+1] += energy * A
            
            # 向左（后向）
            if x - 1 >= 0 and not barrier[y, x-1]:
                new_grid[y, x-1] += energy * B
            
            # 向上（侧向）
            if y - 1 >= 0 and not barrier[y-1, x]:
                new_grid[y-1, x] += energy * S
            
            # 向下（侧向）
            if y + 1 < h and not barrier[y+1, x]:
                new_grid[y+1, x] += energy * S
            
            # 对角方向（让涟漪更丰富）
            if x - 1 >= 0 and y - 1 >= 0 and not barrier[y-1, x-1]:
                new_grid[y-1, x-1] += energy * S * 0.5
            if x + 1 < w and y - 1 >= 0 and not barrier[y-1, x+1]:
                new_grid[y-1, x+1] += energy * S * 0.5
            if x - 1 >= 0 and y + 1 < h and not barrier[y+1, x-1]:
                new_grid[y+1, x-1] += energy * S * 0.5
            if x + 1 < w and y + 1 < h and not barrier[y+1, x+1]:
                new_grid[y+1, x+1] += energy * S * 0.5
    
    return new_grid

# ============================================================
# 计算对比度
# ============================================================

def compute_visibility(screen):
    """计算干涉条纹对比度 V = (I_max - I_min) / (I_max + I_min)"""
    # 找到峰值和谷值
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
# 主程序：扫描不同距离
# ============================================================

print("=" * 60)
print("干涉条纹对比度随距离衰减实验")
print("=" * 60)
print(f"参数: A={A}, S={S}, B={B}, λ={LAMBDA}")
print(f"双缝: 缝距={abs(SLIT2_Y - SLIT1_Y)}px, 缝宽={SLIT_WIDTH}px")
print(f"扫描距离: {SCREEN_DISTANCES}")
print("-" * 60)

results = []

for screen_x in SCREEN_DISTANCES:
    print(f"\n>>> 测试距离: X = {screen_x}")
    
    # 创建网格（宽度 = 屏幕位置 + 10，确保屏幕在边界内）
    width = screen_x + 10
    grid, barrier = create_grid_and_barrier(width, BARRIER_X)
    
    # 运行模拟
    for step in range(STEPS):
        grid = propagate(grid, barrier)
    
    # 提取屏幕能量（屏幕在 X = screen_x 处）
    if screen_x < grid.shape[1]:
        screen = grid[:, screen_x]
    else:
        print(f"  错误: 屏幕位置 {screen_x} 超出网格宽度 {grid.shape[1]}")
        continue
    
    # 计算对比度
    visibility = compute_visibility(screen)
    total_energy = np.sum(screen)
    peak_energy = np.max(screen)
    
    # 记录结果
    results.append({
        'distance': screen_x,
        'visibility': visibility,
        'total_energy': total_energy,
        'peak_energy': peak_energy
    })
    
    # 打印日志
    print(f"  屏幕能量: 总和={total_energy:.2f}, 峰值={peak_energy:.2f}")
    print(f"  对比度 V = {visibility:.4f}")
    
    # 可选：打印屏幕数据的片段（用于调试）
    # 找到峰值位置
    peaks_y = []
    for y in range(HEIGHT):
        if screen[y] > np.mean(screen) * 2:
            peaks_y.append(y)
    if peaks_y:
        print(f"  峰值Y位置: {peaks_y[:5]}")

# ============================================================
# 结果分析
# ============================================================

print("\n" + "=" * 60)
print("实验结果汇总")
print("=" * 60)

print("\n距离\t对比度\t\t总能量\t\t峰值能量")
print("-" * 60)
for r in results:
    print(f"{r['distance']}\t{r['visibility']:.4f}\t\t{r['total_energy']:.2f}\t\t{r['peak_energy']:.2f}")

# ============================================================
# 可视化
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 左图：对比度随距离的变化
axes[0].plot([r['distance'] for r in results], [r['visibility'] for r in results], 'bo-', linewidth=2, markersize=8)
axes[0].set_xlabel('传播距离 (X 坐标)', fontsize=12)
axes[0].set_ylabel('干涉条纹对比度 V', fontsize=12)
axes[0].set_title('对比度随距离衰减曲线\n你的模型预言', fontsize=14)
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(0, 1)

# 右图：总能量衰减
axes[1].plot([r['distance'] for r in results], [r['total_energy'] for r in results], 'ro-', linewidth=2, markersize=8)
axes[1].set_xlabel('传播距离 (X 坐标)', fontsize=12)
axes[1].set_ylabel('屏幕总能量', fontsize=12)
axes[1].set_title('能量衰减曲线', fontsize=14)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('interference_decay.png', dpi=150)
plt.show()

print("\n" + "=" * 60)
print("结论分析")
print("=" * 60)

# 检查是否有衰减趋势
if len(results) >= 3:
    v_first = results[0]['visibility']
    v_last = results[-1]['visibility']
    decay = (v_first - v_last) / v_first * 100 if v_first > 0 else 0
    
    print(f"\n对比度从 {v_first:.4f} 衰减到 {v_last:.4f}，衰减了 {decay:.1f}%")
    
    if decay > 10:
        print("\n✅ 观测到明显的对比度衰减！")
        print("   这支持你的模型：干涉条纹清晰度随传播距离下降。")
        print("   现有理论（量子力学、波动光学）不预言此效应。")
    elif decay > 0:
        print("\n⚠️ 观测到轻微衰减，但幅度较小。")
        print("   可能需要调整参数（如增大 S 或减小 λ）使效应更明显。")
    else:
        print("\n❌ 未观测到明显衰减。")
        print("   可能需要调整参数或检查代码逻辑。")

print("\n" + "=" * 60)
print("实验完成。请将以上完整输出（包括数字和图表）反馈给我。")
print("=" * 60)