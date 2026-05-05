# 第二章 · Chapter 2

**为什么我开始怀疑**  
*Why I started asking questions*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**Bell 实验**可以粗想成「两处读数有多同步」的考场；**NIST** 是美国国家标准与技术研究院，这里主要把它当作**公开实验数据从哪下载**的一个名字。
> - **这章回答什么**：模型再美，别人凭什么信？当公开记录显示**同一批数，换一步处理，故事会从 1.1 变到 2.3**，普通人该不该问一句：**规则写清了吗？**
> - **教科书常识**：Bell、CHSH 等与**量子纠缠、非经典关联**绑在一起；主流共识有牢固实验支撑。**本书不宣称「一夜推翻教科书」**。
> - **本书在干什么**：作者以**非学院派**身份交代：**为什么去抠公开数据、为什么关心「怎么计数」**；你可以把它当**侦探手记的前传**。
> - **和物理学家们**：**不做人身攻击**；争论对象是**记录、协议、统计口径**是否透明，不是「谁笨」。

## 2.0　先说说我是谁

我不是物理学家，也没有受过任何正规的物理训练。我是一个普通人，平时对数字和逻辑感兴趣，业余时间会读一些科普文章、跑一些代码。

有一天，我在读关于双缝实验的科普——就是那个「光穿过两条缝，后面出现条纹」的实验。教科书的解释是「波粒二象性」：光有时候像波，有时候像粒子。我读了很多遍，总觉得这个解释像是在回避问题，而不是在回答问题。

于是我开始自己想：有没有更简单的图像，能解释同样的现象？

第一章的那个泡泡模型，就是我想出来的答案。我觉得它很美，很直接。我开始用代码把它实现出来，测试它能不能解释各种光学现象。

结果它通过了很多测试。有一次我随口问聊天程序：「这个模型能不能解释量子纠缠？」——对方说，不能，常见理由是 Bell 一类实验。**这只是我个人追问的起点，不是拿 AI 当权威论据。**

我不太服气，决定自己去找公开数据、用代码试。

## 2.1　模型很美，但被判了死刑

Bell 实验是物理学里一个著名的实验，它讨论「两处读数的同步性能强到什么地步」。

它有一个结论（在通行的理论表述里）：如果世界是像涟漪一样「一步步局域传递」的——就像我的球面泡泡模型——那么那种同步性在 **S** 这类指标上**过不了某道栏杆**。许多实验报告说栏杆被跨过去了。于是**在那一套叙述里**，我的模型像是被判了死刑。

我接受了这个判决，暂时放下了这个问题。

## 2.2　但我回来了

一段时间之后，我开始好奇：论文里那个 **S**（同步分数），到底是怎么算出来的？

我找到了一组公开的实验数据——美国国家标准与技术研究院（NIST）在 2015 年公开的一批实验记录。任何人都可以下载。我就下载了，然后开始用代码分析。

我做了一件很简单的事：用两种方式处理同一批数据，看看那个「同步分数」**S**会不会不一样。

结果让我停下来很久。

## 2.3　同一批数据，两个不同的数字

那个衡量「两处读数有多步调一致」的数字，在论文里常记作 **S**（你把它想成一个**同步分数**就行）。许多介绍会说：S 超过 **2**，就像跨过了一道栏杆，用来支持「量子纠缠」的说法。

我用第一种方式处理数据——把探测器的输出保留为连续的数值——得到：

**S = 1.117**

我用第二种方式处理同一批数据——把探测器的输出强制读成 +1 或 -1 两个值——得到：

**S = 2.297**

同一批数据。同一组实验记录。只改了一个处理步骤：把连续的数字砍成两个值。

S 从 1.1 跳到了 2.3。

那道栏杆在 **S = 2**。很多人把「跨过去」当作量子世界的证据。但我发现：**跨过去的那一段高度，有很大一块是后来「把连续读数砍成 +1/-1」这一步抬出来的**——不是原始记录自己变高了，是我们换了一把尺子。

> **挑剔的读者会问：** 这两个数是不是「放之四海而皆准」？  
> **不是。** 它们来自**一批具体的公开记录 + 一套写进代码的后处理**。换数据子集、换符合窗、换归一化，数字会变——本书后面要做的，正是把**尺子**一条条摊开；**任何 headline 数字都以该章写明的定义为准**，不要把本章当成中学实验室的操作指南。

## 2.4　这让我想到了什么

我回想起第一章的那张图：探测器读取的，是泡泡上的一个点。

把连续的数字砍成 +1/-1——这一步，是不是就是把「球面泡泡上的一个局部读数」强制读成「一个完整的粒子」？

如果是，那么 S 值的跳跃，也许不是因为「量子纠缠很神秘」，而是因为「我们在测量的时候，用了一把不合适的尺子」。

这个问题，我对着数据和规则**查了好几个月**。后面各章，就是我沿着这个问题往下挖的过程。我不会只给你看两个数字，我会把每一把尺子都摆在桌上，让你自己去比。

## 2.5　小结与下一章

这一章只完成一件事：让你记住**同一批记录，换一把后处理尺子，故事会变**——并且记住：**任何数字都要回到「定义与管道」**，不要把我举的 **1.1 / 2.3** 当成放之四海皆准的实验课结论。

下一章不接着吵 Bell，而是回到更底层：**格子程序里，能量为什么会「漏」、书里说的「热」指什么**——那是后面所有「洗掉条纹、改掉统计」的共同地面。

Bell 与 GHZ 的**历史、不等式到底排除什么、实验长什么样**，见档案 **`06-archive-bell.md`**、**`07-archive-ghz.md`**（可与本章交叉阅读）。

---

# Chapter 2 · Why I started asking questions

**为什么我开始怀疑**  
*Why I started asking questions*

> **For general readers — what this picture is about**
>
> - **In plain words**: A **Bell test** is roughly an exam in **how tightly two distant readouts line up**; **NIST** is the U.S. National Institute of Standards and Technology — here, mainly **where a public dataset was downloaded**.
> - **What this chapter answers**: However pretty a model is, why should anyone trust it? When public records show **the same batch of numbers can move the story from 1.1 to 2.3 after one processing step**, shouldn’t a lay reader ask: **were the rules written down?**
> - **Textbook baseline**: Bell, CHSH, etc. are tied to **entanglement and nonclassical correlations**; the mainstream consensus has strong experimental support. **This book does not claim to “overturn the textbook overnight.”**
> - **What the book is doing**: The author, **outside the academy**, explains **why public data and “how we count” matter**; treat it as **prequel to a detective notebook**.
> - **For working physicists**: **No personal attacks**; the argument is whether **records, protocols, and statistical definitions** are transparent — not “who is dumb.”

## 2.0 Who I am, briefly

I am not a physicist and have no formal physics training. I am an ordinary person who likes numbers and logic and sometimes reads popular science and runs code.

One day I was reading about the double-slit experiment — light through two slits, stripes on a screen. Textbooks invoke “wave–particle duality”: light is wave-like sometimes, particle-like other times. I reread that many times; it felt like **dodging the question** rather than answering it.

So I asked whether a **simpler picture** could explain the same thing.

The bubble model in Chapter 1 was my answer. I liked how direct it was. I coded it and tested it against optical phenomena.

It passed a lot of checks. Once I casually asked a chatbot whether the model could explain quantum entanglement — the usual answer was no, citing Bell-type tests. **That was only my personal starting point, not an appeal to AI as authority.**

I was stubborn enough to **pull public data and try it in code**.

## 2.1 A beautiful model, “sentenced”

Bell tests are famous: they probe **how correlated two distant readouts can be**.

In the standard theoretical packaging: if the world propagates **locally, step by step** — like my spherical-bubble picture — then a quantity like **S** cannot cross a certain bar. Many experiments report crossing it. **In that narrative**, my model looks **dead on arrival**.

I accepted the verdict and set the question aside — for a while.

## 2.2 But I came back

Later I wondered: in papers, how exactly is **S** computed?

I found a public dataset — NIST released experimental records in 2015. Anyone can download them. I did, and started analyzing in code.

I did something simple: process **the same batch** two ways and see whether **S** moved.

The result made me pause for a long time.

## 2.3 One dataset, two headline numbers

The figure that measures “how in-step two readouts are” is often called **S** (think **synchronization score**). Popular accounts say: if **S** clears **2**, a bar is crossed — evidence for “quantum entanglement.”

**First pipeline** — keep detector outputs **continuous**:

**S = 1.117**

**Second pipeline** — **force** outputs into **+1 or −1**:

**S = 2.297**

Same batch. Same experimental record. One changed step: **chopping continuous numbers into two buckets.**

S jumped from 1.1 to 2.3.

The bar sits at **S = 2**. Many treat crossing it as evidence of the quantum world. What I saw: **a chunk of the “height” over the bar came from the step that hard-bins continuous readouts into ±1** — the raw record did not magically rise; **we swapped yardsticks.**

> **A skeptical reader asks:** Are these two numbers universal?  
> **No.** They come from **one specific public record + one pipeline frozen in code.** Change the subset, coincidence window, normalization — numbers move. Later chapters **lay out each yardstick**; **any headline figure follows the definition in that chapter** — do not treat this as a high-school lab recipe.

## 2.4 What that suggested

I thought back to Chapter 1: the detector samples **a point on the bubble.**

Chopping continuous numbers into ±1 — is that **forcing a local sample on a spherical bubble** into **a whole “particle”**?

If so, the jump in **S** might owe less to “mysterious entanglement” and more to **measuring with the wrong ruler.**

I spent **months** on the data and the rules. The following chapters are the dig. I will not flash only two numbers; I will put **every ruler on the table** so you can compare.

## 2.5 Close and next chapter

This chapter does one job: remember **one record, swap post-processing, the story moves** — and remember **every number returns to “definition and pipeline”**; do not treat my **1.1 / 2.3** as a universal lab moral.

Next chapter does not keep arguing Bell; it goes under the floor: **why energy “leaks” on the lattice and what “heat” means here** — the shared ground for later “washing out fringes” and “moving statistics.”

Bell and GHZ **history, what inequalities rule out, what experiments look like**: archives **`06-archive-bell.md`**, **`07-archive-ghz.md`** (can be read alongside this chapter).