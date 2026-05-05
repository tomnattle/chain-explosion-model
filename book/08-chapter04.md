# 第四章 · Chapter 4

**栅格涟漪：双缝与屏上统计**  
*Ripple grid: double-slit and screen statistics*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**双缝实验**就是「光过两条缝，背后出现明暗条纹」；**可见度**粗想成**条纹清不清楚**。
> - **这章解决什么**：不用实验室，先在**电脑格子**里回答：给定规则，**能不能自己长出条纹**、条纹如何随距离/参数变糊。
> - **教科书常识**：**杨氏双缝**是经典波动光学名片；量子版会讨论**单光子**等。**本章是模型内演示**，不宣称新光学定律。
> - **本书在干什么**：用 `ce_00` 等脚本（你**不必运行**）对应「**规则 → 图样**」；后文 **NIST** 才涉及真实事件表。
> - **和物理学家们**：**不违背**波动图像的核心现象；数字只在**我们的离散规则**下有效。

> **本章任务**  
> 把第一章的泡泡**落实**为 `scripts/ce/` 里可跑的格子：双缝几何、屏上强度与**可见度**——并说明这些量如何随**距离与耦合**变化。

## 4.1　从泡泡到格子

第三章说过：**程序里每一步都会「漏」**。本章在**最干净的设定**下先看**条纹与屏统计**：`chain_explosion_numba` 内核里，能量（或强度）在二维格上按 **A、B、S** 与 **LAMBDA** 分给邻格；**一整列挡板 + 两条缝**由布尔矩阵 `barrier` 刻出来，图样是**规则推出来的**，不是后期画上去的。

## 4.2　`ce_00`：最小双缝故事

`scripts/ce/ce_00_double_slit_demo.py` 是入口：典型参数在脚本顶部（栅格宽高、**A/S/B**、**LAMBDA**、缝位、步数）。运行后你会得到屏上一条**累积能量曲线**与场的热力图。若侧向耦合 **S** 太小或衰减过猛，条纹会「糊」——这不是玄学，是**参数扫描**能复现的事。

### 一次运行快照（模型内，非实验室）

下面是一条**可复跑**的「档案式」记录，便于把**口头说有条纹**换成脚本里打印的键值。数值来自 **2026-05-05**、仓库根目录、**默认常量**、在终端设 `PYTHONPATH` 指向仓库根、`MPLBACKEND=Agg`；在 Windows 上另设 `PYTHONIOENCODING=utf-8` 可避免控制台在 emoji 处编码报错。**换机器或改一行参数，`local_max_count` 与 `fringe_verdict` 都可能变**——这正是本章要说的：先固定定义，再谈像不像「明显干涉」。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | 在仓库根：`python scripts/ce/ce_00_double_slit_demo.py`（需能 `import chain_explosion_numba`） |
| **常量（脚本默认）** | A=1.0，S=0.25，B=0.05，λ=0.85；WIDTH=300，HEIGHT=200；STEPS=300；缝距 50px，缝宽 6px；光源 (5, HEIGHT/2)；挡板列 `BARRIER_X`=WIDTH/2 |
| **产出图** | `scripts/ce/ce_00_double_slit_demo.png`（与脚本同目录） |
| **`emit_case_dossier` 摘要** | `screen_column_x`: 160；`local_max_count_on_screen`: **2**；`fringe_verdict`: **`weak`**；`screen_max` ≈ **7.25×10¹⁴**（未归一化累积能，量级随步数变，仅作同参对比用） |

脚本用右边界整列上对 `screen` 做**简单峰计数**作快速判据；默认参数下得到 **`weak`**，反而诚实：**栅格双缝不是「画了缝就自动 obvious」**。读者可增大 **S** 或略降 **LAMBDA** 重跑，对照 `EXPERIMENT_DOSSIER_JSON` 块里 `observed_outcome` 的变化，把叙事钉在**同一套定义**上。

## 4.3　`ce_01` 与可见度随距离

`ce_01_visibility_vs_screen_distance.py` 问的是：**屏放远或拉近，条纹对比（可见度）怎么变**。仓库把可见度写成屏上峰谷对比的经典式（各章若改定义会写明）。这条线把「传播几何」和**可检验曲线**绑在一起：模型若自称类波动，通常要交代**随距离的衰减或振荡**，不能只说「有缝就有纹」。

## 4.4　`ce_02`、`ce_03`（屏统计与侧向耦合）

- **`scripts/ce/ce_02_double_slit_screen_statistics.py`**：在固定双缝几何下，抽取**屏上统计量**（分布、对比等，以脚本内导出为准），便于与「肉眼判条纹」脱钩。  
- **`scripts/ce/ce_03_visibility_vs_side_coupling_S.py`**：扫**侧向耦合 S** 对**可见度**的影响——直接回答「扩散/侧漏多了，条纹还能不能站稳」。

读法：仍用 **ce_00** 建立基线，再对照 **ce_02/ce_03** 看**换了哪几个旋钮、输出 CSV/图**落在哪。若脚本挂了 `experiment_dossier`，归档路径以运行时配置为准。

> **本章边界**  
> 本章是**模型内**栅格实验；**不**引用某次真实实验室的双缝原始迹。与公开数据的对照从**后文 NIST / CHSH 章**另起炉灶。

## 4.5　小结

你现在已经有一块**会漏、有缝、有屏**的**标准试验田**。下一章在同一格子上加 **缝口吸收与有限吸收体**：「测量」开始变成**局域乘子**与区域损耗——接续第三章的 **η** 语言。

---

# Chapter 4 · Ripple grid: double-slit and screen statistics

**栅格涟漪：双缝与屏上统计**  
*Ripple grid: double-slit and screen statistics*

> **For general readers — what this picture is about**
>
> - **In plain words**: **Double-slit** means “light through two slits, bright/dark stripes behind”; **visibility** roughly means **how crisp the fringes are**.
> - **What this chapter does**: Without a lab, ask on a **computer lattice**: under fixed rules, **can fringes grow on their own**, and how they blur with distance / parameters.
> - **Textbook baseline**: **Young’s double slit** is classic wave optics; quantum versions discuss **single photons**, etc. **This chapter is an in-model demo**, not a claim of new optical laws.
> - **What the book is doing**: Map `ce_00` scripts (you **need not run them**) to **rules → pattern**; real event tables come later with **NIST**.
> - **For working physicists**: **No clash** with core wave phenomena; numbers are valid **only under our discrete rules**.

> **This chapter’s job**  
> Turn Chapter 1’s bubble into runnable grids in `scripts/ce/`: double-slit geometry, screen intensity, **visibility** — and show how those quantities move with **distance and coupling**.

## 4.1 From bubble to lattice

Chapter 3: **every step leaks.** This chapter starts in the **cleanest setting** for **fringes and screen stats**: in the `chain_explosion_numba` kernel, energy (or intensity) on a 2D grid splits to neighbors with **A, B, S** and **LAMBDA**; a **full barrier column + two slits** is a boolean `barrier` mask — the pattern is **emergent from rules**, not painted in post.

## 4.2 `ce_00`: minimal double-slit story

`scripts/ce/ce_00_double_slit_demo.py` is the entry: typical parameters live at the top (grid size, **A/S/B**, **LAMBDA**, slit positions, steps). You get a **cumulative energy curve** on the screen and a heatmap. If side coupling **S** is tiny or decay is brutal, fringes “mush” — not mysticism, something **parameter sweeps** reproduce.

### One-run snapshot (in-model, not a lab)

A **rerunnable** “dossier” line replaces “we see fringes” with printed keys. Numbers from **2026-05-05**, repo root, **default constants**, terminal `PYTHONPATH` at repo root, `MPLBACKEND=Agg`; on Windows, `PYTHONIOENCODING=utf-8` avoids console emoji encoding errors. **Change machine or one constant and `local_max_count` / `fringe_verdict` may move** — the chapter’s point: **fix definitions, then argue “obvious interference.”**

| Item | Content |
| :--- | :--- |
| **Command** | From repo root: `python scripts/ce/ce_00_double_slit_demo.py` (needs `import chain_explosion_numba`) |
| **Constants (script defaults)** | A=1.0, S=0.25, B=0.05, λ=0.85; WIDTH=300, HEIGHT=200; STEPS=300; slit spacing 50px, slit width 6px; source (5, HEIGHT/2); barrier column `BARRIER_X`=WIDTH/2 |
| **Figure** | `scripts/ce/ce_00_double_slit_demo.png` (same folder as script) |
| **`emit_case_dossier` summary** | `screen_column_x`: 160; `local_max_count_on_screen`: **2**; `fringe_verdict`: **`weak`**; `screen_max` ≈ **7.25×10¹⁴** (unnormalized cumulative energy — scale drifts with steps; for same-parameter comparison only) |

The script uses simple peak counting on the right-edge screen column as a quick verdict; defaults yield **`weak`** — honestly: **grid double slit is not “obvious fringes for free.”** Raise **S** or trim **LAMBDA** and rerun; track `EXPERIMENT_DOSSIER_JSON` / `observed_outcome` so the story stays on **one definition**.

## 4.3 `ce_01` and visibility vs distance

`ce_01_visibility_vs_screen_distance.py` asks: **move the screen in or out — how does fringe contrast (visibility) move?** The repo writes visibility in a classical peak–valley sense (if a chapter redefines it, the chapter says so). This ties **propagation geometry** to a **checkable curve**: a wave-like model owes a story about **decay or oscillation with distance**, not just “slits imply stripes.”

## 4.4 `ce_02`, `ce_03` (screen stats and side coupling)

- **`scripts/ce/ce_02_double_slit_screen_statistics.py`**: fixed double-slit geometry, **screen statistics** (distribution, contrast, etc. — per script exports), decoupling from “I eyeball fringes.”  
- **`scripts/ce/ce_03_visibility_vs_side_coupling_S.py`**: sweep **side coupling S** vs **visibility** — answers whether **more sideways leak still leaves stable fringes.**

Read `ce_02/03` after `ce_00` baseline: **which knobs moved, where CSV/figures land.** If an `experiment_dossier` is attached, archive paths follow the run config.

> **Chapter boundary**  
> This is an **in-model** grid lab; it **does not** cite raw traces from a real double-slit run. Public-data contrast starts fresh in **later NIST / CHSH chapters**.

## 4.5 Close

You now have a **standard plot** that **leaks, has slits, has a screen.** Next chapter adds **slit absorption and finite absorbers** on the same lattice: “measurement” becomes **local multipliers** and regional loss — continuing Chapter 3’s **η** language.
