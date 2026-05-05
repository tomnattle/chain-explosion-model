# 第十六章 · Chapter 16

**没通过的测量：诚实记录**  
*What failed: an honest record*

> **本章任务**  
> 把「失败」从情绪变成**清单**：哪些假设在数据或 in-silico 上**未闭合**、哪些曲线**未过门**、哪些**叙事曾写早**——并说明**是否归档、如何复查**。

## 16.1　失败为什么要入册

若一本书只写胜利，读者无法知道**边界在哪**。本书把**未通过的门禁**、**未复现的对照**、**可辨识性崩溃**与**参数阱**当作**一等公民**：它们告诉你：**别把钱押在尚未钉死的推广上**。

## 16.2　几类「没通过」

- **模型内**：某次 `ce_*` / `ghz_*` / `ripple_*` 扫描**未达阈值**或**与阴性对照冲突**。  
- **审计层**：某条 NIST 管道在**改分母**后结论**不再稳定**；或**子样本**不足以下判断。  
- **解释层**：某段口语推广被 **`explore_critique_*`** 内部否决——**类比保留，机制不升格**。

## 16.3　如何复查（脚本与目录线索）

**目录**：**`battle_results/`**、**`artifacts/`**、**`papers_final/`** —— 优先文件名含 **`fail`**、**`red`**、**`closure`**、**`anatomy`**、**`honest`**、**`hardcore`** 的报告或 JSON。

**脚本级「失败解剖」示例**（非穷尽）：

- **`scripts/explore/ripple_quantum_tests/v10_fail_anatomy.py`**  
- **`scripts/explore/ripple_quantum_tests/ripple_v6_identifiability_audit.py`**  
- **`scripts/explore/ghz_honest_cost_curve_v11.py`**、**`ghz_hardcore_audit_v18.py`**（命名即态度）  
- **`analyze_v3_open_loops.py`**（开放环/未闭合诊断）

复查纪律：**同一 commit** 或 **artifact 内嵌 hash** 对齐版本；**禁止**只贴一张截图不附脚本与数据版本。

> **本章边界**  
> 「没通过」**不是**对任何实验「判死刑」；它是**本书当前版本**在**自述规则**下的状态。下一版可能推翻——前提是**规则与数据一并更新**。

**假大象**要量，也要**量不出来的地方**。第三部分换节奏：**设想**两条——**经典光力学计算路径**与**涟漪动力系统**——明确标为**构想**，不是成品。

---

# Chapter 16 · What failed: an honest record

**没通过的测量：诚实记录**  
*What failed: an honest record*

> **This chapter’s job**  
> Turn “failure” into a **list**: which assumptions stayed **open** on data or in-silico, which curves **missed gates**, which narratives were **premature** — and **whether archived, how to re-audit**.

## 16.1 Why failures belong in the book

If a book only reports wins, readers cannot see **where the edge is**. This book treats **failed gates**, **unreproduced controls**, **identifiability collapses**, and **parameter traps** as **first-class citizens**: they say **do not bet on promotions that are not yet nailed down**.

## 16.2 Kinds of “did not pass”

- **In-model**: a `ce_*` / `ghz_*` / `ripple_*` scan **missed thresholds** or **conflicts with negative controls**.  
- **Audit layer**: a NIST pipeline **stops being stable** after **denominator edits**; or **subsamples** too small to judge.  
- **Explanation layer**: colloquial hype vetoed by **`explore_critique_*`** — **keep analogy, do not upgrade mechanism**.

## 16.3 How to re-audit (directories and script hints)

**Directories**: **`battle_results/`**, **`artifacts/`**, **`papers_final/`** — prefer filenames with **`fail`**, **`red`**, **`closure`**, **`anatomy`**, **`honest`**, **`hardcore`**.

**Script-level “failure anatomy” examples** (non-exhaustive):

- **`scripts/explore/ripple_quantum_tests/v10_fail_anatomy.py`**  
- **`scripts/explore/ripple_quantum_tests/ripple_v6_identifiability_audit.py`**  
- **`scripts/explore/ghz_honest_cost_curve_v11.py`**, **`ghz_hardcore_audit_v18.py`** (names signal intent)  
- **`analyze_v3_open_loops.py`** (open-loop / non-closure diagnostics)

Re-audit discipline: align **same commit** or **artifact-embedded hash**; **do not** post a lone screenshot without script + data version.

> **Chapter boundary**  
> “Did not pass” is **not** a death sentence on any experiment; it is **this book’s current build** under **its own stated rules**. A later edition may reverse — only if **rules and data update together**.

The **fake elephant** must be measured — and **where measurement stops**. Part III shifts tempo: two **sketches** — **classical optical computing pathway** and **ripple propulsion** — explicitly labeled **speculation**, not product.
