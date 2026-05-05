# 第十三章 · Chapter 13

**涟漪专项审计与统一报告**  
*Ripple-focused audits and unified report*

> **本章任务**  
> 把第十二章散落的**硬门禁**收成**叙事**：热波三元组盲测、全频透射、三体恒等式、可辨识性崩溃案例、合并 HTML 报告——**哪些是成果，哪些是反例库**。

## 13.1　热三元组与预注册

- **`scripts/explore/ripple_quantum_tests/ripple_thermal_triplet_preregistered_audit.py`**  
  **预注册门** + 盲测/反作弊叙事；与第三章 **PDE toy** 同态度：**规则先写死，再谈通过/失败**。

## 13.2　全频、三体恒等式与可辨识性

下列除单独注明外，均在 **`scripts/explore/ripple_quantum_tests/`**：

| 脚本 | 大致用途 |
| :--- | :--- |
| `ripple_triplet_fullband_transparency_audit.py` | **全频透射**审计 |
| `ripple_triplet_physics_identity_check.py` | **三体物理恒等式**核对 |
| `ripple_v6_identifiability_audit.py` | **v6 可辨识性**（平坦/多谷 → 明确失败标签） |
| `rho_mu_feasibility_map.py`、`rho_sensitivity_breakdown.py`、`verify_rho_mu2_constraint.py` | **ρ–μ 可行域**与灵敏度分解 |
| `v10_fail_anatomy.py` | **失败解剖**（为何不过门） |

**参数阱**：多脚本交叉扫出来的「好看但不稳」角落——本书视为**反例库**，不是污点。

## 13.3　v7/v8 图包与合并 HTML

- **`generate_v7_paper_figures.py`**、**`generate_v8_paper_figures.py`**：论文级图包导出。  
- **`build_merged_v7_v8_html.py`**：**v7 / v8 合并页**，多曲线一屏对照。  

读法：**先看图例与坐标定义**，再比**参考 vs 涟漪侧**与**范数定义**。

> **本章边界**  
> 「统一报告」是**仓库内**归档组织方式；**不**等于期刊论文已接收。引用图表请**连带脚本 commit 或 artifact hash**（若归档内有）。

涟漪线至此从**玩具**走到**有门禁的审计链**。下一章**兜底**：Born、不确定性、退相干等**其他 explore 基线**，并指向 **`explore_*` 索引**互见。

---

# Chapter 13 · Ripple-focused audits and unified report

**涟漪专项审计与统一报告**  
*Ripple-focused audits and unified report*

> **This chapter’s job**  
> Turn Chapter 12’s scattered **hard gates** into narrative: thermal-wave triplet blind test, full-band transmission, triplet physics identity, identifiability-failure cases, merged HTML reports — **what counts as a win vs a counterexample library**.

## 13.1 Thermal triplet and preregistration

- **`scripts/explore/ripple_quantum_tests/ripple_thermal_triplet_preregistered_audit.py`**  
  **Preregistered gates** + blind-test / anti-cheat narrative; same attitude as Chapter 3’s **PDE toy**: **freeze rules first, then talk pass/fail.**

## 13.2 Full band, triplet physics identity, identifiability

Unless noted, all under **`scripts/explore/ripple_quantum_tests/`**:

| Script | Rough role |
| :--- | :--- |
| `ripple_triplet_fullband_transparency_audit.py` | **Full-band transmission** audit |
| `ripple_triplet_physics_identity_check.py` | **Triplet physics identity** check |
| `ripple_v6_identifiability_audit.py` | **v6 identifiability** (flat / multi-valley → explicit failure labels) |
| `rho_mu_feasibility_map.py`, `rho_sensitivity_breakdown.py`, `verify_rho_mu2_constraint.py` | **ρ–μ feasible sets** and sensitivity breakdown |
| `v10_fail_anatomy.py` | **Failure anatomy** (why a gate failed) |

**Parameter traps**: corners that look good but are unstable under cross-scans — treated here as a **counterexample library**, not a stain.

## 13.3 v7/v8 figure bundles and merged HTML

- **`generate_v7_paper_figures.py`**, **`generate_v8_paper_figures.py`**: publication-style figure export.  
- **`build_merged_v7_v8_html.py`**: **merged v7/v8 page**, many curves on one screen.  

Reading order: **legend and axis definitions first**, then compare **reference vs ripple side** and **norm definitions**.

> **Chapter boundary**  
> “Unified report” is **in-repo** packaging; it is **not** “accepted at a journal.” Cite figures with **script commit or artifact hash** when available.

The ripple thread now moves from **toys** to a **gated audit chain**. Next chapter is the **catch-all**: Born, uncertainty, decoherence, and other **`explore_*` baselines**, with pointers to the **`explore_*` index**.
