# 全书统一写作方案（第二单元起）

本文档约束 **第4章至后记** 的体例，避免各章口吻、边界与主线相互割裂。修订全书时**先改本方案**，再改各章。

---

## 1. 叙事主轴（读者应能复述）

1. **直觉**：泡泡 = 局域传递的图像（第一单元）。  
2. **地面**：格子上有 **λ / 吸收 / 涩格**（第3章）。  
3. **工具**：`ce_*` 把测量落成**可调规则**（第4–7章）。  
4. **公开记录**：NIST 等与 **尺子、分母、符合窗**（第8–10章）。  
5. **多体线**：GHZ **档案** vs **in-silico 审计**（第11章 + `07-archive-ghz.md`）。  
6. **并行探索**：涟漪量子玩具与专项审计（第12–13章）。  
7. **诚实**：失败与开放问题入册（第16章、后记）；第15章为 **Bell 拟合规划占位**。

每一章正文**至少一处**显式扣回以上之一（不必全扣）。

---

## 2. 章内固定结构

| 块 | 要求 |
| :--- | :--- |
| **标题** | `# 第N章 · Chapter N` → `**中文副题**` → `*English*` |
| **章首** | **不再**使用大块 **`【给普通读者 · 这幅图在说什么】`**；术语在**正文**里就地一句带过；序言已写的边界**章内不复读**。 |
| **章首提示**（可选） | `> **本章任务**` 一句：本章把读者带到链上哪一环。 |
| **承接** | 第一节或首段：**从上章落地**（不重复序言四条）。 |
| **小节** | `## N.1` … 用中文全角顿号式编号，与前三章一致。 |
| **边界** | 每章至少一个 `> **本章边界**`（或等价的**一句正文边界**）：数据/模型/结论各属什么。**避免**单独「挑剔的读者」大引用框打断流。 |
| **收束** | **不单立「小结」节**；必要时在末段用**一两句**承上启下 + **下一章钩子**；分层路标仅见 **第2 / 5 / 14 章**末（见 `REVISION_PLAN_NARRATIVE_LAYERING.md`）。 |

---

## 3. 用语与禁忌

- **模型内**（in-silico、栅格跑出来的）与 **对公开记录的审计**（CSV、协议）**分开写**；句子里出现结论时标明属哪一类。  
- ** headline 数字**（CHSH、S、可见度）一律写清：**以该章或脚本锁定的定义为准**。  
- 不用「推翻量子力学」类对抗修辞；用「排除哪一类图像」「协议敏感」等序言已接纳的措辞。  
- 脚本路径：**首次出现写全路径**，后文可只写 `ce_04` 等。  
- 英文专名：Bell、CHSH、GHZ、NIST 保留；首次可括注极简中文。

---

## 4. 交叉引用约定

- 三种口语与离散核：**`01-appendix-three-phrasings.md`**  
- Bell/GHZ **背景档案**：**`06-archive-bell.md`**、**`07-archive-ghz.md`**  
- 损耗地面：**第3章**（`05-chapter.md` 或与目录一致的文件名）  
- 全书目录：**`02-contents.md`**

---

## 5. 文件命名（与目录同步）

| 章 | 文件 |
| :--- | :--- |
| 4–14 | `08-chapter04.md` … `18-chapter14.md` |
| 15 | `19-chapter15.md`（规划稿：Bell 公开数据 · Alice/Bob 球面拟合） |
| 16 | `20-chapter16.md`（没通过的测量） |
| 17–18 | `21-chapter17.md` `22-chapter18.md`（第三部分设想） |
| 后记 | `23-afterword.md` |

第1–3章当前路径（与目录同步）：`book/04-chapter.md`、`book/03-chapter.md`、`book/05-chapter.md`。

---

## 6. 修订日志

- 2026-05-05：初版，用于批量生成第4章至后记。  
- 2026-05-05（续）：第4–7章补全 **`ce_*` 精确文件名**；第8–11章补 **`nist_*` / `explore_chsh_*` / `ghz_medium_v10`** 索引表，便于与仓库 diff 而不改全书口吻。  
- 2026-05-05（再续）：第12章对齐 **`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`** 与 v1–v8 主脚本表；第13章补 **涟漪专项审计**脚本表；第14章补 **`verify_*` / `discover_*` / `explore_critique_*`** 全表；（章号已顺延）第16章补 **失败复查**脚本线索。  
- 2026-05-05（三续）：（章号已顺延）第17章挂钩 **`docs/RESEARCH_MAP.md`**、**`计算机探索/README_探索路线.md`**；第18章挂钩 **`unsolved_problems_collision/ROADMAP_7_PROBLEMS.md`** 题1与 **`explore_critique_04`**；后记补 **仓库级导航链接**。  
- 2026-05-05（四续）：英文序言补 **卷前导航**（与中文「文稿导航」对称）；第4章 **`ce_00` 默认参一次运行快照**（`fringe_verdict=weak` 等，可复跑）。  
- 2026-05-05（五续）：第12章补 **`ripple_quantum_tests.py`（v1）** 四条曲线 NRMSE 快照与产出路径（与索引 §6 的 v5/v6 命令区分）。  
- 2026-05-05（六续）：第6章 **`ce_06`** 默认参一次快照（`visibility_final`、图落盘说明）。  
- 2026-05-05（七续）：**`ce_06_delayed_choice_absorber.py`** 作图改为写入 **`scripts/ce/delayed_choice.png`**（与 `ce_00` 一致）；第6章表格同步。  
- 2026-05-05（八续）：**`ce_04`** 作图改为 **`scripts/ce/measurement_effect.png`**；第5章 **`ce_04` 三联 V 快照** + 启发式 V 误读提醒；第14章补 **`explore_critique_03`** 可复跑示例。  
- 2026-05-05（九续）：**`ce_05`** 作图改为 **`scripts/ce/finite_absorber.png`**；第5章 **`ce_05` 默认参快照**（`visibility_final=0` 与对照实验说明）。  
- 2026-05-05（十续）：**`verify_born_rule.py`** 作图改为 **`scripts/verify/verify_born_rule.png`**；第14章 **`verify_born` 表格式快照**（r、双 V、命中率）与 **Born 边界**提醒。  
- 2026-05-05（十一续）：**`verify_delayed_choice.py`** 作图改为 **`scripts/verify/verify_delayed_choice.png`**；第14章 **`verify_delayed` 快照**（双 V、strict 判据）及与 **`ce_06`** 的对照读法。  
- 2026-05-05（十二续）：**`ce_bell.py`** 作图改为 **`scripts/ce/bell_test_result.png`**；第7章 **`ce_bell` 马吕斯/cos² 快照**（基线、RMSE、脚本自检说明）。  
- 2026-05-05（十三续）：全书相关稿 **`【给普通读者 · 这幅图在说什么】`** 块：第1–3章、第4–17章、档案、附录一、后记、序言导航；体例写入本章 §2 表格。  
- 2026-05-05（十四续）：**新增第15章（规划稿）** Bell 类公开数据 **Alice/Bob 庞加莱球联合拟合**；原第15–17章顺延为 **第16–18章**；后记改为 **`23-afterword.md`**；目录与 §5 文件表同步。
- 2026-05-05（十五续 / narrative-layering）：**取消**章首 **`【给普通读者】`** 大块；**小结**改为末段收束；序言/目录/本方案同步；**第2/5/14章末**加**分层路标**；详见 **`book/REVISION_PLAN_NARRATIVE_LAYERING.md`**。

---

# Unified writing scheme for the whole book (from Part II onward)

This document governs **Chapters 4 through the afterword** so tone, boundaries, and the through-line do not splinter. When revising the manuscript, **edit this scheme first**, then the chapters.

---

## 1. Narrative spine (readers should be able to retell it)

1. **Intuition**: bubble = the picture of **local transfer** (Part I).  
2. **Ground**: on the lattice — **λ / absorption / “sticky” sites** (Chapter 3).  
3. **Tools**: `ce_*` turns measurement into **tunable rules** (Chapters 4–7).  
4. **Public records**: NIST-style tables and **yardsticks, denominators, coincidence windows** (Chapters 8–10).  
5. **Many-body thread**: GHZ **archive** vs **in-silico audit** (Chapter 11 + `07-archive-ghz.md`).  
6. **Parallel exploration**: ripple-quantum toys and focused audits (Chapters 12–13).  
7. **Honesty**: failures and open questions go on the record (Chapter 16, afterword); Chapter 15 is a **Bell fitting roadmap placeholder**.

Each chapter should **explicitly hook back** to at least one of the above (not necessarily all).

---

## 2. Fixed in-chapter structure

| Block | Requirement |
| :--- | :--- |
| **Title** | `# Chapter N · Chapter N` → `**Chinese subtitle**` → `*English*` |
| **Chapter opening** | **No** large **`【给普通读者 · 这幅图在说什么】`** blocks; gloss jargon **in the body**; do not repeat preface boundaries in every chapter. |
| **Chapter opener (optional)** | `> **本章任务**` one line: which link in the chain this chapter advances. |
| **Bridge** | First section or first paragraph: **land from the prior chapter** (do not repeat the preface’s four bullets). |
| **Subsections** | `## N.1` … use the same Chinese full-width enumeration style as the first three chapters. |
| **Boundaries** | At least one `> **本章边界**` (or an equivalent **one-sentence in-text boundary**): what belongs to data vs model vs conclusion. Avoid large “skeptical reader” pull-quotes. |
| **Close** | **No standalone “小结” section**; if needed, **one or two sentences** at the end of the last substantive section + **hook**; layer cues only at ends of **Chapters 2 / 5 / 14** (see `REVISION_PLAN_NARRATIVE_LAYERING.md`). |

---

## 3. Wording and taboos

- Keep **in-model** (in-silico, grid output) **separate** from **public-record audit** (CSV, protocol); when a sentence states a conclusion, say which bucket it belongs to.  
- **Headline numbers** (CHSH, S, visibility) must always cite **the definition locked in that chapter or script**.  
- Avoid combative rhetoric like “overthrow quantum mechanics”; prefer preface-safe wording such as **which pictures are ruled out** and **protocol sensitivity**.  
- Script paths: **full path on first mention**, then shorthand like `ce_04` later.  
- English proper nouns: Bell, CHSH, GHZ, NIST stay as-is; optional minimal Chinese gloss on first use.

---

## 4. Cross-reference conventions

- Three colloquial phrasings and the discrete kernel: **`01-appendix-three-phrasings.md`**  
- Bell/GHZ **background archives**: **`06-archive-bell.md`**, **`07-archive-ghz.md`**  
- Lossy ground: **Chapter 3** (`05-chapter.md` or the filename aligned with the TOC)  
- Full TOC: **`02-contents.md`**

---

## 5. File naming (synced with the TOC)

| Chapter | File |
| :--- | :--- |
| 4–14 | `08-chapter04.md` … `18-chapter14.md` |
| 15 | `19-chapter15.md` (planning draft: Bell public data · Alice/Bob spherical fit) |
| 16 | `20-chapter16.md` (measurements that did not pass) |
| 17–18 | `21-chapter17.md` `22-chapter18.md` (Part III sketches) |
| Afterword | `23-afterword.md` |

Chapters 1–3 paths (TOC-aligned): `book/04-chapter.md`, `book/03-chapter.md`, `book/05-chapter.md`.

---

## 6. Revision log

- 2026-05-05: First version, used to batch-generate Chapter 4 through the afterword.  
- 2026-05-05 (cont.): Chapters 4–7 filled in exact **`ce_*` filenames**; Chapters 8–11 added **`nist_*` / `explore_chsh_*` / `ghz_medium_v10` index tables** for repo diffs without changing voice.  
- 2026-05-05 (again): Chapter 12 aligned to **`docs/RIPPLE_QUANTUM_TESTS_INDEX.md`** and the v1–v8 main script table; Chapter 13 added the **ripple-focused audit** script table; Chapter 14 added the full **`verify_*` / `discover_*` / `explore_critique_*` table**; (renumbered) Chapter 16 added **failure-review** script leads.  
- 2026-05-05 (third): (renumbered) Chapter 17 links **`docs/RESEARCH_MAP.md`**, **`计算机探索/README_探索路线.md`**; Chapter 18 links **`unsolved_problems_collision/ROADMAP_7_PROBLEMS.md`** problem 1 and **`explore_critique_04`**; afterword adds **repo-level nav links**.  
- 2026-05-05 (fourth): English preface adds **front-matter navigation** (mirrors Chinese “文稿导航”); Chapter 4 adds a **one-run `ce_00` default snapshot** (`fringe_verdict=weak`, etc., rerunnable).  
- 2026-05-05 (fifth): Chapter 12 adds **`ripple_quantum_tests.py` (v1)** four-curve NRMSE snapshot and output paths (distinct from index §6 v5/v6 commands).  
- 2026-05-05 (sixth): Chapter 6 **`ce_06`** default snapshot (`visibility_final`, figure path note).  
- 2026-05-05 (seventh): **`ce_06_delayed_choice_absorber.py`** writes figures to **`scripts/ce/delayed_choice.png`** (like `ce_00`); Chapter 6 table synced.  
- 2026-05-05 (eighth): **`ce_04`** writes **`scripts/ce/measurement_effect.png`**; Chapter 5 **`ce_04` triptych V snapshot** + heuristic V misread warning; Chapter 14 adds **`explore_critique_03`** rerunnable example.  
- 2026-05-05 (ninth): **`ce_05`** writes **`scripts/ce/finite_absorber.png`**; Chapter 5 **`ce_05` default snapshot** (`visibility_final=0` and control-run note).  
- 2026-05-05 (tenth): **`verify_born_rule.py`** writes **`scripts/verify/verify_born_rule.png`**; Chapter 14 **`verify_born` table snapshot** (r, dual V, hit rate) and **Born boundary** reminder.  
- 2026-05-05 (eleventh): **`verify_delayed_choice.py`** writes **`scripts/verify/verify_delayed_choice.png`**; Chapter 14 **`verify_delayed` snapshot** (dual V, strict criterion) and readout contrast with **`ce_06`**.  
- 2026-05-05 (twelfth): **`ce_bell.py`** writes **`scripts/ce/bell_test_result.png`**; Chapter 7 **`ce_bell` Malus / cos² snapshot** (baseline, RMSE, script self-check note).  
- 2026-05-05 (thirteenth): Manuscript-wide **`【给普通读者 · 这幅图在说什么】`** blocks: Chapters 1–3, 4–17, archives, Appendix I, afterword, preface nav; style written into §2 table here.  
- 2026-05-05 (fourteenth): **New Chapter 15 (planning)** Bell-type public data **joint Alice/Bob Poincaré-sphere fit**; former Chapters 15–17 become **16–18**; afterword file **`23-afterword.md`**; TOC and §5 file table synced.
- 2026-05-05 (fifteenth / narrative-layering): **Removed** large chapter-opening reader blocks; **小结** folded into closing paragraphs; **layer cues** at ends of **Chapters 2, 5, 14**; see **`book/REVISION_PLAN_NARRATIVE_LAYERING.md`**.
