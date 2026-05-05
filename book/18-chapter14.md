# 第十四章 · Chapter 14

**其他基线与探索**  
*Other baselines and exploration*

> **本章任务**  
> 说明仓库中**未编入前述主线、仍值得知道**的探索：`verify_*`、`discover_*`、部分 `explore_critique_*`——**Born 规则抽查**、**不确定性扫描**、**退相干 toy**、**相对论格子批评**等。

## 14.1　为什么需要「杂物抽屉」章

若只读 `ce_*` 与 NIST，会误以为全书**只有双缝与 Bell**。实际上，仓库长期用**小脚本**回答：**某条经典结论在格点上是否稳定复现**、**哪一步推广会踩雷**。本章**不逐文件讲**，只给**地图**。

## 14.2　`scripts/verify/`（一次性基线）

下列路径均为 **`scripts/verify/`**：

| 文件 | 大致用途 |
| :--- | :--- |
| `verify_born_rule.py` | **Born 规则**式概率在格点设定下是否自洽 |
| `verify_delayed_choice.py` | **延迟选择**相关基线（与 `ce_06` 叙事互证） |
| `verify_interference_decay.py` | **干涉衰减**行为 |
| `verify_uncertainty.py` | **不确定性**关系 toy |
| `verify_which_way.py` | **which-way** 类对照 |

### 可复跑快照：`verify_born_rule.py`

连续场屏分布 vs 蒙特卡洛光子累计（**`ce_engine_v2`**）。默认 **N_PHOTONS=50000**、**seed=42**；运行约 **数十秒** 量级（视 CPU）。**图**已固定写入 **`scripts/verify/verify_born_rule.png`**（与脚本同目录，不依赖 cwd）。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | 在仓库根：`PYTHONPATH` 指向仓库根后执行 `python scripts/verify/verify_born_rule.py` |
| **快照日期** | **2026-05-05**（默认常量，未改 `N_PHOTONS`） |

| `observed` 键 | 值（快照） |
| :--- | :--- |
| `pearson_r_continuous_vs_mc` | ≈ **0.9441** |
| `visibility_continuous` | ≈ **0.6859** |
| `visibility_mc` | ≈ **0.1646** |
| `hit_rate` | ≈ **0.0421**（击中屏光子占比） |

**读法**：**皮尔逊 r** 衡量两列**形状对齐**，与 **`ce_05`** 里那种单列 **V** 不是同一对象；MC 的 **V** 低而 **r** 仍可高，因计数噪声与归一化方式不同。**档案假设**里已写明：**r 高不代表在测度论意义上证明了 Born**——本书把该脚本当作 **「同一引擎下两场叙事是否同形」** 的基线，不把脚本末尾的修辞句当判决书。

### 可复跑快照：`verify_delayed_choice.py`

**`ce_engine_v2`** 上先长跑再对场做**行域裁剪/放大**（模拟「过缝后再选路径」），与 **`ce_06`**「第几步插入圆吸收器」是**同一类**——**因果顺序写进循环**，但**实现细节不同**。图写入 **`scripts/verify/verify_delayed_choice.png`**。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | 在仓库根：`PYTHONPATH` 指向仓库根后执行 `python scripts/verify/verify_delayed_choice.py` |
| **快照日期** | **2026-05-05**（默认常量） |

| `observed` 键 | 值（快照） |
| :--- | :--- |
| `vis_no_measurement` | ≈ **0.5613** |
| `vis_delayed_slit_mask` | **0.0** |
| `verdict_strict_qm_style` | **true**（脚本内置：`V_无测量>0.3` 且 `V_延迟掩模<0.15`） |
| `verdict_trend_only` | **false** |

**读法**：这里的「延迟测量」是**网格上的显式掩模代数**，不是实验室光子学；**V=0** 来自 **`compute_visibility`** 在裁剪后**找不到有效峰谷**。与 **`ce_06`** 对照阅读：圆斑吸收 vs 行带清零，何者在几何上更「钝」、何者更「狠」，可以用**同一屏列定义**做表。勿把脚本里的口号式 stdout 当全书结论——**档案 `reviewer_prompts`** 已邀请「经典场论类比是否完全等价」类质疑。

## 14.3　`scripts/discover/`（现象扫描）

下列路径均为 **`scripts/discover/`**：

| 文件 | 大致用途 |
| :--- | :--- |
| `discover_visibility_decay.py` | **可见度**随参数衰减 |
| `discover_coupling_constant.py` | **耦合常数**敏感区 |
| `discover_measurement_continuity.py` | **测量/连续**参数扫描 |

## 14.4　`explore_critique_*`（内部批评）

均在 **`scripts/explore/`**：

| 文件 | 主题（见脚本内标题） |
| :--- | :--- |
| `explore_critique_01_unification_scope.py` | 统一范围 |
| `explore_critique_02_bell_hypothesis_boundary.py` | Bell 假设边界 |
| `explore_critique_03_analogy_vs_mechanism.py` | 类比 vs 机制 |
| `explore_critique_04_sr_not_derived_from_lattice.py` | 相对论未从格子导出 |
| `explore_critique_05_decay_nonuniqueness.py` | 衰减非唯一 |
| `explore_critique_06_energy_growth_explosion.py` | 能量增长 |
| `explore_critique_07_fringe_spacing_theory_gap.py` | 条纹间距理论缝 |

与序言 **「非法典」**一致：**类比可以养直觉，机制要另过门**。

### 可复跑示例：`explore_critique_03`（措辞门禁，无数值物理）

**`scripts/explore/explore_critique_03_analogy_vs_mechanism.py`** 不跑格子，只打印三条**对外表述建议**并生成示意图，stdout 带 **`[OK] critique_03_analogy_language`**。适合当作「写论文/写书前过一遍」的自动化便签。

| 项目 | 内容 |
| :--- | :--- |
| **命令** | `python scripts/explore/explore_critique_03_analogy_vs_mechanism.py` |
| **产出图** | **`scripts/explore/explore_critique_03_analogy_vs_mechanism.png`** |
| **`observed` 标记** | `marker`: `[OK] critique_03_analogy_language`（**2026-05-05** 跑通快照） |

## 14.5　如何自己索引

涟漪子树以 **`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`** 为纲；其余以 **`scripts/explore/`** 目录 + 文件名为纲。**命名即意图**：`explore_` 多扫描，`verify_` 多一次性检验，`discover_` 多现象发现。

> **本章边界**  
> 「探索」**不**都是成稿结论；部分脚本保留**失败输出**。引用前请**跑一遍**或读 artifact 注释。

仓库的**可复现性**不仅来自主线，也来自这些**小基线**与**自我批评脚本**。下一章为**规划占位**：**Bell 类公开数据上 Alice/Bob 球面坐标联合拟合**（**文稿先行，代码待补**）；再下一章才是**诚实列出没通过的测量**。

**路标**：**栅格 + NIST + CHSH 审计**的主线在中腹已大体铺完；**第12–13章的涟漪量子 toy**是**并行探索**，曲线再漂亮也要先问门禁与失败记录。若你**只要公开数据与读数规则的诚实记录**，可侧重**第8–10章与第16章**；**第17–18章**为**设想与动力系统草图**，读来完全可选。

---

# Chapter 14 · Other baselines and exploration

**其他基线与探索**  
*Other baselines and exploration*

> **This chapter’s job**  
> Map explorations **not wired into the main line but still worth knowing**: `verify_*`, `discover_*`, selected `explore_critique_*` — **Born spot checks**, **uncertainty scans**, **decoherence toys**, **relativistic-lattice critique**, etc.

## 14.1 Why a “junk drawer” chapter

Reading only `ce_*` and NIST can imply the repo is **only double slit and Bell**. In practice, **small scripts** ask whether **classic conclusions reproduce stably on the grid** and **which generalization blows up**. This chapter **does not walk file-by-file**; it gives a **map**.

## 14.2 `scripts/verify/` (one-shot baselines)

All paths **`scripts/verify/`**:

| File | Rough role |
| :--- | :--- |
| `verify_born_rule.py` | Whether **Born-style** probabilities stay coherent on this lattice setup |
| `verify_delayed_choice.py` | Delayed-choice baseline (cross-read `ce_06`) |
| `verify_interference_decay.py` | **Interference decay** behavior |
| `verify_uncertainty.py` | **Uncertainty** relation toy |
| `verify_which_way.py` | **Which-way**-style controls |

### Rerunnable snapshot: `verify_born_rule.py`

Continuous field screen distribution vs Monte Carlo photon accumulation (**`ce_engine_v2`**). Defaults **N_PHOTONS=50000**, **seed=42**; run time **tens of seconds** (CPU dependent). Figure pinned to **`scripts/verify/verify_born_rule.png`** (same directory as script, cwd-independent).

| Item | Content |
| :--- | :--- |
| **Command** | From repo root with `PYTHONPATH`: `python scripts/verify/verify_born_rule.py` |
| **Snapshot date** | **2026-05-05** (default constants, `N_PHOTONS` unchanged) |

| `observed` key | Value (snapshot) |
| :--- | :--- |
| `pearson_r_continuous_vs_mc` | ≈ **0.9441** |
| `visibility_continuous` | ≈ **0.6859** |
| `visibility_mc` | ≈ **0.1646** |
| `hit_rate` | ≈ **0.0421** (fraction of photons hitting screen) |

**How to read**: **Pearson r** measures **shape alignment between two columns** — not the same object as single-column **V** in **`ce_05`**; MC **V** can be low while **r** stays high because of counting noise and normalization. Assumptions in the dossier state clearly: **high r is not a measure-theoretic proof of Born** — the script is a baseline for **“do two narratives on the same engine share shape?”**; do not treat closing rhetoric in stdout as a verdict.

### Rerunnable snapshot: `verify_delayed_choice.py`

On **`ce_engine_v2`**, long run then **row-domain crop / zoom** on the field (“choose path after the slits”), same **family** as **`ce_06`**’s “which step inserts the round absorber” — **causal order in the loop**, **different implementation**. Figure: **`scripts/verify/verify_delayed_choice.png`**.

| Item | Content |
| :--- | :--- |
| **Command** | From repo root with `PYTHONPATH`: `python scripts/verify/verify_delayed_choice.py` |
| **Snapshot date** | **2026-05-05** (defaults) |

| `observed` key | Value (snapshot) |
| :--- | :--- |
| `vis_no_measurement` | ≈ **0.5613** |
| `vis_delayed_slit_mask` | **0.0** |
| `verdict_strict_qm_style` | **true** (built-in: `V_no_meas > 0.3` and `V_delayed_mask < 0.15`) |
| `verdict_trend_only` | **false** |

**How to read**: “Delayed measurement” here is **explicit mask algebra on the grid**, not lab photonics; **V = 0** because **`compute_visibility`** finds **no usable peaks/troughs** after cropping. Cross-read **`ce_06`**: round absorber vs row zeroing — which geometry is “blunter” vs “harsher” — tabulate under **the same screen-column definition**. Do not treat slogan stdout as the book’s conclusion — dossier **`reviewer_prompts`** already invites “is the classical-field analogy fully equivalent?” style doubt.

## 14.3 `scripts/discover/` (phenomenon scans)

All **`scripts/discover/`**:

| File | Rough role |
| :--- | :--- |
| `discover_visibility_decay.py` | **Visibility** vs parameter decay |
| `discover_coupling_constant.py` | **Coupling** sensitive regions |
| `discover_measurement_continuity.py` | **Measurement / continuity** scans |

## 14.4 `explore_critique_*` (internal critique)

All **`scripts/explore/`**:

| File | Theme (see in-file title) |
| :--- | :--- |
| `explore_critique_01_unification_scope.py` | Unification scope |
| `explore_critique_02_bell_hypothesis_boundary.py` | Bell hypothesis boundary |
| `explore_critique_03_analogy_vs_mechanism.py` | Analogy vs mechanism |
| `explore_critique_04_sr_not_derived_from_lattice.py` | SR not derived from lattice |
| `explore_critique_05_decay_nonuniqueness.py` | Decay non-uniqueness |
| `explore_critique_06_energy_growth_explosion.py` | Energy growth |
| `explore_critique_07_fringe_spacing_theory_gap.py` | Fringe-spacing theory gap |

Matches preface **“not a codex”**: **analogies may train intuition; mechanisms must pass their own gates.**

### Rerunnable example: `explore_critique_03` (language gate, no numerical physics)

**`scripts/explore/explore_critique_03_analogy_vs_mechanism.py`** does not run the lattice; it prints three **outward phrasing suggestions** and emits a schematic; stdout carries **`[OK] critique_03_analogy_language`**. Handy automated sticky note **before drafting a paper or chapter**.

| Item | Content |
| :--- | :--- |
| **Command** | `python scripts/explore/explore_critique_03_analogy_vs_mechanism.py` |
| **Figure** | **`scripts/explore/explore_critique_03_analogy_vs_mechanism.png`** |
| **`observed` marker** | `marker`: `[OK] critique_03_analogy_language` (**2026-05-05** run) |

## 14.5 How to index yourself

Ripple subtree: **`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`**; otherwise **`scripts/explore/`** by directory + filename. **Names signal intent**: `explore_` scans, `verify_` one-off checks, `discover_` phenomenon sweeps.

> **Chapter boundary**  
> “Exploration” is **not** always a finished conclusion; some scripts keep **failure outputs**. **Rerun** or read artifact notes before citing.

Reproducibility here comes from the **main line** and from these **small baselines** plus **self-critique scripts**. Next is a **planning placeholder**: **joint Alice/Bob sphere fit on Bell-type public data** (**manuscript first, code TBD**); after that comes the **honest list of measurements that did not pass**.

**Layer cue**: The **grid + NIST + CHSH audit spine** is largely set by mid-book; **Chapters 12–13 ripple-quantum toys** are **parallel exploration** — ask which gates a curve passed before admiring it. If you mainly want **public-data / readout honesty**, lean on **Chapters 8–10 and 16**; **Chapters 17–18** are **optional sketches** of ideas and dynamics.
