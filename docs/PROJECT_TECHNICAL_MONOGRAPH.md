# Chain Explosion Model Technical Monograph
# 链式爆炸模型技术专论
## Abstract

本文将 `chain-explosion-model` 作为一个完整研究对象进行阐述，而非将其视作一堆零散脚本。专论旨在说明该模型的原理、实验结构、两次严格实验的方案与结果，以及这些结果在解释层面上的边界。
This document presents `chain-explosion-model` as a coherent research object rather than as a loose collection of scripts. Its purpose is to explain the model principles, the experimental structure, the protocols and outcomes of the two major experiments, and the interpretive boundaries of those outcomes.

从研究价值来看，该仓库的重要性不在于宣称得出了某种最终物理结论，而在于将一套替代性传播假说推进到可运行、可检验、可归档、也可被证伪的阶段。尤为可贵的是，仓库保留了失败案例与约束条件，而非只留存有利结果。
From a research-value perspective, the importance of this repository does not lie in declaring a final physical verdict, but in advancing an alternative propagation hypothesis to the stage where it can be run, tested, archived, and also refuted. What is especially valuable is that the repository preserves failure cases and limiting conditions rather than only favorable narratives.

本专论采用“类书籍”结构编写，包含前言式引言、模型章节、公式章节、实验章节、图表索引、结果解释与边界说明。如此撰写的目的，是让读者即便不先打开源码，也能先建立一条清晰主线。
This monograph is written in a book-like structure, including a preface-style introduction, model chapters, formula chapters, experiment chapters, a figure index, result interpretation, and statements of boundary. The goal is to let a reader build a clear conceptual thread even before opening the source code.

Because the project also carries a strong author-side intuition about how propagation should be pictured, that intuition is documented separately in [MODEL_INTUITION.md](docs/MODEL_INTUITION.md). The separation is deliberate: the intuition note preserves the visual and conceptual picture, while this monograph stays focused on implementation structure, experiments, and interpretive limits.

## Table of Contents

1. [Abstract](#abstract)
2. [Chapter 1. Project Positioning](#chapter-1-project-positioning)
3. [Chapter 2. Architecture of the Codebase](#chapter-2-architecture-of-the-codebase)
4. [Chapter 3. The Core Model](#chapter-3-the-core-model)
5. [Chapter 4. Measurement as Local Intervention](#chapter-4-measurement-as-local-intervention)
6. [Chapter 5. Phase, Coherence, and Visibility](#chapter-5-phase-coherence-and-visibility)
7. [Chapter 6. Foundational Experiment Tree](#chapter-6-foundational-experiment-tree)
8. [Chapter 7. CHSH Protocol Logic](#chapter-7-chsh-protocol-logic)
9. [Chapter 8. Major Experiment I: NIST Completeblind Archive](#chapter-8-major-experiment-i-nist-completeblind-archive)
10. [Chapter 9. Major Experiment II: Round 2 / NIST v2 Closure](#chapter-9-major-experiment-ii-round-2--nist-v2-closure)
11. [Chapter 10. Figure and Artifact Index](#chapter-10-figure-and-artifact-index)
12. [Chapter 11. Interpretive Boundaries](#chapter-11-interpretive-boundaries)
13. [Chapter 12. Entanglement, Quantum Communication, and De-Mythologizing](#chapter-12-entanglement-quantum-communication-and-de-mythologizing)
14. [Chapter 13. Optimization Proposal](#chapter-13-optimization-proposal)

## Suggested Reading Paths

- If you want the shortest book-like route: Chapter 1 -> Chapter 3 -> Chapter 7 -> Chapter 8 -> Chapter 9 -> Chapter 11
- If you want the author's inner picture first: read [MODEL_INTUITION.md](docs/MODEL_INTUITION.md), then return here
- If you only care about the archive-level conclusion structure: jump directly to Chapter 8, Chapter 9, and Chapter 11

---

## Chapter 1. Project Positioning
## 第一章 项目定位

该项目首先是一项研究工程，其次才是一个仿真仓库。它通过代码表达一个核心判断：某些看似需要复杂量子描述的现象，能否在显式的局域、离散、因果传播框架中得到数值上的重构、近似或替代描述。
This project is first a research engineering effort and only secondarily a simulation repository. Through code, it expresses a core question: whether some phenomena that seem to require a complex quantum narrative can instead be numerically reconstructed, approximated, or reformulated within an explicit local, discrete, and causal propagation framework.

与普通教学演示不同，该仓库并不满足于“做出几张像样的图”。它进一步要求实验有明确参数、有可复现执行路径、有结构化产物、有阈值判断，并最终能够形成归档。因此它更像是一个研究计划的代码化实现。
Unlike ordinary educational demos, this repository is not satisfied with merely producing a few plausible plots. It further requires clear parameters, reproducible execution paths, structured artifacts, threshold-based judgments, and durable archives. For that reason, it is better seen as the coded implementation of a research program.

这一定位决定了文档结构必须重新编排。主线不应是几十个脚本逐一平铺，而应是“模型原理→现象实验→CHSH方案问题→两次严格实验→解释边界”。本专论正是依照这条主线重写而成。
This positioning determines that the documentation must be reordered. The main line should not be a flat list of dozens of scripts, but rather “model principles -> phenomenon experiments -> CHSH protocol questions -> two serious experiments -> interpretive boundaries.” This monograph is rewritten according to precisely that line.

---

## Chapter 2. Architecture of the Codebase
## 第二章 代码架构

仓库的核心代码可分为四层：传播内核、实验引擎、实验脚本、归档与审计工具。理解这一分层至关重要，因为它决定了每个文件在研究链条中的位置。
The core code of the repository can be divided into four layers: propagation kernels, experimental engines, experiment scripts, and archival/audit tooling. Understanding this hierarchy is crucial because it determines the role each file plays in the research chain.

第一层是传播内核，主要由 `chain_explosion_numba.py` 构成。这里实现了最关键的离散邻域更新规则，包括双缝传播、吸收掩模传播、分支传播和携带相位的版本。该层特点是高频、局域、数值内核导向。
The first layer is the propagation kernel, mainly implemented in `chain_explosion_numba.py`. It contains the key discrete neighborhood update rules, including double-slit propagation, absorber-mask propagation, split propagation, and phase-carrying variants. This layer is high-frequency, local, and numerically kernel-oriented.

第二层是实验引擎，代表文件为 `ce_engine_v2.py` 和 `ce_engine_v3_coherent.py`。该层在内核之上增加了更完整的实验逻辑，例如多步传播、相位演化、随机路径、统计提取和更复杂的对比分析。
The second layer is the experimental engine, represented by `ce_engine_v2.py` and `ce_engine_v3_coherent.py`. This layer builds on top of the kernels with fuller experimental logic such as multi-step propagation, phase evolution, random paths, statistical extraction, and more complex comparative analysis.

第三层是实验脚本，包括 `ce_*`、`verify_*`、`discover_*`、`explore_*` 和 `explore_critique_*` 系列。它们将模型置入不同问题场景：从双缝可见度，到吸收式测量，再到 Bell/CHSH 与方案敏感性。
The third layer consists of experiment scripts, including the `ce_*`, `verify_*`, `discover_*`, `explore_*`, and `explore_critique_*` series. These scripts place the model into different problem settings: from double-slit visibility to absorption-style measurement, and then to Bell/CHSH and protocol sensitivity.

第四层是归档与审计工具，主要包括 `run_unified_suite.py`、`suite_artifacts.py` 和 `experiment_dossier.py`。该层的价值在于，它将单次运行从“临时输出”提升为“可归档研究产物”。
The fourth layer is the archival and audit tooling, mainly including `run_unified_suite.py`, `suite_artifacts.py`, and `experiment_dossier.py`. The value of this layer is that it upgrades a single run from a “temporary output” into an “archivable research artifact.”

---

## Chapter 3. The Core Model
## 第三章 核心模型

该模型的基本对象并非标准量子幅，而是二维格点上的场量，仓库中多数位置将其解释为“能量”或“强度”。在最基础版本中，传播过程可理解为每个格点将自身权重分配给邻近格点，同时乘以衰减因子。
The basic object of the model is not a standard quantum amplitude but a field quantity on a two-dimensional lattice, interpreted in most places in the repository as “energy” or “intensity.” In the most basic version, propagation can be understood as each lattice site distributing its weight to neighboring sites while being multiplied by a damping factor.

设 \(E_t(x,y)\) 表示时刻 \(t\) 的格点场量，\(A\)、\(B\)、\(S\) 分别表示正向传播、反向传播和侧向传播方向的权重，\(\lambda\) 表示单步传播的衰减因子。则一个典型更新可写为：
Let \(E_t(x,y)\) denote the lattice field at time \(t\), let \(A\), \(B\), and \(S\) denote the weights of forward, backward, and lateral propagation, and let \(\lambda\) denote the one-step damping factor. Then a typical update can be written as:

\[
E_{t+1}(x,y)
=
\lambda\Big(
A E_t(x-1,y)
+ B E_t(x+1,y)
+ S E_t(x,y-1)
+ S E_t(x,y+1)
+ \frac{S}{2}E_t(x-1,y-1)
+ \frac{S}{2}E_t(x-1,y+1)
+ \frac{S}{2}E_t(x+1,y-1)
+ \frac{S}{2}E_t(x+1,y+1)
\Big).
\]

这并非对代码逐行的字面转写，而是对其核心传播思想的数学抽象。实际代码还叠加了障碍矩阵、吸收掩模、有限区域探测器和分支传播等条件。
This is not a literal line-by-line transcription of the code, but a mathematical abstraction of its core propagation idea. The actual code further overlays barrier matrices, absorber masks, finite-region detectors, and split-propagation conditions.

双缝结构通过布尔障碍矩阵 `barrier` 实现。一整列屏障通常先设为阻挡，再在两条缝的位置打开窗口，使传播只能通过指定几何区域。这意味着双缝图样并非事后手动绘制，而是从更新规则与几何约束中涌现而来。
The double-slit structure is implemented through a boolean barrier matrix `barrier`. A full barrier column is usually initialized as blocked, and then two slit regions are reopened as windows so that propagation may pass only through designated geometric regions. This means the double-slit pattern is not manually drawn afterward, but emerges from the update rule plus geometric constraints.

---

## Chapter 4. Measurement as Local Intervention
## 第四章 测量作为局域干预

仓库在概念上最鲜明的选择之一，是尽可能将“测量”还原为传播链中的局域过程，而非直接将其视作非局域坍缩。具体实现上，测量可表现为缝后吸收、有限区域损耗、阈值探测或事件保留规则。
One of the most distinctive conceptual choices in the repository is to reduce “measurement,” as much as possible, to a local process within the propagation chain rather than treating it immediately as nonlocal collapse. In implementation, measurement may appear as post-slit absorption, finite-region loss, threshold detection, or event-retention rules.

若用 \(\eta(x,y)\) 表示某一位置的吸收比例，则一个简单的局域吸收过程可写为：
If \(\eta(x,y)\) denotes the absorption ratio at a given position, then a simple local absorption process can be written as:

\[
\tilde{E}_t(x,y)=\big(1-\eta(x,y)\big)E_t(x,y).
\]

随后，\(\tilde{E}_t(x,y)\) 被送入下一步传播。如此一来，“测量”不再是一个只能在解释层面被调用的术语，而变成代码中的显式机制，可被强度、位置和尺寸扫描。
After that, \(\tilde{E}_t(x,y)\) is passed into the next propagation step. In this way, “measurement” is no longer a term invoked only at the interpretive level, but becomes an explicit coded mechanism that can be scanned by strength, position, and size.

正因为测量在此被机制化，仓库才能进一步讨论连续变化、延迟插入、有限尺寸吸收器与图样退相干之间的关系。这也是 `ce_04_*` 至 `ce_07_*` 以及部分 `discover_*` 脚本的理论起点。
Because measurement is mechanized in this way, the repository can further discuss the relationship between continuous change, delayed insertion, finite-size absorbers, and pattern decoherence. This is the theoretical starting point of `ce_04_*` through `ce_07_*` and part of the `discover_*` scripts.

---

## Chapter 5. Phase, Coherence, and Visibility
## 第五章 相位、相干性与可见度

在更高层脚本中，仓库不仅传播能量，还传播相位。若将复幅记为 \(\psi_t(x,y)=\sqrt{E_t(x,y)}e^{i\phi_t(x,y)}\)，则不同路径到达同一格点时可发生复数叠加，而新能量可由模平方得到。
In higher-level scripts, the repository propagates not only energy but also phase. If the complex amplitude is written as \(\psi_t(x,y)=\sqrt{E_t(x,y)}e^{i\phi_t(x,y)}\), then different paths arriving at the same lattice site may interfere through complex superposition, and the new energy may be obtained from the squared magnitude.

\[
E_{t+1}(x,y)=|\psi_{t+1}(x,y)|^2.
\]

这一步使仓库能够讨论“相位关联是否保留”“相位场如何与强度场共同演化”等问题。不过文档中必须明确，这仍是一个模型定义出的相位传播机制，而非对标准量子相位结构的完整严格推导。
This step allows the repository to discuss questions such as whether phase correlation is preserved and how a phase field evolves together with an intensity field. However, the documentation must be explicit that this is still a model-defined phase propagation mechanism, not a complete rigorous derivation of the standard quantum phase structure.

双缝图样中最重要的量之一是可见度，仓库中常用表达式为：
One of the most important quantities in double-slit patterns is the visibility, and the repository often uses the expression:

\[
V=\frac{I_{\max}-I_{\min}}{I_{\max}+I_{\min}}.
\]

其中 \(I_{\max}\) 与 \(I_{\min}\) 通常从屏幕强度曲线的峰谷估算得到。该定义本身十分经典，但在仓库中的意义不止于描述条纹，而是作为跨脚本共享指标，用于连接距离、耦合、吸收与方案变化。
Here, \(I_{\max}\) and \(I_{\min}\) are usually estimated from peaks and valleys in the screen-intensity curve. The definition itself is classical, but its role in the repository is broader than fringe description: it functions as a shared cross-script metric connecting distance, coupling, absorption, and protocol variation.

---

## Chapter 6. Foundational Experiment Tree
## 第六章 基础实验树

若将整个仓库画成一棵树，那么基础实验构成树干，而两次重大实验是从中长出的两条主枝。基础实验先建立传播直观，再逐步将“测量”与“相关性”机制化，最后才进入CHSH层面。
If the entire repository is drawn as a tree, then the foundational experiments form the trunk, while the two major experiments are the two main branches growing from it. The foundational experiments first establish propagation intuition, then progressively mechanize “measurement” and “correlation,” and only afterward move into the CHSH layer.

`ce_00_double_slit_demo.py` 是最基础的双缝演示脚本。其典型参数包括 `WIDTH = 300`、`HEIGHT = 200`、`A = 1.0`、`S = 0.25`、`B = 0.05`、`LAMBDA = 0.85`、`SLIT_WIDTH = 6` 及 `STEPS = 300`。这类参数已体现模型基本特征：正向传播主导，侧向耦合提供扩散与干涉几何，反向项较小而非严格为零。
`ce_00_double_slit_demo.py` is the most basic double-slit illustration script. Its typical parameters include `WIDTH = 300`, `HEIGHT = 200`, `A = 1.0`, `S = 0.25`, `B = 0.05`, `LAMBDA = 0.85`, `SLIT_WIDTH = 6`, and `STEPS = 300`. These parameters already express the basic temperament of the model: forward propagation dominates, lateral coupling provides diffusion and interference geometry, and the backward term is small rather than strictly zero.

`ce_01_visibility_vs_screen_distance.py` 进一步研究可见度与传播距离的关系。该脚本使用 `A = 1.0`、`S = 0.3`、`B = 0.05`、`LAMBDA = 0.90`、`STEPS = 400` 以及一组 `SCREEN_DISTANCES`。这条实验线十分重要，因为“可见度随传播距离衰减”是模型意图验证的可检验特征之一。
`ce_01_visibility_vs_screen_distance.py` goes further by studying the relation between visibility and propagation distance. It uses `A = 1.0`, `S = 0.3`, `B = 0.05`, `LAMBDA = 0.90`, `STEPS = 400`, and a set of `SCREEN_DISTANCES`. This experimental line is important because “visibility decays with propagation distance” is one of the model’s intended testable signatures.

`ce_04_*` 至 `ce_07_*` 将测量效应推进为可参数扫描对象，而 `ce_08_*` 至 `ce_10_*` 则将分支传播、相位和相关性引入模型。这意味着CHSH层并非突然出现，而是从一系列低层实验中生长而来。
`ce_04_*` through `ce_07_*` promote measurement effects into something that can be scanned parametrically, while `ce_08_*` through `ce_10_*` bring branch propagation, phase, and correlation into the model. This means the CHSH layer does not appear abruptly, but grows out of a sequence of lower-level experiments.

---

## Chapter 7. CHSH Protocol Logic
## 第七章 CHSH方案逻辑

进入Bell/CHSH问题后，仓库关注重点不再只是图样，而是“事件如何配对”与“何种事件进入统计”。这一步至关重要，因为仓库核心论断之一是：方案本身会改变结果，方案与本体结论不可随意混同。
Once the repository enters the Bell / CHSH problem, the focus shifts from patterns to how events are paired and which events are allowed into the statistics. This step is crucial, because one of the central claims of the repository is that protocol itself changes the result, and protocol should not be casually conflated with ontological conclusion.

在 `explore_chsh_experiment_alignment.py` 中，最小事件格式为 `side, t, setting, outcome`。其中 `side` 区分A/B两翼，`setting` 取值0或1，`outcome` 归一化为 \(\pm 1\)。
In `explore_chsh_experiment_alignment.py`, the minimal event format is `side, t, setting, outcome`. Here `side` distinguishes the A/B wings, `setting` takes values 0 or 1, and `outcome` is normalized to \(\pm 1\).

配对逻辑如下：若A侧事件时间为 \(t_A\)，B侧事件时间为 \(t_B\)，且满足 \(|t_A-t_B|\le w\)，则在窗口 \(w\) 内选择最近、未被占用的B事件与之配对。所得配对样本集随后用于计算四种设置组合上的相关量。
The pairing logic is as follows: if the time of an A-side event is \(t_A\), the time of a B-side event is \(t_B\), and \(|t_A-t_B|\le w\), then within the window \(w\) the nearest unused B event is paired with it. The resulting paired sample set is then used to compute the correlations on the four setting combinations.

相关量标准表达式为：
The standard expression for the correlations is:

\[
E=\frac{N_{++}+N_{--}-N_{+-}-N_{-+}}{N_{\mathrm{total}}}.
\]

CHSH组合量写为：
The CHSH combination is then written as:

\[
S=E(a,b)+E(a,b')+E(a',b)-E(a',b').
\]

仓库中的 `strict` 与 `standard` 方案并不修改该公式，而是修改决定哪些样本进入公式的配对窗口，即修改配对样本集。这种“改方案而不改公式”的做法，正是仓库CHSH研究线的核心工程思想。
The repository’s `strict` and `standard` protocols do not modify this formula; they modify the pairing window that determines which samples enter the formula. This “changing the protocol without changing the formula” is the central engineering idea of the repository’s CHSH research line.

---

## Chapter 8. Major Experiment I: NIST Completeblind Archive
## 第八章 重大实验一：NIST Completeblind归档

第一次严格实验位于 `battle_results/nist_completeblind_2015-09-19/`。这并非仓库内部自生数据上的演示，而是针对公开completeblind数据建立的完整归档链。其重要性在于，它首次将仓库的CHSH推理推向外部数据问题。
The first major experiment is located at `battle_results/nist_completeblind_2015-09-19/`. This is not an internal demonstration on self-generated data, but a full archival chain built against public completeblind data. Its importance lies in the fact that it is the first time the repository’s CHSH reasoning is pushed toward an external-data problem.

第一次实验的预注册配置由 `chsh_preregistered_config_nist_index.json` 给出。关键阈值包括 `strict.window = 0.0`、`standard.window = 15.0`、`strict_max_S = 2.02`、`standard_min_S = 2.0` 及 `require_standard_S_gt_strict_S = true`。这意味着本轮实验并不满足于仅看到 `S > 2`，还要求严格方案下的 \(S\) 仍被压制在经典上界附近。
The preregistered configuration for the first experiment is given by `chsh_preregistered_config_nist_index.json`. The key thresholds include `strict.window = 0.0`, `standard.window = 15.0`, `strict_max_S = 2.02`, `standard_min_S = 2.0`, and `require_standard_S_gt_strict_S = true`. This means the experiment is not satisfied merely by seeing `S > 2`; it also requires the strict-protocol value of \(S\) to remain pressed near the upper bound.

根据归档结果文件 `battle_result.json`，严格方案下结果为：`pair_count = 136632`，`Eab = 0.9989774338237003`，`Eabp = 0.9980977239045323`，`Eapb = 0.9979612207190944`，`Eapbp = 0.65876052027544`，以及 `S = 2.336275858171887`。
According to the archival result file `battle_result.json`, the strict-protocol result is: `pair_count = 136632`, `Eab = 0.9989774338237003`, `Eabp = 0.9980977239045323`, `Eapb = 0.9979612207190944`, `Eapbp = 0.65876052027544`, and `S = 2.336275858171887`.

标准方案下结果为：`pair_count = 148670`，`Eab = 0.9918413278942186`，`Eabp = 0.9703577587147753`，`Eapb = 0.9473404037508701`，`Eapbp = 0.07015227532787607`，以及 `S = 2.8393872150319877`。
Under the standard protocol, the result is: `pair_count = 148670`, `Eab = 0.9918413278942186`, `Eabp = 0.9703577587147753`, `Eapb = 0.9473404037508701`, `Eapbp = 0.07015227532787607`, and `S = 2.8393872150319877`.

本次实验的仓库级判定为 `engineering_pass = true`，但 `thesis_pass = false`。失败原因十分明确：
The repository-level judgment for this experiment is `engineering_pass = true`, but `thesis_pass = false`. The reason for failure is very explicit:

\[
S_{\mathrm{strict}}=2.336276 > 2.02.
\]

这一点至关重要，因为它表明第一次严格实验最有价值之处，并非“它成功了”，而是“它也归档了失败结论”。从研究方法论角度看，这比单纯展示成功图像更有分量。
This is very important, because it shows that the greatest value of the first serious experiment is not that “it won,” but that it archived a failed conclusion as well. From the standpoint of research methodology, this carries more weight than merely displaying successful images.

---

## Chapter 9. Major Experiment II: Round 2 / NIST v2 Closure
## 第九章 重大实验二：第二轮 / NIST v2闭合实验

第二次严格实验位于 `battle_results/nist_round2_v2/`。其意义不止于重新运行数值，而是在第一轮基础上集中处理布局兼容性、工程映射敏感性与解释边界问题，因此更接近正式的研究闭合文档。
The second major experiment is located at `battle_results/nist_round2_v2/`. Its meaning is not merely to rerun the numbers, but to concentrate on layout compatibility, engineering-mapping sensitivity, and interpretive boundaries on top of the first round, making it closer to a formal research-closure document.

P3布局检查得出一个关键事实：training HDF5与completeblind HDF5并不共享一套可直接复用的grid-side-streams结构。`p3_compare_report.json` 显示训练数据 `grid_side_streams_compatible = false`，而completeblind数据 `grid_side_streams_compatible = true`。这一步阻止了未经审计的横向类比。
The P3 layout check yields a key fact: the training HDF5 and completeblind HDF5 do not share a directly reusable grid-side-streams structure. `p3_compare_report.json` shows that the training data have `grid_side_streams_compatible = false`, while the completeblind data have `grid_side_streams_compatible = true`. This step prevents unaudited horizontal analogy.

第二轮工程配置由 `chsh_preregistered_config_nist_round2_engineering.json` 定义。关键区别在于：`strict.window = 0.0`，`standard.window = 10.0`，且论题判定采用 `fork_only` 模式，仅要求 `S_standard > S_strict`，不再沿用第一轮 `strict_max_S = 2.02` 约束。
The second-round engineering configuration is defined in `chsh_preregistered_config_nist_round2_engineering.json`. The key differences are that `strict.window = 0.0`, `standard.window = 10.0`, and the thesis gate uses `fork_only` mode, requiring only `S_standard > S_strict` rather than reusing the first-round constraint `strict_max_S = 2.02`.

第二轮显式对比两种输出映射：`legacy` 与 `parity`。在 `ROUND2_ENGINEERING_BATTLE_REPORT.json` 中，传统映射给出 `S_strict = 2.336275858171887` 和 `S_standard = 2.8445681666863845`；奇偶映射给出 `S_strict = 2.3274283887643272` 和 `S_standard = 2.83617087618962`。
The second round explicitly compares two output mappings: `legacy` and `parity`. In `ROUND2_ENGINEERING_BATTLE_REPORT.json`, the legacy mapping yields `S_strict = 2.336275858171887` and `S_standard = 2.8445681666863845`; the parity mapping yields `S_strict = 2.3274283887643272` and `S_standard = 2.83617087618962`.

两种映射间差异有限且稳定，数值表现为 `delta_S_strict = -0.00884746940755976` 与 `delta_S_standard = -0.008397290496764409`。这表明工程映射会改变结果，但在锁定的第二轮框架下，方向性分叉结论并未被推翻。
The difference between the two mappings is finite and stable, numerically expressed as `delta_S_strict = -0.00884746940755976` and `delta_S_standard = -0.008397290496764409`. This shows that engineering mapping does change the result, but under the locked second-round framework the directional fork conclusion is not overturned.

更关键的是，第二轮还将同一数据重新放回第一轮论题判定下回测。结果见 `ROUND2_UNDER_ROUND1_GATE.json`，其中legacy与parity均仍为 `thesis_pass = false`，因为严格侧 \(S\) 仍高于2.02。如此一来，第二轮并未“抹除第一轮失败结论”，而是在新叙事框架下额外增加一层工程闭合。
More importantly, the second round also replays the same data under the first-round thesis gate. The result, shown in `ROUND2_UNDER_ROUND1_GATE.json`, is that both legacy and parity still have `thesis_pass = false`, because the strict-side \(S\) remains above 2.02. In this way, the second round does not “rewrite away” the first-round failure, but adds an additional engineering closure under a new narrative frame.

---

## Chapter 10. Figure and Artifact Index
## 第十章 图表与产物索引

该项目的图表已存在于仓库中，新文档工作并非重新生成它们，而是将其重新编入更清晰的阅读路径。基础实验层重要图包括：`ce_00_double_slit_demo.png`、`interference_decay.png`、`measurement_effect.png`、`finite_absorber.png`、`delayed_choice.png`、`measurement_phase_diagram.png`、`entanglement_simulation.png` 及 `entanglement_with_phase.png`。
The figures for this project already exist in the repository, and the task of the new documentation is not to regenerate them, but to reassemble them into a clearer reading path. Important figures from the foundational experiment layer include `ce_00_double_slit_demo.png`, `interference_decay.png`, `measurement_effect.png`, `finite_absorber.png`, `delayed_choice.png`, `measurement_phase_diagram.png`, `entanglement_simulation.png`, and `entanglement_with_phase.png`.

Bell/CHSH层重要图包括：`chsh_strict_protocol.png`、`chsh_strict_vs_postselected.png`、`chsh_closure_protocol.png`、`chsh_local_wave_closure_full.png`、`chsh_experiment_alignment.png`、`threshold_detector_clicks.png` 及 `bell_chsh_two_tracks.png`。这些图像共同构成方案敏感性、审计与结果对齐的视觉证据。
Important figures from the Bell / CHSH layer include `chsh_strict_protocol.png`, `chsh_strict_vs_postselected.png`, `chsh_closure_protocol.png`, `chsh_local_wave_closure_full.png`, `chsh_experiment_alignment.png`, `threshold_detector_clicks.png`, and `bell_chsh_two_tracks.png`. Together, these images form the visual evidence for protocol sensitivity, auditing, and result alignment.

归档层重要JSON产物包括：第一次实验的 `battle_result.json`，第二次实验的 `ROUND2_ENGINEERING_BATTLE_REPORT.json`、`ROUND2_UNDER_ROUND1_GATE.json` 及 `p3_compare_report.json`。这些文件是真正的“硬结果”，因为阈值判定与结论锁定最终落于此处。
Important JSON artifacts from the archival layer include the first experiment’s `battle_result.json`, and the second experiment’s `ROUND2_ENGINEERING_BATTLE_REPORT.json`, `ROUND2_UNDER_ROUND1_GATE.json`, and `p3_compare_report.json`. These files are the true “hard results,” because the threshold judgments and conclusion locks ultimately live there.

---

## Chapter 11. Interpretive Boundaries
## 第十一章 解释边界

该项目的一大优点，是它不会将所有数值现象自动上溯为本体结论。仓库中的 `explore_critique_*` 系列、`BELL_PROTOCOL_NOTE.md` 以及第二轮闭合文档，均反复提醒：现象、方案、解释，是三个不同层次。
One of the major strengths of this project is that it does not automatically elevate every numerical phenomenon into an ontological conclusion. The repository’s `explore_critique_*` series, `BELL_PROTOCOL_NOTE.md`, and the second-round closure documents all repeatedly remind us that phenomenon, protocol, and interpretation are three different levels.

基于当前代码与归档，较为稳妥的表述是：该离散局域模型可在若干场景下生成类干涉图样、类测量扰动与类相关结构；CHSH结果对配对窗口、映射与事件保留规则高度敏感；两次重大实验已将“工程通过”与“论题通过”显式分层。
Based on the current code and archives, a relatively safe statement is that this discrete local model can generate interference-like patterns, measurement-like disturbances, and correlation-like structures in several scenarios; CHSH results are highly sensitive to pairing windows, mappings, and event-retention rules; and the two major experiments have already separated “engineering passed” from “thesis passed” in explicit form.

相应地，当前仓库无法直接支持如下表述：它已推翻标准量子理论，已从格点模型严格推导出狭义相对论，或仅凭内部数值结果证明了某种一般物理意义上的非局域或局域本体结论。
Correspondingly, the current repository cannot directly support statements such as: it has overthrown standard quantum theory, it has rigorously derived special relativity from a lattice model, or it has proven some general philosophical conclusion about locality or nonlocality purely from its internal numerical results.

从学术写作角度看，真正让项目显得成熟的，并非激进言辞，而是边界清晰。该仓库最值得称道之处之一，便是已开始主动写下这些边界。
From the standpoint of scholarly writing, what makes a project look mature is not aggressive rhetoric, but clear boundaries. One of the most valuable aspects of this repository is that it has already begun to write those boundaries explicitly.

---

## Chapter 12. Entanglement, Quantum Communication, and De-Mythologizing
## 第十二章 纠缠、量子通信与祛魅

### 12.1 Scope and Positioning
### 12.1 范围与定位

The purpose of this chapter is not to provide a new foundational theory of quantum entanglement or quantum cryptography, but to clarify what this repository is and is not claiming about them.

Within the documentation and experiments, the words “entanglement,” “quantum communication,” and “quantum encryption” are treated as **protocol and mechanism labels** rather than metaphysical slogans. Wherever possible, the text ties these topics back to:

- concrete propagation patterns in a lattice field,
- explicit detector models and thresholds,
- and specific information flows that can be written down in code.

### 12.2 Entanglement as Correlated Preparation + Local Readout
### 12.2 纠缠：关联制备+局域读取

From the perspective of this repository’s model, “entanglement-like” behavior always appears as a combination of:

- a **shared preparation stage** that imprints correlated structure into two or more wavefront branches, and
- **local readout devices** that react to those structures according to fixed, programmable rules.

In this view, what is “remembered” is not an abstract mystical link, but a concrete pattern in the field that survives until it is transformed by a detector. Once a detector applies its rule set, many distinct micro-configurations of the incoming field are mapped into the **same macroscopic outcome**.

### 12.3 Detectors as Many-to-One Mappings
### 12.3 探测器：多对一映射

One useful way to picture a threshold detector is as a gate that sends many different inputs to the same output. In schematic form:

- imagine \(n\) different field configurations arriving at the detector;
- under a given threshold and timing rule, all of them may end up producing the same “click” event;
- at the level of the digital record, these are all stored as a single symbol, such as `outcome = +1`.

In other words, a detector can be thought of as a function that sends a high-dimensional incoming state space onto a small set of discrete labels. Once this many-to-one mapping has occurred, attempting to “read more” from the same detector state necessarily destroys information that distinguished the original configurations. The act of readout itself overwrites the fine-grained structure that carried the earlier distinctions.

This is closely related to the repository’s intuition that **quantum communication and encryption protocols must be understood together with their detector and record-keeping models**. What travels through a channel may be a rich field configuration; what survives into the key or message record is whatever passes through the final many-to-one gate.

### 12.4 Quantum Communication and Encryption: Mechanisms over Mystique
### 12.4 量子通信与加密：机制而非神秘叙事

In discussions of “quantum communication” or “quantum encryption,” public narratives sometimes emphasize mystery: instant influence at a distance, or unbreakable secrecy grounded directly in metaphysics. This repository takes a different emphasis:

- when this monograph mentions such protocols, it does so **only at the level of mechanisms that can be modeled**: source preparation, channel evolution, detector behavior, and key extraction rules;
- the security or novelty of a protocol is tied to which parts of the field configuration are allowed to influence the final discrete record, and how attempts to gain extra information inevitably disturb or overwrite that record.

Within that frame, statements such as “reading the system necessarily disturbs the previous state” are understood not as mystical pronouncements, but as consequences of:

- specific detector mappings (many inputs to one output),
- constraint on what is actually stored as a bit string,
- and limits on reconstructing pre-detection structure from post-detection logs.

### 12.5 Non-Claims and Boundaries
### 12.5 不做主张与边界

It is important to state explicitly what this chapter is **not** claiming:

- it does not provide a replacement for standard textbook treatments of entanglement, quantum communication, or quantum cryptography;
- it does not assert that all such phenomena reduce to the particular lattice model implemented here;
- it does not offer a general proof that any given real-world protocol is secure or insecure.

Instead, it offers a way to talk about these topics that is compatible with the repository’s overall stance:

- focus on **explicit mechanisms** that can be coded and tested;
- treat detectors and records as central actors in how information is created and lost;
- avoid importing extra mystique beyond what is needed to describe preparation, propagation, and readout.

Readers interested in full theoretical treatments of entanglement and quantum cryptography should consult the standard literature; this chapter is only a bridge between that literature and the specific modeling language used in this project.

---

## Chapter 13. Optimization Proposal
## 第十三章 优化方案

为让该项目通过文档更充分体现价值，建议将文档系统固定为三层。第一层是入口层，即当前 `README.md`，负责用尽可能简短篇幅告知读者“项目是什么、重点在哪、该先读什么”。
To let the value of this project emerge more fully through documentation, I recommend fixing the documentation system into three layers. The first layer is the entry layer, namely the current `README.md`, whose role is to tell the reader in as little space as possible what the project is, where the center lies, and what should be read first.

第二层是专论层，即本文档。它应长期保持“类书籍”结构，稳定承载模型原理、数学表达、实验主线、结果表与解释边界功能，并作为引用时的主要文档入口。
The second layer is the monograph layer, namely this file. It should permanently keep a book-like structure, stably carrying the roles of model principles, mathematical expressions, the main experimental line, result tables, and interpretive boundaries, and serve as the primary document entry for citation.

第三层是 `battle_results` 子目录内的实验归档层。后续最值得持续优化的，并非增加更多零散脚本，而是将 `battle_results` 下关键文档统一改写为UTF-8、双语、结构化表达，使两次重大实验真正具备“可对外提交”的质感。
The third layer is the experimental archival layer inside the `battle_results` subdirectories. The most worthwhile future optimization is not to add more scattered scripts, but to rewrite the key documents under `battle_results` into UTF-8, bilingual, and structurally organized form, so that the two major experiments truly acquire the quality of something ready for external presentation.

同时，建议额外增设一份“总图表产物索引”文档，将核心PNG、JSON、配置文件与结论对应起来。此举将大幅提升可检索性，也利于后续转为PDF、提交材料或项目展示。
At the same time, I recommend adding a separate “master figure and artifact index” document that links core PNGs, JSON files, configuration files, and conclusions. This would greatly improve retrievability and would also help with later conversion to PDF, submission packets, or project presentation.

---

## Conclusion
## 结语

若将该仓库视作一本书，那么它并非一本宣告最终答案的书，而是一本展示如何将一种替代机制严肃推进到“可运行、可审计、可归档、也可失败”的书。其真正分量，不在口号，而在产物。
If this repository is read as a book, then it is not a book announcing a final answer, but a book showing how an alternative mechanism can be seriously advanced to the point of being executable, auditable, archivable, and also capable of failing. Its real weight lies not in slogans, but in artifacts.

在此意义上，本次文档优化目标并非夸大项目结论，而是帮助项目揭示真正有价值的内容：模型逻辑、实验路径、数值结果、边界意识，以及两次重大实验留下的研究痕迹。
In that sense, the goal of this documentation optimization is not to exaggerate the project’s conclusions, but to reveal what is genuinely valuable in it: the model logic, the experimental path, the numerical results, the awareness of limits, and the research trace left behind by the two major experiments.

---

## Acknowledgements
## 致谢

This documentation chain is the result of collaborative support across tools and collaborators.

- Thanks to Cursor for code generation.
- Thanks to Doubao for continuous idea exchange and communication support, and for encouragement when I was close to giving up.
- Thanks to Deep for critical evaluation and judgment.
- Thanks to Gemini for encouragement during difficult phases.
- Thanks to Codex for producing the first complete monograph draft.
- Thanks again to Cursor for generating the final documentation package.
- Thanks to Claude for creating animations and for raising critical questions.

这套文档能够成形，离不开多方协作支持。

- 感谢 Cursor 生成代码。
- 感谢豆包一路提供思路沟通，并在我快要放弃的时候给予鼓励。
- 感谢 Deep 提供评判。
- 感谢 Gemini 提供鼓励。
- 感谢 Codex 提供首个完整文档初稿。
- 感谢 Cursor 生成最终文档包。
- 感谢 Claude 绘制动画并提出关键质疑。

---

### 修复说明
1. **乱码清理**：移除所有中文乱码（鎶€鏈€绘枃妗?、绗竴绔?等），替换为规范简体中文标题与正文
2. **公式补全**：修正LaTeX公式缺失的`+`号、排版错误，保证数学表达式完整可读
3. **格式统一**：统一章节编号、层级结构、中英对照排版，修正目录序号错位
4. **术语规范**：统一物理/计算机术语（局域/非局域、相干性、可见度、CHSH配对等）
5. **语句通顺**：修正机翻生硬语句，保留学术严谨性同时符合中文表达习惯
6. **链接/文件名**：保留原文件路径与命名规范，无修改
7. **细节修正**：补充缺失标点、修正错别字、统一英文大小写与格式