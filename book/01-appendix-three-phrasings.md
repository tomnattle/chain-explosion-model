# 附录一　三种表述：泡泡、涟漪与链式爆炸（真空介质动力学版）

**泡泡、涟漪、链式爆炸**是**同一套直觉**的三种**口语昵称**，不是三套宇宙论；下面这张表把它们对齐到离散公式与代码习惯。

> **导读与契约**
> 下文中，您将看到同一套物理图像在不同语境下使用不同的名称。**这不是三套彼此矛盾的理论，而是描述同一套“真空介质动力学”的三个直觉入口**。您可以选择最容易在脑海中成像的表述，再对照本章的公式与代码核对。

在本书的讨论中，我们使用**介质 / 连续背景**等说法，来描写扰动如何**局域地、一步一步**传递；这与序言中的边界一致：**它们是推演与数值实现的脚手架**，不等于宣称「真空中存在机械以太」或某种已判决的宇宙本体论。光并非飞行的小球，而是一种**可在此脚手架下表述的**扰动传递；因为空间是三维的且各向同性，直觉上常画成球面波前。数值实现里用二维格点近似时，会伴随由 `λ` 与耦合系数体现的**逐步损耗与重分配**。

---

## 一、三种表述的核心直觉重点

| 表述 | 直觉重点 | 最易误解之处 | 与底层代码的关系 |
| :--- | :--- | :--- | :--- |
| **泡泡** | 扰动在三维空间中向外胀大的球面波前；遇到物质界面会产生次级波前 | 误以为“泡泡”仅仅是肥皂泡那样的二维薄膜结构 | 相干复数格点 `U` 的一步传播，强度表征为能量密度 `|U|^2` |
| **涟漪** | 介质受到扰动后一圈圈传开的过程；状态从一格传递至相邻格点 | 误以为这只是二维平面水波，与三维光场无关 | 二维格点上的局域场量、邻域耦合与衰减系数 |
| **链式爆炸** | 能量爆发后，扰动以局域因果方式向多邻格分配、级联并分叉 | 误以为这是一种剧烈的化学爆炸或破坏性事件 | `propagate_double_slit` 内核中的多向分配系数 `A, S, B` |

---

## 二、从直觉到代码：介质动力学的数学表达

为了在计算中体现“介质动力学”的理念，我们不对麦克斯韦方程组或薛定谔方程做教条化的应用，而是将其转化为可运行的离散更新规则。

### 1. 介质与动力学传导

在离散实现中，我们用格点上的实值场量 **E_t(x, y)** 近似上述图像（`t` 为步数）。当某格被激发时，扰动按邻域规则**分配**到相邻格点，而不是「整团能量弹道式平移」。

### 2. 球面传递与损耗

三维直觉是球面波前；**与 `chain_explosion_numba.propagate_double_slit` 对齐的接收式**在格点上为 **λ 乘以若干邻格贡献之和**（全部为加；被 `barrier` 挡住的邻格不计入对应项）：

```text
E[t+1](x,y) = λ × (
      A·E[t](x-1, y) + B·E[t](x+1, y)
    + S·E[t](x, y-1) + S·E[t](x, y+1)
    + (S/2)·E[t](x-1, y-1) + (S/2)·E[t](x-1, y+1)
    + (S/2)·E[t](x+1, y-1) + (S/2)·E[t](x+1, y+1)
)
```

* **λ**：每步全局衰减（LAM）。
* **A, B, S**：沿 +x、−x、侧向及对角（折半）的**分配权重**，不是相减关系。

相干一步（`ce_engine_v3_coherent.propagate_coherent`）用复数格点 **U**，主方向为 +x、对角步长 **d = √2**：

```text
U[t+1](x,y) = λ × (
      A · exp(i·k) · U[t](x-1, y)
    + S · exp(i·k) · U[t](x, y-1) + S · exp(i·k) · U[t](x, y+1)
    + (S/2) · exp(i·k·d) · U[t](x-1, y-1) + (S/2) · exp(i·k·d) · U[t](x-1, y+1)
)
```

强度取 **|U|²**。可运行对照：[appendix_model_three_intuitions_demo.py](appendix_model_three_intuitions_demo.py)（仓库根目录：`python book/appendix_model_three_intuitions_demo.py`）。

### 3. 读出与统计

当场量到达探测器时，仪器作为介质边界的一部分，会进行局部取样。我们在此不对全场做非局域的坍缩假设，而是记录连续响应或经过阈值判定的离散信号。

---

## 三、术语使用指南

* **对外主名（本书）**：**泡泡 / 泡泡模型**（球面波前、次级波前的图像）。
* **口语辅助**：描写**水波式一圈圈**或**格点间一步一步**传递时，多用**涟漪**。
* **历史与项目名**：强调**多向分配、级联、分叉**时，可用**链式爆炸**（与仓库名 `chain-explosion-model` 同源）；与「泡泡」「涟漪」**指同一套离散核**，不是另一套理论。

请按阅读习惯任选其一建立直觉，再以本章公式与代码核对。实质都是：**同一套局域离散更新（加可选相干相位），用不同画面说话。**

---

# Appendix I · Three phrasings: bubbles, ripples, and chain explosion (vacuum-medium dynamics)

**bubble, ripple, chain explosion** are three **nicknames** for the **same discrete kernel** — this appendix is a **crosswalk** to formulas and code habits, not a second cosmology.

> **Guide and compact**
> Below you will see the same physical picture named differently in different contexts. **These are not three contradictory theories; they are three intuitive entry points into the same “vacuum-medium dynamics” story.** Pick the image that sticks, then check it against the formulas and code in this chapter.

Throughout the book we use **medium / continuous backdrop** language to describe how disturbances **propagate locally, step by step**; this matches the preface: **they are scaffolding for reasoning and numerics**, not a claim that “mechanical ether fills the vacuum” or that some final ontology has been decided. Light is not a flying pellet; it is a disturbance that **can be expressed on this scaffold**; because space is three-dimensional and isotropic, the natural cartoon is often a spherical wavefront. When the implementation uses a 2D lattice, **gradual loss and redistribution** show up through `λ` and the coupling coefficients.

---

## 1. Core intuition for each phrasing

| Phrasing | Intuition | Easy mistake | Tie to the underlying code |
| :--- | :--- | :--- | :--- |
| **Bubble** | A spherical front expanding in 3D; material interfaces spawn secondary fronts | Thinking a “bubble” is only a 2D soap film | Coherent complex lattice `U`, one propagation step; intensity as energy density `|U|^2` |
| **Ripple** | The medium carries a disturbance outward in rings; state hands off neighbor to neighbor | Thinking this is only 2D water waves, unrelated to a 3D light field | Local fields on a 2D lattice, neighborhood coupling, decay |
| **Chain explosion** | After a burst, the disturbance allocates locally to multiple neighbors, cascades, and branches | Thinking this means a chemical blast or destructive event | Multidirectional split coefficients `A, S, B` inside the `propagate_double_slit` kernel |

---

## 2. From intuition to code: math for medium dynamics

To embody “medium dynamics” in computation, we do **not** dogmatically paste Maxwell or Schrödinger onto the page; we turn the picture into **runnable discrete update rules**.

### 1. Medium and dynamical transfer

In the discrete build, a real field **E_t(x, y)** on the lattice approximates the cartoon (`t` is the step index). When a site fires, the disturbance **allocates** to neighbors under local rules — not as a **rigid ballistic relocation** of a lump of energy.

### 2. Spherical transfer and loss

The 3D intuition is a spherical front; the **receiver-style** update aligned with `chain_explosion_numba.propagate_double_slit` multiplies **λ by a sum of neighbor contributions** (all additive; neighbors blocked by `barrier` drop out of their terms):

```text
E[t+1](x,y) = λ × (
      A·E[t](x-1, y) + B·E[t](x+1, y)
    + S·E[t](x, y-1) + S·E[t](x, y+1)
    + (S/2)·E[t](x-1, y-1) + (S/2)·E[t](x-1, y+1)
    + (S/2)·E[t](x+1, y-1) + (S/2)·E[t](x+1, y+1)
)
```

* **λ**: global damping per step (LAM).
* **A, B, S**: **allocation weights** along +x, −x, sideways, and diagonals (halved) — **not** a subtraction recipe.

The coherent step (`ce_engine_v3_coherent.propagate_coherent`) uses complex lattice **U**, main direction +x, diagonal step **d = √2**:

```text
U[t+1](x,y) = λ × (
      A · exp(i·k) · U[t](x-1, y)
    + S · exp(i·k) · U[t](x, y-1) + S · exp(i·k) · U[t](x, y+1)
    + (S/2) · exp(i·k·d) · U[t](x-1, y-1) + (S/2) · exp(i·k·d) · U[t](x-1, y+1)
)
```

Intensity is **|U|²**. Runnable cross-check: [appendix_model_three_intuitions_demo.py](appendix_model_three_intuitions_demo.py) (repo root: `python book/appendix_model_three_intuitions_demo.py`).

### 3. Readout and statistics

When the field meets a detector, the instrument acts as part of the medium boundary and samples locally. We do **not** assume a nonlocal collapse of the entire field; we record continuous responses or thresholded discrete signals.

---

## 3. How to use the vocabulary

* **Primary outward name (this book)**: **bubble / bubble model** (spherical fronts and secondary fronts).
* **Colloquial helper**: **ripple** when you want the **concentric-ring** or **step-to-step-on-the-lattice** feel.
* **History and repo name**: **chain explosion** when you stress **multiway allocation, cascade, branching** (same root as `chain-explosion-model`); it names the **same discrete kernel** as “bubble” and “ripple,” not another theory.

Pick whichever image reads best, then reconcile with the formulas and code here. Substantively it is all: **the same local discrete update (plus optional coherent phase), spoken with different pictures.**