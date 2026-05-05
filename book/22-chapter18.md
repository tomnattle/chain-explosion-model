# 第十八章 · Chapter 18

**涟漪动力系统的设想**  
*A ripple-based propulsion concept*

> **本章任务**  
> **构想章**：把**介质里传播的扰动**想象成一种**可记账的动量/能量交换**——讨论**在何种对称性与损耗模型下**，「涟漪推进」在**原理上**可能说什么、**不可能**说什么。

## 18.1　从科普隐喻到方程纪律

「涟漪推船」在口语里好听，在物理里要先问：**动量去哪了、介质反冲算不算、开放系统熵增在哪**。本书前几章的格子**没有**自动包含**宏观 Navier–Stokes**；因此本章**不**给出具体推力公式，只列**若要认真，必须补哪类连续极限**。

**仓库内最接近「动量/能量口径」的可操作讨论**，见 **`unsolved_problems_collision/ROADMAP_7_PROBLEMS.md`** **第 1 题**（亚伯拉罕–闵可夫斯基动量表述之争的 toy 化）：文中给出 **前沿速度比、能流积分、界面反冲代理** 等**可证伪指标**与**失败判据**——这正是把「涟漪推进」从**修辞**拉回**指标**的示范格式。**本书不宣称该路线图已闭合**；只建议：**谁若谈推进，谁先认领一套类似 `I1/I2/I3` 的数**。

## 18.2　与第三章「热」的衔接

若有**净推力**，往往伴随**不对称损耗**或**不对称辐射**——第三章里「漏进浴」的份额，在这里可能变成**定向动量**。任何具体数值都需要把 **bath 自由度**或**辐射场**写清，否则只是**词语游戏**。

## 18.3　与「相对论未从格子导出」的提醒

**`scripts/explore/explore_critique_04_sr_not_derived_from_lattice.py`** 内部立场：当前离散格子**没有**自动推出**洛伦兹对称**——若「推进」叙事偷偷借用相对论动量公式，却未建立**模型与 SR 的接口**，属于**范畴错配**。推进构想必须先说清：**你在哪一套极限/哪一类对称性下谈动量**。

## 18.4　开放问题

- 离散格子**能否**、**在何尺度下**与某类**连续介质方程**严格对接（见 **`00-unified-writing-scheme.md`** 与 **`01-appendix-three-phrasings.md`**）。  
- **可证伪预测**：沿用 **`ROADMAP_7_PROBLEMS.md`** 的写法，为「宏观推进」锁定 **metrics.json + verdict.md** 式输出——**本书尚未**代你做完这一步。

> **本章边界**  
> **纯设想**；**禁止**把本章当专利说明书或工程可行性背书。

**泡泡**可以讲故事；**推进**要写**方程与账本**——仓库里已有**路线图模板**（`ROADMAP_7_PROBLEMS.md`），缺的只是你是否愿意把口号压成**指标与失败判据**。后记收束全书。

---

# Chapter 18 · A ripple-based propulsion concept

**涟漪动力系统的设想**  
*A ripple-based propulsion concept*

> **This chapter’s job**  
> **Sketch**: imagine **disturbance propagating in a medium** as **bookable momentum / energy exchange** — under **which symmetry and loss models** “ripple propulsion” can **say** something in principle and **cannot**.

## 18.1 From pop metaphor to equation discipline

“Ripple pushes the boat” sounds good in prose; in physics ask first: **where momentum went, whether medium recoil counts, where open-system entropy production lives.** Earlier lattice chapters **do not** automatically embed **macro Navier–Stokes**; this chapter **does not** give a thrust formula — only **which continuum limit you must add** to be serious.

**Closest in-repo, operational momentum/energy discussion**: **`unsolved_problems_collision/ROADMAP_7_PROBLEMS.md` problem 1** (Abraham–Minkowski toy): **front-velocity ratios, energy-flux integrals, interface-recoil proxies** as **falsifiable metrics** and **failure criteria** — a template for dragging “ripple propulsion” from **rhetoric** to **numbers**. **This book does not claim that roadmap is closed**; it only suggests: **whoever talks thrust should own numbers in the I1/I2/I3 spirit.**

## 18.2 Bridge to Chapter 3 “heat”

**Net thrust** often rides with **asymmetric loss** or **asymmetric radiation** — the share that Chapter 3 “leaks into the bath” can become **directed momentum** here. Any concrete number needs **bath degrees of freedom** or a **radiation field** written explicitly; otherwise it is **wordplay**.

## 18.3 Reminder: “SR not derived from lattice”

**`scripts/explore/explore_critique_04_sr_not_derived_from_lattice.py`** states: the current discrete grid **does not** automatically yield **Lorentz symmetry** — if a “propulsion” story quietly borrows relativistic momentum formulas without a **model–SR interface**, that is a **category mistake**. Any propulsion sketch must first say **which limit and which symmetry class** define “momentum.”

## 18.4 Open questions

- Can the discrete lattice **lock**, and **at what scale**, to a chosen **continuum medium equation** (see **`00-unified-writing-scheme.md`** and **`01-appendix-three-phrasings.md`**).  
- **Falsifiable prediction**: reuse **`ROADMAP_7_PROBLEMS.md`** style to pin **macro propulsion** to **`metrics.json + verdict.md`** outputs — **this book does not** do that step for you.

> **Chapter boundary**  
> **Pure speculation**; **do not** treat this chapter as a patent filing or engineering sign-off.

**Bubbles** can tell stories; **propulsion** needs **equations and ledgers** — the repo already has a **roadmap template** (`ROADMAP_7_PROBLEMS.md`); what is missing is willingness to compress slogans into **metrics and failure criteria.** The afterword closes the book.
