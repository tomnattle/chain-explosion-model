import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 参数配置（可随意调整，感受不同效果）
# ============================================================

# 网格尺寸（像素）
WIDTH = 300      # 宽度（光传播方向为从左到右）
HEIGHT = 200     # 高度

# 传播参数（你的核心规则）
A = 1.0          # 主方向强度（向右）
S = 0.25         # 侧向强度（上下）
B = 0.05         # 后向强度（向左）
LAMBDA = 0.85    # 能量衰减系数（每次传播后剩余比例）

# 光源位置（左边界中央）
SOURCE_X = 5
SOURCE_Y = HEIGHT // 2

# 双缝参数
BARRIER_X = WIDTH // 2          # 挡板位置
SLIT1_Y = HEIGHT // 2 - 25      # 上缝中心
SLIT2_Y = HEIGHT // 2 + 25      # 下缝中心
SLIT_WIDTH = 6                  # 缝宽（像素）

# 传播步数
STEPS = 300

# ============================================================
# 初始化
# ============================================================

# 能量网格
grid = np.zeros((HEIGHT, WIDTH))

# 光源
grid[SOURCE_Y, SOURCE_X] = 100.0

# 挡板（True = 阻挡）
barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BARRIER_X] = True                     # 整列阻挡
barrier[SLIT1_Y:SLIT1_Y+SLIT_WIDTH, BARRIER_X] = False   # 开上缝
barrier[SLIT2_Y:SLIT2_Y+SLIT_WIDTH, BARRIER_X] = False   # 开下缝

# 屏幕（记录右侧边界到达的能量）
screen = np.zeros(HEIGHT)

# ============================================================
# 传播函数（实现你的链式爆炸规则）
# ============================================================

def propagate(grid, barrier):
    """一次传播步：每个有能量的格子向四周触发"""
    new_grid = np.zeros_like(grid)
    h, w = grid.shape
    
    for y in range(h):
        for x in range(w):
            energy = grid[y, x]
            if energy <= 0:
                continue
            
            # 能量衰减（每次触发都会损耗）
            energy *= LAMBDA
            
            # 向右（主方向，最强）
            if x + 1 < w and not barrier[y, x+1]:
                new_grid[y, x+1] += energy * A
            
            # 向左（后向，最弱）
            if x - 1 >= 0 and not barrier[y, x-1]:
                new_grid[y, x-1] += energy * B
            
            # 向上（侧向）
            if y - 1 >= 0 and not barrier[y-1, x]:
                new_grid[y-1, x] += energy * S
            
            # 向下（侧向）
            if y + 1 < h and not barrier[y+1, x]:
                new_grid[y+1, x] += energy * S
            
            # 可选：对角方向（涟漪更丰富）
            # 左上
            if x - 1 >= 0 and y - 1 >= 0 and not barrier[y-1, x-1]:
                new_grid[y-1, x-1] += energy * S * 0.5
            # 右上
            if x + 1 < w and y - 1 >= 0 and not barrier[y-1, x+1]:
                new_grid[y-1, x+1] += energy * S * 0.5
            # 左下
            if x - 1 >= 0 and y + 1 < h and not barrier[y+1, x-1]:
                new_grid[y+1, x-1] += energy * S * 0.5
            # 右下
            if x + 1 < w and y + 1 < h and not barrier[y+1, x+1]:
                new_grid[y+1, x+1] += energy * S * 0.5
    
    return new_grid

# ============================================================
# 运行模拟
# ============================================================

print("正在运行模拟...")
for step in range(STEPS):
    grid = propagate(grid, barrier)
    # 记录屏幕（右侧边界）能量
    screen += grid[:, -1]
    
    # 每50步打印进度
    if (step + 1) % 50 == 0:
        print(f"  步数: {step + 1} / {STEPS}")

# ============================================================
# 可视化
# ============================================================

# 1. 干涉条纹
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(screen)
plt.title("干涉条纹（屏幕能量分布）")
plt.xlabel("Y 位置（像素）")
plt.ylabel("累积能量")
plt.grid(True, alpha=0.3)

# 2. 最终能量分布热力图
plt.subplot(1, 2, 2)
# 对数缩放，让弱信号可见
energy_display = np.log1p(grid)
plt.imshow(energy_display, cmap='hot', aspect='auto', origin='upper')
plt.axvline(x=BARRIER_X, color='cyan', linestyle='--', linewidth=1, label='挡板位置')
plt.title(f"最终能量分布（对数显示）\nA={A}, S={S}, B={B}, λ={LAMBDA}")
plt.xlabel("X 位置")
plt.ylabel("Y 位置")
plt.colorbar(label='log(1+能量)')
plt.legend()

plt.tight_layout()
plt.show()

# 3. 打印参数和观察结果
print("\n" + "="*50)
print("模拟完成！")
print(f"参数: A={A}, S={S}, B={B}, λ={LAMBDA}")
print(f"光源: ({SOURCE_X}, {SOURCE_Y})")
print(f"双缝: 缝距={abs(SLIT2_Y - SLIT1_Y)}px, 缝宽={SLIT_WIDTH}px")

# 简单判断是否有干涉条纹
peak_count = 0
for i in range(1, len(screen)-1):
    if screen[i] > screen[i-1] and screen[i] > screen[i+1]:
        peak_count += 1

if peak_count >= 3:
    print("\n✅ 检测到明显的干涉条纹！你的链式爆炸模型成功产生了波动现象。")
else:
    print("\n⚠️ 条纹不明显。建议调整参数：增加 S（侧向强度）或降低 LAMBDA（衰减）")