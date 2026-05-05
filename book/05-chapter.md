# 第三章 · Chapter 3

**介质、损耗与热**  
*Medium, loss, and heat*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**λ（lambda）** 在程序里常表示「每一步还剩百分之几的能量」——像传接力时**每一棒都掉一点球**；**热**在这里多半是**漏掉的能量还没细讲去哪**，诚实留空。
> - **这章回答什么**：漂亮泡泡进电脑后，**为什么条纹会糊、为什么能量不会无限堆**？也就是：**理想故事和带损耗的模拟差在哪**。
> - **教科书常识**：真实介质有吸收、色散；热力学里损耗常对应**不可逆**。本书格子是**极简卡通**，不是材料手册。
> - **本书在干什么**：把「漏」写成**你能调的数字**，避免嘴上说衰减、图上却永远不衰减；**不要求**你打开代码，看见希腊字母可**整段跳过**。
> - **和物理学家们**：**不宣称新热力学定律**；只交代**模型里哪些已写、哪些故意没写**。

---

## 3.1　理想图与真实模拟

主画面可以略写细节，**一进具体程序就要把「漏」接上线**。

最简单的双缝演示在程序 `scripts/ce/ce_00_double_slit_demo.py` 里。每走一步，场上的数会先乘一个**小于 1** 的系数，代码里叫 **LAMBDA**，书里常写成 **λ**，这里你可以先记成 **「每步留下百分之多少」**——典型大约 **0.85**，也就是**每步大约丢掉一成多**（不是精确物理换算，只是量级直觉）。

**没传下去的那一份，在格子里不再出现**——你可以想象成传接力时球掉了一块、被草皮吃掉了；**掉到哪、变成什么温度**，我们多数脚本**没有细画**，只诚实说：**这里停笔了**。

---

## 3.2　三种「漏法」（故事版）

格子程序里，**漏**常见有三种摆法（可以叠在一起）：

**（1）每一步都按比例变瘦——λ（LAMBDA）**  
像全班传纸条，每人抄完撕掉一小角再往下传。除非程序里另外写了**一直在发光的源**，否则**不会凭空变胖**。

**（2）在某些格子多吞一口——吸收**  
经过缝口、吸收片、探测器那块区域时，再乘一个 **(1−η)**：η 越大，吞得越狠。条纹变浅，常常是你在路上**加了一块会吃能量的海绵**——**吃多少写在参数里**，不是事后说一句「神秘退相干」。

**（3）有的格子天生难走——「涩格子」**  
在 `scripts/explore/explore_disordered_media_scan.py` 这类实验里，有的格点像**泥洼**，传导打折扣。路还是那条邻格传递的路，但**难走的地方多了，远处就更暗、更花**。

**自己问一句就行：** 这张图有没有「每步变瘦」？有没有「某块特别能吃」？光是不是一直在补充？

---

## 3.3　「热」在本书里=什么意思

**不是说**我们已经算清了每一摄氏度的来龙去脉。

在本书里，**「热」多半是一句短话**：指**没留在格子「可传播数字」里的那些份额**。它们**不再进入下一步**——叙事上可以想成一个**很大的环境口袋**（专业书常叫**热浴 / bath**），**口袋里面具体装着什么**，我们**多数时候没画**。

还有一种「热」是**故意捣乱**：程序里给数字加一点随机抖动，看结论会不会翻船——这叫**压力测试**，**不是**宣称算出了真实温度场。

另有一条名字里带 **thermal** 的审计脚本（`scripts/explore/ripple_quantum_tests/ripple_thermal_triplet_preregistered_audit.py`）：它用**另一套连续方程**玩「有损波动 + 参数能不能被规矩地找回来」的游戏，和 `ce_*` 那种**爬楼梯式格子**不是同一个式子，但**态度一样：损耗写清楚，规则写清楚**。

---

## 3.4　哪些算「已经做实」，哪些算「留口子」

**程序里已经一而再、再而三用到的：**

- **漏**可以用变瘦、吃一口、涩格子等方式**写进代码**；  
- 漏法会改变**亮暗、条纹清不清、传得远不远**——后面 Bell/CHSH、GHZ 模拟、涟漪玩具曲线，都默认**世界会吃能量**，只是每章盯的侧面不同。

**我们故意不说死、留给以后研究的：**

- 很多旋钮还是**没有和现实米、秒一一钉死**的「纯数字把手」；  
- 环境口袋里到底该装哪种微观图像、格子极限能不能和某条连续方程**严丝合缝对上**——**书里没有装成已经做完的定理**。

---

## 3.5　小结

**世界会饿，传播会瘦**——这不是模型丢脸，而是**后面谈测量、谈统计时，默认站着的地面**。下一部分（从第4章起，见 `02-contents.md`）会把同一套「会吃能量的格子」接进**双缝、吸收体、延迟选择与 Bell/CHSH 玩具**——条纹怎么弱、曲线怎么弯，都站在本章这块地上；统计尺子怎么换，则接续第二章那条线。

本章把**「会漏」**接进程序，与第一章主画面形成**有意的分工**，而不是互相打架。

---

# Chapter 3 · Medium, loss, and heat

**介质、损耗与热**  
*Medium, loss, and heat*

> **For general readers — what this picture is about**
>
> - **In plain words**: **λ (lambda)** in code often means “what fraction of energy survives each step” — like **dropping the baton a little every relay leg**; **heat** here mostly means **energy that leaked out without a full micro-story yet** — honestly left open.
> - **What this chapter answers**: Once the pretty bubble enters the computer, **why fringes blur and why energy does not pile up forever** — i.e., **what changes between the ideal story and a lossy simulation**.
> - **Textbook baseline**: Real media absorb and disperse; thermodynamics ties loss to **irreversibility**. This lattice is a **minimal cartoon**, not a materials handbook.
> - **What the book is doing**: Write the “leak” as **knobs you can turn**, so we do not preach decay while plots never decay; **no** code required — if Greek letters irritate you, **skip the paragraph**.
> - **For working physicists**: **No claim of new thermodynamic laws**; only **what is implemented vs deliberately omitted** in the model.

---

## 3.1 Ideal pictures vs honest simulation

The main cartoon can stay clean; **once you run code, plug in the leak.**

The minimal double-slit demo lives in `scripts/ce/ce_00_double_slit_demo.py`. Each step multiplies the field by a **number below 1**, called **LAMBDA** in code and **λ** in the book — shorthand: **“what fraction survives each step.”** A typical value is about **0.85**, i.e. **you lose a bit more than ten percent per step** (order-of-magnitude intuition, not a calibrated physical conversion).

**What does not propagate onward simply disappears from the lattice** — like dropping part of the baton into the grass; **where it went and what temperature it became** is **not detailed** in most scripts — we **stop the story there**, honestly.

---

## 3.2 Three ways to “leak” (story version)

Lattice code usually implements **loss** in three combinable ways:

**(1) Uniform thinning every step — λ (LAMBDA)**  
Like passing a note: each person tears off a corner before forwarding. Unless the code adds a **steady source**, nothing **grows from nothing**.

**(2) Extra bites at certain sites — absorption**  
At slits, absorber sheets, or detector regions, multiply by **(1−η)**; larger **η** means a hungrier sponge. **Shallower fringes** often mean you **put a sponge on the path** — **how much is a parameter**, not a post-hoc “mysterious decoherence.”

**(3) Intrinsically rough sites — “sticky” cells**  
In scans like `scripts/explore/explore_disordered_media_scan.py`, some sites act like **mud** — coupling is discounted. The neighborhood rule is the same, but **more rough patches** make the far field **dimmer and messier**.

**Sanity check:** Does this picture have per-step thinning? Local hungry patches? A steady source?

---

## 3.3 What “heat” means in this book

**Not** that we have traced every Celsius degree.

Here **“heat” is usually shorthand** for **whatever share no longer lives in the lattice’s “propagating numbers.”** It **does not enter the next step** — narratively, think of a **huge environment pocket** (textbooks say **thermal bath**); **what exactly sits inside** is **mostly not drawn**.

Another “heat” is **deliberate noise**: jitter added to stress-test whether conclusions flip — **a robustness test**, **not** a claim about a real temperature field.

There is also an audit script with **thermal** in the name (`scripts/explore/ripple_quantum_tests/ripple_thermal_triplet_preregistered_audit.py`): it plays a **different continuous equation** game (“lossy waves + can parameters be recovered cleanly”). It is **not** the same formula as the **stair-step `ce_*` lattice**, but the **attitude matches: write loss, write rules.**

---

## 3.4 What is “done” vs what stays open

**Already used again and again in code:**

- **Leak** can be coded as thinning, local bites, sticky cells;  
- leak changes **brightness, fringe clarity, reach** — later Bell/CHSH, GHZ sims, and ripple toy curves all assume **the world eats energy**, focusing on different sides each chapter.

**Deliberately not closed:**

- many knobs are still **pure numbers**, not pinned to real meters and seconds;  
- what belongs inside the environment pocket, whether the lattice limit **locks cleanly** to a chosen continuum equation — **the book does not pretend those theorems are finished.**

---

## 3.5 Close

**The world gets hungry; propagation gets thin** — not a shame for the model, but **the floor assumed when we later talk measurement and statistics.** From Chapter 4 on (see `02-contents.md`), the same **energy-eating lattice** meets **double slits, absorbers, delayed choice, and Bell/CHSH toys** — fringe weakening and curve bending stand on this ground; swapping statistical yardsticks continues Chapter 2’s thread.

This chapter wires **leakage** into the program, **on purpose alongside** Chapter 1’s main picture — they **divide labor**, they do not fight.
