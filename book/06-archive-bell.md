# 档案一 · Bell 实验与 Bell 不等式

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**Bell 不等式**像一道**应用题上限**：若世界完全由「本地小抄」决定（测量前结果就写好了，且不能超光速通气），某些**关联统计**不能太高；实验上若反复测到更高，就逼你放弃「那种」本地解释。
> - **这档案解决什么**：把**历史脉络**（EPR、隐变量、Bell、Aspect 以降）和**实验长什么样**说清楚，让你读后面章节时不至于「只见过一个 S 数字」。
> - **教科书里的名字**：爱因斯坦—波多尔斯基—罗森（**EPR**）、**Bell（贝尔）**、**CHSH**（四人姓氏缩写，一种常用的 Bell 型检验）、**Aspect（阿斯佩）** 等实验家。**公式**在档案后文有，但**核心是比较界 vs 观测**。
> - **本书立场**：仓库既做**格子玩具**，也做**公开数据审计**；**不**把某一趟仿真直接等同于「证伪整个量子力学」。**是否违背教科书**：实验共识支持量子预言；本书问的是**公开记录上统计对象怎么取**。
> - **你需要会代码吗**：**不需要**；这是**背景说明书**。

**文稿性质**：供本书读者对照的背景档案；**不是**对当代实验的完整综述，也不是对任何实验室的判决书。具体数值与协议以各章及原始论文为准。

---

## A. 历史脉络：问题从哪来

**1935，EPR**  
爱因斯坦、波多尔斯基、罗森提出一个思想实验：若量子力学完备，某些「纠缠」粒子对似乎允许**超距关联**；他们相信自然界底层应是**局域的**（一边发生的事不应瞬间决定另一边的结果），因而怀疑量子力学的描述是否完备。

**玻尔与哥本哈根传统**  
强调测量与互补性，不把「同时赋予粒子确定位置与动量」当作合法图景。

**隐变量思路**  
若存在**我们尚未看见的额外变量**（隐变量），粒子在测量前就可能带有「预定结果」，表观随机只是对隐变量的无知——这样世界仍可想象成**局域、经典式因果**的，只要这些隐变量按局域规则分布。

**Bell 登场前的气氛**  
许多人直觉上希望：存在一种**局域、实在**的底层图像，能复现量子预言。Bell 要追问的是：**这到底行不行？能不能用数学钉死边界？**

---

## B. Bell 做了什么：不等式是什么，不是什么

**1964，John Bell**  
在一篇现在已成为经典的论文里，Bell 关心的不是「量子力学对不对」，而是：

> 若世界由**局域隐变量**按某种经典概率规则产生结果，且满足**局域性**（一边的测量设定不能瞬间改变另一边的隐变量分布），那么某些**可观测的相关量**必须满足一组**不等式**。

这就是**Bell 型不等式**的家族。最常在实验里出现的一种变形叫 **CHSH 不等式**（四人名字 Clauser–Horne–Shimony–Holt）：用四个计数率组合成一个量 **S**，在一大类**局域隐变量模型**里必须满足 **|S| ≤ 2**（书中第二章用 **S** 讲故事时，指的就是这一类对象；具体定义依赖**如何把连续读数变成 ±1、事件如何配对、分母怎么取**——所以同一批原始记录可以算出不同的 **S**）。

**Bell 不等式证明了什么？**

- **证明了**：在明确写出的前提（局域性 + 隐变量产生结果的通常假设）下，**有一类数学结构必须成立**；量子力学对某些纠缠态的预言**会打破**这类结构。  
- **没有证明**：「意识」「超光速信号」或某一种解释学；也没有单独「证明量子力学终极正确」——它是对**一类经典式局域模型**的**排除**（在实验与附加假设满足时）。

**一句话**：Bell 给「局域经典式因果 + 通常隐变量」画了一条**红线**；标准量子纠缠预言**踩过红线**。

---

## C. 「实验」在测什么：思想骨架

典型 **Bell 测试**（以两光子偏振为例）：

1. **制备**：产生一对在某种意义上「关联」的光子（实验室宣称接近理论上的纠缠态）。  
2. **分开**：光子 **A**、**B** 飞向两处，空间上拉开，保证类空分离（尽可能关**局域性漏洞**）。  
3. **独立选择测量方向**：Alice 随机选一组分析角度，Bob 随机选另一组；角度在飞行中或临近测量前选定（与**测量设定独立性**、关闭**自由选择漏洞**有关）。  
4. **记录**：每次符合得到计数；累积统计。  
5. **构造 S 或类似量**：把计数组合成 Bell 不等式里出现的那类表达式。  
6. **对比**：若 **S**（或等价量）稳定地**超过经典界**（CHSH 里常取 **2** 为讨论栏杆），在**标准诠释 + 标准漏洞关闭叙事**下，就**不利于**「局域隐变量按那种方式产生关联」的简单图像。

**常见「漏洞」**（读者在新闻里会见到）：

- **探测效率 / 探测漏洞**：探测器只抓到一部分事件，若子样本有偏，经典模型有时可「模仿」违反。  
- **局域性漏洞**：若测量设定或结果仍能以低于光速的方式串通，不等式的前提被破坏。  
- **记忆 / 记忆型隐变量**：若允许设备跨轮次「记仇」，讨论要换模型类。  

**2015 年前后**，多个实验组宣称在**同时关断主要漏洞**的前提下观察到违反（不同平台：光子、金刚石色心、超导等）。学界对「哲学上是否已彻底说服所有人」仍有讨论，但**技术共识**大致是：在当代接受的假设包下，**局域隐变量按 Bell 那类方式组织**已极难自洽。

---

## D. 已做过哪些类型的实验（档案式列举）

下列是**类型学**，不是完整文献表；年份与组名便于你按关键词检索。

| 类型 | 大致内容 |
|------|-----------|
| **早期光学** | 20 世纪 70–80 年代起，用光子偏振做 CHSH；Aspect 等（1982）缩小局域性漏洞关切。 |
| **离子阱** | 用囚禁离子做纠缠与 Bell 违反，探测效率高、态制备可控。 |
| **光子 + 高效率探测器** | 向关闭探测漏洞推进。 |
| **随机数 + 类空分离** | 用遥远随机源选测量基，强化「设定独立性」叙事。 |
| ** loophole-free / 全主要漏洞关闭** | 2015 年前后多个实验室报道（不同物理平台）。 |
| **表观违反经典界的大规模网络与场测** | 量子通信、设备无关协议等工程方向延伸。 |

**与本书仓库的交点**：第二章讨论的 **NIST 公开记录**属于「把同一批数据用不同后处理管道算 **S**」——这**不替代**上述实验物理学史，但**承接** Bell 测试对**统计对象与协议**的敏感性。

---

## E. 与「泡泡 / 局域传递」模型的关系（本书立场）

本书第一章的泡泡图像，在**叙事上**强调：**扰动局域地、一步一步传递**；第二章又交代：在**通行的 Bell 叙述**里，这类**局域经典因果 + 通常隐变量**的打包，很难与**已报道的纠缠违反**兼容。

**因此**：Bell 实验在当代话语里，常被说成对「你这种直观」的**死刑判决**——本书第二章接受这句话的**情绪**，但把**数字怎么算**拉回可审计地面。

**读者应带走的三点**

1. **Bell 不等式**是**数学**：在给定前提下，局域隐变量必须满足某条界。  
2. **实验**是在**尽力满足那些前提**的前提下，看自然界是否**踩界**。  
3. **本书**关心：踩界叙事里，**尺子与分母**是否总已摊开——这与 Bell 的精神（把假设写清）**同向**，而不是反科学。

---

## F. 推荐阅读入口（自行深入）

- Bell 原论文及现代教科书中的 **CHSH** 推导。  
- 综述与科普：以「局域隐变量」「loophole-free」为关键词检索近年 **Review**。  
- 本书后文：栅格 **Bell/CHSH 玩具**（`ce_bell*`）与公开数据审计章节——**模型内数值**与**对记录的审计**分开阅读。

---

# Archive I · Bell tests and Bell inequalities

> **For general readers — what this picture is about**
>
> - **In plain words**: A **Bell inequality** is like a **homework upper bound**: if the world were entirely driven by **local hidden instructions** (outcomes fixed before measurement, no faster-than-light coordination), certain **correlation statistics** cannot get too large; if experiments keep exceeding the bound, you must give up **that** local picture.
> - **What this archive does**: Lay out **history** (EPR, hidden variables, Bell, Aspect and after) and **what experiments look like**, so later chapters are not “just an S number.”
> - **Textbook names**: Einstein–Podolsky–Rosen (**EPR**), **Bell**, **CHSH** (four surnames — a common Bell-type test), experimentalists like **Aspect**. **Formulas** appear below, but the spine is **bound vs observation**.
> - **This book’s stance**: The repo runs **grid toys** and **public-data audits**; it does **not** equate one simulation run with “disproving all of quantum mechanics.” **Does it contradict textbooks?** Experimental consensus backs quantum predictions; this book asks **how statistical objects are chosen on public records**.
> - **Code required?** **No** — this is **background**.

**Nature of this text**: background for readers of this book; **not** a full survey of contemporary experiments and **not** a verdict on any lab. Numbers and protocols follow each chapter and the primary literature.

---

## A. Historical thread: where the problem came from

**1935, EPR**  
Einstein, Podolsky, and Rosen posed a thought experiment: if quantum mechanics is complete, some “entangled” pairs seem to allow **nonlocal correlations**; they believed nature’s substrate should be **local** (what happens on one side should not instantly fix the other), so they questioned whether quantum mechanics is complete.

**Bohr and the Copenhagen line**  
Stress measurement and complementarity; assigning simultaneous definite position and momentum to one particle is not treated as a valid picture.

**Hidden-variable hope**  
If **extra variables we do not see** exist, outcomes might be **predetermined** before measurement; apparent randomness is ignorance of those variables — the world could still look **locally, classically causal** if the variables obey local rules.

**Before Bell**  
Many hoped for a **local, realistic** substrate that reproduces quantum predictions. Bell asked: **can this work at all — can math draw a hard line?**

---

## B. What Bell did: what the inequality is — and is not

**1964, John Bell**  
In what became a classic paper, Bell was not asking “is quantum mechanics right?” but:

> If the world is produced by **local hidden variables** under ordinary classical probability rules, and **locality** holds (one side’s measurement setting cannot instantly retune the other side’s hidden-variable distribution), then certain **observable correlations** must obey **inequalities**.

That is the Bell family. A common experimental variant is **CHSH** (Clauser–Horne–Shimony–Holt): four rates combine into **S**; a broad class of **local hidden-variable models** requires **|S| ≤ 2** (when Chapter 2 uses **S**, it means this kind of object; the exact definition depends on **how continuous readouts become ±1, how events pair, how denominators are chosen** — so one raw table can yield different **S**).

**What Bell inequalities prove**

- **They prove**: Under stated premises (locality + ordinary hidden-variable outcome generation), **a mathematical structure must hold**; quantum predictions for some entangled states **break** that structure.  
- **They do not prove**: “consciousness,” “superluminal signals,” or any one interpretation; nor do they alone “prove quantum mechanics forever” — they **rule out a class of classical local models** (when experiments and auxiliary assumptions hold).

**One line**: Bell drew a **red line** for “local classical causality + ordinary hidden variables”; standard entanglement predictions **step over** that line.

---

## C. What a “Bell test” measures: conceptual skeleton

A typical **Bell test** (two photons, polarization):

1. **Prepare** a pair “correlated” in the lab’s claimed sense (near an entangled state).  
2. **Separate** photons **A** and **B** spatially for spacelike separation (closing the **locality loophole** as far as possible).  
3. **Choose bases independently** — Alice picks an analysis angle, Bob another; angles are set in flight or just before measurement (ties to **measurement-setting independence** and the **free-choice loophole**).  
4. **Record** coincidences per trial; accumulate statistics.  
5. **Build S or an equivalent** from counts.  
6. **Compare** — if **S** stably **beats the classical bar** (CHSH often uses **2** as the rhetorical fence), under **standard interpretation + standard loophole narrative**, that **disfavors** the simple picture of “local hidden variables producing correlations that way.”

**Common “loopholes”** (you will see these in news):

- **Detection / fair-sampling**: if detectors miss many events, biased subsamples can let classical models mimic violations.  
- **Locality**: if settings or outcomes can still coordinate subluminally, the inequality’s premises fail.  
- **Memory / memory-type hidden variables**: if devices “remember” across rounds, the model class changes.

**Around 2015**, several groups reported violations with **major loopholes closed** in one run (photons, NV centers, superconducting qubits, etc.). “Has everyone been philosophically persuaded?” is still debated; the **technical consensus** is roughly: under accepted auxiliary packages, **local hidden variables organized Bell’s way** are extremely hard to sustain.

---

## D. Types of experiments (taxonomy, not a full bibliography)

This is a **type list**, not exhaustive literature; years and group names help keyword search.

| Type | Rough content |
|------|---------------|
| **Early optics** | Photons, CHSH from the 1970s–80s; Aspect et al. (1982) narrowed locality concerns. |
| **Ion traps** | High control, high detection efficiency for entanglement and Bell violations. |
| **Photons + high-efficiency detectors** | Push toward closing the detection loophole. |
| **Random numbers + spacelike separation** | Distant random sources for bases, strengthening “setting independence” narratives. |
| **Loophole-free / all-major-loopholes-closed** | Multiple labs ~2015 (different platforms). |
| **Large network / field demos** | Quantum communication, device-independent protocols, engineering extensions. |

**Intersection with this repo**: Chapter 2’s **NIST public record** is “**same data, different pipelines for S**” — it **does not replace** experimental history, but it **inherits** Bell tests’ sensitivity to **statistical objects and protocols**.

---

## E. Relation to the “bubble / local propagation” picture (this book)

Chapter 1’s bubble story **narratively** stresses **local, step-by-step propagation**; Chapter 2 adds: in the **standard Bell narrative**, that package of **local classical causality + ordinary hidden variables** struggles with **reported entanglement violations**.

**So**: Bell tests are often called a **death sentence** for “your intuition” — this book accepts the **emotional weight** of that line, but pulls **how the number is computed** back onto auditable ground.

**Take away three things**

1. **Bell inequalities** are **math**: under given premises, local hidden variables must obey a bound.  
2. **Experiments** ask whether nature **crosses the bound** while **trying to satisfy those premises**.  
3. **This book** asks whether **yardsticks and denominators** are always laid bare — aligned with Bell’s spirit (write assumptions clearly), **not** anti-science.

---

## F. Pointers if you want to go deeper

- Bell’s original paper and **CHSH** derivations in modern textbooks.  
- Reviews and popular pieces: search **local hidden variables**, **loophole-free**.  
- Later in this book: grid **Bell/CHSH toys** (`ce_bell*`) and public-data audit chapters — read **in-model numbers** and **record audits** **separately**.
