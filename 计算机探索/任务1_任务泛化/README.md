# 任务1：任务泛化（不作弊）

目标：在同一套纯级联机制下，测试多个计算任务，不用 `sqrt`、不用牛顿、不用后置兜底。

## 覆盖任务

- `sqrt3`：求接近 `sqrt(3)` 的固定点
- `reciprocal`：求接近 `1/x`（示例 `1/7`）
- `quadratic`：求二次方程根（示例 `x^2 - 5x + 6 = 0`）

## 运行

```powershell
python "计算机探索/任务1_任务泛化/task_generalization.py"
```

## 产出

- 终态值
- 残差
- 停止原因（`delta_zero` / `cycle_k` / `max_steps`）
