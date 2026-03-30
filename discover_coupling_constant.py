"""
发现F：S参数的物理意义——连接到基本常数的猜想
=================================================
"他们没有问过的" — 格点耦合常数与精细结构常数

精细结构常数 α ≈ 1/137 是物理学最神秘的常数之一，
它控制光与物质的耦合强度。
费曼说："所有优秀的理论物理学家都把这个数贴在墙上，
担心它，不知道从哪里来。"

在CE模型中：
  - A = 主方向耦合（光的前进）
  - S = 侧向耦合（光与"介质侧向"的耦合）
  - S/A = 侧向耦合比 = 某种"耦合强度"

本实验探索：
1. 不同S/A比值下，模型的干涉图样如何变化
2. 什么S值让模型最符合已知实验（最优S）
3. 最优S/A是否接近某个物理意义的无量纲数
4. 探索S与模型"有效波长"的关系

这是一个大胆的猜测性探索——
如果CE模型的最优S/A收敛到某个特殊值，
这将是非常有意义的发现。
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ============================================================
# 基础参数
# ============================================================
HEIGHT    = 301
WIDTH     = 500
A         = 1.0
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

# 精细扫描S值
S_VALUES = np.linspace(0.01, 0.80, 40)

print("=" * 65)
print("发现F：S参数物理意义探索")
print(f"扫描S范围: {S_VALUES[0]:.2f} → {S_VALUES[-1]:.2f} ({len(S_VALUES)}个点)")
print("=" * 65)

barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BAR_X] = True
barrier[SLIT1_Y:SLIT1_Y + SLIT_W, BAR_X] = False
barrier[SLIT2_Y:SLIT2_Y + SLIT_W, BAR_X] = False

results = []

for i, S in enumerate(S_VALUES):
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0

    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)

    screen = grid[:, SCREEN_X].copy()
    total = screen.sum()
    vis = compute_visibility(screen)

    # 计算等效衍射角（主峰半宽）
    center = SOURCE_Y
    half_max = screen[center] * 0.5 if screen[center] > 0 else screen.max() * 0.5
    # 找半高全宽
    above_half = np.where(screen > half_max)[0]
    if len(above_half) >= 2:
        fwhm = above_half[-1] - above_half[0]
    else:
        fwhm = 0

    # 等效波长：从一级峰位置推算
    peaks = []
    for y in range(1, HEIGHT - 1):
        if screen[y] > screen[y-1] and screen[y] > screen[y+1] and screen[y] > screen.max() * 0.05:
            peaks.append((y, screen[y]))
    peaks_sorted = sorted(peaks, key=lambda p: p[1], reverse=True)

    lambda_eff = 0.0
    if len(peaks_sorted) >= 2:
        # 取最高峰和第二高峰的间距
        y_peaks = sorted([p[0] for p in peaks_sorted[:3]])
        if len(y_peaks) >= 2:
            # 从双缝公式反推：Δy = λL/d
            d = abs(SLIT2_Y - SLIT1_Y)
            L = SCREEN_X - BAR_X
            dy = abs(y_peaks[-1] - y_peaks[0]) / max(len(y_peaks) - 1, 1)
            lambda_eff = dy * d / L

    results.append({
        'S': S,
        'vis': vis,
        'total': total,
        'fwhm': fwhm,
        'lambda_eff': lambda_eff,
    })

    if i % 8 == 0:
        print(f"  S={S:.3f}  V={vis:.4f}  λ_eff={lambda_eff:.2f}  FWHM={fwhm}")

S_arr = np.array([r['S'] for r in results])
V_arr = np.array([r['vis'] for r in results])
L_arr = np.array([r['lambda_eff'] for r in results])
T_arr = np.array([r['total'] for r in results])
F_arr = np.array([r['fwhm'] for r in results])

# 找对比度最高的S值
best_idx = np.argmax(V_arr)
best_S = S_arr[best_idx]
best_V = V_arr[best_idx]
print(f"\n最优对比度: V={best_V:.4f} 在 S={best_S:.4f}")
print(f"最优 S/A = {best_S/A:.4f}")

# 一些有意思的无量纲数
alpha_fine = 1/137.036   # 精细结构常数
sqrt2 = np.sqrt(2)
pi_inv = 1/np.pi
print(f"\n参考值（纯好奇）：")
print(f"  精细结构常数 α       = {alpha_fine:.6f}")
print(f"  1/π                  = {pi_inv:.6f}")
print(f"  1/√2                 = {1/sqrt2:.6f}")
print(f"  最优 S/A             = {best_S:.6f}")
print(f"  最优 S/A / (1/√2)   = {best_S * sqrt2:.4f}")

# ============================================================
# 分析：有效波长 vs S 的关系
# ============================================================
valid = L_arr > 0.1
if valid.sum() > 3:
    from numpy.polynomial import polynomial as P
    coeffs = np.polyfit(np.log(S_arr[valid] + 0.001), np.log(L_arr[valid] + 0.001), 1)
    lambda_power = coeffs[0]
    print(f"\n有效波长幂律: λ_eff ∝ S^{lambda_power:.3f}")
    # 理论预言：λ_eff ∝ S^(-0.5) 或类似？

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.patch.set_facecolor('#0d1117')
for ax in axes.flat:
    ax.set_facecolor('#0d1117')
    ax.tick_params(colors='#8b949e')
    for spine in ax.spines.values():
        spine.set_color('#30363d')

# 图1：V vs S
ax = axes[0][0]
ax.plot(S_arr, V_arr, color='#58a6ff', linewidth=2)
ax.axvline(best_S, color='#f78166', linestyle='--', linewidth=2,
           label=f'最优 S={best_S:.3f}')
ax.scatter([best_S], [best_V], color='#ffa657', s=150, zorder=6)
ax.set_title('干涉对比度 vs S参数', color='white', fontsize=11)
ax.set_xlabel('侧向耦合强度 S', color='#8b949e')
ax.set_ylabel('干涉对比度 V', color='#8b949e')
legend_kw(ax, facecolor='#161b22')
ax.grid(True, alpha=0.15, color='#30363d')

# 图2：有效波长 vs S
ax = axes[0][1]
ax.plot(S_arr[valid], L_arr[valid], color='#3fb950', linewidth=2, marker='o',
        markersize=4)
ax.set_title('等效波长 vs S参数\n（从峰位反推）', color='white', fontsize=11)
ax.set_xlabel('侧向耦合强度 S', color='#8b949e')
ax.set_ylabel('等效波长 λ_eff（格点）', color='#8b949e')
ax.grid(True, alpha=0.15, color='#30363d')

# 图3：S×V 乘积（探索守恒量）
ax = axes[0][2]
SV_product = S_arr * V_arr
ax.plot(S_arr, SV_product, color='#ffa657', linewidth=2)
ax.axhline(SV_product.max(), color='#8b949e', linestyle=':', linewidth=1)
ax.set_title('S × V 乘积\n（是否有守恒量？）', color='white', fontsize=11)
ax.set_xlabel('S', color='#8b949e')
ax.set_ylabel('S × V', color='#8b949e')
ax.grid(True, alpha=0.15, color='#30363d')

# 图4：在最优S值附近的精细扫描
S_fine = np.linspace(max(0.01, best_S - 0.15), min(0.80, best_S + 0.15), 30)
V_fine = []
print(f"\n精细扫描 S ∈ [{S_fine[0]:.3f}, {S_fine[-1]:.3f}]...")
for S_f in S_fine:
    g = np.zeros((HEIGHT, WIDTH))
    g[SOURCE_Y, SOURCE_X] = 1000.0
    b = barrier.copy()
    g = propagate_double_slit_n_steps(g, b, A, S_f, B, LAM, STEPS)
    V_fine.append(compute_visibility(g[:, SCREEN_X]))

ax = axes[1][0]
ax.plot(S_fine, V_fine, color='#79c0ff', linewidth=2.5, marker='o', markersize=5)
ax.axvline(best_S, color='#f78166', linestyle='--', linewidth=2,
           label=f'粗扫最优 S={best_S:.3f}')
fine_best = S_fine[np.argmax(V_fine)]
ax.axvline(fine_best, color='#3fb950', linestyle=':', linewidth=2,
           label=f'精扫最优 S={fine_best:.3f}')
ax.set_title(f'最优S附近精细扫描\n精扫最优 S={fine_best:.4f}', color='white', fontsize=11)
ax.set_xlabel('S', color='#8b949e')
ax.set_ylabel('对比度 V', color='#8b949e')
legend_kw(ax, facecolor='#161b22')
ax.grid(True, alpha=0.15, color='#30363d')

# 图5：各S下的干涉图样（代表性）
ax = axes[1][1]
y_axis = np.arange(HEIGHT) - SOURCE_Y
S_showcase = [0.05, 0.15, best_S, 0.50, 0.70]
showcase_colors = ['#f0e68c', '#87ceeb', '#f78166', '#98fb98', '#dda0dd']
for S_show, sc in zip(S_showcase, showcase_colors):
    g = np.zeros((HEIGHT, WIDTH))
    g[SOURCE_Y, SOURCE_X] = 1000.0
    g = propagate_double_slit_n_steps(g, barrier, A, S_show, B, LAM, STEPS)
    s = g[:, SCREEN_X]
    if s.max() > 1e-6:
        lbl = f'S={S_show}'
        if abs(S_show - best_S) < 0.01:
            lbl += ' ★最优'
        ax.plot(y_axis, s / s.max(), color=sc, linewidth=1.5, alpha=0.85, label=lbl)
ax.set_title('代表性S值的干涉图样', color='white', fontsize=11)
ax.set_xlabel('Y 位置（相对中心）', color='#8b949e')
ax.set_ylabel('归一化强度', color='#8b949e')
legend_kw(ax, facecolor='#161b22', fontsize=8)
ax.grid(True, alpha=0.15, color='#30363d')

# 图6：发现总结
ax = axes[1][2]
ax.axis('off')
summary = (
    "发现F：S参数意义\n\n"
    f"  最优 S/A = {fine_best:.4f}\n\n"
    "参考物理常数：\n"
    f"  精细结构常数 α = {alpha_fine:.6f}\n"
    f"  1/π            = {pi_inv:.6f}\n"
    f"  1/√2           = {1/sqrt2:.6f}\n\n"
    f"  比值 (S_opt)/(1/√2) = {fine_best * sqrt2:.4f}\n\n"
    "物理猜想：\n"
    "  S/A 可能对应某种真实的\n"
    "  光-介质耦合常数。\n\n"
    "  如果在不同格点尺寸下\n"
    "  最优S/A收敛到同一个数，\n"
    "  这将是一个重要发现。\n\n"
    "  下一步：\n"
    "  改变格点间距，验证\n"
    "  最优S/A是否尺度不变。"
)
ax.text(0.05, 0.95, summary, transform=ax.transAxes,
        color='white', fontsize=9.5, va='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#161b22', alpha=0.9, pad=0.8))

plt.suptitle(f'发现F：S参数物理意义——最优耦合常数探索\n'
             f'精扫最优 S={fine_best:.4f}  A={A}  S/A={fine_best:.4f}',
             color='white', fontsize=13)
plt.tight_layout()
plt.savefig('discover_coupling_constant.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117')
print("\n图片已保存: discover_coupling_constant.png")
print(f"\n最终结论：最优S/A = {fine_best:.6f}")
print("这个数有没有物理意义，值得进一步研究。")
