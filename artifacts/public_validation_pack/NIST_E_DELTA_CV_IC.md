# NIST E(Delta) CV + IC 诊断

- 数据: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`
- 映射: `half_split`
- bins: `9`

## In-sample 参数与误差

- LowCos 拟合: `a=0.907410`, `b=0.092241`
- HighCos 符号: `s=1`
- weighted SSE (Bell/Low/High): `464.687010` / `28.565594` / `37.431042`

## LOBO-CV（留一bin）

- CV neg-loglik (Bell): `2593.057086`
- CV neg-loglik (LowCos): `21003.996391`
- CV neg-loglik (HighCos): `369.469383`

## 信息准则（二项似然）

| model | k | logLik | AICc | BIC |
|---|---:|---:|---:|---:|
| Bell polyline | 0 | -2593.057086 | 5186.114171 | 5186.114171 |
| LowCos a*cos+b | 2 | -388.355083 | 782.710166 | 781.104615 |
| HighCos s*cos | 1 | -369.469383 | 741.510194 | 741.135990 |

## 读取建议

- 若 LowCos 同时在 CV 与 AICc/BIC 上占优，说明不是纯拟合自由度幻觉。
- 若 in-sample 占优但 CV 或 BIC 不占优，说明存在过拟合或不稳健。
