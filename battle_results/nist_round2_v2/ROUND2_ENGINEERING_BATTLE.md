# 第二场 · 工程战（已开战）

**性质**：在 **不写信、不声称 yaml 官方** 的前提下，用 **两条预注册的槽位→±1 假设** 对同一 HDF5 做 **敏感性对照**。  
**不等于**：NIST 论文复现。  
**等于**：量化「读出假设」对 CHSH `S` 的杠杆，为第三场换映射/换窗做数据。

## 预注册文件

| 文件 | 作用 |
|------|------|
| `nist_convert_config_round2_legacy.json` | `legacy_self`：0–7/+ ，8–15/-（第一场同款占位） |
| `nist_convert_config_round2_parity.json` | `parity`：bit 索引 `k` 偶 → +1，奇 → -1 |
| `chsh_preregistered_config_nist_round2_engineering.json` | `strict` 窗 0；`standard` 窗 **10**（`floor( grid/|alice_laserPulseNumber| / 2 )`，见官方对齐日志比例 ≈20.19） |
| `thesis_gate.mode` | **`fork_only`**：只判 `S_standard > S_strict`，**不再**绑第一场 `strict_max_S=2.02` |

## 一键跑

```bash
python run_round2_engineering_battle.py
```

产出：

- `data/nist_round2_engineering_legacy.csv`、`data/nist_round2_engineering_parity.csv`
- `ROUND2_chsh_result_legacy.json`、`ROUND2_chsh_result_parity.json`
- `ROUND2_figure_*.png`
- **`ROUND2_ENGINEERING_BATTLE_REPORT.json`**（汇总 + `delta_S_*` + **`under_round1_gate`**）
- **`ROUND2_UNDER_ROUND1_GATE.json`**：两场 CSV 上沿用 **`chsh_preregistered_config_nist_index.json`**（第一场宽窗 15、`strict_max_S=2.02` 等）的判辞
- `ROUND2_chsh_*_under_round1_gate.json`、`ROUND2_figure_*_under_round1_gate.png`

## 如何读结果

- **`thesis_pass`**：在 fork_only 下表示「宽窗 S 是否仍高于严窗 S」——与第一场「压回 2.02」无关。  
- **`delta_S_strict` / `delta_S_standard`**：`parity` 相对 `legacy` 的 S 漂移；大则说明 CHSH 数 **高度依赖** 占位映射，更证明第一场要 yaml/SI。
