# 第二场战斗工作区（v2，与第一场隔离）

本目录存放 **Round 2** 的配置草案、layout 报告、对照脚本输出。**不得**覆盖 `nist_completeblind_2015-09-19/` 内第一场快照。

## 收束说明（第二场文档告一段落）

- **`ROUND2_CLOSURE_PAPER.md`**：预注册范围内的结果归档、主要数值表、**非声称**边界与读者复核路径（**非** NIST 官方复现声明）。
- **`ROUND2_FINAL_DECLARATION.md`**：仅指向上述收束稿与工件索引，不含扩展物理解读。

## 统一战线 — 从这里开始

1. 阅读 **`ROUND2_KICKOFF.md`**（阶段划分与完成标准）。
2. 在仓库根目录执行 **`python round2_phase0_kickoff.py`**，生成合规日志 + layout 快照。

## 目录约定

| 文件 | 含义 |
|------|------|
| `README.md` | 本说明 |
| `NIST_BUILD_SOURCES.md` | 官方构建参数/软件来源线索 |
| `P4_PROTOCOL_AUDIT_SCOPE.md` | 协议审计战线（P4）与 NIST 复现的结论边界 |
| `p3_compare_report.json` | 运行 `run_nist_round2_compare.py` 后生成的 layout/P3 阻塞说明 |
| `diagnostics_completeblind.json` | completeblind CSV 边际与配对粗统计 |
| `chsh_alignment_completeblind_rerun.json` | 可选：对齐脚本重跑输出 |
| `figure_chsh_alignment_rerun.png` | 可选：重跑图 |
| `ROUND2_KICKOFF.md` | 第二场阶段书（Phase 0–3） |
| `PHASE0_LAST_RUN.txt` | 运行 `round2_phase0_kickoff.py` 后的时间戳摘要 |
| `PHASE0_layouts_snapshot.json` | Phase0 自动写的 layout 快照 |
| `ROUND2_ENGINEERING_BATTLE.md` / `ROUND2_ENGINEERING_BATTLE_REPORT.json` | 第二场工程战说明与汇总（双映射敏感性） |
| `ROUND2_CLOSURE_PAPER.md` | 第二场收束说明（归档摘要 + 解释边界） |
| `ROUND2_FINAL_DECLARATION.md` | 收束指针（指向闭包正文） |

## P3 事实前提（已验证）

当前仓库中的 **training** HDF5（`03_31_*_training*.hdf5`）与 **completeblind** HDF5 **不是同一种网格布局**：

- completeblind：`alice/clicks` 与 `alice/settings` **等长**，可走 `nist_convert_config.json` 的 `nist_hdf5_grid` + `side_streams`。
- training：`clicks` 仅数百点，`settings` 千万级 ⇒ **不能与 completeblind 共用同一网格转换管**；P3 的「同一 v2 管跑两遍」在取得 **training 的专用解码** 或 **另一份同构 HDF5** 之前 **阻塞**。

用 `python nist_hdf5_layout_check.py --hdf5 <path>` 自检任意文件。

## 立即命令

```bash
# Layout 对照（training vs completeblind）
python nist_hdf5_layout_check.py --hdf5 data/03_31_CH_pockel_100kHz.run4.afterTimingfix2_training.dat.compressed.build.hdf5 --hdf5 data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5 --json battle_results/nist_round2_v2/layouts_snapshot.json

# 诊断 + 可选对齐重跑（需已有 completeblind CSV）
python run_nist_round2_compare.py --training-hdf5 data/03_31_CH_pockel_100kHz.run4.afterTimingfix2_training.dat.compressed.build.hdf5 --completeblind-hdf5 data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5 --completeblind-csv data/nist_completeblind_side_streams.csv --out-dir battle_results/nist_round2_v2
```

## v2 预注册模板（未开盲）

仓库根目录：`chsh_preregistered_config_nist_v2_TEMPLATE.json`（`DRAFT_NOT_FOR_BLIND`）。

## NIST 官方文档对齐（映射 + 时间窗分级）

- `NIST_OFFICIAL_MAPPING_AND_WINDOWS_REPORT.md`：人读结论（槽位 one-hot、**非**官方 ±1、窗 A/B/C 分级）。
- `NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json`：机器日志（clicks 校验、HDF5 形状、`window=15` 非官方说明）。
- 生成命令：`python nist_official_compliance_report.py`
