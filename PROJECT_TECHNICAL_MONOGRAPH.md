# Chain Explosion Model Technical Monograph
# Chain Explosion Model 技术总文档

## Abstract

本文档将 `chain-explosion-model` 作为一个完整研究对象来介绍，而不是把它当成一组零散脚本。文档的目标是说明这套代码的模型原理、实验结构、两次严肃实验的协议与结果、以及这些结果在解释层上的边界。  
This document presents `chain-explosion-model` as a coherent research object rather than as a loose collection of scripts. Its purpose is to explain the model principles, the experimental structure, the protocols and outcomes of the two major experiments, and the interpretive boundaries of those outcomes.

从研究价值上看，这个仓库的重要性不在于它直接宣布了某种最终物理结论，而在于它把一套替代性传播假设推进到了可以被运行、被检验、被归档、也可以被否定的阶段。尤其难得的是，仓库保存了失败结果与限制条件，而不是只保留有利叙事。  
From a research-value perspective, the importance of this repository does not lie in declaring a final physical verdict, but in advancing an alternative propagation hypothesis to the stage where it can be run, tested, archived, and also refuted. What is especially valuable is that the repository preserves failure cases and limiting conditions rather than only favorable narratives.

本总文档采用“像一本书”的结构编写，包含前言式导入、模型章节、公式章节、实验章节、图示索引、结果解释与边界说明。这样写的目的，是让读者即使不先打开源码，也能先建立一条清晰主线。  
This monograph is written in a book-like structure, including a preface-style introduction, model chapters, formula chapters, experiment chapters, a figure index, result interpretation, and statements of boundary. The goal is to let a reader build a clear conceptual thread even before opening the source code.

Because the project also carries a strong author-side intuition about how propagation should be pictured, that intuition is documented separately in [MODEL_INTUITION.md](D:/workspace/golang/nakama/chain-explosion-model/MODEL_INTUITION.md). The separation is deliberate: the intuition note preserves the visual and conceptual picture, while this monograph stays focused on implementation structure, experiments, and interpretive limits.

---

## Chapter 1. Project Positioning
## 第一章 项目定位

这个项目首先是一个研究工程，其次才是一个模拟仓库。它通过代码去表达一种核心判断：某些看上去需要复杂量子叙事的现象，是否能够在显式的局域、离散、因果传播框架中获得数值上的重建、近似或替代表述。  
This project is first a research engineering effort and only secondarily a simulation repository. Through code, it expresses a core question: whether some phenomena that seem to require a complex quantum narrative can instead be numerically reconstructed, approximated, or reformulated within an explicit local, discrete, and causal propagation framework.

与普通的教学演示不同，这个仓库并不满足于“做出几张像样的图”。它进一步要求实验有明确参数、有可重复执行路径、有结构化产物、有门槛判断，并最终能够留下归档。因此它更像一个研究计划的代码化实现。  
Unlike ordinary educational demos, this repository is not satisfied with merely producing a few plausible plots. It further requires clear parameters, reproducible execution paths, structured artifacts, threshold-based judgments, and durable archives. For that reason, it is better seen as the coded implementation of a research program.

这个定位决定了文档结构必须重新排序。主线不应该是几十个脚本逐个平铺，而应该是“模型原理 -> 现象实验 -> CHSH 协议问题 -> 两次严肃实验 -> 解释边界”。本总文档就是依照这条主线来重写的。  
This positioning determines that the documentation must be reordered. The main line should not be a flat list of dozens of scripts, but rather “model principles -> phenomenon experiments -> CHSH protocol questions -> two serious experiments -> interpretive boundaries.” This monograph is rewritten according to precisely that line.

---

## Chapter 2. Architecture of the Codebase
## 第二章 代码架构

仓库的核心代码可分为四个层次：传播内核、实验引擎、实验脚本、归档与审计工具。理解这个分层非常重要，因为它决定了每一个文件在研究链中的地位。  
The core code of the repository can be divided into four layers: propagation kernels, experimental engines, experiment scripts, and archival/audit tooling. Understanding this hierarchy is crucial because it determines the role each file plays in the research chain.

第一层是传播内核，主要由 `chain_explosion_numba.py` 组成。这里实现了最关键的离散邻域传播规则，包括双缝传播、吸收掩膜传播、分支传播和带相位的版本。这一层的特点是高频、局部、偏数值内核。  
The first layer is the propagation kernel, mainly implemented in `chain_explosion_numba.py`. It contains the key discrete neighborhood update rules, including double-slit propagation, absorber-mask propagation, split propagation, and phase-carrying variants. This layer is high-frequency, local, and numerically kernel-oriented.

第二层是实验引擎，代表文件是 `ce_engine_v2.py` 和 `ce_engine_v3_coherent.py`。这一层在内核之上增加了更完整的实验逻辑，例如多步传播、相位演化、随机路径、统计提取和更复杂的对比分析。  
The second layer is the experimental engine, represented by `ce_engine_v2.py` and `ce_engine_v3_coherent.py`. This layer builds on top of the kernels with fuller experimental logic such as multi-step propagation, phase evolution, random paths, statistical extraction, and more complex comparative analysis.

第三层是实验脚本，包括 `ce_*`、`verify_*`、`discover_*`、`explore_*` 和 `explore_critique_*` 系列。它们把模型放进不同问题中测试：从双缝可见度，到吸收式测量，再到 Bell/CHSH 和协议敏感性。  
The third layer consists of experiment scripts, including the `ce_*`, `verify_*`, `discover_*`, `explore_*`, and `explore_critique_*` series. These scripts place the model into different problem settings: from double-slit visibility to absorption-style measurement, and then to Bell/CHSH and protocol sensitivity.

第四层是归档与审计工具，主要包括 `run_unified_suite.py`、`suite_artifacts.py` 和 `experiment_dossier.py`。这一层的价值在于，它把单次运行从“临时输出”提升为“可归档研究工件”。  
The fourth layer is the archival and audit tooling, mainly including `run_unified_suite.py`, `suite_artifacts.py`, and `experiment_dossier.py`. The value of this layer is that it upgrades a single run from a “temporary output” into an “archivable research artifact.”

---

## Chapter 3. The Core Model
## 第三章 核心模型

这套模型的基本对象不是标准量子振幅，而是二维格点上的场量，仓库多数位置将其解释为“能量”或“强度”。在最基础版本中，传播过程可以理解为每个格点把自身权重分发给周围若干格点，同时乘以衰减因子。  
The basic object of the model is not a standard quantum amplitude but a field quantity on a two-dimensional lattice, interpreted in most places in the repository as “energy” or “intensity.” In the most basic version, propagation can be understood as each lattice site distributing its weight to neighboring sites while being multiplied by a damping factor.

设 \(E_t(x,y)\) 表示时刻 \(t\) 的格点场量，\(A\)、\(B\)、\(S\) 分别表示主传播方向、反向传播方向和侧向传播方向的权重，\(\lambda\) 表示一步传播的衰减因子。那么一个典型更新可写为：  
Let \(E_t(x,y)\) denote the lattice field at time \(t\), let \(A\), \(B\), and \(S\) denote the weights of forward, backward, and lateral propagation, and let \(\lambda\) denote the one-step damping factor. Then a typical update can be written as:

\[
E_{t+1}(x,y)
=
\lambda\Big(
A E_t(x-1,y)
 B E_t(x+1,y)
 S E_t(x,y-1)
 S E_t(x,y+1)
 \frac{S}{2}E_t(x-1,y-1)
 \frac{S}{2}E_t(x-1,y+1)
 \frac{S}{2}E_t(x+1,y-1)
 \frac{S}{2}E_t(x+1,y+1)
\Big).
\]

这并不是对代码逐行的字面转写，而是对其核心传播思想的数学抽象。真正的代码还叠加了障碍矩阵、吸收矩阵、有限区域探测器和分支传播等条件。  
This is not a literal line-by-line transcription of the code, but a mathematical abstraction of its core propagation idea. The actual code further overlays barrier matrices, absorber masks, finite-region detectors, and split-propagation conditions.

双缝结构通过布尔障碍矩阵 `barrier` 实现。整列挡板通常先被置为阻挡，再在两条缝的位置打开窗口，使传播仅能穿过指定几何区域。这意味着双缝图样并不是额外绘制出来的，而是从更新规则和几何约束中涌现出来的。  
The double-slit structure is implemented through a boolean barrier matrix `barrier`. A full barrier column is usually initialized as blocked, and then two slit regions are reopened as windows so that propagation may pass only through designated geometric regions. This means the double-slit pattern is not manually drawn afterward, but emerges from the update rule plus geometric constraints.

---

## Chapter 4. Measurement as Local Intervention
## 第四章 测量作为局域介入

仓库在概念上最鲜明的选择之一，是尽量把“测量”还原为传播链中的局域过程，而不是直接把它设为非局域坍缩。具体实现上，测量可以表现为缝后吸收、有限区域损耗、阈值探测或事件保留规则。  
One of the most distinctive conceptual choices in the repository is to reduce “measurement,” as much as possible, to a local process within the propagation chain rather than treating it immediately as nonlocal collapse. In implementation, measurement may appear as post-slit absorption, finite-region loss, threshold detection, or event-retention rules.

如果用 \(\eta(x,y)\) 表示某个位置的吸收比例，那么一个简单的局域吸收过程可写成：  
If \(\eta(x,y)\) denotes the absorption ratio at a given position, then a simple local absorption process can be written as:

\[
\tilde{E}_t(x,y)=\big(1-\eta(x,y)\big)E_t(x,y).
\]

随后，\(\tilde{E}_t(x,y)\) 再被送入下一步传播。这样一来，“测量”不再是一个只能在解释层被调用的术语，而变成了代码中的显式机制，可以被强弱扫描、位置扫描和尺寸扫描。  
After that, \(\tilde{E}_t(x,y)\) is passed into the next propagation step. In this way, “measurement” is no longer a term invoked only at the interpretive level, but becomes an explicit coded mechanism that can be scanned by strength, position, and size.

正因为测量在这里被机制化，仓库才能进一步讨论连续变化、延迟插入、有限尺寸吸收器与图样退相干之间的关系。这也是 `ce_04_*` 到 `ce_07_*` 以及部分 `discover_*` 脚本的理论起点。  
Because measurement is mechanized in this way, the repository can further discuss the relationship between continuous change, delayed insertion, finite-size absorbers, and pattern decoherence. This is the theoretical starting point of `ce_04_*` through `ce_07_*` and part of the `discover_*` scripts.

---

## Chapter 5. Phase, Coherence, and Visibility
## 第五章 相位、相干与可见度

在更高层的脚本中，仓库不只传播能量，还会传播相位。若把复幅记为 \(\psi_t(x,y)=\sqrt{E_t(x,y)}e^{i\phi_t(x,y)}\)，那么不同路径到达同一格点时可发生复数叠加，而新的能量则可由模平方得到。  
In higher-level scripts, the repository propagates not only energy but also phase. If the complex amplitude is written as \(\psi_t(x,y)=\sqrt{E_t(x,y)}e^{i\phi_t(x,y)}\), then different paths arriving at the same lattice site may interfere through complex superposition, and the new energy may be obtained from the squared magnitude.

\[
E_{t+1}(x,y)=|\psi_{t+1}(x,y)|^2.
\]

这一步使得仓库可以讨论“相位关联是否保留”“相位场如何与强度场共同演化”等问题。不过文档上必须明确，这仍然是一个模型定义出来的相位传播机制，而不是对标准量子相位结构的完整严格导出。  
This step allows the repository to discuss questions such as whether phase correlation is preserved and how a phase field evolves together with an intensity field. However, the documentation must be explicit that this is still a model-defined phase propagation mechanism, not a complete rigorous derivation of the standard quantum phase structure.

双缝图样中最重要的量之一是可见度，仓库中常用的表达是：  
One of the most important quantities in double-slit patterns is the visibility, and the repository often uses the expression:

\[
V=\frac{I_{\max}-I_{\min}}{I_{\max}+I_{\min}}.
\]

这里的 \(I_{\max}\) 与 \(I_{\min}\) 通常从屏幕强度曲线的峰与谷估计得到。这个定义本身很经典，但在仓库中的意义并不只是描述条纹，而是作为一个跨脚本共享指标，用来连接距离、耦合、吸收与协议变化。  
Here, \(I_{\max}\) and \(I_{\min}\) are usually estimated from peaks and valleys in the screen-intensity curve. The definition itself is classical, but its role in the repository is broader than fringe description: it functions as a shared cross-script metric connecting distance, coupling, absorption, and protocol variation.

---

## Chapter 6. Foundational Experiment Tree
## 第六章 基础实验树

如果把整个仓库画成一棵树，那么基础实验是树干，而两次严肃实验是长出来的两条主枝。基础实验首先建立传播直觉，然后把“测量”和“相关性”逐步机制化，最后才进入 CHSH 层。  
If the entire repository is drawn as a tree, then the foundational experiments form the trunk, while the two major experiments are the two main branches growing from it. The foundational experiments first establish propagation intuition, then progressively mechanize “measurement” and “correlation,” and only afterward move into the CHSH layer.

`ce_00_double_slit_demo.py` 是最基础的双缝示意脚本。它采用的典型参数包括 `WIDTH = 300`、`HEIGHT = 200`、`A = 1.0`、`S = 0.25`、`B = 0.05`、`LAMBDA = 0.85`、`SLIT_WIDTH = 6` 和 `STEPS = 300`。这类参数体现出该模型的基本性格：前向传播占主导，侧向耦合提供扩散与干涉几何，反向项较小而非完全为零。  
`ce_00_double_slit_demo.py` is the most basic double-slit illustration script. Its typical parameters include `WIDTH = 300`, `HEIGHT = 200`, `A = 1.0`, `S = 0.25`, `B = 0.05`, `LAMBDA = 0.85`, `SLIT_WIDTH = 6`, and `STEPS = 300`. These parameters already express the basic temperament of the model: forward propagation dominates, lateral coupling provides diffusion and interference geometry, and the backward term is small rather than strictly zero.

`ce_01_visibility_vs_screen_distance.py` 进一步研究可见度与传播距离的关系。该脚本使用 `A = 1.0`、`S = 0.3`、`B = 0.05`、`LAMBDA = 0.90`、`STEPS = 400` 以及一组 `SCREEN_DISTANCES`。这条实验线在仓库中很重要，因为“可见度随传播距离衰减”是模型试图强调的可检验特征之一。  
`ce_01_visibility_vs_screen_distance.py` goes further by studying the relation between visibility and propagation distance. It uses `A = 1.0`, `S = 0.3`, `B = 0.05`, `LAMBDA = 0.90`, `STEPS = 400`, and a set of `SCREEN_DISTANCES`. This experimental line is important because “visibility decays with propagation distance” is one of the model’s intended testable signatures.

`ce_04_*` 到 `ce_07_*` 把测量效应推进成一个可扫描对象，而 `ce_08_*` 到 `ce_10_*` 则把支路传播、相位和相关性带入模型。这意味着 CHSH 层不是突然出现的，而是从一系列较低层实验上长出来的。  
`ce_04_*` through `ce_07_*` promote measurement effects into something that can be scanned parametrically, while `ce_08_*` through `ce_10_*` bring branch propagation, phase, and correlation into the model. This means the CHSH layer does not appear abruptly, but grows out of a sequence of lower-level experiments.

---

## Chapter 7. CHSH Protocol Logic
## 第七章 CHSH 协议逻辑

进入 Bell / CHSH 问题后，仓库关注的重点不再只是图样，而是“事件如何配对”和“什么样的事件进入统计”。这一步非常关键，因为仓库的核心判断之一就是：协议本身会改变结果，而协议与本体结论不能被轻易混同。  
Once the repository enters the Bell / CHSH problem, the focus shifts from patterns to how events are paired and which events are allowed into the statistics. This step is crucial, because one of the central claims of the repository is that protocol itself changes the result, and protocol should not be casually conflated with ontological conclusion.

在 `explore_chsh_experiment_alignment.py` 中，最小事件格式是 `side, t, setting, outcome`。其中 `side` 区分 A/B 两翼，`setting` 取值为 0 或 1，`outcome` 规范到 \(\pm 1\)。  
In `explore_chsh_experiment_alignment.py`, the minimal event format is `side, t, setting, outcome`. Here `side` distinguishes the A/B wings, `setting` takes values 0 or 1, and `outcome` is normalized to \(\pm 1\).

配对逻辑是这样的：若 A 侧事件时间为 \(t_A\)，B 侧事件时间为 \(t_B\)，且满足 \(|t_A-t_B|\le w\)，则在窗口 \(w\) 内选择最近、未被占用的 B 事件与之配对。这样得到的 paired 样本集合随后被用于计算四种设置组合上的相关量。  
The pairing logic is as follows: if the time of an A-side event is \(t_A\), the time of a B-side event is \(t_B\), and \(|t_A-t_B|\le w\), then within the window \(w\) the nearest unused B event is paired with it. The resulting paired sample set is then used to compute the correlations on the four setting combinations.

相关量的标准表达式为：  
The standard expression for the correlations is:

\[
E=\frac{N_{++}+N_{--}-N_{+-}-N_{-+}}{N_{\mathrm{total}}}.
\]

CHSH 组合量则写成：  
The CHSH combination is then written as:

\[
S=E(a,b)+E(a,b')+E(a',b)-E(a',b').
\]

仓库中的 `strict` 与 `standard` 并不修改这个公式，而是修改进入公式的配对窗口，也就修改了 paired 样本集。这种“改协议而不改公式”的做法，正是仓库 CHSH 研究线最核心的工程思想。  
The repository’s `strict` and `standard` protocols do not modify this formula; they modify the pairing window that determines which samples enter the formula. This “changing the protocol without changing the formula” is the central engineering idea of the repository’s CHSH research line.

---

## Chapter 8. Major Experiment I: NIST Completeblind Archive
## 第八章 重大实验一：NIST Completeblind 归档战

第一次严肃实验位于 `battle_results/nist_completeblind_2015-09-19/`。这不是仓库内部自生成数据上的演示，而是针对公开 completeblind 数据建立的一条完整归档链。它的重要性在于，它第一次把仓库的 CHSH 论证推向了外部数据问题。  
The first major experiment is located at `battle_results/nist_completeblind_2015-09-19/`. This is not an internal demonstration on self-generated data, but a full archival chain built against public completeblind data. Its importance lies in the fact that it is the first time the repository’s CHSH reasoning is pushed toward an external-data problem.

第一次实验的预注册配置由 `chsh_preregistered_config_nist_index.json` 给出。关键门槛包括 `strict.window = 0.0`、`standard.window = 15.0`、`strict_max_S = 2.02`、`standard_min_S = 2.0` 和 `require_standard_S_gt_strict_S = true`。这意味着此轮实验并不满足于看到 `S > 2`，而是要求严格协议下的 \(S\) 仍被压在上界附近。  
The preregistered configuration for the first experiment is given by `chsh_preregistered_config_nist_index.json`. The key thresholds include `strict.window = 0.0`, `standard.window = 15.0`, `strict_max_S = 2.02`, `standard_min_S = 2.0`, and `require_standard_S_gt_strict_S = true`. This means the experiment is not satisfied merely by seeing `S > 2`; it also requires the strict-protocol value of \(S\) to remain pressed near the upper bound.

根据归档结果文件 `battle_result.json`，strict 协议下的结果为：`pair_count = 136632`，`Eab = 0.9989774338237003`，`Eabp = 0.9980977239045323`，`Eapb = 0.9979612207190944`，`Eapbp = 0.65876052027544`，以及 `S = 2.336275858171887`。  
According to the archival result file `battle_result.json`, the strict-protocol result is: `pair_count = 136632`, `Eab = 0.9989774338237003`, `Eabp = 0.9980977239045323`, `Eapb = 0.9979612207190944`, `Eapbp = 0.65876052027544`, and `S = 2.336275858171887`.

standard 协议下的结果为：`pair_count = 148670`，`Eab = 0.9918413278942186`，`Eabp = 0.9703577587147753`，`Eapb = 0.9473404037508701`，`Eapbp = 0.07015227532787607`，以及 `S = 2.8393872150319877`。  
Under the standard protocol, the result is: `pair_count = 148670`, `Eab = 0.9918413278942186`, `Eabp = 0.9703577587147753`, `Eapb = 0.9473404037508701`, `Eapbp = 0.07015227532787607`, and `S = 2.8393872150319877`.

这次实验的仓库级判定是 `engineering_pass = true`，但 `thesis_pass = false`。失败原因非常明确：  
The repository-level judgment for this experiment is `engineering_pass = true`, but `thesis_pass = false`. The reason for failure is very explicit:

\[
S_{\mathrm{strict}}=2.336276 > 2.02.
\]

这一点非常重要，因为它说明第一次严肃实验最有价值的地方，不是“它胜利了”，而是“它把失败结论也归档了”。从研究方法论角度看，这比单纯展示成功图像更有分量。  
This is very important, because it shows that the greatest value of the first serious experiment is not that “it won,” but that it archived a failed conclusion as well. From the standpoint of research methodology, this carries more weight than merely displaying successful images.

---

## Chapter 9. Major Experiment II: Round 2 / NIST v2 Closure
## 第九章 重大实验二：Round 2 / NIST v2 收束实验

第二次严肃实验位于 `battle_results/nist_round2_v2/`。它的意义不只是再跑一遍数值，而是在第一轮基础上把布局兼容性、工程映射敏感性和解释边界问题集中处理掉，因此更接近一份正式的研究收束文档。  
The second major experiment is located at `battle_results/nist_round2_v2/`. Its meaning is not merely to rerun the numbers, but to concentrate on layout compatibility, engineering-mapping sensitivity, and interpretive boundaries on top of the first round, making it closer to a formal research-closure document.

P3 布局检查给出了一个关键事实：training HDF5 与 completeblind HDF5 并不共享同一套可直接复用的 grid-side-streams 结构。`p3_compare_report.json` 表明 training 数据 `grid_side_streams_compatible = false`，而 completeblind 数据 `grid_side_streams_compatible = true`。这一步阻止了未经审计的横向类比。  
The P3 layout check yields a key fact: the training HDF5 and completeblind HDF5 do not share a directly reusable grid-side-streams structure. `p3_compare_report.json` shows that the training data have `grid_side_streams_compatible = false`, while the completeblind data have `grid_side_streams_compatible = true`. This step prevents unaudited horizontal analogy.

第二轮 engineering 配置由 `chsh_preregistered_config_nist_round2_engineering.json` 定义。关键区别在于：`strict.window = 0.0`，`standard.window = 10.0`，并且 thesis gate 使用 `fork_only` 模式，只要求 `S_standard > S_strict`，而不再沿用第一轮的 `strict_max_S = 2.02` 约束。  
The second-round engineering configuration is defined in `chsh_preregistered_config_nist_round2_engineering.json`. The key differences are that `strict.window = 0.0`, `standard.window = 10.0`, and the thesis gate uses `fork_only` mode, requiring only `S_standard > S_strict` rather than reusing the first-round constraint `strict_max_S = 2.02`.

第二轮显式比较了两种输出映射：`legacy` 与 `parity`。在 `ROUND2_ENGINEERING_BATTLE_REPORT.json` 中，legacy 映射给出 `S_strict = 2.336275858171887` 和 `S_standard = 2.8445681666863845`；parity 映射给出 `S_strict = 2.3274283887643272` 和 `S_standard = 2.83617087618962`。  
The second round explicitly compares two output mappings: `legacy` and `parity`. In `ROUND2_ENGINEERING_BATTLE_REPORT.json`, the legacy mapping yields `S_strict = 2.336275858171887` and `S_standard = 2.8445681666863845`; the parity mapping yields `S_strict = 2.3274283887643272` and `S_standard = 2.83617087618962`.

这两种映射之间的差异是有限而稳定的，数值上表现为 `delta_S_strict = -0.00884746940755976` 与 `delta_S_standard = -0.008397290496764409`。这说明工程映射会改变结果，但在第二轮锁定框架下，方向性分叉结论并没有被推翻。  
The difference between the two mappings is finite and stable, numerically expressed as `delta_S_strict = -0.00884746940755976` and `delta_S_standard = -0.008397290496764409`. This shows that engineering mapping does change the result, but under the locked second-round framework the directional fork conclusion is not overturned.

更关键的是，第二轮还把同一数据重新放回第一轮 thesis gate 下回放。结果见 `ROUND2_UNDER_ROUND1_GATE.json`，其中 legacy 与 parity 都仍然是 `thesis_pass = false`，因为 strict 侧的 \(S\) 依旧高于 2.02。这样一来，第二轮并没有“篡改第一轮失败结论”，而是在新的叙事框架下额外增加了一层 engineering closure。  
More importantly, the second round also replays the same data under the first-round thesis gate. The result, shown in `ROUND2_UNDER_ROUND1_GATE.json`, is that both legacy and parity still have `thesis_pass = false`, because the strict-side \(S\) remains above 2.02. In this way, the second round does not “rewrite away” the first-round failure, but adds an additional engineering closure under a new narrative frame.

---

## Chapter 10. Figure and Artifact Index
## 第十章 图示与产物索引

这个项目的图示已经存在于仓库中，新的文档工作不是重新生成它们，而是把它们重新编排进一条更清晰的阅读路径。基础实验层的重要图包括：`ce_00_double_slit_demo.png`、`interference_decay.png`、`measurement_effect.png`、`finite_absorber.png`、`delayed_choice.png`、`measurement_phase_diagram.png`、`entanglement_simulation.png` 和 `entanglement_with_phase.png`。  
The figures for this project already exist in the repository, and the task of the new documentation is not to regenerate them, but to reassemble them into a clearer reading path. Important figures from the foundational experiment layer include `ce_00_double_slit_demo.png`, `interference_decay.png`, `measurement_effect.png`, `finite_absorber.png`, `delayed_choice.png`, `measurement_phase_diagram.png`, `entanglement_simulation.png`, and `entanglement_with_phase.png`.

Bell / CHSH 层的重要图包括：`chsh_strict_protocol.png`、`chsh_strict_vs_postselected.png`、`chsh_closure_protocol.png`、`chsh_local_wave_closure_full.png`、`chsh_experiment_alignment.png`、`threshold_detector_clicks.png` 和 `bell_chsh_two_tracks.png`。这些图像共同构成了协议敏感性、审计与结果对齐的视觉证据。  
Important figures from the Bell / CHSH layer include `chsh_strict_protocol.png`, `chsh_strict_vs_postselected.png`, `chsh_closure_protocol.png`, `chsh_local_wave_closure_full.png`, `chsh_experiment_alignment.png`, `threshold_detector_clicks.png`, and `bell_chsh_two_tracks.png`. Together, these images form the visual evidence for protocol sensitivity, auditing, and result alignment.

归档层的重要 JSON 产物包括：第一次实验的 `battle_result.json`，第二次实验的 `ROUND2_ENGINEERING_BATTLE_REPORT.json`、`ROUND2_UNDER_ROUND1_GATE.json` 和 `p3_compare_report.json`。这些文件是真正的“硬结果”，因为阈值判断和结论锁定都最终落在这里。  
Important JSON artifacts from the archival layer include the first experiment’s `battle_result.json`, and the second experiment’s `ROUND2_ENGINEERING_BATTLE_REPORT.json`, `ROUND2_UNDER_ROUND1_GATE.json`, and `p3_compare_report.json`. These files are the true “hard results,” because the threshold judgments and conclusion locks ultimately live there.

---

## Chapter 11. Interpretive Boundaries
## 第十一章 解释边界

这个项目的一大优点，是它并不把所有数值现象都自动上升为本体结论。仓库中的 `explore_critique_*` 系列、`BELL_PROTOCOL_NOTE.md` 以及第二轮收束文档，都在不断提醒：现象、协议、解释，是三个不同层次。  
One of the major strengths of this project is that it does not automatically elevate every numerical phenomenon into an ontological conclusion. The repository’s `explore_critique_*` series, `BELL_PROTOCOL_NOTE.md`, and the second-round closure documents all repeatedly remind us that phenomenon, protocol, and interpretation are three different levels.

基于当前代码和归档，较为安全的说法是：这套离散局域模型能够在若干场景下生成类干涉、类测量扰动和类相关性结构；CHSH 结果对配对窗口、映射和事件保留规则十分敏感；两轮严肃实验已经把“工程通过”和“论点通过”分层写清楚。  
Based on the current code and archives, a relatively safe statement is that this discrete local model can generate interference-like patterns, measurement-like disturbances, and correlation-like structures in several scenarios; CHSH results are highly sensitive to pairing windows, mappings, and event-retention rules; and the two major experiments have already separated “engineering passed” from “thesis passed” in explicit form.

相应地，当前仓库并不能直接支持如下说法：它已经推翻标准量子理论，它已经从格点模型严格推出狭义相对论，或者它已经凭借内部数值结果证明了某种一般哲学意义上的非局域或局域本体结论。  
Correspondingly, the current repository cannot directly support statements such as: it has overthrown standard quantum theory, it has rigorously derived special relativity from a lattice model, or it has proven some general philosophical conclusion about locality or nonlocality purely from its internal numerical results.

从学术写作的角度看，真正使项目显得成熟的，不是措辞激进，而是边界清楚。这个仓库最值得珍惜的地方之一，就是它已经开始主动写出这些边界。  
From the standpoint of scholarly writing, what makes a project look mature is not aggressive rhetoric, but clear boundaries. One of the most valuable aspects of this repository is that it has already begun to write those boundaries explicitly.

---

## Chapter 12. Optimization Proposal
## 第十二章 优化方案

为了让这个项目通过文档更充分地体现价值，我建议将文档系统固定为三层。第一层是入口层，即当前的 `README.md`，它负责用尽量短的篇幅告诉读者“这个项目是什么、重点在哪里、该先读什么”。  
To let the value of this project emerge more fully through documentation, I recommend fixing the documentation system into three layers. The first layer is the entry layer, namely the current `README.md`, whose role is to tell the reader in as little space as possible what the project is, where the center lies, and what should be read first.

第二层是总文档层，即本文件。它应长期保持“像一本书”的结构，稳定承担模型原理、数学表达、实验主线、结果表与解释边界的功能，并成为引用时的主要文档入口。  
The second layer is the monograph layer, namely this file. It should permanently keep a book-like structure, stably carrying the roles of model principles, mathematical expressions, the main experimental line, result tables, and interpretive boundaries, and serve as the primary document entry for citation.

第三层是 battle 子目录中的实验归档层。后续最值得继续优化的，不是增加更多零散脚本，而是把 `battle_results` 下的关键文档统一改写成 UTF-8、双语、结构化表述，让两轮严肃实验真正具备“可对外提交”的质感。  
The third layer is the experimental archival layer inside the `battle_results` subdirectories. The most worthwhile future optimization is not to add more scattered scripts, but to rewrite the key documents under `battle_results` into UTF-8, bilingual, and structurally organized form, so that the two major experiments truly acquire the quality of something ready for external presentation.

同时，建议额外增加一个“图表总索引”文档，把核心 PNG、JSON、配置文件和结论对应起来。这样做会极大增强可检索性，也有利于后续转成 PDF、投递说明或项目展示。  
At the same time, I recommend adding a separate “master figure and artifact index” document that links core PNGs, JSON files, configuration files, and conclusions. This would greatly improve retrievability and would also help with later conversion to PDF, submission packets, or project presentation.

---

## Conclusion
## 结语

如果把这个仓库看作一本书，那么它不是一本宣布最终答案的书，而是一本展示如何把一种替代性机制认真推进到“可运行、可审计、可归档、也可失败”的书。它真正的分量，不在口号，而在工件。  
If this repository is read as a book, then it is not a book announcing a final answer, but a book showing how an alternative mechanism can be seriously advanced to the point of being executable, auditable, archivable, and also capable of failing. Its real weight lies not in slogans, but in artifacts.

在这个意义上，本次文档优化的目标并不是替项目夸张结论，而是帮助项目把真正有价值的东西显露出来：模型逻辑、实验路径、数值结果、边界意识，以及两次严肃实验留下的研究痕迹。  
In that sense, the goal of this documentation optimization is not to exaggerate the project’s conclusions, but to reveal what is genuinely valuable in it: the model logic, the experimental path, the numerical results, the awareness of limits, and the research trace left behind by the two major experiments.
