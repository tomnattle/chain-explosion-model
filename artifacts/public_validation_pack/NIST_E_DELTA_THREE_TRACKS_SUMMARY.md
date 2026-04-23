# NIST E(Δ) 三线对照

- 数据文件: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`
- 有效样本定义: Alice/Bob 均为 one-hot 单槽点击 (`v=2^k`)
- Δ 定义: 槽位循环距离折叠到 0..8，再映射到 `0..180°`（每档 22.5°）
- 二值 outcome: `slot 0..7 => +1`, `slot 8..15 => -1`

## 拟合结果

- 原始矮余弦: `E_low(Δ) = 0.907410 * cos(Δ) + 0.092241`
- Bell 二值化折线 RMSE: `0.929737`
- 连续原始矮余弦 RMSE: `0.200994`
- 连续归一化高余弦 RMSE: `0.213850`
- 最贴近实测点曲线: **连续原始矮余弦**

## 产物

- 图像: `artifacts/public_validation_pack/fig5_nist_e_delta_three_tracks.png`
