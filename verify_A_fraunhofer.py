"""
验证A：链式爆炸模型 vs 夫琅禾费衍射公式
========================================
"大象的耳朵" — 夫琅禾费双缝干涉公式

标准公式预言的屏幕强度分布：
  I(θ) = I₀ · cos²(π·d·sinθ/λ) · [sin(π·a·sinθ/λ)/(π·a·sinθ/λ)]²

其中：
  d = 缝间距
  a = 缝宽
  λ = 波长（在CE模型中由传播参数决定）
  θ = 衍射角

本实验：
1. 用CE模型跑双缝，得到屏幕分布
2. 用夫琅禾费公式拟合同样的几何参数
3. 计算两者的相关系数 —— 越高越好
4. 输出对比图，用数据"堵嘴"
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ============================================================
# 参数
# ============================================================
HEIGHT    = 301
WIDTH     = 500
A         = 1.0
S         = 0.30
B         = 0.05
LAM       = 0.92
SOURCE_X  = 5
SOURCE_Y  = HEIGHT // 2
BAR_X     = 150
SLIT1_Y   = HEIGHT // 2 - 30
SLIT2_Y   = HEIGHT // 2 + 30
SLIT_W    = 8
SCREEN_X  = WIDTH - 20
STEPS     = 600

print("=" * 65)
print("验证A：CE模型 vs 夫琅禾费双缝衍射公式")
print("=" * 65)

# ============================================================
# 运行CE模型
# ============================================================
grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1000.0

barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BAR_X] = True
barrier[SLIT1_Y:SLIT1_Y + SLIT_W, BAR_X] = False
barrier[SLIT2_Y:SLIT2_Y + SLIT_W, BAR_X] = False

print(f"  CE传播: {STEPS} 步（fused）")
grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)

ce_screen = grid[:, SCREEN_X].copy()
vis_ce = compute_visibility(ce_screen)
print(f"\nCE模型 干涉对比度 V = {vis_ce:.4f}")

# ============================================================
# 夫琅禾费公式
# ============================================================
# 从CE模型几何参数估算等效波长
# CE模型中，侧向传播角度 θ_s = arctan(S/A)
# 这对应一个等效波长

d = abs(SLIT2_Y - SLIT1_Y)   # 缝间距（格点数）
a = SLIT_W                    # 缝宽
L = SCREEN_X - BAR_X          # 屏幕距离

# 等效波长：从峰位推算
# 找CE屏幕的第一个侧峰位置
ce_norm = ce_screen / (ce_screen.max() + 1e-12)
center = SOURCE_Y
half = HEIGHT // 2

# 找中心两侧第一个局部最大
peaks_above = []
for y in range(center - 5, 0, -1):
    if ce_norm[y] > ce_norm[y-1] and ce_norm[y] > ce_norm[y+1] and ce_norm[y] > 0.05:
        peaks_above.append(y)
        break

# 估算等效波长 λ_eff：Δy = λ·L/d
if peaks_above:
    delta_y = abs(peaks_above[0] - center)
    lambda_eff = delta_y * d / L
    print(f"\n从CE峰位推算等效波长 λ_eff ≈ {lambda_eff:.2f} 格点")
else:
    lambda_eff = d * 0.5  # 默认估算
    print(f"\n未找到明显侧峰，使用默认 λ_eff = {lambda_eff:.2f}")

# 计算夫琅禾费强度分布
y_positions = np.arange(HEIGHT) - center
theta = np.arctan2(y_positions, L)  # 衍射角

# 双缝因子（缝间距）
phase_double = np.pi * d * np.sin(theta) / lambda_eff
I_double = np.cos(phase_double) ** 2

# 单缝包络（缝宽）
phase_single = np.pi * a * np.sin(theta) / lambda_eff
with np.errstate(divide='ignore', invalid='ignore'):
    sinc_term = np.where(
        np.abs(phase_single) < 1e-10,
        1.0,
        np.sin(phase_single) / phase_single
    )
I_single = sinc_term ** 2

fraunhofer = I_double * I_single

# 归一化到CE最大值
fraunhofer_norm = fraunhofer / fraunhofer.max() * ce_screen.max()

# ============================================================
# 相关系数
# ============================================================
corr = np.corrcoef(ce_screen, fraunhofer_norm)[0, 1]
print(f"\n与夫琅禾费公式的皮尔逊相关系数: r = {corr:.4f}")

if corr > 0.90:
    verdict = "✅ 高度吻合（r > 0.90）——CE模型可以描述夫琅禾费衍射"
elif corr > 0.70:
    verdict = "⚠️ 中度吻合（r > 0.70）——主要特征相符，细节有差异"
else:
    verdict = "❌ 吻合度不足——需要调整模型参数"
print(verdict)

# ============================================================
# 对比可视化
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.patch.set_facecolor('#0d1117')
for ax in axes:
    ax.set_facecolor('#0d1117')
    ax.tick_params(colors='#8b949e')
    ax.spines['bottom'].set_color('#30363d')
    ax.spines['left'].set_color('#30363d')
    ax.spines['top'].set_color('#30363d')
    ax.spines['right'].set_color('#30363d')

y_axis = np.arange(HEIGHT) - center

# 图1：CE模型屏幕
axes[0].plot(y_axis, ce_screen / ce_screen.max(), color='#58a6ff', linewidth=1.5, label='CE模型')
axes[0].set_title('CE模型屏幕分布', color='white', fontsize=12)
axes[0].set_xlabel('Y 位置（相对中心）', color='#8b949e')
axes[0].set_ylabel('归一化强度', color='#8b949e')
legend_kw(axes[0], facecolor='#161b22')
axes[0].grid(True, alpha=0.2, color='#30363d')

# 图2：夫琅禾费公式
axes[1].plot(y_axis, fraunhofer / fraunhofer.max(), color='#f78166', linewidth=1.5, label='夫琅禾费公式')
axes[1].set_title('夫琅禾费理论预言', color='white', fontsize=12)
axes[1].set_xlabel('Y 位置（相对中心）', color='#8b949e')
legend_kw(axes[1], facecolor='#161b22')
axes[1].grid(True, alpha=0.2, color='#30363d')

# 图3：叠加对比
axes[2].plot(y_axis, ce_screen / ce_screen.max(), color='#58a6ff', linewidth=2,
             label=f'CE模型 (V={vis_ce:.3f})', alpha=0.9)
axes[2].plot(y_axis, fraunhofer / fraunhofer.max(), color='#f78166', linewidth=1.5,
             linestyle='--', label=f'夫琅禾费 (r={corr:.3f})', alpha=0.9)
axes[2].set_title(f'叠加对比\n皮尔逊 r = {corr:.4f}', color='white', fontsize=12)
axes[2].set_xlabel('Y 位置（相对中心）', color='#8b949e')
legend_kw(axes[2], facecolor='#161b22')
axes[2].grid(True, alpha=0.2, color='#30363d')

# 填充差异区域
axes[2].fill_between(y_axis,
                     ce_screen / ce_screen.max(),
                     fraunhofer / fraunhofer.max(),
                     alpha=0.15, color='#3fb950', label='差异')

plt.suptitle(f'验证A：链式爆炸模型 vs 夫琅禾费衍射\n'
             f'λ_eff={lambda_eff:.1f}格点  d={d}px  a={a}px  L={L}px',
             color='white', fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig('verify_A_fraunhofer.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117')
print("\n图片已保存: verify_A_fraunhofer.png")

# ============================================================
# 总结报告
# ============================================================
print("\n" + "=" * 65)
print("验证A 总结")
print("=" * 65)
print(f"  CE模型干涉对比度:      V = {vis_ce:.4f}")
print(f"  等效波长估算:          λ = {lambda_eff:.2f} 格点")
print(f"  与夫琅禾费公式相关性:  r = {corr:.4f}")
print(f"  结论: {verdict}")
print()
print("物理意义：")
print("  夫琅禾费公式是'大象耳朵'——描述远场衍射图样。")
print("  如果CE模型的r > 0.90，说明你的格点传播机制")
print("  在宏观行为上与经典波动光学吻合，")
print("  这是模型最基础的正确性验证。")
