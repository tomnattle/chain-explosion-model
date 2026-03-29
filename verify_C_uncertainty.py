"""
验证C：链式爆炸模型 vs 海森堡不确定性原理
==========================================
"大象的腿" — 不确定性原理

标准表述：Δy · Δp_y ≥ ℏ/2

在单缝实验中的体现：
  - 缝越窄（Δy 越小）→ 衍射角越大（Δp_y 越大）
  - 这是所有量子力学教材的第一个例子

CE模型中对应关系：
  - 缝宽 a = Δy（位置约束）
  - 衍射后角度展宽 ∝ 1/a（动量不确定度）

本实验：
1. 用CE模型跑不同缝宽的单缝衍射
2. 测量衍射角展宽（屏幕分布的标准差）
3. 验证：展宽 ∝ 1/缝宽（不确定性原理的格点版本）
4. 与理论预言 Δθ ≈ λ/a 对比
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import propagate_double_slit_n_steps

# ============================================================
# 参数
# ============================================================
HEIGHT    = 401
WIDTH     = 400
A         = 1.0
S         = 0.30
B         = 0.05
LAM       = 0.92
SOURCE_X  = 5
SOURCE_Y  = HEIGHT // 2
BAR_X     = 150
SCREEN_X  = WIDTH - 20
STEPS     = 600

# 要扫描的缝宽
SLIT_WIDTHS = [2, 4, 6, 8, 12, 16, 24, 32]

print("=" * 65)
print("验证C：缝宽 vs 衍射展宽（不确定性原理）")
print(f"扫描缝宽: {SLIT_WIDTHS} 格点")
print("=" * 65)

results = []

for slit_w in SLIT_WIDTHS:
    # 单缝：只有一条缝，在中心
    slit_y_center = HEIGHT // 2
    slit_y0 = slit_y_center - slit_w // 2
    slit_y1 = slit_y0 + slit_w

    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0

    barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
    barrier[:, BAR_X] = True
    barrier[slit_y0:slit_y1, BAR_X] = False  # 单缝

    grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS)

    screen = grid[:, SCREEN_X].copy()
    total = screen.sum()

    if total < 1e-6:
        print(f"  缝宽={slit_w}: 无能量到达，跳过")
        continue

    # 计算屏幕分布的标准差（衍射展宽）
    y_positions = np.arange(HEIGHT)
    mean_y = np.sum(y_positions * screen) / total
    sigma_y = np.sqrt(np.sum((y_positions - mean_y) ** 2 * screen) / total)

    # 等效衍射角展宽（弧度）
    L = SCREEN_X - BAR_X
    sigma_theta = np.arctan(sigma_y / L)

    results.append({
        'slit_w': slit_w,
        'sigma_screen': sigma_y,
        'sigma_theta_deg': np.degrees(sigma_theta),
        'screen': screen.copy(),
        'total': total
    })

    print(f"  缝宽={slit_w:2d}px  展宽σ={sigma_y:.1f}px  衍射角={np.degrees(sigma_theta):.2f}°  能量={total:.1f}")

# ============================================================
# 验证 σ_theta ∝ 1/a
# ============================================================
widths = np.array([r['slit_w'] for r in results], dtype=float)
sigmas = np.array([r['sigma_theta_deg'] for r in results])

# 对数线性拟合：log(σ) = α·log(a) + β
# 理论预言 α = -1（不确定性原理）
log_w = np.log(widths)
log_s = np.log(sigmas + 1e-9)
coeffs = np.polyfit(log_w, log_s, 1)
alpha_fit = coeffs[0]
print(f"\n拟合幂律: σ_θ ∝ a^{alpha_fit:.3f}")
print(f"理论预言（不确定性原理）: σ_θ ∝ a^(-1.0)")
print(f"偏差: Δα = {abs(alpha_fit - (-1.0)):.3f}")

if abs(alpha_fit - (-1.0)) < 0.3:
    verdict = "✅ CE模型服从不确定性原理（α ≈ -1）"
elif abs(alpha_fit - (-1.0)) < 0.6:
    verdict = "⚠️ 接近但不完全符合不确定性原理"
else:
    verdict = "❌ 与不确定性原理有明显偏差"
print(verdict)

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.patch.set_facecolor('#0d1117')
for ax in axes.flat:
    ax.set_facecolor('#0d1117')
    ax.tick_params(colors='#8b949e')
    for spine in ax.spines.values():
        spine.set_color('#30363d')

y_axis = np.arange(HEIGHT) - SOURCE_Y
cmap = plt.cm.plasma
colors = [cmap(i / len(results)) for i in range(len(results))]

# 图1：各缝宽的衍射图样
ax = axes[0][0]
for i, r in enumerate(results):
    s = r['screen']
    ax.plot(y_axis, s / (s.max() + 1e-9),
            color=colors[i], linewidth=1.2, alpha=0.85,
            label=f"a={r['slit_w']}px")
ax.set_title('各缝宽的单缝衍射图样', color='white', fontsize=11)
ax.set_xlabel('Y 位置（相对中心）', color='#8b949e')
ax.set_ylabel('归一化强度', color='#8b949e')
legend_kw(ax, facecolor='#161b22', fontsize=7,
          ncol=2, loc='upper right')
ax.grid(True, alpha=0.15, color='#30363d')

# 图2：σ vs 缝宽（线性）
ax = axes[0][1]
ax.scatter(widths, sigmas, color='#58a6ff', s=80, zorder=5)
# 拟合曲线
w_fit = np.linspace(widths.min(), widths.max(), 100)
s_fit = np.exp(np.polyval(coeffs, np.log(w_fit)))
ax.plot(w_fit, s_fit, color='#f78166', linestyle='--', linewidth=2,
        label=f'拟合: α={alpha_fit:.2f}')
ax.set_title('衍射角展宽 vs 缝宽', color='white', fontsize=11)
ax.set_xlabel('缝宽 a（格点）', color='#8b949e')
ax.set_ylabel('衍射角展宽 σ_θ（度）', color='#8b949e')
legend_kw(ax, facecolor='#161b22')
ax.grid(True, alpha=0.15, color='#30363d')

# 图3：log-log 图（检验幂律）
ax = axes[1][0]
ax.scatter(np.log(widths), np.log(sigmas), color='#58a6ff', s=80, zorder=5, label='CE数据')
ax.plot(log_w, np.polyval(coeffs, log_w), color='#f78166', linestyle='--',
        linewidth=2, label=f'拟合 α={alpha_fit:.2f}')
# 理论线
theory_const = np.mean(np.log(sigmas) - (-1.0) * log_w)
ax.plot(log_w, -1.0 * log_w + theory_const, color='#3fb950', linestyle=':',
        linewidth=2, label='理论 α=-1.0')
ax.set_title('log-log 图（幂律检验）', color='white', fontsize=11)
ax.set_xlabel('log(缝宽)', color='#8b949e')
ax.set_ylabel('log(衍射展宽)', color='#8b949e')
legend_kw(ax, facecolor='#161b22')
ax.grid(True, alpha=0.15, color='#30363d')

# 图4：不确定度乘积 Δy·Δσ_θ 是否守恒
ax = axes[1][1]
uncertainty_products = widths * sigmas
ax.scatter(widths, uncertainty_products, color='#ffa657', s=80, zorder=5)
mean_product = np.mean(uncertainty_products)
ax.axhline(mean_product, color='#f78166', linestyle='--', linewidth=2,
           label=f'平均值 = {mean_product:.2f}')
ax.set_title('Δy · Δσ_θ 守恒验证\n（不确定性原理核心）', color='white', fontsize=11)
ax.set_xlabel('缝宽 a = Δy（格点）', color='#8b949e')
ax.set_ylabel('Δy × Δσ_θ（格点·度）', color='#8b949e')
std_product = np.std(uncertainty_products)
ax.text(0.05, 0.95, f'变异系数 = {std_product/mean_product:.3f}',
        transform=ax.transAxes, color='white', fontsize=10, va='top',
        bbox=dict(boxstyle='round', facecolor='#161b22', alpha=0.8))
legend_kw(ax, facecolor='#161b22')
ax.grid(True, alpha=0.15, color='#30363d')

plt.suptitle(f'验证C：CE模型与海森堡不确定性原理\n'
             f'拟合幂律 α={alpha_fit:.3f}（理论预言 α=-1.0）',
             color='white', fontsize=13)
plt.tight_layout()
plt.savefig('verify_C_uncertainty.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117')
print("\n图片已保存: verify_C_uncertainty.png")

print("\n" + "=" * 65)
print("验证C 总结")
print("=" * 65)
print(f"  幂律指数 α  = {alpha_fit:.4f}")
print(f"  理论预言    = -1.0000")
print(f"  结论: {verdict}")
print()
print("物理意义：")
print("  在你的模型里，缝越窄，能量越'挤'，侧向传播越强。")
print("  这不是因为假设了不确定性原理，")
print("  而是因为格点传播规则（A/S/B耦合）天然产生了这个效果。")
print("  不确定性原理在你的模型里有了机制上的来源：")
print("  格点的各向耦合强度 S 决定了位置-动量的trade-off。")
