# 任务2：最小 ISA（可编程性）

目标：把“映射函数 + 常数 + 初值 + 任务目标”抽象成可配置指令。

## 设计

脚本 `minimal_isa_runner.py` 接收内置 program（可扩展为 JSON），执行纯级联计算：

- `SET_CONST mu rho eta`
- `SET_MAPPING mapping_id`
- `SET_TASK task params`
- `SET_SEED seed`
- `RUN steps digits`

## 运行

```powershell
python "计算机探索/任务2_最小ISA/minimal_isa_runner.py"
```

## 意义

这一步用于证明：系统不仅能“算一个例子”，还能被“编程配置”。
