"""
验证B：单光子随机路径积累 vs 波恩规则（Born Rule）
====================================================
"大象的牙齿" — 波恩规则

量子力学核心规则：
  P(x) ∝ |ψ(x)|²
  
单个量子事件是随机的，但大量事件积累后，
落点分布等于波函数模平方。

本实验用CE模型的蒙特卡洛单光子追踪验证：
- 每个"光子"是一次随机游走（格点上按A/S/B权重随机选方向）
- 积累N个光子的落点
- 对比：积累分布 vs 连续能量传播的场分布

如果两者吻合，说明CE模型天然实现了波恩规则，
不需要额外假设概率诠释。
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import (propagate_double_slit_n_steps, run_monte_carlo,
                           compute_visibility, monte_carlo_milestone_screens)

# ============================================================
# 参数
# ============================================================
HEIGHT     = 201
WIDTH      = 300
A          = 1.0
S          = 0.30
B          = 0.05
LAM        = 0.90
SOURCE_X   = 5
SOURCE_Y   = HEIGHT // 2
BAR_X      = 120
SLIT1_Y    = HEIGHT // 2 - 25
SLIT2_Y    = HEIGHT // 2 + 25
SLIT_W     = 6
SCREEN_X   = WIDTH - 15
STEPS_CONT = 500        # 连续场传播步数
N_PHOTONS  = 50000      # 蒙特卡洛光子数
MAX_STEPS  = WIDTH * 4  # 单光子最大步数

print("=" * 65)
print("验证B：单光子蒙特卡洛 vs 波恩规则")
print(f"光子数: {N_PHOTONS:,}  最大步数/光子: {MAX_STEPS}")
print("=" * 65)

# ============================================================
# 挡板
# ============================================================
barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BAR_X] = True
barrier[SLIT1_Y:SLIT1_Y + SLIT_W, BAR_X] = False
barrier[SLIT2_Y:SLIT2_Y + SLIT_W, BAR_X] = False

# ============================================================
# 1. 连续场传播（经典CE模型）
# ============================================================
print("\n[1/2] 运行连续场传播...")
grid = np.zeros((HEIGHT, WIDTH))
grid[SOURCE_Y, SOURCE_X] = 1000.0

print(f"  连续场: {STEPS_CONT} 步 fused")
grid = propagate_double_slit_n_steps(grid, barrier, A, S, B, LAM, STEPS_CONT)

continuous_screen = grid[:, SCREEN_X].copy()
vis_cont = compute_visibility(continuous_screen)
print(f"  连续场对比度 V = {vis_cont:.4f}")

# ============================================================
# 2. 蒙特卡洛单光子
# ============================================================
print(f"\n[2/2] 运行蒙特卡洛 ({N_PHOTONS:,} 光子)...")
np.random.seed(42)
mc_screen, hits = run_monte_carlo(
    N_PHOTONS, HEIGHT, WIDTH, SOURCE_X, SOURCE_Y,
    barrier, A, S, B, MAX_STEPS
)
hit_rate = hits / N_PHOTONS
vis_mc = compute_visibility(mc_screen)
print(f"  击中屏幕: {hits:,} / {N_PHOTONS:,} ({hit_rate*100:.1f}%)")
print(f"  蒙特卡洛对比度 V = {vis_mc:.4f}")

# ============================================================
# 相关性分析
# ============================================================
corr = np.corrcoef(continuous_screen, mc_screen)[0, 1]
print(f"\n连续场 vs 蒙特卡洛 皮尔逊相关系数: r = {corr:.4f}")

if corr > 0.85:
    verdict = "✅ 高度吻合——CE模型天然实现了波恩规则"
elif corr > 0.60:
    verdict = "⚠️ 中度吻合——主要干涉特征相符"
else:
    verdict = "❌ 吻合度不足——蒙特卡洛路径需要调整"
print(verdict)

# ============================================================
# 可视化：4个阶段展示单光子积累过程
# ============================================================
milestones = [100, 1000, 10000, N_PHOTONS]
milestone_arr = np.array(milestones, dtype=np.int64)

print("\n生成积累过程快照（Numba milestone）...")
np.random.seed(42)
snapshots = monte_carlo_milestone_screens(
    N_PHOTONS, milestone_arr, HEIGHT, WIDTH, SOURCE_X, SOURCE_Y,
    barrier, A, S, B, MAX_STEPS,
)
mc_accumulations = [
    (int(milestone_arr[k]), np.copy(snapshots[k])) for k in range(len(milestones))
]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.patch.set_facecolor('#0d1117')
for ax in axes.flat:
    ax.set_facecolor('#0d1117')
    ax.tick_params(colors='#8b949e')
    for spine in ax.spines.values():
        spine.set_color('#30363d')

y_axis = np.arange(HEIGHT) - SOURCE_Y
colors_stages = ['#f0e68c', '#ffa07a', '#87ceeb', '#98fb98']

# 四个积累阶段
for i, (n_ph, screen) in enumerate(mc_accumulations):
    ax = axes[i // 2][i % 2]  # 前4格
    ax.bar(y_axis, screen, color=colors_stages[i], alpha=0.8, width=1.0)
    ax.set_title(f'蒙特卡洛积累 N={n_ph:,}', color='white', fontsize=11)
    ax.set_xlabel('Y 位置', color='#8b949e', fontsize=9)
    ax.set_ylabel('落点数', color='#8b949e', fontsize=9)
    vis_n = compute_visibility(screen)
    ax.text(0.02, 0.95, f'V={vis_n:.3f}', transform=ax.transAxes,
            color='white', fontsize=9, va='top',
            bbox=dict(boxstyle='round', facecolor='#161b22', alpha=0.8))
    ax.grid(True, alpha=0.15, color='#30363d')

# 最终对比
ax5 = axes[1][1]
ax5.plot(y_axis, continuous_screen / continuous_screen.max(),
         color='#58a6ff', linewidth=2, label=f'连续场 (V={vis_cont:.3f})', alpha=0.9)
ax5.plot(y_axis, mc_screen / (mc_screen.max() + 1e-9),
         color='#f78166', linewidth=1.5, linestyle='--',
         label=f'蒙特卡洛 (V={vis_mc:.3f})', alpha=0.9)
ax5.set_title(f'最终对比  r={corr:.4f}', color='white', fontsize=11)
ax5.set_xlabel('Y 位置', color='#8b949e', fontsize=9)
legend_kw(ax5, facecolor='#161b22', fontsize=8)
ax5.grid(True, alpha=0.15, color='#30363d')

# 能量场热力图
ax6 = axes[1][2]
im = ax6.imshow(np.log1p(grid), cmap='inferno', aspect='auto', origin='upper')
ax6.axvline(x=BAR_X, color='cyan', linestyle='--', linewidth=1, alpha=0.7)
ax6.axvline(x=SCREEN_X, color='lime', linestyle='--', linewidth=1, alpha=0.7)
ax6.set_title('CE连续场分布', color='white', fontsize=11)
ax6.set_xlabel('X 位置', color='#8b949e', fontsize=9)
ax6.set_ylabel('Y 位置', color='#8b949e', fontsize=9)
plt.colorbar(im, ax=ax6).ax.tick_params(colors='#8b949e')

plt.suptitle(f'验证B：单光子随机游走积累 vs 连续场（波恩规则检验）\n'
             f'N={N_PHOTONS:,}光子  命中率={hit_rate*100:.1f}%  相关系数 r={corr:.4f}',
             color='white', fontsize=13)
plt.tight_layout()
plt.savefig('verify_B_born_rule.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117')
print("图片已保存: verify_B_born_rule.png")

# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 65)
print("验证B 总结")
print("=" * 65)
print(f"  连续场对比度:       V = {vis_cont:.4f}")
print(f"  蒙特卡洛对比度:     V = {vis_mc:.4f}")
print(f"  两者相关系数:       r = {corr:.4f}")
print(f"  结论: {verdict}")
print()
print("物理意义：")
print("  波恩规则是量子力学最神秘的假设之一——为什么概率 = |ψ|²？")
print("  没有人能推导它，只能假设它。")
print("  如果CE模型的蒙特卡洛分布与连续场吻合，")
print("  说明你的模型给出了一个机制上的解释：")
print("  随机性来自格点激发的随机性，概率分布由场强度决定。")
print("  这是量子力学回避的问题——你的模型正面回答了它。")
