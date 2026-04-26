# v3 未闭环原因诊断（derived）

本报告只基于 `constant_mode=derived` 结果。

## MRI 未闭环原因

- shape_pass: `True`
- constant_pass: `False`
- final_pass: `False`
- 诊断信息: `gamma_qm=42.577000, gamma_ripple=35.299448, rel_err=0.170927`

判定：当前主要问题不是曲线形状，而是关键常数（gamma）没有由模型参数推导到容差范围内。

## 原子钟未闭环原因

- shape_pass: `False`
- constant_pass: `False`
- final_pass: `False`
- 诊断信息: `f0_qm=9.192631770 GHz, f0_ripple=9.194251101 GHz, err=1619330.917 Hz`

判定：原子钟同时存在形状与常数两层差距；当前 cavity 参数映射尚不足以稳定复现实测目标中心频率。

## 下一步任务（只做 derived）

1. MRI：对 `(mu, kappa, rho, eta)` 进行受限扫描，最小化 `gamma_rel_err`；
2. 原子钟：对 `(length_m, wave_speed_m_s, mode_index)` 做物理可行约束扫描，最小化 `center_err_hz` 与形状误差；
3. 新结论仅以 `final_pass` 报告，禁止单独引用 `shape_pass`。