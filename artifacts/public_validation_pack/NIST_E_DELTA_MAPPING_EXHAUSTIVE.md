# NIST E(Delta) 映射全枚举稳健性

- 数据: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`
- 扫描方式: `canonical (slot0=+1)`
- 映射总数: `32768`

## 全局统计

- `LowCos better than Bell` 数量: `23697` (`72.3175%`)
- `HighCos better than Bell` 数量: `9329` (`28.4698%`)
- `Bell best among three` 数量: `9071` (`27.6825%`)

## 极值映射（用 mask 表示）

- `best_low_rmse_mask`: `65535` with RMSE `0.000000`
- `best_bell_rmse_mask`: `50115` with RMSE `0.067767`
- `most_low_favored_mask` (`low-bell` 最小): `65535` with gap `-1.105542`
- `most_bell_favored_mask` (`low-bell` 最大): `34695` with gap `0.809325`

## 读取建议

- 若 `LowCos better than Bell` 比例远高于 50%，说明结论有映射稳健性。
- 若比例接近 50% 或更低，说明当前结论强依赖映射假设，应谨慎外推。
