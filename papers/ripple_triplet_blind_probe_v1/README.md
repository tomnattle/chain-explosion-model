# Ripple Triplet Blind Probe v1

本目录用于三元组 `(mu, rho, eta)` 的盲测推演，聚焦两类可计算量：

1. 光传播“减速”代理量（effective speed ratio / n_eff）
2. 光传播“减弱”代理量（振幅与强度指数衰减）

## 脚本入口

- `scripts/explore/ripple_quantum_tests/triplet_light_probe_v1.py`

## 运行方式（仓库根目录）

`python scripts/explore/ripple_quantum_tests/triplet_light_probe_v1.py`

可选参数示例：

`python scripts/explore/ripple_quantum_tests/triplet_light_probe_v1.py --mu 1.55 --rho 2.35 --eta 0.08 --distance-max 50 --n-points 26`

## 输出目录

- `artifacts/ripple_triplet_light_probe_v1/TRIPLET_LIGHT_PROBE_V1.json`
- `artifacts/ripple_triplet_light_probe_v1/TRIPLET_LIGHT_PROBE_V1.csv`
- `artifacts/ripple_triplet_light_probe_v1/TRIPLET_LIGHT_PROBE_V1.md`

## 说明

- 该工具是“模型内可比性”探针，不是 SI 单位下的最终物理定标。
- `distance_unit` 当前是模型路径单位，后续可通过实验基准映射到 SI 米。
- 下一步建议：把 `v_eff` 与衰减曲线，和固体声子传播、光纤损耗等公开参考曲线并列比较。

