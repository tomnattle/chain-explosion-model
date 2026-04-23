# NIST E(Delta) 严格2D CV Bootstrap

- 数据: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`
- 映射: `half_split`
- bootstrap: `2000`
- seed: `20260422`
- 说明: 仅使用 `Δ` 轴（2D 简化），每次留一bin严格训练/测试分离。

## 点估计（LOBO-CV neg-loglik）

- Bell: `2593.057086`
- LowCos: `21003.996391`
- HighCos: `369.469383`

## Bootstrap 95% CI

- Bell CI: `[ 2362.117263, 2830.773475 ]`
- LowCos CI: `[ 12018.730346, 31647.216454 ]`
- HighCos CI: `[ 335.182210, 405.230895 ]`

## 胜率（CV最优模型频率）

- P(Bell wins): `0.0000`
- P(LowCos wins): `0.0000`
- P(HighCos wins): `1.0000`

## 读取建议

- 若某模型胜率接近1，说明在当前2D定义下泛化优势稳定。
- 若胜率分散，说明模型优劣对采样波动敏感，尚不能定论。
