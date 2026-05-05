# Chain Explosion Model

这是一个围绕离散、局域、可审计传播模型构建的研究型代码仓库。它不是量子力学教科书，也不是标准量子理论的直接替代证明；它更像一个把假设写进代码、把实验写进归档、把边界写进文档的研究工程。

This is a research-oriented code repository built around a discrete, local, and auditable propagation model. It is neither a quantum mechanics textbook nor a direct proof against standard quantum theory; it is better understood as a research program that encodes hypotheses into code, experiments into archives, and limits into documentation.

这个仓库真正的重点不是零散的双缝脚本，而是两次严肃的 CHSH / NIST 归档实验。其余 `ce_*`、`verify_*`、`discover_*`、`explore_*`、`critique_*` 脚本，主要承担基础建模、数值支撑和边界审计的作用。

The true center of this repository is not the scattered double-slit scripts, but two serious CHSH / NIST archival experiments. The other `ce_*`, `verify_*`, `discover_*`, `explore_*`, and `critique_*` scripts mainly serve as foundational modeling, numerical support, and boundary-audit layers.

## Contents

1. [Reading Guide](#reading-guide)
2. [Book manuscript · 叙事手稿《假大象与泡泡》](#book-manuscript)
3. [Quick Start Paths](#quick-start-paths)
4. [What This Repository Contains](#what-this-repository-contains)
5. [The Two Major Experiments](#the-two-major-experiments)
6. [Audit Findings Summary](#audit-findings-summary)
7. [Why The Project Has Value](#why-the-project-has-value)
8. [Recommended Reading Order](#recommended-reading-order)
9. [Contact](#contact)
10. [Quick Note](#quick-note)

## Reading Guide

如果你只想快速理解这个项目，建议先读这份入口文档，再读总文档 [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md)。后者按“像一本书”的方式组织内容，包含摘要、章节、原理、公式、实验、结果与解释边界。

If you want a fast understanding of the project, start with this entry document and then read the full monograph [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md). The monograph is organized like a book, with an abstract, chapters, principles, formulas, experiments, results, and interpretive limits.

如果你想先看作者对传播、测量和模型直觉的自我图景，再进入技术主线，可以阅读 [MODEL_INTUITION.md](docs/MODEL_INTUITION.md)。这个文件被刻意与结果文档分开，以避免把“直觉”和“结论”混写在一起。

If you want to see the author's intuitive picture of propagation and measurement before diving into the technical structure, read [MODEL_INTUITION.md](docs/MODEL_INTUITION.md). That file is intentionally separated from the result documents so that intuition and conclusion are not conflated.

## Book manuscript · 叙事手稿《假大象与泡泡》

<a id="book-manuscript"></a>

**这本书写什么（几句）**：《假大象与泡泡》是一份**第一人称**的研究手记——先用「球面泡泡」式的局域传播直觉搭一座**假大象**，再拿**同一批公开实验记录**追问：当**读数规则、二值化、分母与符合窗**等统计口径改变时，故事会不会跟着变（主线落在 **NIST / Bell–CHSH** 一类审计上）。它不是量子教科书，也**无意**宣称一夜推翻教科书；正文里把**模型内的格子模拟**与**磁盘上的协议审计**分开写，并如实记下**没过门禁的结果**与仍开放的模型设想，方便不同读者**分层阅读**、各取所需。

*What this book is (in short):* **The Fake Elephant and the Bubble** is a first-person research notebook — a “spherical bubble” picture as scaffolding, then pressing the **same public lab records** to ask whether the narrative moves when **yardsticks move** (binarization, denominators, coincidence windows), centered on **NIST / Bell–CHSH-style** audits. It is **not** a quantum textbook and does **not** claim to overturn mainstream physics overnight; **in-model grid runs** stay separate from **on-disk protocol audits**, with failed gates and speculative chapters labeled honestly so readers can **stop at different depths**.

仓库 **`book/`** 下有一份按章组织的**叙事手稿**（工作书名 **《假大象与泡泡》**，英文并列名见目录页）。它把「泡泡直觉 → 格子与损耗 → 公开数据与 Bell/GHZ 审计 → 构想章」串成可读主线，并与代码、归档路径交叉引用；**不等同**于专论里的全部技术细节。

- **目录与章节链接**：[book/02-contents.md](book/02-contents.md)  
- **序言与读法边界**：[book/00-preface.md](book/00-preface.md)  
- **封面稿（含扉页说明）**：[book/cover.md](book/cover.md)  
- **全书体例与交叉引用**：[book/00-unified-writing-scheme.md](book/00-unified-writing-scheme.md)

The **`book/`** folder holds a **chapter-style manuscript** (working Chinese title **《假大象与泡泡》**; English subtitle on the contents page). It threads bubble intuition, lattice/loss models, public-data and Bell/GHZ audits, and closing “concept” chapters, with pointers into scripts and archives. It is **not** a full substitute for the technical monograph.

- **Table of contents**：[book/02-contents.md](book/02-contents.md)  
- **Preface & reading boundaries**：[book/00-preface.md](book/00-preface.md)  
- **Cover / half-title notes**：[book/cover.md](book/cover.md)  
- **House style & cross-references**：[book/00-unified-writing-scheme.md](book/00-unified-writing-scheme.md)

**PDF 书稿（汇编）**：在仓库根目录执行 `.\activate_conda.ps1 base`（或已装 Pandoc 的 PATH）后运行 `.\scripts\build_book_pdf.ps1`；优先 `xelatex`，否则自动使用 conda **tectonic**；默认输出 **`book/_build/manuscript-zh.pdf`**（可用 `-OutPdf` 自定义路径）。*Build PDF*: `.\activate_conda.ps1 base` then `.\scripts\build_book_pdf.ps1` → `book/_build/manuscript-zh.pdf`.

**中英稿 PDF（当前推荐阅读的导出件）**：叙事手稿另有**中英合并**导出，路径 **[book/_build/假大象与泡泡-zh-en.pdf](book/_build/假大象与泡泡-zh-en.pdf)**。`book/_build/` 中的成品 PDF **已纳入本仓库版本控制**，克隆后即可使用；若本地重新执行 `.\scripts\build_book_pdf.ps1` 或覆盖导出件，请注意自行备份以免冲掉未提交的修改。*Bilingual manuscript PDF*: **[book/_build/假大象与泡泡-zh-en.pdf](book/_build/假大象与泡泡-zh-en.pdf)** — PDFs under `book/_build/` are **tracked in git**; re-running the build script may overwrite them locally.

## Quick Start Paths

如果你想从不同入口理解仓库，可以按下面的路径进入。

If you want different ways to enter the repository, use one of these paths.

- **Published audit pack (Zenodo, bilingual PDFs / 双语 PDF，当前引用):**
  - Bell / CHSH denominator audit: https://doi.org/10.5281/zenodo.19784937 — https://zenodo.org/records/19784937
  - GHZ `medium-v10` in-silico audit (V10.4): https://doi.org/10.5281/zenodo.19785022 — https://zenodo.org/records/19785022
  - Audit trilogy (Bell + GHZ V10.4): https://doi.org/10.5281/zenodo.19785083 — https://zenodo.org/records/19785083

- **已发布审计三部曲（Zenodo，当前引用）：**
  - 贝尔 / CHSH 分母审计：https://doi.org/10.5281/zenodo.19784937 — https://zenodo.org/records/19784937
  - GHZ `medium-v10` 仿真审计（V10.4）：https://doi.org/10.5281/zenodo.19785022 — https://zenodo.org/records/19785022
  - 审计综合篇（贝尔 + GHZ V10.4）：https://doi.org/10.5281/zenodo.19785083 — https://zenodo.org/records/19785083

- Brief note / 简要说明：
  - EN: These three papers form a reproducible audit trilogy focused on analysis-rule sensitivity, protocol transparency, and claim-boundary reporting for Bell/GHZ statistics.
  - 中文：这三篇论文构成一个可复现的审计三部曲，核心关注 Bell/GHZ 统计中的分析规则敏感性、协议透明度与结论边界报告。

- Fast overview: [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md)
- Author's model picture: [MODEL_INTUITION.md](docs/MODEL_INTUITION.md)
- Author's memory note: [AUTHOR_MEMORY_NOTE.md](docs/AUTHOR_MEMORY_NOTE.md)
- Bell / CHSH protocol layer: [BELL_PROTOCOL_NOTE.md](docs/BELL_PROTOCOL_NOTE.md)
- Paper strategy package: [PAPER_STRATEGY_PACKAGE.md](docs/PAPER_STRATEGY_PACKAGE.md)
- Research map: [RESEARCH_MAP.md](docs/RESEARCH_MAP.md)
- **Ripple quantum tests (four toy benchmarks, v1–v6):** [docs/RIPPLE_QUANTUM_TESTS_INDEX.md](docs/RIPPLE_QUANTUM_TESTS_INDEX.md) — laser / semiconductor / MRI / atomic-clock curve suite; scripts under `scripts/explore/ripple_quantum_tests/`
- Static site (navigator + treejs): [docs/site/index.html](docs/site/index.html)
  - Regenerate experiment pages: `python scripts/explore/generate_experiment_animation_pages.py`
- Archived battle results: [battle_results/README.md](battle_results/README.md)

## What This Repository Contains

这个仓库包含三类核心内容：第一类是离散传播模型本身，第二类是围绕双缝、测量、延迟选择和相关性的基础实验，第三类是面向 CHSH / NIST 问题的两轮严肃归档与解释收束。

This repository contains three core layers: first, the discrete propagation model itself; second, foundational experiments on double-slit behavior, measurement, delayed choice, and correlations; third, two rounds of serious archival work and interpretive closure around CHSH / NIST questions.

- `chain_explosion_numba.py` / 高性能传播内核  
  `chain_explosion_numba.py` / high-performance propagation kernels
- `ce_engine_v2.py`, `ce_engine_v3_coherent.py` / 更完整的实验引擎  
  `ce_engine_v2.py`, `ce_engine_v3_coherent.py` / fuller experimental engines
- `ce_00_*` 到 `ce_10_*` / 基础现象实验  
  `ce_00_*` to `ce_10_*` / foundational phenomenon experiments
- `verify_*`, `discover_*`, `explore_*` / 验证、发现与探索层  
  `verify_*`, `discover_*`, `explore_*` / verification, discovery, and exploration layers
- `battle_results/` / 两次严肃实验的归档区  
  `battle_results/` / archival zone for the two serious experiments

## The Two Major Experiments

第一次严肃实验位于 `battle_results/nist_completeblind_2015-09-19/`。它围绕公开 completeblind 数据建立了从 HDF5、事件 CSV、配对协议、CHSH 计算到 JSON 归档的完整链路，并明确记录了“工程通过、论点未通过”的结论。

The first major experiment is located at `battle_results/nist_completeblind_2015-09-19/`. It builds a full chain from HDF5 to event CSV, pairing protocols, CHSH computation, and JSON archiving over public completeblind data, and explicitly records the conclusion that the engineering path passed while the thesis gate failed.

第二次严肃实验位于 `battle_results/nist_round2_v2/`。它进一步处理了布局兼容性、映射敏感性、协议边界和解释收束问题，因此比第一轮更像一份正式研究归档。

The second major experiment is located at `battle_results/nist_round2_v2/`. It goes further by addressing layout compatibility, mapping sensitivity, protocol boundaries, and interpretive closure, making it closer to a formal research archive than the first round.

## Audit Findings Summary

在 2026 年的深度诚实审计中，我们对 Bell 和 GHZ 实验得出了以下关键结论：

1. **Bell 实验的“二值化陷阱”**：我们证明了 $S=2.828$ 是局域简谐波在**归一化互相关 (NCC)** 协议下的数学解析解，而经典的 $S \le 2$ 限制仅仅是强制二值化采样（Binarization）导致的信息损失产物。
2. **NIST 数据审计**：NIST 2015 数据的 $S$ 值对重合窗口（Window）和判定门禁（Gate）极度敏感。审计发现所谓的“通过”依赖于事后修改判定准则（HARKing）以及挑选特定的重合窗口。
3. **GHZ 终极解构**：我们成功复现了 $F=4.000000$ 的理想关联。通过**相位环路 (Phase-Loop)** 几何模型结合**连锁爆炸 (Chain-Explosion)** 阈值触发机制，我们证明了 GHZ 违背是局域波场干涉与非线性探测共同作用的必然结果，无需非局域纠缠。

In the 2026 Honest Audit, we reached the following key conclusions:

1. **The Binarization Trap in Bell Tests**: We proved that $S=2.828$ is the analytical solution for local harmonic waves under **Normalized Cross-Correlation (NCC)**, while the $S \le 2$ limit is an artifact of information loss due to forced Binarization.
2. **NIST Data Audit**: The $S$ values in NIST 2015 data are extremely sensitive to the coincidence window and gate criteria. The audit revealed that "success" relied on shifting gate criteria (HARKing) and specific window selection.
3. **GHZ Final Deconstruction**: We successfully replicated the ideal $F=4.000000$ correlation. Using a **Phase-Loop** geometric model combined with a **Chain-Explosion** threshold trigger, we demonstrated that the GHZ violation is an inevitable result of local wave-field interference and non-linear detection, requiring no non-local entanglement.

Detailed Report: [docs/BELL_HONEST_AUDIT_REPORT_2026.md](docs/BELL_HONEST_AUDIT_REPORT_2026.md)

## Why The Project Has Value

这个项目最有价值的地方，不是它简单声称解释了量子现象，而是它把一套替代性传播叙事推进到了可运行、可审计、可失败、可归档的程度。尤其重要的是，失败结果也被保留下来了，而不是被文档掩盖。

The strongest value of this project is not that it simply claims to explain quantum-like phenomena, but that it advances an alternative propagation narrative to the point where it is executable, auditable, falsifiable, and archivable. Crucially, failed results are also preserved rather than hidden by the documentation.

## Recommended Reading Order

**若偏好叙事线**：先 [book/00-preface.md](book/00-preface.md)，再按 [book/02-contents.md](book/02-contents.md) 逐章打开（档案 `06`/`07`，第 4–18 章正文稿约 `08`–`22`，后记 [book/23-afterword.md](book/23-afterword.md)）；需要核对脚本与归档时再回到本文档与专论。

**若偏好技术线**：建议按下面编号顺序阅读：本文档、总文档、Bell 协议说明、两轮 battle 归档，再回头看基础脚本。这样主线和支线不会混在一起。

**Narrative-first**: start with [book/00-preface.md](book/00-preface.md), then follow [book/02-contents.md](book/02-contents.md) chapter by chapter (archives `06`/`07`, chapter bodies roughly `08`–`22`, afterword [book/23-afterword.md](book/23-afterword.md)); dip into this README and the monograph when you need executable detail.

**Technical-first** (recommended if you are reproducing numbers): use the numbered list below.

1. [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md)
2. [MODEL_INTUITION.md](docs/MODEL_INTUITION.md)
3. [AUTHOR_MEMORY_NOTE.md](docs/AUTHOR_MEMORY_NOTE.md)
4. [BELL_PROTOCOL_NOTE.md](docs/BELL_PROTOCOL_NOTE.md)
5. [battle_results/README.md](battle_results/README.md)
6. [battle_results/nist_completeblind_2015-09-19/README.md](battle_results/nist_completeblind_2015-09-19/README.md)
7. [battle_results/nist_round2_v2/README.md](battle_results/nist_round2_v2/README.md)
8. [docs/RIPPLE_QUANTUM_TESTS_INDEX.md](docs/RIPPLE_QUANTUM_TESTS_INDEX.md)（涟漪量子四项玩具基准 v1–v6，与 CHSH 归档独立）

## Contact

如果你愿意交流这个项目（研究讨论、复现反馈或合作可能），可以通过以下方式联系：

- Email: `651775257 [at] qq [dot] com`
- 或在本仓库开启 issue / discussion

If you would like to discuss this project (research exchange, reproduction feedback, or potential collaboration), feel free to contact:

- Email: `651775257 [at] qq [dot] com`
- Or open an issue / discussion in this repository

## Licensing / 许可证

- **Software / 软件**（本仓库 `.py` 等源代码）：**GNU Affero General Public License v3.0 or later** — 见根目录 [`LICENSE`](LICENSE) 与 [`NOTICE`](NOTICE)。  
  AGPL 约束的是“分发或以网络服务方式提供衍生程序时，须按许可证提供对应源码”等 copyleft 义务；**并不**自动禁止一切收费或商业场景。若你需要“任何商业使用一律禁止”，须在具体合作中单签协议或使用额外条款。
- **Manuscripts & docs / 论文稿与叙事文档**（默认 `papers_final/`、`docs/` 中的文档类材料）：**CC BY-NC-ND 4.0** — 见 [`LICENSE-DOCS.md`](LICENSE-DOCS.md)（非商业、署名、禁止演绎再分发）。
- **Plain-language seal note / 平实说明（含陷阱参数库与人审节点）**：[`docs/LICENSE_AND_SEAL.md`](docs/LICENSE_AND_SEAL.md)、[`docs/AUDIT_PARAMETER_TRAP_LIBRARY.md`](docs/AUDIT_PARAMETER_TRAP_LIBRARY.md)。
- **Contributor licensing policy / 贡献许可政策**：[`CONTRIBUTING_LICENSE.md`](CONTRIBUTING_LICENSE.md)（防止外部贡献许可污染）。
- **Pull request template / PR 模板**：[`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)（提交 PR 时的许可勾选框）。

## Quick Note

仓库里仍有一部分旧文档存在历史编码污染，这会影响专业展示效果。新的入口文档、总文档和关键归档页已经按中英双语结构重写；后续如果继续优化，建议把其余历史文档也统一清洗为 UTF-8 版本。

Some legacy documents in the repository still carry historical encoding pollution, which affects the professional presentation of the project. The new entry document, monograph, and key archive pages have already been rewritten in a bilingual structure; if we continue refining the repository, the remaining historical files should also be normalized to UTF-8.




