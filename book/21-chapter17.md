# 第十七章 · Chapter 17

**经典光力学计算路径的设想**  
*A classical optical computing pathway*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**构想章**=作者**没想完**、但想**把条件列清**的草稿；不是产品说明书。
> - **这章解决什么**：若坚持「**局域传播 + 可调损耗 + 读数规则写死**」，能不能想象一种**经典光学式**的信息处理？**天花板**在哪？
> - **教科书常识**：光计算、硅光子在工程上是**真实赛道**；**量子计算**是另一条赛道。本书**不参与口水战**。
> - **本书在干什么**：用仓库已有脚本当**思维脚手架**（`ce_*`、研究地图、计算机探索 README）；**无新实验数据**。
> - **和物理学家们**：**不宣称**已替代量子器件；只列**若要认真必须补的课**。

> **本章任务**  
> **构想章**：若坚持**局域传播 + 可调损耗 + 显式测量规则**，能否在工程上走出一条**经典光学式**的信息处理路径——**不**宣称已替代量子器件，只列**必要条件**与**已知的硬天花板**。

## 17.1　从格子到器件想象

前几章的格子是**思想与审计的试验田**。设想把它**芯片化**：波导、分束、可调吸收、相位片——每一层都对应**参数化规则**。优势是**透明**；风险是**尺度与噪声**把「干净定理」磨糊。

## 17.2　仓库里已有的「算力」隐喻（不是成品光芯片）

本书**尚未**实现商用光计算流片；但有两条**可对照的仓库线索**，说明「经典路径」在**方法论**上不是空话：

| 线索 | 路径 | 与「光力学计算」的关系 |
| :--- | :--- | :--- |
| **网格 + 协议** | `scripts/ce/*`、`chain_explosion_numba.py` | **可编程规则**已在 Python 里跑通：传播、吸收、分支、读出——相当于**软件定义的光学积木**（数字 toy）。 |
| **最小计算 ISA 探索** | **`计算机探索/README_探索路线.md`** 及同目录脚本 | 在**禁止 sqrt / 牛顿迭代**等约束下，讨论「介质动力学能否完成可重复映射」——是**经典计算哲学**的极端洁癖版，与工程光计算**同族不同阶**。 |
| **研究地图** | **`docs/RESEARCH_MAP.md`** 第三层「计算与审计」 | 强调 **可复现脚本替代口头争论**；光计算若要走通，最终也要过**同一类门禁**。 |

读法：**先把 `ce_*` 当「逻辑门级仿真」理解**，再谈是否映射到 **EDA/FDTD**；中间缺的那几层，正是本章所说的**里程碑**。

## 17.3　与量子路线的关系

本书**不**参与「量子霸权」口水战。务实问题是：**哪类任务**在**误差与能耗约束**下仍值得用经典波动模拟；**哪类任务**公开证据已显示**优势在量子侧**。`RESEARCH_MAP.md` 第二层把 **Bell/CHSH 统计对象**定为「核心战场」——经典光路**不**自动退出战场，但**多体相关**仍受 **`07-archive-ghz.md`** 一类论证约束。

## 17.4　需要的里程碑（工程化）

- **协议语言**与工业 **EDA / 光电仿真**对齐（不仅是 Python toy）。  
- **可制造性**：**λ、η、几何**的批次波动是否纳入**良率模型**。  
- **审计链**：从 **layout → 仿真 → 流片测试** 能否保留本书坚持的 **JSON/版本/hash** 习惯（见专论与 `experiment_dossier` 思想）。

> **本章边界**  
> 全章为**设想**；**无**新实验数据。若未来落地，应**另开技术专册**，本书不升格为工程手册。

## 17.5　小结

**经典路径**不是退路，是**一条需要重新定价的路**：仓库已证明**规则可编码、可审计**；**未证明**的是**尺度、噪声与多体边界**下的性价比。下一章换更「宏观」的涟漪想象：**动量/能量账本**——同样**只作构想**，但会挂钩 **`unsolved_problems_collision`** 里的**可证伪指标**思路。

---

# Chapter 17 · A classical optical computing pathway

**经典光力学计算路径的设想**  
*A classical optical computing pathway*

> **For general readers — what this picture is about**
>
> - **In plain words**: A **sketch chapter** — the author **has not finished thinking** but wants **conditions spelled out**; not a product manual.
> - **What it does**: If we insist on **local propagation + tunable loss + frozen readout rules**, can we imagine **classical optics–style** information processing? Where is the **ceiling**?
> - **Textbook baseline**: Optical computing and silicon photonics are **real engineering tracks**; **quantum computing** is another track. This book **does not** join flame wars.
> - **What the book is doing**: Use existing repo scripts as **scaffolding** (`ce_*`, research map, `计算机探索/README_探索路线.md`); **no** new experimental data.
> - **For working physicists**: **No** claim to replace quantum devices; only **homework** if you take it seriously.

> **This chapter’s job**  
> **Sketch**: With **local propagation + tunable loss + explicit measurement rules**, could an engineering path emerge for **classical optics–style** information processing — **without** claiming to replace quantum hardware; list **necessary conditions** and **known hard ceilings**.

## 17.1 From lattice to device imagination

Earlier chapters’ lattice is a **testbed for ideas and audits**. Imagine **chip-scale** realization: waveguides, splitters, tunable absorbers, phase plates — each maps to **parameterized rules**. Upside: **transparency**; risk: **scale and noise** blur “clean theorems.”

## 17.2 “Compute” metaphors already in the repo (not a commercial photonic chip)

No commercial optical-compute tape-out yet; two **repo clues** show the classical path is **not hollow methodologically**:

| Thread | Path | Relation to “optical computing” |
| :--- | :--- | :--- |
| **Grid + protocol** | `scripts/ce/*`, `chain_explosion_numba.py` | **Programmable rules** already run in Python: propagate, absorb, branch, read out — **software-defined optical blocks** (digital toy). |
| **Minimal compute ISA exploration** | **`计算机探索/README_探索路线.md`** and sibling scripts | Under bans like **no sqrt / Newton iteration**, asks whether **medium dynamics can implement repeatable maps** — an extreme **classical computing philosophy** exercise, **same family, different rung** than engineering photonics. |
| **Research map** | **`docs/RESEARCH_MAP.md`**, layer three “compute and audit” | Stresses **reproducible scripts instead of oral argument**; optical computing, if serious, must pass **the same style of gates**. |

Reading path: treat **`ce_*` as “logic-level simulation”** first, then ask whether it maps to **EDA/FDTD**; the missing middle layers are the **milestones** this chapter names.

## 17.3 Relation to quantum routes

This book **does not** join “quantum supremacy” shouting matches. Practical question: **which tasks** still reward classical wave simulation under **error and energy budgets**; **which tasks** public evidence already parks on the **quantum side**. `RESEARCH_MAP.md` layer two pins **Bell/CHSH statistical objects** as a “core battlefield” — classical optics **does not** automatically leave the field, but **many-body correlation** still faces arguments like **`07-archive-ghz.md`**.

## 17.4 Milestones if you industrialize

- **Protocol language** aligned with **EDA / optoelectronic simulation** (not only Python toys).  
- **Manufacturability**: batch spread of **λ, η, geometry** inside a **yield model**.  
- **Audit chain**: can **layout → simulation → fab test** keep this book’s **JSON / version / hash** habits (see monograph and `experiment_dossier` spirit).

> **Chapter boundary**  
> Whole chapter is **speculation**; **no** new experimental data. If it ever ships, it deserves a **technical companion volume** — this book does not upgrade to an engineering handbook.

## 17.5 Close

The **classical path** is not a retreat; it is a **route that needs repricing**. The repo already shows **rules can be encoded and audited**; what is **not** proved is **cost–benefit under scale, noise, and many-body edges.** Next chapter widens the aperture: **momentum / energy ledgers** for a **ripple propulsion** sketch — still **speculation**, but hooks **`unsolved_problems_collision`** **falsifiable-metrics** style.
