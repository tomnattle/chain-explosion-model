# 第十五章 · Chapter 15

**（规划稿）Bell 类公开数据：联合拟合 Alice 与 Bob 的球面坐标**  
*Planned: Bell-type public data — joint fit of Alice’s and Bob’s sphere coordinates*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**Alice 和 Bob** 是贝尔实验里的习惯叫法——两个各自做测量的人（或两台装置）。**球面**在这里指 **庞加莱球**：把「偏振怎么转」画成球面上的一点，像地球仪上的经纬度。
> - **这章计划解决什么**：在**同一批公开的 Bell/CHSH 类 trial** 上，不只算一个总指标，而是尝试**反推**：两套装置在数学上等效于在球面上**站在哪儿、怎么转**——方便检查**装置漂移、对不齐、或统计口径**是否让故事变形。
> - **与第9章分工**：**第九章**已写「基于 NIST 的逐 trial 拟合、可辨识性」；本章是**延伸选题**：更强调 **Bell 子样本、与 CHSH 二值化轨道的对齐、联合约束**——**目前仅有规划，没有成品脚本**。
> - **教科书常识**：斯托克斯矢量、庞加莱球是**经典光学标准语言**；实验物理里**装置标定**是硬功夫。本书**不宣称**发明新光学，只做**可审计的拟合叙事**。
> - **和物理学家们**：目标与**仪器科学、量子光学**的表述**同族**；若将来实现，应用**同一纪律**：定义先行、不确定度入册、失败也归档。
> - **你需要会代码吗**：**当前不需要**——作者**动力不足**，实现留待日后；你读本章只为知道**书架上预留了这一格**。

> **本章任务（当前为占位）**  
> 预留**文稿位置**：说明**拟做什么、与第9章及第8–10章审计链如何衔接**；**正文实现（脚本、JSON、图）待补**。

## 15.1　为什么要单开一章（而不是塞进第9章）

- **第9章**已经承担「**NIST 数据 → 庞加莱球等效坐标**」的**独立拟合**叙事；读者应**先读该章**建立语言。  
- **Bell/CHSH 子问题**常额外要求：**哪些 trial 进入 S、二值化阈值是否与拟合假设打架**——若在**同一管道**里混写，容易**口头合并、账目分开**。本章预留为 **「Bell 聚焦 + 联合 Alice/Bob」** 的**专用抽屉**。  
- **诚实边界**：**未实现**不等于**不重要**；先**把意图写死**，避免日后草稿散在 issue 里找不到。

## 15.2　计划中的技术轮廓（无代码承诺）

下列条目**描述意图**，**不构成**已实现接口：

| 块 | 计划内容 |
| :--- | :--- |
| **输入** | 与 **`battle_results/`** 或 **`papers_final/`** 中已冻结的 Bell/CHSH 事件表对齐的 CSV/HDF5；字段语义遵循第8–10章。 |
| **输出** | 每侧（Alice / Bob）**球面坐标轨迹**或**分段常值** + **不确定度**；可选：**与 CHSH 四设定同步索引**。 |
| **对照** | 与 **第9章**拟合结果**差分**（同一数据子集）；**阴性对照**：打乱 trial 顺序、伪造标签。 |
| **门禁** | **可辨识性**崩溃则**不写胜利句**；**metrics.json + verdict.md** 式归档（与全书习惯一致）。 |

## 15.3　作者说明：为何此刻只有纸面

实现这一章需要**连续投入**：数据对齐、优化器、诊断图、与现有 NIST 管道**回归测试**。作者当前**动力不足**，选择**先把章节占住、把边界写清**，以免日后补上时与全书**体例冲突**。

> **本章边界**  
> **规划稿**；**无**可运行脚本、**无**新实验数据。读者**不得**把本章当作已完成工作引用。下一章回到**已写内容**：**没通过的测量**清单。

## 15.4　小结

**球面上的 Alice/Bob** 是**给仪器和统计对齐用的语言**；本书预留一章把 **Bell 类公开数据** 接进这套语言——**待办**。读完请直接去 **第十六章**：那里记录**已经发生的失败与未闭合**。

---

# Chapter 15 · Planned: Bell-type public data — joint fit of Alice’s and Bob’s sphere coordinates

**（规划稿）Bell 类公开数据：联合拟合 Alice 与 Bob 的球面坐标**  
*Planned: Bell-type public data — joint fit of Alice’s and Bob’s sphere coordinates*

> **For general readers — what this picture is about**
>
> - **In plain words**: **Alice and Bob** are Bell-test nicknames — two people (or two boxes) measuring separately. **Sphere** here means the **Poincaré sphere**: “how polarization is rotated” drawn as a point on a globe.
> - **What this chapter plans**: On **one public Bell/CHSH-style trial table**, not only a headline scalar but trying to **invert**: where on the sphere each apparatus **sits and turns** in math — to check whether **drift, misalignment, or statistical definition** bends the story.
> - **Division of labor with Chapter 9**: Chapter **9** already carries **NIST → per-trial Poincaré fit + identifiability**; this chapter is an **extension**: emphasize **Bell subsamples, alignment with CHSH binarization tracks, joint constraints** — **planning only, no finished scripts yet**.
> - **Textbook baseline**: Stokes vectors and the Poincaré sphere are **standard classical optics**; **instrument calibration** is hard experimental work. The book **does not** claim new optics — only **auditable fitting narrative**.
> - **For working physicists**: Goals sit next to **instrument science / quantum optics** phrasing; if implemented later, same discipline: **definitions first, uncertainty on record, failures archived**.
> - **Code right now?** **Not needed** — author **low on steam**; implementation later; read this to know **a shelf slot exists**.

> **This chapter’s job (placeholder)**  
> Reserve **manuscript space**: what is intended, how it hooks **Chapter 9** and the **Chapters 8–10 audit chain**; **implementation (scripts, JSON, figures) TBD**.

## 15.1 Why a separate chapter (not folded into Chapter 9)

- Chapter **9** already owns **NIST data → independent Poincaré fit**; read it first for language.  
- **Bell/CHSH subproblems** often need **which trials enter S, whether binarization thresholds fight fit assumptions** — mixing into one pipeline risks **merged rhetoric, split ledgers**. This slot is the **“Bell-focused + joint Alice/Bob”** drawer.  
- **Honest boundary**: **unimplemented** ≠ **unimportant**; **nail intent in text** so drafts do not scatter across issues.

## 15.2 Planned technical outline (no code promise)

These lines **describe intent**, **not** shipped interfaces:

| Block | Planned content |
| :--- | :--- |
| **Input** | CSV/HDF5 aligned to frozen Bell/CHSH event tables under **`battle_results/`** or **`papers_final/`**; field semantics follow Chapters 8–10. |
| **Output** | Per side (Alice / Bob) **sphere-coordinate traces** or **piecewise constants** + **uncertainty**; optional: **index locked to CHSH’s four settings**. |
| **Controls** | **Diff** vs Chapter **9** fits on the **same subset**; **negative controls**: shuffle trials, fake labels. |
| **Gates** | If **identifiability** collapses, **no victory sentences**; archive **`metrics.json + verdict.md`** style like the rest of the book. |

## 15.3 Author note: why only paper for now

Shipping this chapter needs **sustained work**: data alignment, optimizers, diagnostic plots, **regression tests** against existing NIST plumbing. The author is **low on energy** right now and chose to **hold the chapter slot and write boundaries** so a future implementation does not **fight house style**.

> **Chapter boundary**  
> **Planning draft**; **no** runnable scripts, **no** new experimental data. **Do not** cite this chapter as finished work. Next chapter returns to **written material**: a **list of measurements that did not pass**.

## 15.4 Close

**Alice/Bob on the sphere** is **language for aligning instruments and statistics**; this book reserves a chapter to plug **Bell-type public data** into that language — **todo**. Go next to **Chapter 16**: **failures and open loops already on record**.
