# Chain Explosion Model

这是一个围绕离散、局域、可审计传播模型构建的研究型代码仓库。它不是量子力学教科书，也不是标准量子理论的直接替代证明；它更像一个把假设写进代码、把实验写进归档、把边界写进文档的研究工程。

This is a research-oriented code repository built around a discrete, local, and auditable propagation model. It is neither a quantum mechanics textbook nor a direct proof against standard quantum theory; it is better understood as a research program that encodes hypotheses into code, experiments into archives, and limits into documentation.

这个仓库真正的重点不是零散的双缝脚本，而是两次严肃的 CHSH / NIST 归档实验。其余 `ce_*`、`verify_*`、`discover_*`、`explore_*`、`critique_*` 脚本，主要承担基础建模、数值支撑和边界审计的作用。

The true center of this repository is not the scattered double-slit scripts, but two serious CHSH / NIST archival experiments. The other `ce_*`, `verify_*`, `discover_*`, `explore_*`, and `critique_*` scripts mainly serve as foundational modeling, numerical support, and boundary-audit layers.

## Contents

1. [Reading Guide](#reading-guide)
2. [Quick Start Paths](#quick-start-paths)
3. [What This Repository Contains](#what-this-repository-contains)
4. [The Two Major Experiments](#the-two-major-experiments)
5. [Audit Findings Summary](#audit-findings-summary)
6. [Why The Project Has Value](#why-the-project-has-value)
7. [Recommended Reading Order](#recommended-reading-order)
8. [Quick Note](#quick-note)

## Reading Guide

如果你只想快速理解这个项目，建议先读这份入口文档，再读总文档 [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md)。后者按“像一本书”的方式组织内容，包含摘要、章节、原理、公式、实验、结果与解释边界。

If you want a fast understanding of the project, start with this entry document and then read the full monograph [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md). The monograph is organized like a book, with an abstract, chapters, principles, formulas, experiments, results, and interpretive limits.

如果你想先看作者对传播、测量和模型直觉的自我图景，再进入技术主线，可以阅读 [MODEL_INTUITION.md](docs/MODEL_INTUITION.md)。这个文件被刻意与结果文档分开，以避免把“直觉”和“结论”混写在一起。

If you want to see the author's intuitive picture of propagation and measurement before diving into the technical structure, read [MODEL_INTUITION.md](docs/MODEL_INTUITION.md). That file is intentionally separated from the result documents so that intuition and conclusion are not conflated.

## Quick Start Paths

如果你想从不同入口理解仓库，可以按下面的路径进入。

If you want different ways to enter the repository, use one of these paths.

- Latest preprint trilogy (Zenodo):
  - Bell deconstruction (V3): https://doi.org/10.5281/zenodo.19767740
  - Bell audit (V2 legacy): https://doi.org/10.5281/zenodo.19763027
  - GHZ audit: https://doi.org/10.5281/zenodo.19765061
  - Trilogy synthesis: https://doi.org/10.5281/zenodo.19764505

- 最新预印本三部曲（Zenodo）：
  - Bell 局域几何解构 (V3)：https://doi.org/10.5281/zenodo.19767740
  - Bell 审计论文 (V2 遗留)：https://doi.org/10.5281/zenodo.19763027
  - GHZ 审计论文：https://doi.org/10.5281/zenodo.19765061
  - 综合终章论文：https://doi.org/10.5281/zenodo.19764505

- Brief note / 简要说明：
  - EN: These three papers form a reproducible audit trilogy focused on analysis-rule sensitivity, protocol transparency, and claim-boundary reporting for Bell/GHZ statistics.
  - 中文：这三篇论文构成一个可复现的审计三部曲，核心关注 Bell/GHZ 统计中的分析规则敏感性、协议透明度与结论边界报告。

- Fast overview: [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md)
- Author's model picture: [MODEL_INTUITION.md](docs/MODEL_INTUITION.md)
- Author's memory note: [AUTHOR_MEMORY_NOTE.md](docs/AUTHOR_MEMORY_NOTE.md)
- Bell / CHSH protocol layer: [BELL_PROTOCOL_NOTE.md](docs/BELL_PROTOCOL_NOTE.md)
- Paper strategy package: [PAPER_STRATEGY_PACKAGE.md](docs/PAPER_STRATEGY_PACKAGE.md)
- Research map: [RESEARCH_MAP.md](docs/RESEARCH_MAP.md)
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
3. **GHZ 现状**：目前 GHZ 实验在标准审计口径下的 $F$ 值处于低幅区间（~0.08）。这说明在三体干涉中，简单的二体归一化逻辑尚未能完全捕捉到三体相位锁存的几何特征。

In the 2026 Honest Audit, we reached the following key conclusions:

1. **The Binarization Trap in Bell Tests**: We proved that $S=2.828$ is the analytical solution for local harmonic waves under **Normalized Cross-Correlation (NCC)**, while the $S \le 2$ limit is an artifact of information loss due to forced Binarization.
2. **NIST Data Audit**: The $S$ values in NIST 2015 data are extremely sensitive to the coincidence window and gate criteria. The audit revealed that "success" relied on shifting gate criteria (HARKing) and specific window selection.
3. **GHZ Status**: The current GHZ pipeline reports low $F$ values (~0.08) under standard audit. This suggests that the simple two-body normalization logic has yet to fully capture the three-body phase-locking geometry.

Detailed Report: [docs/BELL_HONEST_AUDIT_REPORT_2026.md](docs/BELL_HONEST_AUDIT_REPORT_2026.md)

## Why The Project Has Value

这个项目最有价值的地方，不是它简单声称解释了量子现象，而是它把一套替代性传播叙事推进到了可运行、可审计、可失败、可归档的程度。尤其重要的是，失败结果也被保留下来了，而不是被文档掩盖。

The strongest value of this project is not that it simply claims to explain quantum-like phenomena, but that it advances an alternative propagation narrative to the point where it is executable, auditable, falsifiable, and archivable. Crucially, failed results are also preserved rather than hidden by the documentation.

## Recommended Reading Order

建议按这个顺序阅读：本文档、总文档、Bell 协议说明、两轮 battle 归档，再回头看基础脚本。这样主线和支线不会混在一起。

The recommended reading order is: this file, the full monograph, the Bell protocol note, the two battle archives, and only then the foundational scripts. This keeps the main line and supporting branches from being confused.

1. [PROJECT_TECHNICAL_MONOGRAPH.md](docs/PROJECT_TECHNICAL_MONOGRAPH.md)
2. [MODEL_INTUITION.md](docs/MODEL_INTUITION.md)
3. [AUTHOR_MEMORY_NOTE.md](docs/AUTHOR_MEMORY_NOTE.md)
4. [BELL_PROTOCOL_NOTE.md](docs/BELL_PROTOCOL_NOTE.md)
5. [battle_results/README.md](battle_results/README.md)
6. [battle_results/nist_completeblind_2015-09-19/README.md](battle_results/nist_completeblind_2015-09-19/README.md)
7. [battle_results/nist_round2_v2/README.md](battle_results/nist_round2_v2/README.md)

## Quick Note

仓库里仍有一部分旧文档存在历史编码污染，这会影响专业展示效果。新的入口文档、总文档和关键归档页已经按中英双语结构重写；后续如果继续优化，建议把其余历史文档也统一清洗为 UTF-8 版本。

Some legacy documents in the repository still carry historical encoding pollution, which affects the professional presentation of the project. The new entry document, monograph, and key archive pages have already been rewritten in a bilingual structure; if we continue refining the repository, the remaining historical files should also be normalized to UTF-8.
