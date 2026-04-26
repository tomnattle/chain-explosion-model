# Ripple Quantum Tests — Documentation Index
# 涟漪量子测试 — 文档树索引

本页是仓库内 **四条涟漪量子玩具基准**（激光阈值、半导体截止、MRI 拉莫尔、原子钟谱线）的**唯一导航入口**，避免脚本与 `artifacts/` 碎片化。

This page is the **single navigation hub** for the four **toy ripple-vs-QM-like curve benchmarks** (laser threshold, semiconductor absorption edge, MRI Larmor linearity, atomic-clock line shape), so scripts and `artifacts/` are not orphaned.

---

## 1. 四条子实验（逻辑名 → 内容）

| 逻辑名 `name` | 物理意图（玩具层） | 参考轴（概念） |
|---------------|-------------------|----------------|
| `laser_threshold` | 阈值下弱响应、阈值上陡增 | 泵浦/激励强度 |
| `semiconductor_cutoff` | 吸收边陡变 | 归一化频率 |
| `mri_larmor` | 旋磁比线性 \(\omega \propto B\) | 磁场 \(B\)（T） |
| `atomic_clock_modes` | 超精细线附近高斯谱形 | 频率（GHz） |

**边界 / Boundary:** 参考曲线为 **手写解析 QM-like**，不是公开实验 CSV；结论层级为 **形状/门禁/联合一致性**，不是「已证标准量子力学错误或替代」。

---

## 2. 代码版本树（v1 → v6）

| 版本 | 脚本 | 要点 |
|------|------|------|
| v1 | `ripple_quantum_tests.py` | NRMSE 阈值；默认 `artifacts/ripple_quantum_tests/` |
| v2 | `ripple_quantum_tests_v2.py` | `shape_pass` ∧ `constant_pass` |
| v3 | `ripple_quantum_tests_v3.py` | `derived` / `calibrated`；反作弊：`calibrated` 需 `--allow-calibrated` |
| v4 | `ripple_quantum_tests_v4_plot_optimize.py` | 作图 + `scipy` 差分进化；`artifacts/ripple_quantum_tests_v4/` |
| v5 | `ripple_quantum_tests_v5_rigorous.py` | `nrmse_x` / `nrmse_y` / `R²`；MRI 代数 κ；原子钟 \(v=c\) + 代数 \(L\)；可选 `--semi-tanh` |
| v6 | `ripple_quantum_tests_v6_joint.py` | 联合 \((\mu,\rho,\eta,bw)\)；`--stress` / `--stress-refine`；`--wave-speed derived` + `ripple_medium_dispersion.py` |

任务目录说明（中文细节）：[`scripts/explore/ripple_quantum_tests/README.zh.md`](../scripts/explore/ripple_quantum_tests/README.zh.md)

---

## 3. 归档产物（提交/引用建议）

| 目录 | 内容 |
|------|------|
| `artifacts/ripple_quantum_tests_v4/` | v4 JSON/MD/图；**`PEER_REVIEW_BRIEF.zh.md`**（外部审阅简报） |
| `artifacts/ripple_quantum_tests_v5/` | v5 默认严谨运行 |
| `artifacts/ripple_quantum_tests_v5_tanh/` | 半导体异族（tanh）压力示例 |
| `artifacts/ripple_quantum_tests_v6/` | v6 联合默认（`joint_pass`） |
| `artifacts/ripple_quantum_tests_v6_derived_alpha0/` | `derived` 相速 + `atomic_rho_exponent=0` 可过线示例 |

历史基线仍保留：`artifacts/ripple_quantum_tests/`、`ripple_quantum_tests_v2/`、`v3_*` 等。

---

## 4. 依赖

- `numpy`, `matplotlib`；v4+ 需 **`scipy`**（见根目录 `requirements.txt`）。

---

## 5. 与主文档的关系

- **总论**：与本索引交叉引用见 [`PROJECT_TECHNICAL_MONOGRAPH.md`](PROJECT_TECHNICAL_MONOGRAPH.md) **第六章** 内「涟漪量子测试」小节。  
- **研究地图**：[`RESEARCH_MAP.md`](RESEARCH_MAP.md) 中「可复现输出」与探索分支。  
- **入口 README**：[`README.md`](../README.md) Quick Start / 阅读路径。

---

## 6. 一键命令（仓库根目录）

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v5_rigorous.py --maxiter 120 --seed 42
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --maxiter 200 --seed 7
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --wave-speed derived --atomic-rho-exponent 0 --maxiter 220 --seed 7
```

更多参数见 `README.zh.md` 与各脚本 `--help`。
