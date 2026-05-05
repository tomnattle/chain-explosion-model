# 目录 · Contents

---

## 书名 · Working title（工作稿，可再斟酌）

| 用途 | 文案 |
| :--- | :--- |
| **中文主名（短，好记）** | **《假大象与泡泡》** |
| **中文副题（告诉别人我们要干嘛）** | **公开数据、Bell/GHZ 与读数规则的审计手记** |
| **英文并列名（简介、仓库 About 可用）** | *The Fake Elephant and the Bubble — Notes on Auditing Readout Rules in Public Data and Bell-Type Experiments* |

**一句话 pitch**：用「球面泡泡」的直觉搭一座**假大象**，再用同一套**公开记录**问：**换一把统计与二值化的尺子，故事会不会变**——并把格子模拟与协议假设**写清、可复现**。

**正式封面图**：`book/image/cover.jpg`；Markdown 扉页与说明见 **`book/cover.md`**（图上主英文为 *THE ABSENT ELEPHANT AND THE BUBBLES*，与「假大象 / 缺席的大象」同旨）。

**备选主名**（若更希望突出模型词）：《泡泡与尺子》《测量假大象：泡泡模型与协议审计》——与上表主名二选一即可，避免封面字数过多。

---

## 卷前 · Front matter

| 文件 | 说明 |
| :--- | :--- |
| [cover.md](cover.md) | **封面稿**（Markdown / HTML 居中版式；腰封、封底文案） |
| [00-preface.md](00-preface.md) | 序言（中英）与全书读法边界 |
| [01-appendix-three-phrasings.md](01-appendix-three-phrasings.md) | 附录一：泡泡 / 涟漪 / 链式爆炸；离散核与代码索引 |
| [02-contents.md](02-contents.md) | 本目录（当前版） |
| [00-unified-writing-scheme.md](00-unified-writing-scheme.md) | **全书统一写作方案**（第4章起：结构、边界、交叉引用） |

**零基础导读（不必读代码）**  
术语在正文就地解释；序言里**一次**写清全书边界。若关心「读到哪里停」，见 **`book/REVISION_PLAN_NARRATIVE_LAYERING.md`** 与**第2、5、14章**末路标。

---

## 第一部分 · Part I　模型 · The model

**体例（全书）**  
读法、非本体论态度、非人身等边界，在《序言》**「全书读法与边界（写在前面一次）」**统一说明；**泡泡 / 涟漪 / 链式爆炸**三种表述及项目内离散公式见 **`book/01-appendix-three-phrasings.md`**。第4章起另遵 **`book/00-unified-writing-scheme.md`**。各章以叙事与可选的 **`本章任务`** 接入，**章内不单段重复**序言四条，以免打断正文。

1. **第1章**　泡泡  
   *Ch.1 · The bubble*  
   正文稿：`book/04-chapter.md`

2. **第2章**　为什么我开始怀疑  
   *Ch.2 · Why I started asking questions*  
   正文稿：`book/03-chapter.md`

3. **第3章**　介质、损耗与热：已知与未知  
   *Ch.3 · Medium, loss, and heat: what is known and what is not*  
   正文稿：`book/05-chapter.md`

**档案（第一单元背景，可与第2–3章交叉阅读）**  

- **档案一**　Bell 实验与 Bell 不等式：历史脉络、证明了什么、实验骨架与类型列举  
  正文稿：`book/06-archive-bell.md`  
- **档案二**　GHZ 与多体纠缠：悖论结构、实验类型、**为何与「局域递推 + 简单预先赋值」类模型冲突**（表述钉死）  
  正文稿：`book/07-archive-ghz.md`  

---

## 第二部分 · Part II　测量假大象 · Testing the fake elephant

*（与仓库冻结脚本及归档对齐：`scripts/ce/` 栅格引擎；`battle_results/`、`papers_final` 公开数据审计；`scripts/explore/ghz_medium_v10` 等 in-silico；`scripts/explore/ripple_quantum_tests/` 与 `artifacts/ripple_*`。玩具曲线与 NIST CSV 分流见章内说明。）*  
*Aligned to frozen scripts and archives: `scripts/ce/` grid engines; public-data audits under `battle_results/` and `papers_final/`; in-silico GHZ under `scripts/explore/ghz_medium_v10/`; ripple suites under `scripts/explore/ripple_quantum_tests/` and `artifacts/ripple_*`. Toy curves vs NIST CSV are split in-text.*

4. **第4章**　栅格涟漪：双缝与屏上统计（`ce_00`–`ce_03`）  
   *Ch.4 · Ripple grid: double-slit and screen statistics (`ce_00`–`ce_03`)*  
   正文稿：`book/08-chapter04.md`

5. **第5章**　栅格涟漪：缝口吸收、有限吸收体与探测器（`ce_04`–`ce_05`）  
   *Ch.5 · Ripple grid: slit absorption and finite absorber–detector (`ce_04`–`ce_05`)*  
   正文稿：`book/09-chapter05.md`

6. **第6章**　栅格涟漪：延迟选择、测量相图与纠缠扫描（`ce_06`–`ce_10`）  
   *Ch.6 · Ripple grid: delayed choice, measurement phase diagram, entanglement scans (`ce_06`–`ce_10`)*  
   正文稿：`book/10-chapter06.md`

7. **第7章**　栅格 Bell/CHSH 玩具与前沿曲线（`ce_bell*` 等）  
   *Ch.7 · Grid Bell/CHSH toys and frontier curves (`ce_bell*`, etc.)*  
   正文稿：`book/11-chapter07.md`

8. **第8章**　公开数据：NIST complete-blind 上的 Bell/CHSH 分母与符合窗审计  
   *Ch.8 · Public data: Bell/CHSH denominator and coincidence-window audit on NIST complete-blind*  
   正文稿：`book/12-chapter08.md`

9. **第9章**　基于 NIST 数据：逐次测量拟合 Alice 与 Bob 偏振装置在庞加莱球上的等效坐标（独立实验；可辨识性与不确定度章内锁定）  
   *Ch.9 · NIST-based experiment: per-trial fit of effective Poincaré-sphere coordinates for Alice’s and Bob’s polarization apparatus (standalone; identifiability & uncertainty budget in-chapter)*  
   正文稿：`book/13-chapter09.md`

10. **第10章**　CHSH：二值化、连续代理与统计对象分轨（含合成样本对照与章内边界）  
    *Ch.10 · CHSH: binarization, continuous proxies, and split statistical objects (synthetic baselines + in-chapter bounds)*  
    正文稿：`book/14-chapter10.md`

11. **第11章**　GHZ 与 in-silico 协议审计（`ghz_medium_v10`、门控与保留率；非实验室原始迹）  
    *Ch.11 · GHZ and in-silico protocol audit (`ghz_medium_v10`, gating and retention; not raw lab traces)*  
    正文稿：`book/15-chapter11.md`

12. **第12章**　涟漪量子四项玩具基准 v1–v8（激光阈值、半导体截止、MRI 拉莫尔、原子钟谱形；色散与 v8 unify）  
    *Ch.12 · Ripple quantum four benchmarks v1–v8 (laser, semiconductor, MRI Larmor, atomic clock; dispersion & v8 unify)*  
    正文稿：`book/16-chapter12.md`

13. **第13章**　涟漪专项审计与统一报告（热三元组预注册、全频透射、三体物理恒等式、v6 可辨识性、v7 三曲线、v7/v8 合并页与参数阱库）  
    *Ch.13 · Ripple-focused audits and unified report (thermal triplet preregistration, full-band transparency, triplet identity, v6 identifiability, v7 triple, v7/v8 merge page, parameter-trap library)*  
    正文稿：`book/17-chapter13.md`

14. **第14章**　其他基线与探索（波恩规则、不确定性、退相干等；与 `explore_*` 索引互见）  
    *Ch.14 · Other baselines and exploration (Born, uncertainty, decoherence; cross-ref `explore_*` index)*  
    正文稿：`book/18-chapter14.md`

15. **第15章**　（规划稿）Bell 类公开数据：联合拟合 Alice 与 Bob 的球面坐标  
    *Ch.15 · Planned: Bell-type public data — joint fit of Alice’s and Bob’s sphere coordinates*  
    正文稿：`book/19-chapter15.md`（**文稿占位，实现待补；见章内作者说明**）

16. **第16章**　没通过的测量：诚实记录  
    *Ch.16 · What failed: an honest record*  
    正文稿：`book/20-chapter16.md`

---

## 第三部分 · Part III　设想 · Possibilities

17. **第17章**　经典光力学计算路径的设想  
    *Ch.17 · A classical optical computing pathway*  
    正文稿：`book/21-chapter17.md`

18. **第18章**　涟漪动力系统的设想  
    *Ch.18 · A ripple-based propulsion concept*  
    正文稿：`book/22-chapter18.md`

---

## 后记 · Afterword

正文稿：`book/23-afterword.md`（含中英收束）

- **开放问题与未完成的介质逻辑**  
  *Open questions and the unfinished medium logic*

- **交给后来者**  
  *To those who follow*

---

**体例说明 · Note on entries**  
斜体章节为开放问题，尚未完成。这是诚实的边界，不是遗漏。  
*Italic entries are open questions, not yet resolved. This is an honest boundary, not an omission.*

---

**存档 · Archive**  
序言与目录在全文优化前的快照见 `存档/preface-v1.0.md` 与 `存档/contents-v1.0.md`。当前卷前与目录文件为：`book/00-preface.md`、`book/01-appendix-three-phrasings.md`、`book/02-contents.md`（本文件）。**若需旧章号或旧章题（第二部分止于第9章等）请对照 `存档/contents-v1.0.md`。**

---

# Table of contents

---

## Working title

| Use | Copy |
| :--- | :--- |
| **Short Chinese main title** | **《假大象与泡泡》** (*The Fake Elephant and the Bubble*) |
| **Chinese subtitle (what we are doing)** | **公开数据、Bell/GHZ 与读数规则的审计手记** — *Notes on auditing readout rules in public data and Bell-type experiments* |
| **English parallel title (blurb, repo About)** | *The Fake Elephant and the Bubble — Notes on Auditing Readout Rules in Public Data and Bell-Type Experiments* |

**One-sentence pitch**: Build a **fake elephant** from the “spherical bubble” intuition, then ask the **same public records**: **if we swap the statistical yardstick and binarization rule, does the story change** — while keeping lattice simulations and protocol assumptions **explicit and reproducible**.

**Formal cover art**: `book/image/cover.jpg`; Markdown title page: **`book/cover.md`** (main English on the art reads *THE ABSENT ELEPHANT AND THE BUBBLES*, same spirit as “fake elephant / the elephant no one fully touches).

**Alternate main titles** (if you want the model word up front): *Bubbles and Yardsticks*, *Measuring a Fake Elephant: the bubble model and protocol audits* — pick one pairing with the table above so the cover does not get crowded.

---

## Front matter

| File | Note |
| :--- | :--- |
| [cover.md](cover.md) | **Cover draft** (Markdown / HTML centered layout; jacket and back-cover copy) |
| [00-preface.md](00-preface.md) | Preface (Chinese + English) and how to read the book |
| [01-appendix-three-phrasings.md](01-appendix-three-phrasings.md) | Appendix I: bubble / ripple / chain explosion; discrete kernel and code index |
| [02-contents.md](02-contents.md) | This TOC (current) |
| [00-unified-writing-scheme.md](00-unified-writing-scheme.md) | **Unified writing scheme** from Chapter 4: structure, boundaries, cross-refs |

**Zero-background guides (no code required)**  
Jargon is glossed in-line; boundaries are stated once in the preface. For “where to stop reading,” see **`book/REVISION_PLAN_NARRATIVE_LAYERING.md`** and the short **layer cues** at the ends of **Chapters 2, 5, and 14**.

---

## Part I · The model

**Style (whole book)**  
How to read the book, the non-ontological stance, and the no–ad-hominem boundary are stated once in the preface under **“全书读法与边界”**; the three phrasings **bubble / ripple / chain explosion** and in-repo discrete formulas are in **`book/01-appendix-three-phrasings.md`**. From Chapter 4 on, also follow **`book/00-unified-writing-scheme.md`**. Chapters enter with **narrative** and an optional **`This chapter’s job`** line; the **body does not restate** the preface’s four bullets paragraph by paragraph, to avoid breaking flow.

1. **Chapter 1** · Bubble — *Ch.1 · The bubble* — `book/04-chapter.md`  
2. **Chapter 2** · Why I started asking questions — *Ch.2* — `book/03-chapter.md`  
3. **Chapter 3** · Medium, loss, and heat — *Ch.3* — `book/05-chapter.md`

**Archives (Part I background; can be read with Chapters 2–3)**

- **Archive I** · Bell tests and Bell inequalities — `book/06-archive-bell.md`  
- **Archive II** · GHZ and many-body entanglement — `book/07-archive-ghz.md`

---

## Part II · Testing the fake elephant

*Frozen scripts and archives: `scripts/ce/` grid engines; public-data audits under `battle_results/` and `papers_final/`; in-silico GHZ under `scripts/explore/ghz_medium_v10/`; ripple suites under `scripts/explore/ripple_quantum_tests/` and `artifacts/ripple_*`. Toy curves vs NIST CSV are separated in the chapters.*

4. **Chapter 4** · Ripple grid: double-slit and screen statistics (`ce_00`–`ce_03`) — `book/08-chapter04.md`  
5. **Chapter 5** · Ripple grid: slit absorption and finite absorber–detector (`ce_04`–`ce_05`) — `book/09-chapter05.md`  
6. **Chapter 6** · Ripple grid: delayed choice, measurement phase diagram, entanglement scans (`ce_06`–`ce_10`) — `book/10-chapter06.md`  
7. **Chapter 7** · Grid Bell/CHSH toys and frontier curves (`ce_bell*`, etc.) — `book/11-chapter07.md`  
8. **Chapter 8** · Public data: Bell/CHSH denominator and coincidence-window audit on NIST complete-blind — `book/12-chapter08.md`  
9. **Chapter 9** · NIST-based experiment: per-trial fit of effective Poincaré-sphere coordinates — `book/13-chapter09.md`  
10. **Chapter 10** · CHSH: binarization, continuous proxies, split statistical objects — `book/14-chapter10.md`  
11. **Chapter 11** · GHZ and in-silico protocol audit — `book/15-chapter11.md`  
12. **Chapter 12** · Ripple quantum four benchmarks v1–v8 — `book/16-chapter12.md`  
13. **Chapter 13** · Ripple-focused audits and unified report — `book/17-chapter13.md`  
14. **Chapter 14** · Other baselines and exploration — `book/18-chapter14.md`  
15. **Chapter 15** · *(Planning draft)* Bell-type public data — joint fit of Alice’s and Bob’s sphere coordinates — `book/19-chapter15.md` (**placeholder; implementation TBD; see in-chapter author note**)  
16. **Chapter 16** · What failed: an honest record — `book/20-chapter16.md`

---

## Part III · Possibilities

17. **Chapter 17** · A classical optical computing pathway — `book/21-chapter17.md`  
18. **Chapter 18** · A ripple-based propulsion concept — `book/22-chapter18.md`

---

## Afterword

`book/23-afterword.md` (includes Chinese + English close)

- *Open questions and the unfinished medium logic*  
- *To those who follow*

---

**Note on entries**  
*Italic chapter lines mark open questions, not finished work. That is an honest boundary, not an oversight.*

---

**Archive**  
Earlier snapshots: `存档/preface-v1.0.md`, `存档/contents-v1.0.md`. Current front matter and TOC: `book/00-preface.md`, `book/01-appendix-three-phrasings.md`, `book/02-contents.md`. **For old chapter numbering or titles (Part II ending at Chapter 9, etc.), see `存档/contents-v1.0.md`.**
