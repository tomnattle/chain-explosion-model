# 档案二 · GHZ 实验与 GHZ 态：为什么它「否定」我们这一类模型

**人话一句**：**GHZ** 是 Greenberger、Horne、Zeilinger 三人姓氏缩写——可以想成**三人版「谁的小抄对不上号」**：若坚持每人测量前就有固定答案且不能隔空商量，会推出**自相矛盾**；比两体 Bell 更「一刀见骨」，但真实实验仍有噪声与漏洞。后面 **in-silico** 章是**电脑里的协议游戏**，**不能**顶替实验室原始迹。

**文稿性质**：背景档案；把**标准量子力学框架里** GHZ 与**局域经典图像**的冲突说清楚。本书的泡泡/栅格模型属于**局域递推**一类直觉；读完本篇，你应能精确说出：**被否定的是哪一类陈述**，**不是**什么。

---

## A. GHZ 是谁，解决了什么问题

**1989，Greenberger、Horne、Zeilinger（及 Mermin 的清晰表述）**  
Bell 定理对**两体纠缠**给出**统计性**违反：要累积很多次测量，才能看到**平均上**超过 Bell 界。

GHZ 构造则展示：对**三体或更多体**的特定纠缠态（**GHZ 态**），在理想条件下，可以出现一个**逻辑上的尖锐矛盾**——

> 若坚持「每个粒子在测量前就有确定的、与远处设定无关的答案」（一种**非语境的、局域实在**式的赋值），  
> 那么一组**本应同时成立**的等式，会**互撞车**（**0 = 1** 式的矛盾）。

这被称为 **GHZ 悖论**或 **GHZ 定理**：它把「局域隐变量按那种方式给结果」逼到**单轮论证**里就**站不住**，而不必等大数据统计（当然，真实实验仍有噪声与缺陷）。

---

## B. GHZ 态（极简版）

三量子比特的 **GHZ 态**常写成：

```text
|GHZ⟩ = (|000⟩ + |111⟩) / √2
```

（基矢记号仅作示意；本书不在这里教量子计算。）

**直觉**：它不是「三个各自独立的硬币」；也不是「A 定了 B 就跟着定」那种经典关联能轻易穷尽的。它是**三体一起**才能正确描述的一种**纠缠**。

---

## C. 「证明了什么」——分三层说清楚

**第一层（数学-逻辑层，理想 GHZ）**  
在**标准量子规则**下，对某些**互相对易的可观测量**的选择组合，预言一组**完美相关**；若强行给每个粒子预先指定 **+1 / −1** 型的「客观答案」（且答案不依赖远处**本轮**选测什么——一种常见的**局域隐变量**想象），这些答案**无法同时**满足所有关系。**因此：这一类「预先定好、局域携带」的赋值模型被排除。**

**第二层（实验层）**  
真实实验室用离子、光子、超导比特等**逼近** GHZ；读出的是**有限保真度**的数据，要扣噪声、串扰、丢失。结论通常是：**观测与标准量子预言一致**，与「简单局域赋值表」不一致——但**每一句话都要带误差棒与协议**。

**第三层（哲学层——本书不替你下判决书）**  
GHZ **没有**证明「意识创造实在」或某一种诠释；它**尖锐地打击**的是：**把多体纠缠当成三枚各自有预定答案、只靠经典关联串起来的硬币**——那种图像在理想论证里**直接崩**。

---

## D. 实验大致怎么做（档案骨架）

1. **制备多体纠缠**：例如 trapped ions 用门操作把三离子推到接近 |GHZ⟩。  
2. **选基测量**：每人（每离子）可选不同方向；记录 **+1 / −1** 或等价二元结果。  
3. **检验预言的相关**：看联合概率与 GHZ 预言是否一致；或与 **Mermin 型不等式**对比（多体 Bell-type 界）。  
4. **与经典界对照**：若设备与协议可信，违反**多体 Bell / Mermin**界与违反**局域赋值模型**的叙事并行（细节见专业综述）。

**与 Bell 两体案的区别**  
- Bell：**统计积累**见分晓。  
- GHZ：**理想极限下**可在**逻辑链条**上见分晓；实验上仍要谈**有限数据与噪声**。

---

## E. 已做过哪些方向（类型列举）

| 方向 | 说明 |
|------|------|
| **离子阱** | 多离子 GHZ、全纠缠门集，保真度与读出较可控。 |
| **光子** | 多光子纠缠，难在损耗与符合计数；有 GHZ 与类 GHZ 报道。 |
| **超导量子比特** | 中等规模芯片上的多体纠缠与量子优势演示路线。 |
| **与 Bell 测试结合** | 多体不等式、设备无关协议等。 |

本书仓库中 **`scripts/explore/ghz_medium_v10`** 等属于**模型内 in-silico 审计**，**不是**上述实验室原始迹的替代品——档案与代码要**分开读**。

---

## F. 它为什么「否定我们的模型」——把话说到最清

本书模型（泡泡、格点递推、局域耦合）在**叙事上**承诺：

- 信息/扰动**局域地**从一格传到邻格；  
- 「远处」的结果不应依赖一种**即时、非局域**的协调，除非你把那种协调**显式写进**新的场或新的全局变量（那就**不再是**原来那种「只靠局域泡泡碰泡泡」的最小图像）。

**标准 GHZ 论证所打击的**，正是：

- **给每个粒子预先分配确定的测量答案**；  
- 且这些答案**不随远处本轮测量基的选择而「语境式」地整体改口**（否则你引入的是另一种理论，不是那张最简单的「局域藏宝图」）。

因此：

| 陈述 | 是否被 GHZ「否定」 |
|------|---------------------|
| 「三个粒子各有一张**预先印好的经典答案卡**，且与远处当次选基无关」 | **是**，理想 GHZ 论证下**很难保住**。 |
| 「任何**经典场**、任何**耗散**、任何**介质**只要写得够花就能自动逃掉」 | **否**，不是一句话豁免；你要**具体写出**能否复现 GHZ 相关；本书第三章的损耗**没有**单独给这张豁免状。 |
| 「本书的**离散栅格代码**是否已经**复现**标准 GHZ 实验的全部协议与统计」 | **否**，仓库自有边界；见各 **ghz_*** 脚本的说明与失败记录。 |

**一句话给作者自己的模型**：  
若坚持**只有**局域递推、**没有**允许多体在测量事件上按量子规则非平凡关联，则**标准 GHZ 型纠缠所展示的那类多体相关**，与「最小局域经典赋值」**冲突**——这就是**「否定」的精确含义**：**否定那张过于简单的经典藏宝图**，而不是自动否定你**将来**是否可能写出**另一类**仍局域但更丰富的理论（那要另起炉灶并接受新实验的检验）。

---

## G. 与第二章、第三章的衔接

- **第二章**：同一批数据，换**二值化尺子**，**S** 会跳——提醒 **Bell/CHSH 层**的协议敏感。  
- **第三章**：介质会**吃能量**——但**吃能量本身**不自动解决 **GHZ 赋值矛盾**；那是**相关结构**问题，不只是**幅度衰减**问题。  
- **本篇档案**：当你说「GHZ 否定了泡泡模型」时，请说成：**否定了「只靠局域递推 + 简单预先赋值」那一版最小图像**；本书后文若讨论 **in-silico GHZ**，那是在问**另一套**显式规则能不能、在多大程度上**逼近**公开叙事——**与本篇档案并行**，互不顶替。

---

## H. 深入入口

- Mermin 对 GHZ 的「三硬币悖论」式科普表述。  
- 多体 **Bell 不等式**、**Mermin–Klyshko** 界。  
- 本书目录中 **第11章**（GHZ 与 in-silico 协议审计）及 **`ghz_medium_v10`** 索引。

---

# Archive II · GHZ tests and GHZ states: what exactly “rules out” models like ours

**In one line**: **GHZ** (Greenberger–Horne–Zeilinger) is a **three-body “answer-sheet contradiction”** — sharper than two-body Bell in logic, though real data still carry noise and loopholes. Later **in-silico** chapters are **protocol games on a computer**, **not** raw lab traces.

**Nature of this text**: background — clarifies the clash between GHZ in **standard quantum mechanics** and **local classical pictures**. This book’s bubble / grid model belongs to **local update** intuition; after this archive you should say precisely **what statement is negated** — and **what is not**.

---

## A. Who GHZ were and what problem they sharpened

**1989, Greenberger, Horne, Zeilinger (plus Mermin’s crisp version)**  
Bell’s theorem gives a **statistical** violation for **two-body** entanglement: you need many runs to see an **average** cross of the Bell bound.

The GHZ construction shows: for **three or more bodies** in a specific entangled state (**GHZ state**), under ideal conditions you can get a **sharp logical contradiction** —

> If you insist each particle has a **definite answer before measurement, independent of distant settings** (a **noncontextual, local-realistic** assignment flavor),  
> then a set of equalities that **should all hold** **collide** (a **0 = 1**-style clash).

This is the **GHZ paradox** or **GHZ theorem**: it pushes “local hidden variables assigning outcomes that way” into **single-shot** trouble, not only large-sample statistics (real experiments still have noise and imperfections).

---

## B. GHZ state (minimal)

A three-qubit **GHZ state** is often written:

```text
|GHZ⟩ = (|000⟩ + |111⟩) / √2
```

(Basis notation is illustrative; this book is not teaching quantum computing here.)

**Intuition**: not “three independent coins”; not a classical correlation you can exhaust with “if A is fixed, B follows.” It is **many-body entanglement** that needs all three to describe correctly.

---

## C. “What it proves” — three layers

**Layer 1 (math–logic, ideal GHZ)**  
Under **standard quantum rules**, certain **commuting observable** combinations predict **perfect correlations**; if you **force** predetermined **+1 / −1 style “objective answers”** per particle (answers not depending on distant **this-round** basis choices — a common **local hidden-variable** cartoon), those answers **cannot satisfy all relations at once.** **So: that class of “predetermined, locally carried” assignment models is ruled out.**

**Layer 2 (experiment)**  
Real labs approximate GHZ with ions, photons, superconducting qubits, etc.; data are **finite fidelity** — subtract noise, crosstalk, loss. The usual conclusion: **observations match standard quantum predictions** and disagree with a “simple local assignment table” — **but every sentence needs error bars and protocol.**

**Layer 3 (philosophy — this book does not rule for you)**  
GHZ **does not** prove “consciousness creates reality” or pick an interpretation; it **hits hard** the image of **many-body entanglement as three coins with fixed answers stitched by classical correlation** — that picture **breaks** in the ideal argument.

---

## D. Rough experimental skeleton

1. **Prepare many-body entanglement** — e.g., trapped ions steered toward |GHZ⟩ with gates.  
2. **Choose measurement bases** — record **+1 / −1** or equivalent binary outcomes.  
3. **Check predicted correlations** — joint probabilities vs GHZ predictions; compare to **Mermin-type inequalities** (many-body Bell bounds).  
4. **Contrast with classical bounds** — if devices and protocols are trusted, violating many-body Bell / Mermin bounds parallels narratives about violating **local assignment models** (details in specialist reviews).

**Difference from two-body Bell**  
- Bell: **statistics** decide.  
- GHZ: **ideal limit** can decide on a **logic chain**; experiments still argue **finite data and noise**.

---

## E. Directions that have been pursued (taxonomy)

| Direction | Note |
|-----------|------|
| **Ion traps** | Many-ion GHZ, full gate sets, controllable fidelity and readout. |
| **Photons** | Multi-photon entanglement; loss and coincidence counting are hard; GHZ / GHZ-like reports exist. |
| **Superconducting qubits** | Many-body entanglement and “quantum advantage” style demos on chips. |
| **Combined with Bell tests** | Many-body inequalities, device-independent protocols, etc. |

In this repo, **`scripts/explore/ghz_medium_v10`** and friends are **in-silico protocol audits** — **not** substitutes for raw lab traces — read **archive vs code** **separately**.

---

## F. Why it “rules out our model” — say it cleanly

This book’s model (bubble, lattice update, local coupling) **narratively** commits to:

- information / disturbance **propagates locally** cell to neighbor;  
- “distant” outcomes should not depend on **instant, nonlocal coordination** unless you **explicitly add** new fields or global variables (then it is **no longer** the minimal “only local bubbles bumping bubbles” image).

**What the standard GHZ argument attacks** is:

- **predetermined measurement answers for each particle**;  
- and answers **not “contextually” retuned when distant basis choices change this round** (otherwise you are in a different theory, not the simplest “local treasure map”).

Therefore:

| Statement | Ruled out by GHZ? |
|-----------|-------------------|
| “Each particle has a **preprinted classical answer card**, independent of distant basis choice this round” | **Yes** — hard to save under ideal GHZ reasoning. |
| “Any **classical field**, any **dissipation**, any **medium**, if fancy enough, automatically escapes” | **No** — not a one-line exemption; you must **show** whether you can reproduce GHZ correlations; Chapter 3’s loss **does not** hand you a blanket waiver. |
| “This repo’s **discrete grid** has **reproduced** full standard GHZ protocol and statistics” | **No** — repo has its own bounds; see **`ghz_*`** script notes and failure logs. |

**One line to the author’s model**:  
If you insist on **only** local updates **without** nontrivial many-body correlations at measurement events in the quantum sense, then the **many-body correlations** highlighted by standard GHZ **clash** with the **minimal classical assignment map** — that is the **precise sense of “negation”**: **negating an overly simple classical treasure map**, not automatically negating whether you might someday write **another** still-local but richer theory (that would be a new project with new experimental tests).

---

## G. Bridge to Chapters 2 and 3

- **Chapter 2**: same data, swap **binarization yardstick**, **S** jumps — protocol sensitivity on the **Bell/CHSH** layer.  
- **Chapter 3**: media **eat energy** — but **eating energy alone** does not dissolve the **GHZ assignment contradiction**; that is a **correlation-structure** problem, not only **amplitude decay**.  
- **This archive**: when you say “GHZ kills the bubble model,” say instead: **it kills the minimal “only local updates + simple predetermined assignments” image**; later **in-silico GHZ** asks whether **another explicit ruleset** can **approximate** the public narrative — **parallel** to this archive, **not** a substitute.

---

## H. Deeper pointers

- Mermin’s “three-coin paradox” style exposition of GHZ.  
- Many-body **Bell inequalities**, **Mermin–Klyshko** bounds.  
- In this book’s TOC: **Chapter 11** (GHZ and in-silico protocol audit) and the **`ghz_medium_v10`** index.
