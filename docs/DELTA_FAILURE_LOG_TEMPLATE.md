# DELTA Failure Log Template

## 基本信息

- Run ID:
- Date:
- Data path:
- Data SHA256:
- Script version / commit:
- Operator:

---

## 触发条款

勾选触发项（可多选）：

- [ ] 轻微扰动导致 violation/non-violation 结论翻转
- [ ] NCC 分母估计对筛选参数极端敏感且无物理解释
- [ ] 跨实现不可复现（超出容忍阈值）
- [ ] 量纲链无法闭合（存在未解释缩放）

---

## 复现步骤

```powershell
# Paste exact command(s) used for reproduction
```

---

## 观测现象

- 期望结果：
- 实际结果：
- 差异描述：
- 影响范围（哪些结论受影响）：

---

## 证据附件

- 主报告路径：
- sanity 报告路径：
- 相关图表路径：
- 其他日志路径：

---

## 处置与降格

- [ ] 在 `DELTA_CLOSURE_CHECKLIST.md` 标记 `FAILED_CLOSURE`
- [ ] NIST 段落降格为 `provisional evidence`
- [ ] 暂停强结论外联
- [ ] 新增修复任务并分配负责人

---

## 修复计划

- 根因假设：
- 验证方案：
- 预计完成时间：
- 回归验收标准：
