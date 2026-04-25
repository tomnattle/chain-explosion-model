# 量子计算负责人外发就绪度报告

更新时间：自动生成前期流程后

## 当前判定

- 结论：**不可外发（NOT READY）**
- 原因：存在致命阻断项（见下）

## 致命阻断项（必须先清零）

1. `NCC` 桥接结果当前来自 `simulated`，不是公开实验真实事件流。  
2. `events_csv` 为空，无法让对方复验“分母可观测映射”。

## 已完成修复（工程层）

1. 已补“踵”对应脚本：`scripts/explore/explore_ncc_singles_coincidence_bridge.py`  
   - 输出 `singles/coincidences/C_norm/C_signed_norm`
   - 支持 `strict/standard` 双窗口并行
   - 支持图输出（PNG）

2. 已补“外发前闸门”：`scripts/explore/generate_quantum_outreach_package.py`  
   - 自动判定 pass/fail
   - 自动生成：
     - `GATE_STATUS.json`
     - `CHECKLIST.zh.md`
     - `EMAIL_DRAFT.en.md`
   - 若输入为模拟数据会自动阻断

3. 已补“一键流水线”：`scripts/explore/run_quantum_outreach_preflight.ps1`  
   - HDF5 -> events CSV -> NCC 桥接 -> 外发包生成

## 下一步（可执行）

在拿到真实 HDF5 后运行：

```powershell
./scripts/explore/run_quantum_outreach_preflight.ps1 `
  -Hdf5Path "data/nist_completeblind.hdf5"
```

若闸门通过，再发送 `EMAIL_DRAFT.en.md`（按对象做轻微定制）。

## 对外口径建议

- 只主张：`coincidences / sqrt(singles_A*singles_B)` 的可复验映射与窗口敏感性。  
- 不主张：该桥接已自动等价 CHSH 本体结论。  
- 邮件只问一个技术问题，避免进入本体论争辩。
