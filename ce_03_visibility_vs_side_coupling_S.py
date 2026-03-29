import numpy as np
import matplotlib.pyplot as plt

from chain_explosion_numba import propagate_double_slit

# ============================================================
# 固定参数（除了 S 以外都保持不变）
# ============================================================

HEIGHT = 201
WIDTH = 400
A = 1.0
B = 0.05
LAMBDA = 0.90
SOURCE_X = 10
SOURCE_Y = HEIGHT // 2
BARRIER_X = WIDTH // 2
SLIT1_Y = HEIGHT // 2 - 25
SLIT2_Y = HEIGHT // 2 + 25
SLIT_WIDTH = 6
STEPS = 500
SCREEN_X = WIDTH - 10

# 要扫描的 S 值列表（侧向强度，从弱到强）
S_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

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
# 单个 S 值的模拟
# ============================================================

def run_simulation(S):
    # 初始化
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 100.0
    
    # 挡板
    barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
    barrier[:, BARRIER_X] = True
    barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, BARRIER_X] = False
    barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, BARRIER_X] = False
    
    # 传播
    for _ in range(STEPS):
        grid = propagate_double_slit(grid, barrier, A, S, B, LAMBDA)
    
    # 提取屏幕数据
    screen = grid[:, SCREEN_X]
    
    # 计算对比度
    visibility = compute_visibility(screen)
    total_energy = np.sum(screen)
    peak_energy = np.max(screen)
    
    return visibility, total_energy, peak_energy

# ============================================================
# 主程序：扫描 S 值
# ============================================================

print("=" * 60)
print("链式爆炸模型 - 干涉对比度 vs 侧向强度 S")
print(f"固定参数: A={A}, B={B}, λ={LAMBDA}")
print(f"扫描 S 范围: {S_values}")
print("=" * 60)

results = []
for S in S_values:
    print(f"\n正在运行 S = {S} ...")
    vis, total, peak = run_simulation(S)
    results.append({
        'S': S,
        'visibility': vis,
        'total_energy': total,
        'peak_energy': peak
    })
    print(f"  对比度 V = {vis:.6f}")
    print(f"  总能量 = {total:.6e}")
    print(f"  峰值能量 = {peak:.6e}")

# ============================================================
# 输出结果表格
# ============================================================

print("\n" + "=" * 60)
print("扫描结果汇总")
print("=" * 60)
print("S\t\t对比度 V\t总能量\t\t峰值能量")
for r in results:
    print(f"{r['S']:.1f}\t\t{r['visibility']:.4f}\t\t{r['total_energy']:.2e}\t{r['peak_energy']:.2e}")

# ============================================================
# 绘制 V-S 曲线
# ============================================================

plt.figure(figsize=(8, 6))
S_vals = [r['S'] for r in results]
V_vals = [r['visibility'] for r in results]

plt.plot(S_vals, V_vals, 'bo-', linewidth=2, markersize=8)
plt.xlabel('侧向强度 S', fontsize=12)
plt.ylabel('干涉对比度 V', fontsize=12)
plt.title('链式爆炸模型：干涉对比度 vs 侧向强度\n(量子力学无此曲线)', fontsize=14)
plt.grid(True, alpha=0.3)
plt.ylim(0, 1.05)
plt.xlim(0, 1.05)

# 保存图片
plt.savefig('V_vs_S.png', dpi=150)
plt.show()

print("\n" + "=" * 60)
print("实验完成！")
print("图片已保存为: V_vs_S.png")
print("请将以上输出（包括表格和图片）反馈给我。")
print("=" * 60)