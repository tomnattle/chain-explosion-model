# Δ Mapping Runbook (Paper A Execution)

## 目标

把 `docs/DELTA_MAPPING_VALIDATION_PROTOCOL.md` 落到可执行命令，稳定产出：

- 主结果表（`S_binary / S_continuous_raw / S_continuous_ncc`）
- 稳健性矩阵（窗口/映射/阈值扰动）
- 闭合检查清单（四闭合）
- 失败日志（如触发）

---

## 0. 前置条件

- 已安装 Python 依赖（`numpy`, `h5py` 等）。
- 本地存在 NIST HDF5 数据文件（默认路径见下文命令）。
- 可使用 `conda` 命令（推荐）或 `activate_conda.ps1`（兜底）。

建议先在仓库根目录执行：

```powershell
conda activate audit-api
```

若当前 shell 尚未初始化 conda，再使用：

```powershell
./activate_conda.ps1
```

---

## 1. 基线数据合法性与统计严谨性

先跑“严谨性补齐报告”，作为主线基线：

```powershell
python "scripts/explore/explore_nist_e_delta_rigor_pack.py" `
  --hdf5 "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5" `
  --mapping "half_split" `
  --bootstrap 3000 `
  --seed 20260422 `
  --out-md "artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md"
```

验收点：

- 成功生成 `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- 报告包含定义合法性矩阵、bootstrap CI、exact permutation 检验

---

## 2. 验证逻辑稳健性排查（LOBO/L2O + clipping）

运行 sanity pack，排查验证流程本身是否引入偏差：

```powershell
python "scripts/explore/explore_nist_e_delta_validation_sanity.py" `
  --hdf5 "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5" `
  --mapping "half_split" `
  --out-md "artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md"
```

验收点：

- 成功生成 `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`
- 报告同时包含 `LOBO` 与 `L2O` 两套结果

---

## 3. 映射敏感性最小扫描

用三种映射最小扫描，验证“结论方向是否稳定”：

```powershell
python "scripts/explore/explore_nist_e_delta_rigor_pack.py" `
  --hdf5 "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5" `
  --mapping "parity" `
  --bootstrap 2000 `
  --seed 20260422 `
  --out-md "artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT_parity.md"

python "scripts/explore/explore_nist_e_delta_rigor_pack.py" `
  --hdf5 "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5" `
  --mapping "quadrant_split" `
  --bootstrap 2000 `
  --seed 20260422 `
  --out-md "artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT_quadrant.md"
```

验收点：

- 至少 3 份报告（`half_split/parity/quadrant_split`）可比对
- 明确记录是否出现“结论翻转级”变化

---

## 4. 组织四闭合检查结果

在 `artifacts/public_validation_pack/` 新建或维护一个汇总文件（推荐名）：

- `DELTA_CLOSURE_CHECKLIST.md`

最小表格字段：

- 运行 ID
- 数据版本与哈希
- 映射模式
- 定义闭合（Pass/Fail）
- 量纲闭合（Pass/Fail）
- 流程闭合（Pass/Fail）
- 统计闭合（Pass/Fail）
- 是否触发失败条件

---

## 5. 失败条件触发后的动作

若发生以下任一项：

- 轻微扰动导致 violation/non-violation 翻转
- 分母估计对筛选参数极端敏感
- 跨实现无法复现
- 量纲链无法闭合

执行动作：

1. 在 `DELTA_CLOSURE_CHECKLIST.md` 标记 `FAILED_CLOSURE`
2. 追加 `FAILURE_LOG_<run_id>.md`（可基于 `docs/DELTA_FAILURE_LOG_TEMPLATE.md`）
3. 论文A中将 NIST 段落标注为 `provisional evidence`
4. 暂停对外“强结论”表述

---

## 6. 论文A最小引用包

投稿前至少准备：

- `NIST_E_DELTA_RIGOR_REPORT.md`
- `NIST_E_DELTA_VALIDATION_SANITY.md`
- `DELTA_CLOSURE_CHECKLIST.md`
- 一页摘要（方法主张 + 边界声明）

摘要建议固定句式：

> 在预注册 `Δ` 映射定义与公开脚本下，我们观察到同一样本在不同统计口径上的 `S` 分裂；结论限定于定义闭合通过的条件域，不外推为理论裁决。

---

## 7. 一键执行（已提供）

仓库已提供：

- `scripts/explore/run_delta_validation_pack.ps1`

默认执行（含 conda 激活）：

```powershell
powershell -ExecutionPolicy Bypass -File "scripts/explore/run_delta_validation_pack.ps1"
```

自定义参数示例：

```powershell
powershell -ExecutionPolicy Bypass -File "scripts/explore/run_delta_validation_pack.ps1" `
  -Hdf5Path "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5" `
  -OutDir "artifacts/public_validation_pack" `
  -BootstrapMain 3000 `
  -BootstrapAlt 2000 `
  -Seed 20260422
```

若当前终端已激活环境，可跳过 conda 激活：

```powershell
powershell -ExecutionPolicy Bypass -File "scripts/explore/run_delta_validation_pack.ps1" -SkipCondaActivation
```

---

## 8. 自动汇总（论文可贴表）

一键脚本会自动调用：

- `scripts/explore/summarize_delta_closure.py`

并生成：

- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.json`

也可单独执行：

```powershell
python "scripts/explore/summarize_delta_closure.py" `
  --artifacts-dir "artifacts/public_validation_pack" `
  --out-md "artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md" `
  --out-json "artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.json"
```

说明：

- 该汇总会给出四闭合 `PASS/WARN/FAIL` 的自动草判；
- 最终投稿前仍需人工确认并在 checklist 上定稿。
