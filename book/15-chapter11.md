# 第十一章 · Chapter 11

**GHZ 与 in-silico 协议审计**  
*GHZ and in-silico protocol audit*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：**in-silico**=在**硅片里**（电脑里）跑；**门控/保留率**=「哪些数据算数、哪些扔掉」的过滤器。
> - **这章解决什么**：**档案里的 GHZ 逻辑**（见 **`07-archive-ghz.md`**）和**仓库里的介质模拟**各管一段；分清**不能互相顶替**。
> - **教科书常识**：多体 GHZ 态、违背检验是**严肃实验前沿**；真实数据有噪声与漏洞分析。
> - **本书在干什么**：展示**协议透明**时故事如何写；**不**拿仿真输出冒充实验室原始迹。
> - **和物理学家们**：**不宣称**「GHZ 被推翻」；只做**边界内**的可复现叙述。

> **本章任务**  
> 分清三件事：**标准 GHZ 叙事**（见 **`07-archive-ghz.md`**）、仓库 **in-silico** 里**门控/保留率/介质 toy**在干什么、以及**为什么不能**用本脚本输出替代实验室原始迹。

## 11.1　档案 vs 代码

档案回答：**局域经典赋值为何在理想 GHZ 论证里碰壁**。`scripts/explore/ghz_medium_v10/` 等回答：**在给定离散规则与协议下，我们能跑到哪一步、哪里失败、哪里需要加成本曲线**。两者**互补**，**不**互替。

## 11.2　`ghz_medium_v10` 族：协议对象是什么

目录 **`scripts/explore/ghz_medium_v10/`**（仓库快照）：

| 文件 | 大致用途 |
| :--- | :--- |
| `explore_ghz_medium_wave_v10.py` | **v10 波/介质**主探索入口 |
| `v10_1_metric_scalpel.py` | **指标解剖**（scalpel） |
| `v10_2_metric_robustness.py` | **鲁棒性**对照 |
| `v10_3_selection_tax_audit.py` | **选样/税**（selection tax）审计——分母是否被「税」改写 |
| `v10_4_real_cost_curve.py` | **成本曲线**（保留率、门控代价等） |

典型产物：**阈值扫描**、**保留率**、**门控子样本**、与**预设失败条件**的对照。读报告时先找：**统计的是哪些事件**、**分母是否被筛选重写**——与第八至十章同一纪律。

## 11.3　其他 `ghz_*` 审计与失败归档

并行可读（**非** `medium_v10` 独占）：**`ghz_chain_explosion_audit_v16.py`**、**`ghz_hardcore_audit_v18.py`**、**`ghz_phase_loop_cost_curve_v14.py`**、**`ghz_honest_cost_curve_v11.py`** 等——命名里带 **honest / hardcore / cost** 的，往往**刻意**把**难看曲线**也存档。

仓库刻意保留**未闭合**与**红色自检**：防止叙事跑在数据前面。

> **本章边界**  
> **in-silico GHZ** 是**模型内**探索；**不**构成对具体实验室 GHZ 实验的复刻结论。 headline 数字以 **`artifacts/ghz_*`** 或章内引用的 JSON 为准。

## 11.4　小结

多体线是**硬**的：直觉上泡泡再美，也要过 **GHZ 类相关**这一关——档案说明**关卡的逻辑形状**，代码说明**我们离那形状还有多远**。下一章换一条**并行管线**：**涟漪量子**四项玩具基准（激光、半导体、MRI、原子钟）。

---

# Chapter 11 · GHZ and in-silico protocol audit

**GHZ 与 in-silico 协议审计**  
*GHZ and in-silico protocol audit*

> **For general readers — what this picture is about**
>
> - **In plain words**: **in-silico** means “on silicon” — **inside a computer**; **gating / retention** is the filter for **which rows count and which get thrown away**.
> - **What this chapter does**: Keep **GHZ logic in the archive** (see **`07-archive-ghz.md`**) **separate** from **medium simulation in the repo** — they **must not replace each other**.
> - **Textbook baseline**: Many-body GHZ states and violation tests are **serious experimental frontiers**; real data carry noise and loophole analysis.
> - **What the book is doing**: Show how the story reads when **protocols stay transparent**; **do not** pass simulation output off as raw lab traces.
> - **For working physicists**: **No** claim that “GHZ experiments are overturned”; only **in-bounds**, reproducible narrative.

> **This chapter’s job**  
> Separate three things: **standard GHZ narrative** (see **`07-archive-ghz.md`**), what **in-silico gating / retention / medium toys** do in the repo, and **why** script output cannot stand in for laboratory raw traces.

## 11.1 Archive vs code

The archive answers **why naive local classical assignments hit a wall in ideal GHZ reasoning**. `scripts/explore/ghz_medium_v10/` and friends answer **under stated discrete rules and protocols, how far we can run, where we fail, where cost curves must be added**. They **complement** each other; they do **not** substitute.

## 11.2 The `ghz_medium_v10` family: what statistical object?

Directory **`scripts/explore/ghz_medium_v10/`** (repo snapshot):

| File | Rough role |
| :--- | :--- |
| `explore_ghz_medium_wave_v10.py` | Main **v10 wave / medium** exploration entry |
| `v10_1_metric_scalpel.py` | **Metric scalpel** |
| `v10_2_metric_robustness.py` | **Robustness** checks |
| `v10_3_selection_tax_audit.py` | **Selection-tax** audit — whether denominators are rewritten by “tax” |
| `v10_4_real_cost_curve.py` | **Cost curves** (retention, gating price, etc.) |

Typical artifacts: **threshold scans**, **retention**, **gated subsamples**, contrasts with **preset failure conditions**. When reading reports, first find **which events are tallied** and **whether denominators are rewritten by selection** — same discipline as Chapters 8–10.

## 11.3 Other `ghz_*` audits and failure archives

Also readable (not exclusive to `medium_v10`): **`ghz_chain_explosion_audit_v16.py`**, **`ghz_hardcore_audit_v18.py`**, **`ghz_phase_loop_cost_curve_v14.py`**, **`ghz_honest_cost_curve_v11.py`** — names with **honest / hardcore / cost** often **intentionally** archive **ugly curves** too.

The repo keeps **open loops** and **red self-checks** on purpose: stop narrative from outrunning data.

> **Chapter boundary**  
> **in-silico GHZ** is **in-model** exploration; it is **not** a replication verdict on any specific lab GHZ run. Headline numbers follow **`artifacts/ghz_*`** or JSON cited in-chapter.

## 11.4 Close

The many-body thread is **hard**: however pretty the bubble intuition, it still faces **GHZ-style correlations** — the archive states **the logical shape of the hurdle**, the code states **how far we still are from that shape**. Next chapter switches to a **parallel pipeline**: the **ripple-quantum** four toy benchmarks (laser, semiconductor, MRI, atomic clock).
