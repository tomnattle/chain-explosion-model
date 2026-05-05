# 第九章 · Chapter 9

**基于 NIST 数据：逐次测量拟合偏振装置在庞加莱球上的等效坐标**  
*NIST-based experiment: per-trial fit of effective Poincaré-sphere coordinates*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**庞加莱球**可以想成「**偏振状态**在球面上的位置」；**拟合**=从读数反推**等效旋钮**转了多少。
> - **这章解决什么**：在 **NIST 同批数据**上，换一条**独立**问题：**装置在数学上等效成什么**？与 **CHSH 主线**并行，互不顶替。
> - **教科书常识**：斯托克斯参数、庞加莱球是**经典光学标准语言**；和量子密度矩阵的**布洛赫球**是亲戚图像。
> - **本书在干什么**：检查**可辨识性**（算出来的旋钮是否靠谱）、**不确定度**；**不要求**你懂矩阵。
> - **和物理学家们**：方法族与光学工程一致；结论层级是**拟合质量**，不是哲学判决。

> **本章任务**  
> 说明仓库中**独立于 CHSH 主线的拟合实验**：把单次 trial 的读出，放到**等效光学元件**（庞加莱球上的角度/相位）语言里，检验**可辨识性**与**不确定度预算**。

## 9.1　为什么要「另一条尺子」

CHSH 关心**关联是否超界**。拟合路线问：**若把装置当成黑箱，单次数据更支持哪组等效参数？**两条线**共享同一 CSV**，但**统计对象不同**——这正是序言里「分开写清」的实例。

## 9.2　逐次拟合与「几何参数」：从哪份脚本进门

本章标题里的**庞加莱球**，在工程上对应：**偏振态 / 波片角 / 等效相位**的一组**连续参数**。仓库**不**保证只有一个「官方拟合脚本」；常见进门点包括：

- **`scripts/explore/nist_same_index_angle_sign_scan_v1.py`**：**角度符号**与指数定义对统计的敏感扫描——拟合前先要**符号约定**不打架。  
- **`scripts/explore/explore_nist_e_delta_three_tracks.py`**：同一底层表上 **多轨（tracks）** 处理对照（文档串里可见 **Alice/Bob one-hot** 等有效样本定义）——与 CHSH 轨**并行**时，须锁**同一 trial 子集**。

对每次符合事件（定义见**你锁定的**那份脚本），构造**代价函数**，在 **Alice/Bob** 各一组角度上搜索最优。输出应包含：**点估计**、**是否病态**（多解、平坦方向）、**不确定度**（自助法或局部线性近似）。**没有不确定度而只有点估计的图，本书不当作定论。**

## 9.3　可辨识性与诚实失败

若数据对某参数组合**几乎不敏感**，拟合会给出**大不确定度**或**多谷**——这在工程上叫**不可辨识**或**弱辨识**。本书把这类输出也当作**有效结果**：说明「这条尺子在此数据上**不够锋利**」，而不是强行给漂亮点估计。

> **本章边界**  
> 等效坐标是**模型类内**的参数化；**不**自动等于设备商提供的校准证书。与 CHSH 数值的**交叉引用**须在**同一 trial 子集与权重**前提下进行。

**与第十五章（规划稿）的关系**：**第15章**预留 **Bell 类公开数据上 Alice/Bob 球面坐标联合拟合** 的专章——**文稿占位、代码待作者有空再写**；**本章已述语言与纪律仍为准**，将来实现时应与此章**对齐定义**而非另起炉灶。

## 9.4　小结

你现在有两类对象：**Bell 型标量**与**装置几何型参数**。下一章专门把 **CHSH** 再拆：**二值化轨道 vs 连续代理轨道**，并用**合成样本**做**阴性对照**。

---

# Chapter 9 · NIST-based experiment: per-trial fit of effective Poincaré-sphere coordinates

**基于 NIST 数据：逐次测量拟合偏振装置在庞加莱球上的等效坐标**  
*NIST-based experiment: per-trial fit of effective Poincaré-sphere coordinates*

> **For general readers — what this picture is about**
>
> - **In plain words**: The **Poincaré sphere** is where **polarization states** sit as points on a ball; **fitting** means inferring **how far the effective knobs turned** from readouts.
> - **What this chapter does**: On **the same NIST batch**, ask a **separate** question: **what does the hardware look like in math?** Runs **parallel** to the **CHSH main line**, not a substitute.
> - **Textbook baseline**: Stokes parameters and the Poincaré sphere are **standard classical optics**; they are cousins of the **Bloch sphere** picture for qubits.
> - **What the book is doing**: Check **identifiability** (whether inferred knobs are meaningful) and **uncertainty**; **no** matrix fluency required.
> - **For working physicists**: Methods sit in the same family as optical engineering; conclusions are about **fit quality**, not philosophy.

> **This chapter’s job**  
> Describe **fitting experiments independent of the CHSH headline pipeline**: put per-trial readouts in the language of **effective optical elements** (angles / phases on the Poincaré sphere), and test **identifiability** plus an **uncertainty budget**.

## 9.1 Why a “second yardstick” helps

CHSH asks whether **correlations cross a bound**. The fitting line asks: **treating the apparatus as a black box, which equivalent parameters does each trial favor?** Both lines **share one CSV** but **different statistical objects** — the preface’s “write them separately” in practice.

## 9.2 Per-trial fitting and “geometry parameters”: where to enter the repo

**Poincaré sphere** here means a **continuous parameter block** for **polarization / waveplate angles / effective phase**. The repo does **not** promise a single “official fit script”; common entry points:

- **`scripts/explore/nist_same_index_angle_sign_scan_v1.py`**: sensitivity of statistics to **angle sign** and index definitions — **fix sign conventions before fitting**.  
- **`scripts/explore/explore_nist_e_delta_three_tracks.py`**: **multi-track** handling on the same underlying table (strings mention **Alice/Bob one-hot** style valid-sample definitions) — when run **parallel** to CHSH tracks, **lock the same trial subset**.

For each coincidence event (definition per **your chosen** script), build a **cost function** and search optimal angles for **Alice** and **Bob**. Outputs should include **point estimates**, **ill-conditioning** (multiple solutions, flat directions), and **uncertainty** (bootstrap or local linearization). **Plots with point estimates but no uncertainty are not treated as verdicts here.**

## 9.3 Identifiability and honest failure

If the data are **nearly insensitive** to some parameter combo, the fit returns **huge uncertainty** or **multiple valleys** — **unidentifiable** or **weakly identifiable** in engineering terms. This book treats that as a **valid result**: the yardstick is **not sharp enough on this table**, rather than forcing a pretty point estimate.

> **Chapter boundary**  
> Equivalent coordinates are **parameterizations inside a model class**; they do **not** automatically equal vendor calibration sheets. **Cross-talk with CHSH numbers** must share the **same trial subset and weights**.

**Relation to Chapter 15 (planning draft)**: Chapter **15** reserves a dedicated slot for **joint Alice/Bob sphere-coordinate fitting on Bell-type public data** — **manuscript placeholder, code when the author has bandwidth**; **the language and discipline in this chapter remain authoritative**; future code should **align definitions** here rather than invent a parallel dialect.

## 9.4 Close

You now have two kinds of objects: **Bell-style scalars** and **device-geometry parameters**. Next chapter unpacks **CHSH** again: **binarization track vs continuous-proxy track**, with **synthetic** **negative controls**.
