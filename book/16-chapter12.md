# 第十二章 · Chapter 12

**涟漪量子四项玩具基准 v1–v8**  
*Ripple quantum four benchmarks v1–v8*

> **【给普通读者 · 这幅图在说什么】**
>
> - **人话词解**：想象有四条**行业曲线**——激光阈值、半导体吸收边、MRI 频率随磁场、原子钟谱线——本书用**可调介质玩具**去**贴**它们的**形状**（像描红）。
> - **这章解决什么**：**不是**宣称发明新器件；是问：这套**参数化涟漪**能不能在**无量纲旋钮**下**长得像**教科书里的参考曲线？
> - **教科书常识**：阈值、吸收边、拉莫尔进动、洛伦兹/高斯线型等，各有**经典/量子**两套讲法；这里参考曲线是**手写 QM-like**，**不是**偷换真实实验 CSV。
> - **本书在干什么**：`ripple_quantum_tests` 系列（**不必运行**）提供**版本演进**与**门禁**；通过后仍只是**形状游戏**。
> - **和物理学家们**：**不违背**已知的「曲线长什么样」常识；**不宣称**已替代第一性原理推导。

> **本章任务**  
> 介绍 `scripts/explore/ripple_quantum_tests/`：**四条一维曲线**上，用**无量纲介质旋钮**去贴 **QM-like 参考形状**；版本 **v1–v8** 各解决什么问题（门禁、色散、合并页等）。

## 12.1　为什么与 `ce_*` 并行

`ce_*` 是**二维格 + 双缝/Bell** 主战场；涟漪量子线是**另一套**参数化介质 toy，服务**四条独立「行业曲线」**直觉：阈值、截止、拉莫尔线性、谱线形。它**不**替代 NIST 事件表，也**不**声称 SI 已全局标定。

## 12.2　四条曲线分别是什么

- **激光**：阈值附近功率–泵浦形状。  
- **半导体**：吸收边附近特征。  
- **MRI**：拉莫尔关系与代数 **κ**（版本靠后引入）。  
- **原子钟**：谱线与腔长代数（版本演进见索引）。

## 12.3　版本演进（v1→v8）与权威索引

**唯一导航入口（仓库内）**：**`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`**（中英并列、含一键命令与 `artifacts/` 目录说明）。中文任务细节：**`scripts/explore/ripple_quantum_tests/README.zh.md`**。

**主脚本树（与索引 §2 一致，快照）**：

| 版本 | 脚本（均在 `scripts/explore/ripple_quantum_tests/`） | 要点 |
| :--- | :--- | :--- |
| v1 | `ripple_quantum_tests.py` | NRMSE 阈值；默认 `artifacts/ripple_quantum_tests/` |
| v2 | `ripple_quantum_tests_v2.py` | `shape_pass` ∧ `constant_pass` |
| v3 | `ripple_quantum_tests_v3.py` | `derived` / `calibrated`；反作弊门 |
| v4 | `ripple_quantum_tests_v4_plot_optimize.py` | 作图 + 差分进化；`artifacts/ripple_quantum_tests_v4/` |
| v5 | `ripple_quantum_tests_v5_rigorous.py` | `nrmse_x` / `nrmse_y` / `R²`；MRI κ；原子钟代数约束 |
| v6 | `ripple_quantum_tests_v6_joint.py` | 联合 \((\mu,\rho,\eta,bw)\)；`--stress`；可选 **derived** 相速 + **`ripple_medium_dispersion.py`** |
| v8 合并 | `ripple_quantum_tests_v8_unify.py` | **v8 unify** 主线（与 v7 图包脚本配套见下章） |

### 一次运行快照（v1：闭式曲线，非优化）

**v1** 不做数值搜索，只在四条轴上比较 **QM-like 参考曲线** 与脚本内写定的 **Ripple 曲线** 的 **NRMSE**（定义见 `ripple_quantum_tests.py`）。下面是一次在仓库根目录、**默认阈值**下的可复跑记录（**2026-05-05**；`--seed 42` 对当前闭式实现几乎不改变数值，仅与输出元数据一致）。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | `python scripts/explore/ripple_quantum_tests/ripple_quantum_tests.py --threshold 0.18 --seed 42` |
| **门禁** | 各子任务 `nrmse ≤ 0.18` 记为通过 |
| **产出** | `artifacts/ripple_quantum_tests/RIPPLE_QUANTUM_TESTS_RESULTS.json`、`…_SUMMARY.md`、`…_PLOTS.png`（路径相对仓库根） |

| 逻辑名 | NRMSE（快照） | 是否通过 |
| :--- | ---: | :---: |
| `laser_threshold` | 0.009503 | 是 |
| `semiconductor_cutoff` | 0.018966 | 是 |
| `mri_larmor` | 0.004509 | 是 |
| `atomic_clock_modes` | 0.072342 | 是 |

读法：**v1 全过**只说明「当前参数化下四条玩具形状贴得近」；**不**推出 SI 标定或替代量子力学。需要 **差分进化、双 NRMSE、R²、MRI κ 代数、原子钟 L 约束** 时，改跑 **v5/v6**（一键命令见 **`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`** §6）。

**四条逻辑名**（索引 §1）：`laser_threshold`、`semiconductor_cutoff`、`mri_larmor`、`atomic_clock_modes`——对应**玩具参考曲线**，**不是**公开实验 CSV。

> **本章边界**  
> **μ, ρ, η** 等在本管线中多为**无量纲旋钮**；读者若把数值直接当物理常数用，需自备 **SI 映射**——本书此处**不装已解决**。

## 12.4　小结

你多了一幅**「介质 toy 能否像四条参考曲线那样弯」**的地图。下一章收束：**热三元组预注册审计**、**v6 可辨识性**、**v7/v8 合并页**与**参数阱库**——把「专项审计」写成**可读的统一报告**。

---

# Chapter 12 · Ripple quantum four benchmarks v1–v8

**涟漪量子四项玩具基准 v1–v8**  
*Ripple quantum four benchmarks v1–v8*

> **For general readers — what this picture is about**
>
> - **In plain words**: Picture four **industry-shaped curves** — laser threshold, semiconductor absorption edge, MRI frequency vs field, atomic-clock spectrum — and a **tunable medium toy** trying to **trace** their **shapes** (like tracing practice sheets).
> - **What this chapter does**: **Not** claiming new devices; asking whether this **parameterized ripple** can **look like** textbook reference curves under **dimensionless knobs**.
> - **Textbook baseline**: Thresholds, absorption edges, Larmor precession, Lorentzian / Gaussian line shapes all have **classical and quantum** tellings; here references are **hand-built QM-like curves**, **not** swapped-in real experiment CSVs.
> - **What the book is doing**: The `ripple_quantum_tests` series (**no need to run**) shows **version evolution** and **gates**; passing is still a **shape game**.
> - **For working physicists**: **No clash** with “curves look like this” common knowledge; **no** claim to replace first-principles derivations.

> **This chapter’s job**  
> Introduce `scripts/explore/ripple_quantum_tests/`: on **four 1D axes**, use **dimensionless medium knobs** to match **QM-like reference shapes**; what versions **v1–v8** each add (gates, dispersion, merge pages, etc.).

## 12.1 Why this runs parallel to `ce_*`

`ce_*` is the **2D lattice + double slit / Bell** main front; the ripple-quantum line is **another** parameterized medium toy serving **four separate “industry curve”** intuitions: threshold, cutoff, Larmor linearity, line shape. It **does not** replace NIST event tables or claim **full SI calibration**.

## 12.2 What the four curves are

- **Laser**: power–pump shape near threshold.  
- **Semiconductor**: features near the absorption edge.  
- **MRI**: Larmor relation and algebraic **κ** (introduced in later versions).  
- **Atomic clock**: spectrum and cavity-length algebra (see index for version notes).

## 12.3 Version ladder (v1→v8) and canonical index

**Single navigation entry (in-repo)**: **`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`** (bilingual, one-shot commands, `artifacts/` notes). Chinese task notes: **`scripts/explore/ripple_quantum_tests/README.zh.md`**.

**Main script tree (matches index §2, snapshot)**:

| Version | Script (all under `scripts/explore/ripple_quantum_tests/`) | Notes |
| :--- | :--- | :--- |
| v1 | `ripple_quantum_tests.py` | NRMSE threshold; default `artifacts/ripple_quantum_tests/` |
| v2 | `ripple_quantum_tests_v2.py` | `shape_pass` ∧ `constant_pass` |
| v3 | `ripple_quantum_tests_v3.py` | `derived` / `calibrated`; anti-cheat gates |
| v4 | `ripple_quantum_tests_v4_plot_optimize.py` | Plots + differential evolution; `artifacts/ripple_quantum_tests_v4/` |
| v5 | `ripple_quantum_tests_v5_rigorous.py` | `nrmse_x` / `nrmse_y` / `R²`; MRI κ; atomic-clock algebra |
| v6 | `ripple_quantum_tests_v6_joint.py` | Joint \((\mu,\rho,\eta,bw)\); `--stress`; optional **derived** phase velocity + **`ripple_medium_dispersion.py`** |
| v8 merge | `ripple_quantum_tests_v8_unify.py` | **v8 unify** mainline (pairs with v7 figure bundle scripts — next chapter) |

### One-run snapshot (v1: closed form, no optimization)

**v1** does no numerical search; it compares **NRMSE** between **QM-like reference curves** and script-defined **Ripple curves** on four axes (definition in `ripple_quantum_tests.py`). Rerunnable record from repo root, **default threshold**, **2026-05-05** (`--seed 42` aligns metadata; barely moves numbers for this closed-form build).

| Item | Content |
| :--- | :--- |
| **Command** | `python scripts/explore/ripple_quantum_tests/ripple_quantum_tests.py --threshold 0.18 --seed 42` |
| **Gate** | Each subtask passes if `nrmse ≤ 0.18` |
| **Outputs** | `artifacts/ripple_quantum_tests/RIPPLE_QUANTUM_TESTS_RESULTS.json`, `…_SUMMARY.md`, `…_PLOTS.png` (paths relative to repo root) |

| Logical name | NRMSE (snapshot) | Pass |
| :--- | ---: | :---: |
| `laser_threshold` | 0.009503 | yes |
| `semiconductor_cutoff` | 0.018966 | yes |
| `mri_larmor` | 0.004509 | yes |
| `atomic_clock_modes` | 0.072342 | yes |

**How to read**: **v1 all-pass** only means “under current parameterization the four toy shapes sit close”; it does **not** imply SI calibration or replacing quantum mechanics. For **differential evolution, dual NRMSE, R², MRI κ algebra, atomic-clock L constraints**, run **v5/v6** (commands in **`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`** §6).

**Four logical names** (index §1): `laser_threshold`, `semiconductor_cutoff`, `mri_larmor`, `atomic_clock_modes` — **toy reference curves**, **not** public experiment CSVs.

> **Chapter boundary**  
> **μ, ρ, η** here are mostly **dimensionless knobs**; treating them as physical constants needs your own **SI map** — the book **does not pretend** that mapping is solved here.

## 12.4 Close

You now have a map for **“can a medium toy bend like four reference curves?”** Next chapter tightens: **thermal-triplet preregistered audit**, **v6 identifiability**, **v7/v8 merge pages**, and the **parameter-trap library** — turning “focused audits” into a **readable unified report**.
