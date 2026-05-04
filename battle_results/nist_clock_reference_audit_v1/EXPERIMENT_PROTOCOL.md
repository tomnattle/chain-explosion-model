# Experiment Protocol

## Goal

在同一份事件数据上，比较三种配对语义对 `S` 与样本进入机制的影响，避免把“语义差异”误判为“物理结论”。  

## Inputs

- 事件 CSV，字段：`side,t,setting,outcome`
- 可选窗口列表：`0,1,2,5,10,15`（索引或时间单位取决于数据）

## Locked Rules

- 不改 `CHSH` 公式，仅改“谁进入样本”
- 三方案都使用同一份输入事件
- 每个窗口都记录：`pair_count`、`S`、四个 `E` 值

## Stop Conditions

- 若三方案在宽窗下给出显著分叉（`|S_event_anchor - S_external_clock| > 0.1`），标记为“语义敏感”
- 若 `same_index_only` 与 `external_clock_bin` 接近而 `event_anchor_nearest` 偏离，优先怀疑事件锚定策略引入额外选择效应

## Commands

```bash
python scripts/explore/nist_clock_reference_audit_v1.py --events-csv data/nist_completeblind_side_streams.csv --windows 0,1,2,5,10,15 --out-json battle_results/nist_clock_reference_audit_v1/results/clock_reference_audit.json
```

## Reporting Template

1. 数据层：raw/compressed 还是 processed/hdf5/cw45  
2. 配对语义：外部时钟 or 事件锚定  
3. 结论级别：仅协议敏感性 / 可支持更强解释  
