# Chain explosion model simulations / 链式爆炸模型数值实验

**Repository / 仓库主页：** [https://github.com/tomnattle/chain-explosion-model](https://github.com/tomnattle/chain-explosion-model)

```bash
git clone https://github.com/tomnattle/chain-explosion-model.git
cd chain-explosion-model
```

---

**English:** This repository contains Python scripts that simulate a discrete “chain explosion” propagation model on a 2D grid, applied to double-slit interference, measurement-like absorption, delayed-choice setups, and entangled wave-packet scenarios. Scripts generate figures (PNG) for analysis.

**中文：** 本仓库用 Python 在二维格点上实现「链式爆炸」式能量传播，用于双缝干涉、类测量的吸收、延迟选择设置以及分裂波包（纠缠）等场景；各脚本可生成用于分析的 PNG 图像。

---

## Scripts / 脚本

| File | 中文说明 | English |
|------|----------|---------|
| `ce_00_double_slit_demo.py` | 基础双缝演示：格点传播、挡板与双缝、屏幕能量与条纹图。 | Baseline double-slit demo: grid propagation, barrier, slits, screen profile and fringe plot. |
| `ce_01_visibility_vs_screen_distance.py` | 将屏幕沿传播方向放在不同横向位置，扫描**干涉条纹对比度**随距离的变化；输出 `interference_decay.png`。 | Scan interference **visibility** vs. screen distance along propagation; writes `interference_decay.png`. |
| `ce_02_double_slit_screen_statistics.py` | 单次双缝实验：打印屏幕能量、主峰/谷值与对比度等统计量（默认不写 PNG）。 | Single run with printed screen statistics (peaks, valleys, visibility); no default PNG export. |
| `ce_03_visibility_vs_side_coupling_S.py` | 固定其他参数，扫描侧向耦合强度 **S**，得到对比度 **V** 随 **S** 的变化；输出 `V_vs_S.png`。 | Scan lateral coupling **S** with fixed parameters; visibility **V** vs. **S** → `V_vs_S.png`. |
| `ce_04_measurement_absorption_at_slit.py` | 在上缝后施加吸收（无/部分/完全），对比三种情况下干涉对比度；输出 `measurement_effect.png`。 | Absorption after one slit (none / partial / full); compare visibility → `measurement_effect.png`. |
| `ce_05_finite_absorber_detector.py` | 在缝后以**有限尺寸**圆形区域模拟探测器/吸收体，可调位置、半径、吸收率；输出 `finite_absorber.png`。 | Finite circular absorber behind slits (position, radius, strength) → `finite_absorber.png`. |
| `ce_06_delayed_choice_absorber.py` | 在传播中途某一步插入吸收体（光已过双缝），观察屏幕对比度；输出 `delayed_choice.png`。 | Insert absorber mid-propagation (post-slits); screen visibility → `delayed_choice.png`. |
| `ce_07_measurement_phase_diagram_scan.py` | 扫描探测器**位置**、**尺度**与**吸收率**对对比度的影响；输出 `measurement_phase_diagram.png`。 | Scan detector position, size, and absorption vs. visibility → `measurement_phase_diagram.png`. |
| `ce_08_entanglement_split_wavepackets.py` | 单源分裂为两束波包，远端探测器与（可选）动画；输出 `entanglement_simulation.png`。 | Source splits into two wave packets; remote detectors → `entanglement_simulation.png`. |
| `ce_09_entanglement_with_phase_field.py` | 在能量之外引入相位格点，分析能量衰减与**相位相关性**；输出 `entanglement_with_phase.png`。 | Energy + phase grid; energy decay vs. phase correlation → `entanglement_with_phase.png`. |
| `ce_10_entanglement_distance_scan_numba.py` | 使用 **Numba** 加速，在不同探测器间距下扫描能量与相位相关；输出 `entanglement_scan_numba.png`。 | Numba-accelerated scan over detector separation; → `entanglement_scan_numba.png`. |

> **Note / 说明：** 原仓库中的 `s5.py` 与 `s4.py` 内容完全相同，已删除冗余副本，功能由 `ce_04_measurement_absorption_at_slit.py` 保留。  
> **原文件名对照：** `main.py` → `ce_00_...`，`s1.py`–`s4.py`、`s4.1.py`、`s6.py`–`s10.py` 按上表序号对应（`s5` 已去重）。

---

## Generated figures / 图像文件（示例输出）

| File | 中文说明 | English |
|------|----------|---------|
| `interference_decay.png` | 对比度随屏幕距离衰减的汇总图（由 `ce_01` 生成）。 | Visibility vs. screen distance summary (`ce_01`). |
| `V_vs_S.png` | 干涉对比度对侧向强度 S 的依赖（由 `ce_03` 生成）。 | Visibility vs. lateral coupling S (`ce_03`). |
| `measurement_effect.png` | 缝后吸收对条纹的影响：无/部分/完全吸收对比（`ce_04`）。 | Absorption cases at slit: visibility comparison (`ce_04`). |
| `finite_absorber.png` | 有限大小吸收器/测量区域的单次运行结果（`ce_05`）。 | Single run with finite absorber (`ce_05`). |
| `delayed_choice.png` | 中途插入吸收体后的屏上分布（`ce_06`）。 | Screen pattern after mid-run absorber (`ce_06`). |
| `measurement_phase_diagram.png` | 位置/尺度/吸收率多维扫描的合成图（`ce_07`）。 | Multi-panel scan: position, size, absorption (`ce_07`). |
| `entanglement_simulation.png` | 分裂波包与探测器布局的能量图（`ce_08`）。 | Split wave packets and detectors (`ce_08`). |
| `entanglement_with_phase.png` | 含相位时的能量与相关性可视化（`ce_09`）。 | Energy and phase-correlation view (`ce_09`). |
| `entanglement_scan_numba.png` | 距离扫描下能量与相位相关的曲线（`ce_10`）。 | Distance scan: energy and phase correlation (`ce_10`). |
| `behind_interference.png` | **未**在本仓库当前脚本中被 `savefig` 引用；可能来自其它实验版本或手动导出，供展示用。 | **Not** referenced by current scripts’ `savefig`; may be from another version or manual export. |

---

## Setup / 环境

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python ce_00_double_slit_demo.py
```

`ce_10` 依赖 **Numba**；若仅运行其余脚本，可只安装 `numpy` 与 `matplotlib`。

---

## License / 许可

尚未指定默认许可证；若希望他人可自由复用代码，可在仓库根目录添加 `LICENSE`（例如 MIT）。  
No default license is set; add a `LICENSE` (e.g. MIT) at the repo root if you want to clarify terms for reuse.
