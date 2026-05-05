# 第一章 · Chapter 1

**泡泡**  
*The bubble*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：「波」常被画成一条弯线；这里先把它想成**石头落水后一圈圈往外传的动静**——水并没有整盆泼到对岸，只是**相邻的地方依次晃了一下**。
> - **这章回答什么**：光（或任何「干扰」）到底是**小球直飞**，还是**某种状态在空间里接力传递**？
> - **教科书里常见说法**：经典光学用**波动**也能解释干涉；量子物理会再引入**波粒二象性**等框架。**本章不站队、不推翻**，只给你一张能看懂的**动图**。
> - **本书在干什么**：用泡泡/水波画面，建立**不必先背公式**也能跟上的「传播」直觉；**不要求**你读代码。
> - **和物理学家们**：**不矛盾**——这是**看图说话**的一层翻译，不是替代麦克斯韦或量子力学方程。

## 1.1　一块石头落进水里

你见过石头落进平静水面的样子。

石头落下去的那一刻，水面上出现了一个点。然后，从这个点开始，一圈一圈的纹向外扩散。

现在我问你：那一圈圈向外走的纹，是什么？

不是水从中心跑到了岸边。水分子几乎没有移动，它们只是在原地上下晃动。真正在走的，是一种状态——一种「这里刚刚被扰动过」的状态——从一个点传给了邻居，邻居再传给邻居的邻居。

那个向外走的圆圈，不是一个东西在飞。它是一个消息在传。

## 1.2　现在想象光

我想邀请你用同样的方式想象光。

不是一颗小球从灯泡里射出来，沿直线飞到你眼睛里。

而是：光源发出一个扰动，这个扰动像水面的涟漪一样，向外无限扩展——不是圆圈，而是球面，因为空间是三维的。一个不断膨胀的球面泡泡，从光源向外扩散，碰到什么就在那里产生一个新的泡泡，新的泡泡再继续扩散。

这就是本书的模型。非常简单，只有一张图：

- 光源发出一个球面泡泡。
- 泡泡碰到物体，产生新的泡泡。
- 探测器在泡泡经过的时候，读取到泡泡上的一个点。

就这三句话。

## 1.3　那个「点」是什么

注意最后一句：探测器读取到的，是泡泡上的一个点。

不是整个泡泡。不是泡泡的全部信息。只是泡泡在那一刻经过探测器时，留下的一个局部印记。

就像你站在岸边，水面的涟漪经过你的脚时，你感受到的只是那一刻、那一点的水面高低——而整个水面上其他地方发生的事，你完全感觉不到。

探测器读到的那个点，在物理教科书里有一个名字，叫做「光子」。

本书不打算争论这个名字对不对。本书只是想说：如果光其实是一个球面泡泡，那么「光子」不是泡泡本身，而是泡泡被局部采样的结果。

一个读数，不等于整张图。

## 1.4　这本书要做的事

我不知道这个模型是不是对的。

没有人摸过真正的大象，但每个人都在描述大象。我想画一头假大象，让所有测量真大象的工具来测量我画的这头——哪些能通过，哪些不能，诚实记录下来。

第一章到这里就结束了。几乎没有公式和数字；只借用了教科书里常见的「光子」一词，方便和后面的「一个读数」对照。

只有一张图：一个泡泡，碰到东西，产生新的泡泡，探测器读取一个点。

## 1.5　这本书不是一本哲学书

上面这张图，是本书的起点。但我不是在写哲学。

在后面的章节里，我会把这张图搬进**电脑里的格子世界**：光还是那颗「泡泡」，但每一步传播都会像传球一样**漏掉一点**（后面第三章专门讲这个）；障碍物、缝、探测器，都会变成格子上**看得见、改得动**的规则。

再往后，我会用同一套格子程序去对照一些**著名的物理实验**（例如 Bell 实验、GHZ 实验——名字陌生没关系，第二章会从故事讲起）。我想看的很简单：**当我们换一把「怎么读数、怎么统计」的尺子，结论会不会跟着变。**

第二章里你会看到一个**在本书锁定的数据源与处理定义下**复现的例子：同一批公开实验记录，只改一步后处理，一个关键数字会从大约 **1.1** 跳到大约 **2.3**。它不是「证明全世界怎样」，而是在提醒：**读数和规则若不写清，故事会跟着变。**

具体统计定义、脚本与数据路径，以**后文对应章节**为准；序言与第一章只搭架子。

泡泡、涟漪、链式爆炸三种口语指向同一套离散核，见 **`book/01-appendix-three-phrasings.md`**。

书里如果出现「NIST」「Bootstrap」这类词，都只是**数据来源**和**算不确定性的一种方式**；不懂可以跳过名词，抓住主线——**假大象要经得起同一套、写清楚规则的检验。**

---

# Chapter 1 · The bubble

**泡泡**  
*The bubble*

> **For general readers — what this picture is about**
>
> - **In plain words**: “Wave” is often drawn as a wiggly line; here, think first of **rings spreading after a stone hits water** — the water does not fly across the pond; **neighboring patches nudge each other in turn**.
> - **What this chapter answers**: Is light (or any “disturbance”) **a pellet in straight flight**, or **something handed along through space**?
> - **Textbook baseline**: Classical optics already explains interference with **waves**; quantum physics adds **wave–particle** language and more. **This chapter does not pick a camp or “disprove” anything** — it offers a **picture you can animate in your head**.
> - **What the book is doing**: Use bubble / water imagery to build a propagation intuition **before** you memorize formulas; **no** code required.
> - **For working physicists**: **No contradiction** — this is a **visual gloss**, not a replacement for Maxwell or quantum equations.

## 1.1 A stone drops into still water

You have seen a stone hit a calm surface.

The instant it lands, a dot appears. Then rings move outward from that dot.

Ask yourself: what **are** those rings?

Not water traveling from center to shore. Molecules barely drift; they mostly bob in place. What travels is a **state** — “this patch was just disturbed” — passed to a neighbor, then the neighbor’s neighbor.

The moving circle is not an object in flight. It is **news** on the move.

## 1.2 Now imagine light

Try the same move for light.

Not a tiny ball shooting out of a bulb in a straight line to your eye.

Instead: the source kicks the medium; the kick spreads outward like ripples — not a circle but a **sphere**, because space is 3D. An **expanding spherical bubble** leaves the source, hits objects, spawns new bubbles, and those bubbles keep spreading.

That is the model of this book. Three sentences:

- The source launches a spherical bubble.
- A bubble hitting matter spawns new bubbles.
- When a bubble sweeps a detector, the detector reads **one point** on it.

That is all.

## 1.3 What that “point” is

Note the last line: the detector reads **a point on the bubble**.

Not the whole bubble. Not global information. Just a **local imprint** as the bubble passes.

Standing on the shore, you feel only the height at your feet when a ripple crosses — you feel nothing of the rest of the surface.

In textbooks that local readout is often called a “photon.”

This book will not fight over the name. The claim is simpler: if light is a spherical bubble, then a “photon” is **not** the bubble — it is what you get **sampling the bubble locally**.

One readout is not the whole map.

## 1.4 What this book tries to do

I do not know whether the model is right.

No one has touched the whole elephant, yet everyone describes it. I want to draw a **fake elephant** and run every tool meant for the real one — log what passes, what fails, honestly.

Chapter 1 stops here: almost no formulas or numbers; it borrows the textbook word “photon” only to contrast with “one readout.”

One picture: a bubble hits things, spawns bubbles, a detector reads a point.

## 1.5 This is not a philosophy book

That picture is the starting point — but the book is not doing philosophy.

Later chapters move the image into a **lattice world on a computer**: still the same “bubble,” but each propagation step **leaks** a little (Chapter 3); slits, barriers, and detectors become **explicit, editable rules** on the grid.

Still later, the same lattice code meets **famous experiments** (Bell, GHZ — unfamiliar names are fine; Chapter 2 tells the story). The question is blunt: **when we swap the yardstick for readout and statistics, does the conclusion move?**

Chapter 2 gives a **reproducible example under this book’s locked data source and processing definition**: on one public record, a single post-processing change moves a key figure from about **1.1** to about **2.3**. It is not “proof about the whole world”; it is a reminder: **if readout and rules stay vague, the story moves.**

Exact statistical definitions, scripts, and data paths belong in **later chapters**; preface and Chapter 1 only frame the scaffold.

The three nicknames bubble / ripple / chain explosion point to the **same discrete kernel** — see **`book/01-appendix-three-phrasings.md`**.

Words like “NIST” or “bootstrap” are just **data sources** and **a way to quantify uncertainty**; if the jargon annoys you, skip it and hold the spine — **the fake elephant still has to pass the same, clearly written rules.**
