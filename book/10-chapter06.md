# 第六章 · Chapter 6

**栅格涟漪：延迟选择、测量相图与纠缠扫描**  
*Ripple grid: delayed choice, measurement phase diagram, entanglement scans*

> **本章任务**  
> 在格子上讨论：**吸收/分支规则晚一点插进去**，图样是否变；以及在多参数平面上**系统扫**「测量强度 × 耦合 × ……」时，可见度、对比度等**相图状**结构。

## 6.1　延迟选择：`ce_06`

「延迟选择」在科普里常被神秘化。在仓库里，它更接近工程问题：**第几步**开始启用吸收掩模？

- **`scripts/ce/ce_06_delayed_choice_absorber.py`**：把**吸收体插入步数**参数化；早插 vs 晚插，下游干涉条件不同则屏上统计应**可分辩**——**因果顺序写进循环**，不是口号。

### 一次运行快照（默认参，模型内）

下列数值来自 **2026-05-05**、仓库根目录、`PYTHONPATH` 指向仓库根、`MPLBACKEND=Agg`、建议 `PYTHONIOENCODING=utf-8`（Windows 控制台）下的一次运行。**吸收圆**在第 **300** 步插入（总步数 **500**），盖住**上缝**下游邻域；屏列为 `SCREEN_X = WIDTH - 10`。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | `python scripts/ce/ce_06_delayed_choice_absorber.py` |
| **常量（脚本默认摘录）** | HEIGHT=201，WIDTH=400；A=1.0，S=0.4，B=0.05，λ=0.90；INSERT_STEP=300；ABSORB_RATIO=0.9；吸收圆心约 (BARRIER_X+5, 上缝中心)，半径 8 |
| **`emit_case_dossier` 摘要** | `visibility_final` ≈ **0.8065**（脚本内 `compute_visibility(screen)`，屏列能量） |
| **图文件** | **`scripts/ce/delayed_choice.png`**（与 `ce_00` 相同，写入脚本所在目录，**不**依赖当前工作目录） |

**读法**：本次默认参下 **V 仍高**，对应「晚插圆吸收**未**把条纹打到脚本里的 `<0.1` 判据」——**不**等于量子实验结论；只说明 **同一套可见度定义下，几何与步数可复算**。对比 **`INSERT_STEP=0`** 与「无吸收器」应另跑对照，并把三条曲线的 **V** 并排写进笔记。

## 6.2　测量相图：`ce_07`

- **`scripts/ce/ce_07_measurement_phase_diagram_scan.py`**：在参数平面上扫**测量强度、位置、耦合**等，输出「相图」式摘要（条纹活/死区域）。读法：**固定内核与几何，只动测量旋钮**——与第二章「换尺子」同精神。

## 6.3　`ce_08`–`ce_10`：分支、相位与距离扫描

- **`scripts/ce/ce_08_entanglement_split_wavepackets.py`**：分束/分支掩模下的**双路包络**与相关统计入口。  
- **`scripts/ce/ce_09_entanglement_with_phase_field.py`**：在格点上引入**相位场**与纠缠读出（接口见脚本顶部）。  
- **`scripts/ce/ce_10_entanglement_distance_scan.py`**：扫**空间分离/等效距离**对相关量的影响，为 **第七章 `ce_bell*`** 搭桥。

具体数据结构以各脚本内 **`split_mask`、相位网格、输出数组** 为准。

> **本章边界**  
> 格点上的「纠缠扫描」是**玩具相关矩阵**在定义下的行为；**不**自动等同于某实验室申报的纠缠见证。

你现在能问：**测量规则何时介入、介入多狠、在参数平面上处于何区**——全是可复算问题。下一章把这些机制**接到 Bell/CHSH 标量与前沿曲线**（`ce_bell*`）。

---

# Chapter 6 · Ripple grid: delayed choice, measurement phase diagram, entanglement scans

**栅格涟漪：延迟选择、测量相图与纠缠扫描**  
*Ripple grid: delayed choice, measurement phase diagram, entanglement scans*

> **This chapter’s job**  
> On the lattice: **if absorption / branching rules are inserted late**, do patterns change; and on multi-parameter planes, **systematically scan** “measurement strength × coupling × …” for **phase-diagram-like** structure in visibility and contrast.

## 6.1 Delayed choice: `ce_06`

Pop accounts mystify “delayed choice.” In the repo it is closer to engineering: **at which step** does an absorbing mask turn on?

- **`scripts/ce/ce_06_delayed_choice_absorber.py`**: parameterize **insertion step** for the absorber; early vs late insert changes downstream interference — **causal order lives in the loop**, not in slogans.

### One-run snapshot (defaults, in-model)

**2026-05-05**, repo root, `PYTHONPATH`, `MPLBACKEND=Agg`, `PYTHONIOENCODING=utf-8` (Windows console). **Absorbing disk** inserts at step **300** (total steps **500**), covers **upper-slit** downstream neighborhood; screen column `SCREEN_X = WIDTH - 10`.

| Item | Content |
| :--- | :--- |
| **Command** | `python scripts/ce/ce_06_delayed_choice_absorber.py` |
| **Constants (snippet)** | HEIGHT=201, WIDTH=400; A=1.0, S=0.4, B=0.05, λ=0.90; INSERT_STEP=300; ABSORB_RATIO=0.9; disk center ~(BARRIER_X+5, upper-slit center), radius 8 |
| **`emit_case_dossier` summary** | `visibility_final` ≈ **0.8065** (`compute_visibility(screen)` on screen column energy) |
| **Figure** | **`scripts/ce/delayed_choice.png`** (same pattern as `ce_00`: written next to the script, **not** cwd-dependent) |

**Readout**: under these defaults **V stays high** — late disk **does not** push fringes below the script’s `<0.1` test — **not** a quantum verdict; only that **geometry × step index** recomputes under **one visibility definition.** Contrast **`INSERT_STEP=0`** vs “no absorber” in separate runs and tabulate **V**.

## 6.2 Measurement phase diagram: `ce_07`

- **`scripts/ce/ce_07_measurement_phase_diagram_scan.py`**: scan **measurement strength, position, coupling** on a parameter plane; output “phase-map” summaries (live/dead fringe regions). **Fix kernel and geometry, move only measurement knobs** — same spirit as Chapter 2’s “swap yardsticks.”

## 6.3 `ce_08`–`ce_10`: branching, phase field, distance scan

- **`scripts/ce/ce_08_entanglement_split_wavepackets.py`**: dual-path envelopes and correlation stats under split / branch masks.  
- **`scripts/ce/ce_09_entanglement_with_phase_field.py`**: phase field on the grid and entanglement-style readout (see script header).  
- **`scripts/ce/ce_10_entanglement_distance_scan.py`**: sweep **spatial separation / effective distance** for correlation metrics — bridge to **Chapter 7 `ce_bell*`.**

Data layouts follow each script’s **`split_mask`**, phase grid, output arrays.

> **Chapter boundary**  
> Grid “entanglement scans” are **toy correlation matrices** under stated definitions; they **do not** auto-equal a lab’s entanglement witness.

You can now ask: **when measurement rules bite, how hard, and where in parameter space** — all recomputable. Next chapter pipes these mechanisms into **Bell/CHSH scalars and frontier curves** (`ce_bell*`).
