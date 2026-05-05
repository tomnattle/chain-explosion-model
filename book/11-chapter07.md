# 第七章 · Chapter 7

**栅格 Bell/CHSH 玩具与前沿曲线**  
*Grid Bell/CHSH toys and frontier curves*

> **本章任务**  
> 说明仓库如何用**同一套局域传播 + 分支/偏振规则**构造 **CHSH 型统计**；**S** 或等价量在参数空间里如何扫出**前沿**——以及这些结果**只**在脚本定义下有效。

## 7.1　为什么需要「玩具」层

第二章的 **1.1 / 2.3** 来自**公开记录 + 后处理**。在此之前，仓库用 **`ce_bell*`** 在**完全可控**的格子上问：**当耦合、噪声、阈值、分束比变化时，类 CHSH 指标怎么走**。这是**模型内实验室**：协议写在你眼皮底下。

## 7.2　`ce_bell*` 脚本索引（仓库快照）

下列均在 **`scripts/ce/`**；职责以文件名为纲，细节以**脚本内协议块**为准：

| 文件 | 大致用途 |
| :--- | :--- |
| `ce_bell.py` | Bell/CHSH **栅格玩具**基线入口之一 |
| `ce_bell_chsh_evaluator.py` | CHSH **评估器**（计数→S 或等价量，定义锁定在文件内） |
| `ce_bell_chsh_frontier.py` | 参数空间 **前沿曲线**扫描 |
| `ce_bell_chsh_robustness_fixed.py` | **鲁棒性**对照（固定协议下的扰动） |
| `ce_bell_final_curve_fixed.py` | **定版曲线**复现/汇总型脚本 |
| `ce_bell_v11_stress_test.py` | **应力测试**（缺陷图、噪声等） |

典型要素仍是：两路或多路、**二元标签/偏振代理**、在 **A、S、B、LAMBDA** 上扫描。**不同脚本的「事件」与分母可能不同**——比较两次运行前，先**对齐定义**。

### 一次运行快照（`ce_bell.py`：马吕斯曲线 vs cos²）

**`ce_bell.py`** 对 **10 个偏振角差** 各跑一整轮 **STEPS=800** 传播，在固定探测器像素上取 **符合量 ~ m1×m2**，再除以 **angle2=0** 处的基线做归一化，与 **cos²θ** 逐点比（定义以脚本为准）。图写入 **`scripts/ce/bell_test_result.png`**。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | 在仓库根：`PYTHONPATH` 指向仓库根后执行 `python scripts/ce/ce_bell.py` |
| **快照日期** | **2026-05-05**（脚本默认 HEIGHT/WIDTH、A/S/B、λ、**ANGLES** 等） |
| **基线符合（未归一化）** | 约 **3.79×10⁻⁹**（`angle2=0` 时的 coincidence，仅作归一化分母） |
| **对 cos² 的 RMSE** | 约 **4.5×10⁻¹⁸**（双精度下与解析曲线几乎重合） |
| **`np.allclose(..., atol=0.1)`** | **True**（脚本自检；**仅**曲线贴合，**不是**完整 Bell/CHSH 认证——见脚本 log **「not a full Bell-test certification」**） |

**读法**：这一层是 **「玩具符合 + 马吕斯代理」**；**CHSH 数值与 NIST 档案**在 **第八至十章** 另起炉灶。勿把本图的 **cos² 贴合** 说成实验室 **S 值** 或 **无局域性** 结论。

## 7.3　前沿与 stress

**前沿**：见 `ce_bell_chsh_frontier.py`。**应力**：见 `ce_bell_v11_stress_test.py`（缺陷格、噪声式踢脚等）。目的：**模型在受挤时是否自洽**，不是替自然界下判决书。

> **本章边界**  
> 玩具层 **≠** NIST 审计层；前者服务**直觉与灵敏度**，后者服务**公开记录上的尺子**（第八至十章）。**禁止**把某次 `ce_bell` 的数值直接说成「实验室已证伪/证实」。

你有了**从双缝可见度走到 CHSH 形状**的**内部桥梁**。下一章离开纯玩具，进入 **NIST complete-blind 类公开档案**：**分母、符合窗、索引语义**成为主角。

---

# Chapter 7 · Grid Bell/CHSH toys and frontier curves

**栅格 Bell/CHSH 玩具与前沿曲线**  
*Grid Bell/CHSH toys and frontier curves*

> **This chapter’s job**  
> Explain how the repo builds **CHSH-style statistics** from **one local propagation stack + branching / polarization rules**; how **S** (or an equivalent) is scanned into **frontiers** in parameter space — and why these numbers are **only** valid under each script’s definition.

## 7.1 Why a “toy” layer exists

Chapter 2’s **1.1 / 2.3** came from **public records + post-processing**. Before that, the repo uses **`ce_bell*`** on a **fully controlled** lattice to ask: **as coupling, noise, threshold, and split ratio move, how do CHSH-like figures behave?** This is an **in-model lab**: the protocol is written where you can see it.

## 7.2 `ce_bell*` script index (repo snapshot)

All under **`scripts/ce/`**; details follow the **protocol blocks inside each script**.

| File | Rough role |
| :--- | :--- |
| `ce_bell.py` | Baseline **grid toy** entry for Bell/CHSH |
| `ce_bell_chsh_evaluator.py` | CHSH **evaluator** (counts → S or equivalent; definition locked in file) |
| `ce_bell_chsh_frontier.py` | **Frontier** scans in parameter space |
| `ce_bell_chsh_robustness_fixed.py` | **Robustness** checks under a fixed protocol |
| `ce_bell_final_curve_fixed.py` | **Frozen-curve** reproduce / summary style |
| `ce_bell_v11_stress_test.py` | **Stress test** (defect grids, noise kicks, etc.) |

Typical ingredients: two or more paths, **binary tags / polarization proxies**, scans over **A, S, B, LAMBDA**. **Different scripts may define “events” and denominators differently** — align definitions before comparing two runs.

### One-run snapshot (`ce_bell.py`: Malus curve vs cos²)

**`ce_bell.py`** runs **10 polarization angle gaps**, each for **STEPS=800** propagation, takes **coincidence ~ m1×m2** on fixed detector pixels, normalizes by the baseline at **angle2=0**, and compares pointwise to **cos²θ** (definition per script). Figure: **`scripts/ce/bell_test_result.png`**.

| Item | Content |
| :--- | :--- |
| **Command** | From repo root with `PYTHONPATH` set: `python scripts/ce/ce_bell.py` |
| **Snapshot date** | **2026-05-05** (script defaults for HEIGHT/WIDTH, A/S/B, λ, **ANGLES**, etc.) |
| **Baseline coincidence (unnormalized)** | about **3.79×10⁻⁹** (at `angle2=0`, normalization denominator only) |
| **RMSE vs cos²** | about **4.5×10⁻¹⁸** (nearly exact in double precision) |
| **`np.allclose(..., atol=0.1)`** | **True** (script self-check; **only** curve agreement, **not** full Bell/CHSH certification — see log **“not a full Bell-test certification”**) |

**How to read this**: This layer is **“toy coincidence + Malus proxy”**; **CHSH values and NIST archives** start in **Chapters 8–10**. Do not sell this plot’s **cos² fit** as a lab **S** or a **no-locality** conclusion.

## 7.3 Frontiers and stress

**Frontiers**: `ce_bell_chsh_frontier.py`. **Stress**: `ce_bell_v11_stress_test.py` (defected grids, noise-like kicks). Goal: **whether the model stays coherent under pressure**, not a verdict on nature.

> **Chapter boundary**  
> Toy layer **≠** NIST audit layer; the former serves **intuition and sensitivity**, the latter **yardsticks on public records** (Chapters 8–10). **Do not** relabel a `ce_bell` number as “the lab has falsified / confirmed …”

You now have an **internal bridge from double-slit visibility to CHSH-shaped curves**. Next chapter leaves pure toys and opens **NIST complete-blind-style public archives**: **denominators, coincidence windows, index semantics** take the lead.
