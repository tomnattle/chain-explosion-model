"""
发现E：测量的连续性——量子力学最大的疑惑
==========================================
"他们在思考的" — 测量问题（Measurement Problem）

量子力学的困境：
  - 测量之前：粒子处于叠加态
  - 测量之后：波函数"坍缩"为确定值
  - 坍缩是怎么发生的？没有人知道。
  - 这叫"测量问题"，是量子力学最大的未解问题之一

CE模型的回答：
  - 测量 = 局域吸收
  - 吸收是连续的（0% → 100%）
  - 干涉消失是连续的，不是突变
  - "坍缩"其实是能量被局部吸走的连续过程

本实验系统验证：
1. 吸收率从0到1，干涉对比度如何连续变化
2. 吸收器大小从0到大，干涉连续消失
3. 吸收器位置（主路径 vs 旁路），效果如何不同
4. 关键问题：有没有一个"阈值"使干涉突然消失？
   （量子力学说有：测量要么发生要么不发生）
   （CE模型说没有：一切连续）
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mpl_compat import legend_kw
from ce_engine_v2 import (propagate_double_slit_absorber_mask_n_steps,
                           compute_visibility)
from chain_explosion_numba import set_circle_mask

# ============================================================
# 基础参数
# ============================================================
HEIGHT    = 201
WIDTH     = 400
A         = 1.0
S         = 0.30
B         = 0.05
LAM       = 0.90
SOURCE_X  = 5
SOURCE_Y  = HEIGHT // 2
BAR_X     = 150
SLIT1_Y   = HEIGHT // 2 - 25
SLIT2_Y   = HEIGHT // 2 + 25
SLIT_W    = 6
SCREEN_X  = WIDTH - 15
STEPS     = 500

# 吸收器放在上缝正后方
ABS_X     = BAR_X + 5
ABS_Y     = SLIT1_Y + SLIT_W // 2

print("=" * 65)
print("发现E：测量的连续性——量子坍缩是突变还是渐变？")
print("=" * 65)

# ============================================================
# 扫描1：吸收率 0 → 1，固定大小
# ============================================================
print("\n[扫描1] 吸收率 0→1（吸收器半径=8px）")
ratios = np.linspace(0, 1, 21)
vis_ratio = []

barrier = np.zeros((HEIGHT, WIDTH), dtype=bool)
barrier[:, BAR_X] = True
barrier[SLIT1_Y:SLIT1_Y + SLIT_W, BAR_X] = False
barrier[SLIT2_Y:SLIT2_Y + SLIT_W, BAR_X] = False

absorber = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
set_circle_mask(absorber, ABS_X, ABS_Y, 8)

for ratio in ratios:
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0
    grid = propagate_double_slit_absorber_mask_n_steps(
        grid, barrier, absorber, ratio, A, S, B, LAM, STEPS)
    screen = grid[:, SCREEN_X]
    v = compute_visibility(screen)
    vis_ratio.append(v)
    print(f"  吸收率={ratio:.2f}  V={v:.4f}")

# 检测是否有突变阈值
dV = np.diff(vis_ratio)
max_drop_idx = np.argmax(np.abs(dV))
max_drop = abs(dV[max_drop_idx])
print(f"\n最大单步下降: ΔV={max_drop:.4f} 在吸收率={ratios[max_drop_idx]:.2f}→{ratios[max_drop_idx+1]:.2f}")
if max_drop > 0.15:
    threshold_verdict = (
        f"[警告] 存在较强的非线性下降（在吸收率≈{ratios[max_drop_idx]:.2f}处）"
    )
else:
    threshold_verdict = "[OK] 干涉消失是连续的，没有突变阈值"
print(threshold_verdict)

# ============================================================
# 扫描2：吸收器大小 0 → 40px，固定吸收率
# ============================================================
print("\n[扫描2] 吸收器大小 0→40px（吸收率=0.9）")
radii = [0, 2, 4, 6, 8, 10, 15, 20, 30, 40]
vis_radius = []

for radius in radii:
    absorber2 = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    if radius > 0:
        set_circle_mask(absorber2, ABS_X, ABS_Y, radius)
    else:
        absorber2[ABS_Y, ABS_X] = True

    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0
    grid = propagate_double_slit_absorber_mask_n_steps(
        grid, barrier, absorber2, 0.9, A, S, B, LAM, STEPS)
    screen = grid[:, SCREEN_X]
    v = compute_visibility(screen)
    vis_radius.append(v)
    print(f"  半径={radius:2d}px  V={v:.4f}")

# ============================================================
# 扫描3：吸收器位置 —— 主路径 vs 旁路
# ============================================================
print("\n[扫描3] 吸收器位置扫描（Y方向）")
y_positions = list(range(SOURCE_Y - 60, SOURCE_Y + 65, 10))
vis_position = []
slit_centers = [SLIT1_Y + SLIT_W//2, SLIT2_Y + SLIT_W//2]

for abs_y in y_positions:
    if abs_y < 0 or abs_y >= HEIGHT:
        vis_position.append(np.nan)
        continue
    absorber3 = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
    set_circle_mask(absorber3, ABS_X, abs_y, 8)
    grid = np.zeros((HEIGHT, WIDTH))
    grid[SOURCE_Y, SOURCE_X] = 1000.0
    grid = propagate_double_slit_absorber_mask_n_steps(
        grid, barrier, absorber3, 0.9, A, S, B, LAM, STEPS)
    screen = grid[:, SCREEN_X]
    v = compute_visibility(screen)
    vis_position.append(v)
    label = ""
    if abs(abs_y - slit_centers[0]) < 5:
        label = " ← 上缝"
    elif abs(abs_y - slit_centers[1]) < 5:
        label = " ← 下缝"
    elif abs(abs_y - SOURCE_Y) < 5:
        label = " ← 中心"
    print(f"  Y={abs_y:3d}  V={v:.4f}{label}")

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

# 图1：吸收率 vs 对比度
ax = axes[0][0]
ax.plot(ratios, vis_ratio, color='#58a6ff', linewidth=2.5, marker='o', markersize=6)
ax.axhline(vis_ratio[0], color='#3fb950', linestyle=':', linewidth=1.5, alpha=0.6,
           label='无吸收基准')
ax.set_title('吸收率 → 干涉对比度\n（测量是连续的吗？）', color='white', fontsize=11)
ax.set_xlabel('吸收率（0=无测量，1=完全测量）', color='#8b949e')
ax.set_ylabel('干涉对比度 V', color='#8b949e')
ax.text(0.05, 0.15, threshold_verdict, transform=ax.transAxes,
        color='#ffa657', fontsize=8, va='bottom',
        bbox=dict(boxstyle='round', facecolor='#161b22', alpha=0.8))
legend_kw(ax, facecolor='#161b22')
ax.grid(True, alpha=0.15, color='#30363d')
ax.set_ylim(0, max(vis_ratio) * 1.15)

# 图2：导数（下降速率）
ax = axes[0][1]
dV_dr = np.gradient(vis_ratio, ratios)
ax.plot(ratios, dV_dr, color='#f78166', linewidth=2, marker='o', markersize=5)
ax.axhline(0, color='#8b949e', linestyle='--', linewidth=1)
ax.fill_between(ratios, dV_dr, 0, where=np.array(dV_dr) < 0,
                color='#f78166', alpha=0.3, label='对比度下降区')
ax.set_title('对比度变化速率 dV/d(ratio)\n（有没有突变点？）', color='white', fontsize=11)
ax.set_xlabel('吸收率', color='#8b949e')
ax.set_ylabel('dV/d(ratio)', color='#8b949e')
legend_kw(ax, facecolor='#161b22')
ax.grid(True, alpha=0.15, color='#30363d')

# 图3：吸收器大小 vs 对比度
ax = axes[0][2]
ax.plot(radii, vis_radius, color='#ffa657', linewidth=2.5, marker='s', markersize=7)
ax.set_title('吸收器大小 → 干涉对比度\n（测量精度的影响）', color='white', fontsize=11)
ax.set_xlabel('吸收器半径（格点）', color='#8b949e')
ax.set_ylabel('干涉对比度 V', color='#8b949e')
ax.grid(True, alpha=0.15, color='#30363d')

# 图4：吸收器位置 vs 对比度
ax = axes[1][0]
valid_mask = [not np.isnan(v) for v in vis_position]
y_pos_valid = [y_positions[i] - SOURCE_Y for i, v in enumerate(valid_mask) if v]
vis_pos_valid = [vis_position[i] for i, v in enumerate(valid_mask) if v]
ax.plot(y_pos_valid, vis_pos_valid, color='#79c0ff', linewidth=2, marker='D', markersize=6)
# 标注缝位置
for sc in slit_centers:
    ax.axvline(sc - SOURCE_Y, color='#f78166', linestyle='--', linewidth=1.5,
               alpha=0.7, label=f'缝位置 Y={sc}')
ax.set_title('吸收器Y位置 → 干涉对比度\n（主路径 vs 旁路）', color='white', fontsize=11)
ax.set_xlabel('吸收器Y位置（相对中心）', color='#8b949e')
ax.set_ylabel('干涉对比度 V', color='#8b949e')
legend_kw(ax, facecolor='#161b22', fontsize=8)
ax.grid(True, alpha=0.15, color='#30363d')

# 图5：三维总结图（吸收率 × 大小 → V）
ax = axes[1][1]
# 快速扫描：几个代表性组合
ratio_grid = [0.0, 0.3, 0.6, 1.0]
radius_grid = [2, 8, 20]
V_matrix = np.zeros((len(ratio_grid), len(radius_grid)))

for i, ratio in enumerate(ratio_grid):
    for j, rad in enumerate(radius_grid):
        absorber_m = np.zeros((HEIGHT, WIDTH), dtype=np.bool_)
        set_circle_mask(absorber_m, ABS_X, ABS_Y, rad)
        g = np.zeros((HEIGHT, WIDTH))
        g[SOURCE_Y, SOURCE_X] = 1000.0
        g = propagate_double_slit_absorber_mask_n_steps(
            g, barrier, absorber_m, ratio, A, S, B, LAM, STEPS)
        V_matrix[i, j] = compute_visibility(g[:, SCREEN_X])

im = ax.imshow(V_matrix, cmap='RdYlGn', aspect='auto',
               vmin=0, vmax=max(vis_ratio[0], 0.01))
ax.set_xticks(range(len(radius_grid)))
ax.set_xticklabels([f'r={r}' for r in radius_grid], color='#8b949e')
ax.set_yticks(range(len(ratio_grid)))
ax.set_yticklabels([f'{r:.1f}' for r in ratio_grid], color='#8b949e')
ax.set_title('干涉对比度热力图\n吸收率 × 吸收器大小', color='white', fontsize=11)
ax.set_xlabel('吸收器大小', color='#8b949e')
ax.set_ylabel('吸收率', color='#8b949e')
plt.colorbar(im, ax=ax, label='对比度 V').ax.tick_params(colors='#8b949e')
for i in range(len(ratio_grid)):
    for j in range(len(radius_grid)):
        ax.text(j, i, f'{V_matrix[i,j]:.2f}', ha='center', va='center',
                color='black', fontsize=9, fontweight='bold')

# 图6：与量子力学坍缩对比
ax = axes[1][2]
ax.axis('off')
qm_text = (
    "发现E：核心对比\n\n"
    "量子力学的立场：\n"
    "  测量 = 波函数坍缩\n"
    "  坍缩是瞬时的、非连续的\n"
    "  '测量发生' vs '测量不发生'\n"
    "  没有中间状态\n\n"
    "CE模型的立场：\n"
    "  测量 = 局域能量吸收\n"
    "  吸收率0→1：对比度连续变化\n"
    "  没有突变阈值\n"
    "  '多少测量' 决定 '多少干涉'\n\n"
    "本实验结论：\n"
    f"  {threshold_verdict}\n\n"
    "这是可以做真实实验区分的：\n"
    "  用可调透过率的探测器，\n"
    "  看干涉条纹是否连续消失。"
)
ax.text(0.05, 0.95, qm_text, transform=ax.transAxes,
        color='white', fontsize=9.5, va='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#161b22', alpha=0.9, pad=0.8))

plt.suptitle('发现E：测量连续性——量子坍缩是突变还是渐变？',
             color='white', fontsize=14)
plt.tight_layout()
plt.savefig('discover_E_measurement_continuity.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
print("\n图片已保存: discover_E_measurement_continuity.png")
print("\n" + "=" * 65)
print("发现E 总结")
print("=" * 65)
print(f"  {threshold_verdict}")
print()
print("  量子力学用'测量问题'描述坍缩的神秘性，")
print("  CE模型给出了一个完全局域、连续的替代解释。")
print("  如果真实实验测到连续过渡：CE模型胜出。")
