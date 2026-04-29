# NIST Clock-Reference Audit v1
# NIST 参考时钟语义审计 v1

本目录用于回答一个单点问题：`coincidence window` 的参考语义到底是“外部时钟”还是“探测事件锚定”。  
This directory answers one focused question: whether the `coincidence window` reference semantics is "external clock" or "detection-event anchored".

## Why This Archive Exists

我们当前代码中存在事件锚定配对（A 事件滑窗找最近 B），而 NIST 官方文档描述了共享外部参考时钟与 sync 链。  
Our current code path includes event-anchored pairing (for each A event, search nearest B in a window), while NIST official documentation describes a shared external reference clock and sync chain.

这两者不应被混写为同一种分析语义。  
These should not be conflated as the same analysis semantics.

## Three Schemes (1-3)

- `event_anchor_nearest`  
  对每个 A 事件，在 `|tB-tA|<=w` 内找最近且未使用的 B。  
- `external_clock_bin`  
  用固定全局时间分箱（外部时钟语义），仅在同一 bin 内配对。  
- `same_index_only`  
  仅允许 `tB==tA` 配对（索引空间严格同槽，作为最强约束基线）。

## NIST Data Types (Key Fact)

根据 NIST 文档，至少存在以下两类可用于分析的数据层：  
At least two analyzable data layers exist in NIST docs:

- 原始 timetag 流（raw/compressed，含外部时钟锁定语义）  
- processed 数据（`processed_compressed/cw45` 与 `processed_compressed/hdf5`，带构造规则与 yaml 依赖）

这意味着“数据层类型”和“配对语义”都必须在实验报告中显式声明。  
This means both "data layer type" and "pairing semantics" must be explicitly declared in reports.

## Files In This Folder

- `EXPERIMENT_PROTOCOL.md`：实验执行协议与停止条件  
- `SCHEME_MATRIX.json`：三方案参数矩阵  
- `results/`：后续运行输出（JSON/图）
