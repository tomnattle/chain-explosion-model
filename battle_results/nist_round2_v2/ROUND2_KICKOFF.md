# 第二场统一战线 — 启动书（Round 2 Kickoff）

**原则**：第一场归档不动；本场所有新结论走 `nist_round2_v2/` + **新版本预注册**；**协议审计（P4）** 与 **NIST 复现** **结论句分开**。

---

## Phase 0 — 进门三件套（每次开战先跑）

```bash
python round2_phase0_kickoff.py
```

产出：

- `NIST_OFFICIAL_ALIGNMENT_RUN_LOG.json`（槽位 one-hot 批量校验、窗分级说明的数字底座）
- `PHASE0_layouts_snapshot.json`（training vs completeblind 是否可共用网格管）
- `PHASE0_LAST_RUN.txt`（时间戳 + 退出码摘要）

**读**：`NIST_OFFICIAL_MAPPING_AND_WINDOWS_REPORT.md`（官方 vs 占位、严禁混称）

---

## Phase 0.5 — 工程战（不等 yaml，可先打）

- 阅读 `ROUND2_ENGINEERING_BATTLE.md`
- 执行：`python run_round2_engineering_battle.py`
- 看 `ROUND2_ENGINEERING_BATTLE_REPORT.json` 里的 `delta_S_*`（映射敏感性）

## Phase 1 — 证据输入（乙方与人类共同）

| 序号 | 行动 | 完成标准 |
|------|------|----------|
| 1.1 | 取得 **yaml / `build_file_txt` 参数摘要** 或 **论文 SI** 中 **outcome + coincidence** 唯一条款 | 写入 `chsh_preregistered_config_nist_v2_TEMPLATE.json` → 另存为 **LOCKED** 副本（新文件名） |
| 1.2 | 若 SI 为 **16 列联合事件** 而非单边 ±1 | 在 `nist_convert_config` 或新 strategy 中 **显式**实现该统计，**禁止**静默沿用 `outcome_plus_slots` 占位 |
| 1.3 | **radius → 可实现的配对窗** | 仅有 yaml 等价链或论文给定换算时才写入 `protocols.*.pairing.window`；否则保留 **仅 Δi=0** 为「无 yaml 时唯一无争议窗」 |

联系人线索：`NIST_BUILD_SOURCES.md`、`[redacted-email]`

---

## Phase 2 — 管道与对照

| 序号 | 行动 | 说明 |
|------|------|------|
| 2.1 | **Layout**：任意新 HDF5 必先 `nist_hdf5_layout_check.py` | training ≠ completeblind 网格型已证；新文件勿假设 |
| 2.2 | 转换 → CSV → `nist_chsh_diagnostics.py` | 边际与粗元胞；再 `explore_chsh_experiment_alignment.py`（仅在为 **LOCKED** 配置后算 S） |
| 2.3 | 新子目录归档 | 例：`battle_results/nist_v2_locked_<date>/` 保存 config 快照、`battle_result.json`、图、日志 |

---

## Phase 3 — 平行战线（保底筹码）

**不依赖 NIST 赢面**：持续维护 `run_battle_plan.py` / closure 系列，对外表述边界见 `P4_PROTOCOL_AUDIT_SCOPE.md` 与 `docs/BELL_PROTOCOL_NOTE.md` 的 P4 节。

---

## 当前仓库入口速查

| 用途 | 路径 |
|------|------|
| v2 模板（未开盲） | `chsh_preregistered_config_nist_v2_TEMPLATE.json` |
| 当前网格转换（含**非官方** ±1 占位） | `nist_convert_config.json`（须与官方报告对照使用） |
| 第一场快照 | `battle_results/nist_completeblind_2015-09-19/` |
| 第二场工作区 | `battle_results/nist_round2_v2/` |

---

*统一战线的本质：同一套诚实标注（文档 / 工程 / 论点），分三层写死，再开火。*
