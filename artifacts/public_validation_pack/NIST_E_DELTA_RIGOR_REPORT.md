# NIST E(Delta) 定义合法性与统计严谨性补齐报告

## 1) 定义合法性矩阵

| 定义项 | 当前实现 | 合法性状态 | 备注 |
|---|---|---|---|
| one-hot 槽位解码 | `v=2^k => slot k` | 官方一致 | 与公开文档对齐，且已在本仓库合规报告校验。 |
| `Δ` 构造 | 槽位循环距离折叠到 `0..8`，映射 `0..180°` | 工程定义 | 合理可复现，但非官方唯一定义。 |
| `slot->±1` 二值映射 | `half_split` | 假设定义 | 公开文档未唯一指定，需显式声明。 |
| Bell 折线基准 | 分段线性局域基线 | 理论基线 | 用作比较对象而非数据生成假设。 |

## 2) 点估计（主映射）

- 数据: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`
- 主映射: `half_split`
- 低余弦拟合: `E_low(Δ) = 0.907410 * cos(Δ) + 0.092241`
- `wRMSE(Bell)` = `0.058318`
- `wRMSE(LowCos)` = `0.014459`
- `wRMSE(HighCos)` = `0.016552`

## 3) Bootstrap 置信区间（binomial parametric, 95%）

- `wRMSE(Bell)` 95% CI: `[0.055100, 0.062291]`
- `wRMSE(LowCos)` 95% CI: `[0.010967, 0.020318]`
- `wRMSE(HighCos)` 95% CI: `[0.012790, 0.022511]`
- `wRMSE(LowCos)-wRMSE(Bell)` 95% CI: `[-0.049243, -0.036555]`
- `P(wRMSE(LowCos) < wRMSE(Bell))` = `1.000000`

## 4) 置换检验（9 bins exact paired-swap）

- 统计量 `T = SSE(Bell)-SSE(LowCos)` 的观测值: `436.121416`
- 单侧 p 值（LowCos 优于 Bell）: `0.0117188`
- 双侧 p 值: `0.0234375`

## 5) 审稿友好结论

- 在当前主映射定义下，LowCos 相比 Bell 折线具有显著更低误差。
- 该结论在统计上给出 CI 与 exact permutation 证据，但仍受 `slot->±1` 映射假设约束。
- 因此推荐表述为：**“在预注册映射定义下，实测点形状更贴近余弦轨道。”**
