# Ripple 4项测试反作弊协议（强制）

适用范围：`scripts/explore/ripple_quantum_tests/` 下全部测试脚本与输出。

## 1) 主结论口径

- 任何“模型通过”主结论，必须基于 `constant_mode=derived` 结果。
- `calibrated` 结果仅作对照，不得作为“模型已闭环”的证据。

## 2) 运行约束

- `ripple_quantum_tests_v3.py` 默认只接受 `derived` 作为主模式；
- 若运行 `calibrated`，必须显式加 `--allow-calibrated`；
- 没有 `--allow-calibrated` 时执行会被脚本拒绝。

## 3) 报告约束

报告中必须同时给出：

1. `shape_pass`
2. `constant_pass`
3. `final_pass = shape_pass AND constant_pass`

禁止只报 `shape_pass` 或只报 `NRMSE` 来宣称通过。

## 4) 常数约束

- MRI 与原子钟必须单独披露“常数误差”：
  - MRI：`gamma_rel_err`
  - 原子钟：`center_err_hz`
- 若常数误差不达标，即使曲线形状达标，也必须判为未闭环。

## 5) 文档与产物约束

- 所有结果必须写入 JSON 与 Markdown；
- JSON `meta` 中必须包含：
  - `constant_mode`
  - `allow_calibrated`
  - `anti_cheat_policy`
- 发布图表时必须标注模式（derived/calibrated），防止混淆引用。
