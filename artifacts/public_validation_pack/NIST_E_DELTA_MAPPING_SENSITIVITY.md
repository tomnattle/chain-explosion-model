# NIST E(Delta) 映射敏感性

- 数据: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`
- 目的: 检查不同 `slot->±1` 映射下，三条参考曲线相对贴合度是否稳定。

| mapping | low_cos a | low_cos b | RMSE bell | RMSE low | RMSE high |
|---|---:|---:|---:|---:|---:|
| half_split | 0.907410 | 0.092241 | 0.929737 | 0.200994 | 0.213850 |
| parity | 0.736405 | 0.262063 | 1.105542 | 1.145301 | 1.247219 |
| quadrant_split | 0.704824 | 0.293588 | 0.075788 | 0.884942 | 1.014546 |

结论读取建议：每个 mapping 内，优先比较 `RMSE low` 与 `RMSE bell` 的大小关系。
