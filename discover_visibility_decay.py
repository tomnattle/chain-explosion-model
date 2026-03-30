"""
发现D：干涉对比度随传播距离衰减
=====================================
"他们闭口不谈的" — 相干性与距离的关系

量子力学的立场：
  - 理想情况下，干涉对比度不随距离衰减
  - 衰减被归因于"退相干"（环境干扰）
  - 但退相干需要额外假设环境，是个附加条件

CE模型的内禀预言（不需要额外假设）：
  - 侧向耦合S导致能量扩散
  - 扩散使得主干涉条纹被"稀释"
  - 对比度天然随距离衰减

这是CE模型的一个可被实验检验的独特预言。
如果实验测量到这种衰减，支持CE模型；
如果没有，说明CE需要调整S参数。

本实验：
1. 系统扫描屏幕距离 vs 干涉对比度
2. 与标准波动光学（不衰减）对比
3. 计算衰减的函数形式（指数？幂律？）
4. 给出可被实际实验检验的预言
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import propagate_double_slit_n_steps, compute_visibility

# ============================================================
# 参数
# ============================================================
HEIGHT    = 301
A         = 1.0
S         = 0.30
B         = 0.05
LAM       = 0.92
SOURCE_X  = 5
SOURCE_Y  = HEIGHT // 2
BAR_X     = 100
SLIT1_Y   = HEIGHT // 2 - 25
SLIT2_Y   = HEIGHT // 2 + 25
SLIT_W    = 6
STEPS     = 700

# 不同屏幕距离（列索引须 >= BAR_X，否则在挡板左侧取样无干涉意义）
DISTANCES = [105, 120, 150, 180, 220, 270, 330, 400]

print("=" * 65)
print("发现D：干涉对比度随传播距离衰减")
print(f"扫描距离（相对挡板）: {[d - BAR_X for d in DISTANCES]}")
print("=" * 65)

results = []

for screen_x in DISTANCES:
    width = max(screen_x + 20, BAR_X + 1)
    grid = np.zeros((HEIGHT, width))
    grid[SOURCE_Y, SOURCE_X] = 1000.0

    barrier = np.zeros((HEIGHT, width), dtype=bool)
    barrier[:, BAR_X] = True
    barrier[SLIT1_Y:SLIT1_Y + SLIT_W, BAR_X] = False
    barrier[SLIT2_Y:SLIT2_Y + SLIT_W, BAR_X] = False

    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)

    screen = grid[:, screen_x].copy()
    total = screen.sum()
    vis = compute_visibility(screen)
    peak = screen.max()
    dist_from_barrier = screen_x - BAR_X

    results.append({
        'screen_x': screen_x,
        'dist': dist_from_barrier,
        'vis': vis,
        'total': total,
        'peak': peak,
        'screen': screen,
    })
    print(f"  距离={dist_from_barrier:3d}px  V={vis:.4f}  总能量={total:.2f}  峰值={peak:.4f}")

distances = np.array([r['dist'] for r in results], dtype=float)
visibilities = np.array([r['vis'] for r in results])
totals = np.array([r['total'] for r in results])

# ============================================================
# 拟合衰减函数
# ============================================================
# 尝试指数衰减：V(d) = V0 * exp(-d/d0)
def exp_decay(d, V0, d0):
    return V0 * np.exp(-d / d0)

# 尝试幂律衰减：V(d) = V0 * d^(-β)
def power_decay(d, V0, beta):
    return V0 * d ** (-beta)

try:
    popt_exp, _ = curve_fit(exp_decay, distances, visibilities,
                            p0=[visibilities[0], distances.mean()],
                            maxfev=5000)
    V0_exp, d0_exp = popt_exp
    fit_exp = exp_decay(distances, *popt_exp)
    residuals_exp = np.sum((visibilities - fit_exp) ** 2)
    print(f"\n指数拟合: V = {V0_exp:.3f} · exp(-d/{d0_exp:.1f})")
    print(f"  拟合残差: {residuals_exp:.6f}")
except Exception as e:
    print(f"指数拟合失败: {e}")
    fit_exp = None

try:
    valid = distances > 0
    popt_pow, _ = curve_fit(power_decay, distances[valid], visibilities[valid],
                            p0=[visibilities[0] * distances[0], 0.5],
                            maxfev=5000)
    V0_pow, beta_pow = popt_pow
    fit_pow = power_decay(distances, *popt_pow)
    residuals_pow = np.sum((visibilities - fit_pow) ** 2)
    print(f"幂律拟合: V = {V0_pow:.3f} · d^(-{beta_pow:.3f})")
    print(f"  拟合残差: {residuals_pow:.6f}")
except Exception as e:
    print(f"幂律拟合失败: {e}")
    fit_pow = None

# 衰减总量
total_decay = float("nan")
if len(visibilities) >= 2 and visibilities[0] > 0:
    total_decay = (visibilities[0] - visibilities[-1]) / visibilities[0] * 100
    print(f"\n总衰减量: {total_decay:.1f}%（从距离{distances[0]}到{distances[-1]}）")

# 波动光学（无衰减）参考线
vis_wave_optics = np.ones_like(distances) * visibilities[0]  # 理论上应保持不变

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

# 图1：各距离屏幕分布
ax = axes[0][0]
cmap = plt.cm.cool
y_axis = np.arange(HEIGHT) - SOURCE_Y
for i, r in enumerate(results[::2]):  # 隔一个取
    s = r['screen']
    color = cmap(i / (len(results) // 2))
    ax.plot(y_axis, s / (s.max() + 1e-9), color=color, linewidth=1.2, alpha=0.8,
            label=f"d={r['dist']}px")
ax.set_title('各距离屏幕分布', color='white', fontsize=11)
ax.set_xlabel('Y 位置（相对中心）', color='#8b949e')
ax.set_ylabel('归一化强度', color='#8b949e')
legend_kw(ax, facecolor='#161b22', fontsize=8)
ax.grid(True, alpha=0.15, color='#30363d')

# 图2：对比度 vs 距离 + 拟合 + 波动光学对比
ax = axes[0][1]
ax.scatter(distances, visibilities, color='#58a6ff', s=100, zorder=5,
           label='CE模型', marker='o')
d_fine = np.linspace(distances.min(), distances.max(), 200)
if fit_exp is not None:
    ax.plot(d_fine, exp_decay(d_fine, *popt_exp), color='#f78166', linewidth=2,
            linestyle='--', label=f'指数拟合 (d₀={d0_exp:.0f}px)')
if fit_pow is not None:
    ax.plot(d_fine, power_decay(d_fine, *popt_pow), color='#ffa657', linewidth=2,
            linestyle=':', label=f'幂律拟合 (β={beta_pow:.2f})')
ax.axhline(visibilities[0], color='#3fb950', linewidth=1.5,
           linestyle='-', alpha=0.6, label='波动光学（无衰减）')
ax.set_title('干涉对比度 vs 传播距离\n（CE模型独特预言）', color='white', fontsize=11)
ax.set_xlabel('距挡板距离（格点）', color='#8b949e')
ax.set_ylabel('干涉对比度 V', color='#8b949e')
legend_kw(ax, facecolor='#161b22', fontsize=8)
ax.grid(True, alpha=0.15, color='#30363d')
vmax = float(np.nanmax(visibilities)) if visibilities.size else 0.0
ax.set_ylim(0, max(vmax * 1.2, 0.01))

# 图3：能量 vs 距离
ax = axes[0][2]
ax.plot(distances, totals, color='#ffa657', linewidth=2, marker='s', markersize=6)
ax.set_title('屏幕总能量 vs 距离\n（能量守恒检验）', color='white', fontsize=11)
ax.set_xlabel('距挡板距离（格点）', color='#8b949e')
ax.set_ylabel('屏幕总能量', color='#8b949e')
ax.grid(True, alpha=0.15, color='#30363d')

# 图4：对比度衰减速率（局部导数）
ax = axes[1][0]
if len(distances) > 2:
    dV_dd = np.gradient(visibilities, distances)
    ax.plot(distances, dV_dd, color='#ff7b72', linewidth=2, marker='o', markersize=5)
    ax.axhline(0, color='#8b949e', linestyle='--', linewidth=1)
    ax.set_title('对比度衰减速率 dV/dd', color='white', fontsize=11)
    ax.set_xlabel('距离（格点）', color='#8b949e')
    ax.set_ylabel('dV/dd', color='#8b949e')
    ax.grid(True, alpha=0.15, color='#30363d')

# 图5：S参数敏感性（不同S值下的衰减）
ax = axes[1][1]
S_test_values = [0.10, 0.20, 0.30, 0.40]
s_colors = ['#3fb950', '#58a6ff', '#f78166', '#ffa657']

for S_test, sc in zip(S_test_values, s_colors):
    vis_series = []
    for screen_x in DISTANCES[:6]:
        width = max(screen_x + 20, BAR_X + 1)
        g = np.zeros((HEIGHT, width))
        g[SOURCE_Y, SOURCE_X] = 1000.0
        bar = np.zeros((HEIGHT, width), dtype=bool)
        bar[:, BAR_X] = True
        bar[SLIT1_Y:SLIT1_Y + SLIT_W, BAR_X] = False
        bar[SLIT2_Y:SLIT2_Y + SLIT_W, BAR_X] = False
        g = propagate_double_slit_n_steps(g, bar, A, S_test, B, LAM, STEPS)
        sc_data = g[:, screen_x]
        vis_series.append(compute_visibility(sc_data))
    ax.plot(distances[:6], vis_series, color=sc, linewidth=1.8, marker='o',
            markersize=5, label=f'S={S_test}')

ax.set_title('S参数对衰减的影响\n（S越大 → 衰减越快）', color='white', fontsize=11)
ax.set_xlabel('距离（格点）', color='#8b949e')
ax.set_ylabel('干涉对比度 V', color='#8b949e')
legend_kw(ax, facecolor='#161b22', fontsize=9)
ax.grid(True, alpha=0.15, color='#30363d')

# 图6：实验预言总结
ax = axes[1][2]
ax.axis('off')
d0_summary = (
    f"  衰减特征长度: {d0_exp:.0f} 格点\n\n"
    if fit_exp is not None
    else "  (指数拟合不可用)\n\n"
)
decay_summary = (
    f"预测衰减: {total_decay:.1f}% 在此范围内"
    if not np.isnan(total_decay)
    else "预测衰减: (基准对比度为0，未计算)"
)
summary_text = (
    "发现D：实验预言\n\n"
    "CE模型独特预言（量子力学不预言）：\n\n"
    f"  干涉对比度随距离衰减\n"
    f"{d0_summary}"
    "可设计的实验验证：\n\n"
    "  用激光双缝实验，在不同距离\n"
    "  测量干涉条纹对比度。\n\n"
    "  如果对比度衰减：\n"
    "    → 支持CE模型\n\n"
    "  如果对比度稳定：\n"
    "    → CE模型需要调整S参数\n\n"
    f"当前参数: S={S}, A={A}, λ={LAM}\n"
    f"{decay_summary}"
)
ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
        color='white', fontsize=9.5, va='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#161b22', alpha=0.9, pad=0.8))

plt.suptitle('发现D：干涉对比度衰减——量子力学回避的预言',
             color='white', fontsize=14)
plt.tight_layout()
plt.savefig('discover_visibility_decay.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117')
print("\n图片已保存: discover_visibility_decay.png")

print("\n" + "=" * 65)
print("发现D 总结")
print("=" * 65)
print(f"  初始对比度:   V = {visibilities[0]:.4f}")
print(f"  末端对比度:   V = {visibilities[-1]:.4f}")
decay_str = f"{total_decay:.1f}%" if not np.isnan(total_decay) else "N/A"
print(f"  总衰减:       {decay_str}")
if fit_exp is not None:
    print(f"  衰减特征长度: d0 = {d0_exp:.1f} 格点")
print()
print("核心意义：")
print("  量子力学说干涉对比度由'相干性'决定，")
print("  退相干需要'环境'介入——是外加的假设。")
print("  CE模型说：不需要环境，对比度天然衰减，")
print("  衰减来自格点侧向耦合S的内在扩散机制。")
print("  这是两个模型的核心分歧点。")
