# Chain Explosion Model Simulations / 链式爆炸模型数值实验

**Repository / 仓库：** [github.com/tomnattle/chain-explosion-model](https://github.com/tomnattle/chain-explosion-model)

A local, discrete, causal propagation model for wave-like phenomena, double-slit interference, which-way measurement, delayed choice, and quantum-like entanglement.

一个局域、离散、满足因果律的格点传播模型，用于模拟类波动行为、双缝干涉、路径探测、延迟选择与类量子纠缠现象。

```bash
git clone https://github.com/tomnattle/chain-explosion-model.git
cd chain-explosion-model
```

---

## Core predictions / 核心理论预言

（以下为该格点模型在文档层面的归纳，具体数值以脚本与参数为准。）

- Interference visibility decays with propagation distance (**distinctive testable prediction** in this model).
- Entangled wave packets can maintain **phase correlation** while **energy decays** (e.g. with distance / attenuation).
- **Measurement** is implemented as **local absorption**; the codebase does not assume nonlocal collapse—you compare outcomes to collapse / nonlocal narratives in the literature.

- 干涉条纹对比度**随传播距离衰减**（在本模型中可作为**可对照实验**讨论的重点）。
- 纠缠式波包：**相位关联**与**能量衰减**可在同一模拟中区分考察。
- **测量**在实现上为**局域吸收**；代码不预设非定域坍缩，便于与文献中的「坍缩/非定域」叙述对照。

---

## Overview / 简介

This repository implements a **2D discrete lattice propagation model** (“chain explosion”): energy propagates step-by-step to neighbors with directional coupling, attenuation, and optional phase evolution. Scripts replay a sequence of quantum-optics–style gedanken setups:

- Double-slit interference; visibility vs. distance and vs. lateral coupling **S**
- Which-way–style absorption; finite-size detectors; delayed-choice insertion
- Split wave packets with optional phase fields and distance scans (**all hot loops are Numba JIT** via `chain_explosion_numba.py`)

本仓库在二维离散网格上实现**链式爆炸模型**：能量分步向邻域传播，含方向耦合、衰减与可选相位。脚本对应一系列**量子光学思想实验风格**的数值实验：

- 双缝干涉；对比度随距离、随侧向耦合 **S** 的变化
- 路径信息式吸收；有限探测器；中途插入吸收体（延迟选择）
- 波包分裂 + 相位场 + 距离扫描；**格点传播核心均在 Numba 中 JIT**（见 `chain_explosion_numba.py`）

---

## Scripts / 脚本说明

| File | 中文说明 | English |
|------|----------|---------|
| `ce_00_double_slit_demo.py` | 基础双缝演示；能量场与屏幕条纹。 | Baseline double-slit demo; field and screen pattern. |
| `ce_01_visibility_vs_screen_distance.py` | 多距离屏幕：对比度扫描 → **`interference_decay.png`** | Visibility vs. screen distance → **`interference_decay.png`** |
| `ce_02_double_slit_screen_statistics.py` | 单次运行；屏幕能量、峰谷与对比度等（终端输出为主，默认不写 PNG）。 | Single run; screen statistics (mainly console; no default PNG). |
| `ce_03_visibility_vs_side_coupling_S.py` | 扫描侧向强度 **S** → **`V_vs_S.png`** | Scan lateral **S** → **`V_vs_S.png`** |
| `ce_04_measurement_absorption_at_slit.py` | 缝后无/部分/完全吸收对比 → **`measurement_effect.png`** | None / partial / full absorption → **`measurement_effect.png`** |
| `ce_05_finite_absorber_detector.py` | 有限圆形吸收体 → **`finite_absorber.png`** | Finite circular absorber → **`finite_absorber.png`** |
| `ce_06_delayed_choice_absorber.py` | 传播中途插入吸收体 → **`delayed_choice.png`** | Mid-run absorber → **`delayed_choice.png`** |
| `ce_07_measurement_phase_diagram_scan.py` | 位置/尺度/吸收率扫描 → **`measurement_phase_diagram.png`** | Position / size / absorption scan → **`measurement_phase_diagram.png`** |
| `ce_08_entanglement_split_wavepackets.py` | 分裂波包与探测器 → **`entanglement_simulation.png`** | Split packets & detectors → **`entanglement_simulation.png`** |
| `ce_09_entanglement_with_phase_field.py` | 能量 + 相位 → **`entanglement_with_phase.png`** | Energy + phase field → **`entanglement_with_phase.png`** |
| `ce_10_entanglement_distance_scan.py` | 距离扫描（步内能量归一化）→ **`ce_10_entanglement_scan.png`** | Distance scan (per-step energy renormalization) → **`ce_10_entanglement_scan.png`** |
| `chain_explosion_numba.py` | **共享模块**：双缝 / 缝后吸收 / 吸收掩模 / 分裂与相位传播的 `@jit(nopython=True)` 内核。 | **Shared** `@jit(nopython=True)` kernels for all propagation variants. |

> **Note / 说明：** 旧目录中 `s5.py` 与 `s4.py` 内容相同，已删去冗余；功能由 `ce_04_...` 保留。原 `main.py`、`s1.py`–`s4.py`、`s4.1.py`、`s6.py`–`s10.py` 已统一重命名为上表 `ce_*` 系列。  
> Legacy duplicate `s5.py` was removed (identical to `s4.py`); `main.py` and `s*.py` are renamed into the `ce_*` series above.

---

## Output figures / 输出图像

| File | 中文说明 | English |
|------|----------|---------|
| `interference_decay.png` | `ce_01`：对比度随屏幕距离。 | `ce_01`: visibility vs. distance. |
| `V_vs_S.png` | `ce_03`：对比度随侧向耦合 **S**。 | `ce_03`: visibility vs. **S**. |
| `measurement_effect.png` | `ce_04`：三种吸收情形对比。 | `ce_04`: three absorption cases. |
| `finite_absorber.png` | `ce_05`：有限吸收体单次结果。 | `ce_05`: finite absorber snapshot. |
| `delayed_choice.png` | `ce_06`：延迟选择式插入后的屏分布。 | `ce_06`: screen after delayed insertion. |
| `measurement_phase_diagram.png` | `ce_07`：测量参数多维扫描拼图。 | `ce_07`: multi-panel parameter scan. |
| `entanglement_simulation.png` | `ce_08`：分裂波包能量场。 | `ce_08`: split-packet energy field. |
| `entanglement_with_phase.png` | `ce_09`：相位与相关性。 | `ce_09`: phase & correlation. |
| `ce_10_entanglement_scan.png` | `ce_10`：距离扫描曲线。 | `ce_10`: distance-scan curves. |
| `behind_interference.png` | 当前脚本中**无**对应 `savefig`；或为旧版/手动导出，仅供展示。 | **Not** produced by current `savefig` paths; legacy or manual export for illustration. |

---

## Gallery / 图例（仓库内 PNG）

以下为首屏可浏览的代表性输出（完整列表见上表）。若本地无图，可运行 `python run_all_simulations.py` 重新生成。

Below: a few representative figures from this repo (regenerate via `python run_all_simulations.py` if missing).

**Interference visibility vs. screen distance (`ce_01`)** / 对比度随屏幕距离：

![interference_decay](interference_decay.png)

**Measurement / absorption at slit (`ce_04`)** / 缝后吸收对条纹的影响：

![measurement_effect](measurement_effect.png)

**Measurement parameter scan (`ce_07`)** / 测量参量扫描：

![measurement_phase_diagram](measurement_phase_diagram.png)

**Entanglement-style split packets with phase (`ce_09`)** / 分裂波包与相位场：

![entanglement_with_phase](entanglement_with_phase.png)

---

## Installation / 安装与运行

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
python ce_00_double_slit_demo.py

# 一键重跑全部仿真并检查 PNG（可选）
# python run_all_simulations.py
```

依赖见根目录 **`requirements.txt`**：**`numba` 为必选**（所有 `ce_*` 传播主循环均通过其加速）；另需 `numpy`、`matplotlib`。

---

## Originality / 原创声明

This model and the code in this repository are **independently developed** by the author. Public Git history and timestamps may serve as one form of documentation of priority; formal scientific priority follows journal and community norms.

本模型与本仓库代码为作者**独立实现**。公开提交历史与时间戳可作为优先权的辅助记录；正式学术优先权仍遵循期刊与学界惯例。

---

## License / 许可

Code is released under the **MIT License** — see [`LICENSE`](LICENSE) for the full text. You must **keep the copyright and permission notice** in substantial portions of the Software (standard MIT condition).

学术或技术报告中若使用本仓库的思想、图像或结论，**建议**引用并注明仓库链接，以利于可重复性与致谢（MIT 本身不强制论文引用格式）。

The Software is provided “as is”, without warranty of any kind.
