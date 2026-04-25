# 量子计算负责人外发前检查清单

## 输入工件
- NCC 桥接报告: `artifacts/reports/ncc_singles_bridge_real.json`
- CHSH 对齐报告: `battle_results/nist_round2_v2/ROUND2_chsh_result_parity.json`

## 致命闸门（必须全过）
- [ x ] NCC 来源必须是**真实事件数据**（不能是 simulated）
- [ x ] NCC 报告必须包含 `events_csv` 真实路径
- [ x ] `strict/standard` 都有 4 个 setting-pair 的 singles/coincidences/C_norm

## 可发邮件最低标准
- [ ] 邮件只问一个技术问题（不要夹带本体论辩论）
- [ ] 邮件正文 < 180 词，含 2-4 个硬数字
- [ ] 附最小复现命令（1-2 行）
- [ ] 明确边界：归一化桥接 != 自动等价 CHSH

## 当前阻断项
- 无

## 当前警告项
- 无

