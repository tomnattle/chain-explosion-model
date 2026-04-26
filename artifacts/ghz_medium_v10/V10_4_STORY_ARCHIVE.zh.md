# GHZ 脚本演化档案（v10.3 之后）

本文档用于记录从 `scripts/explore/ghz_medium_v10/v10_3_selection_tax_audit.py` 之后，项目为何连续产出多个版本脚本、每次争议点是什么、我们如何回应，以及当前阶段性结论。  
目标是保留真实上下文，避免后续只看到代码而不知道“为什么会有这些版本”。

---

## 0. 出发点（v10.3 前后的主线）

- 早期工作一度把目标放在“是否能接近/达到 GHZ 高 F（常被讨论为 4）”。
- 这在实践上导致了大量关于门控、筛选、指标口径的分歧：到底是机制增益，还是筛选增益。
- `v10_3_selection_tax_audit.py` 的意义是首次把这件事制度化：同一传播机制下，只改门控强度，联动看 `F_gated`、`R_gated`、`D_gated=F*R` 和 `selection_tax`。

---

## 1. v10.3（选择税审计）

对应脚本：`scripts/explore/ghz_medium_v10/v10_3_selection_tax_audit.py`

### 1.1 当时要回答的问题

- 高 `F` 是否伴随高筛选代价（低保留率）？
- 在同一物理/几何设置下，只改 gate 强度，曲线会如何变化？

### 1.2 方法要点

- 使用 medium-wave 三体几何传播与相位约束；
- 用 `soft_detector` 做门控，按 `gate_k * RMS` 阈值把信号转为 `{-1,0,1}`；
- 对四个 GHZ setting 计算并合成 `F_gated`，同步给出保留率 `R_gated`。

### 1.3 影响

- 形成了“选择税”叙事：高指标不是免费来的，代价要披露。

---

## 2. 外部质疑触发（示意曲线问题）

### 2.1 质疑者与质疑内容

- 质疑来源：Claude Sonnet 4.6（网页版本）相关讨论。
- 质疑核心：此前 `ghz_cost_benefit_curve_2p2_to_4p0.*` 是否为“提前设定端点”的示意曲线，而不是计算结果。

### 2.2 事实核对结果

- 旧脚本 `scripts/explore/ghz_threshold/plot_f_target_cost_curve.py` 的确是参数化示意曲线生成器；
- 旧元数据 `artifacts/ghz_threshold_experiment/ghz_cost_benefit_curve_2p2_to_4p0.meta.json` 明确写有 `illustrative_curve` 与 `retention_anchor_at_f_max`；
- 结论：这条旧曲线不能再作为“实测/实算证据”主图使用。

---

## 3. v11（对“示意锚点”质疑的第一轮回应）

对应脚本：`scripts/explore/ghz_honest_cost_curve_v11.py`

### 3.1 动机

- 去掉锚点与示意端点，声明“无 anchor、固定 retention 网格、先登记参数再跑”。

### 3.2 做法

- 三套 hidden-variable scheme；
- 固定保留率网格 `0.05..1.00`；
- 统一输出 CSV/JSON/MD/图。

### 3.3 局限（后续复盘确认）

- `v11` 不是 `ghz_medium_v10` 同一模型，不是直接复现 v10 介质传播几何；
- 因此它更像“另一套诚实基线实验”，不是“对 v10 的一一对应反证”。

---

## 4. v19（高阈值触发叙事的极端探索）

对应脚本：`scripts/explore/ghz_loop_explosion_v19.py`

### 4.1 动机

- 沿“链式爆发/强触发事件”方向做极端门控探索，观察高阈值下三体指标行为。

### 4.2 特征

- 文案与实现强调 burst trigger（高阈值只记录强事件）；
- 属于“高选择强度”探索脚本。

### 4.3 作用

- 它把“筛选规则可极强改写指标”这件事推到台面上，但也带来更强争议：  
  高分到底是机制，还是规则本身。

---

## 5. v10.4（回到 medium-v10 主模型的计算曲线）

对应脚本：`scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`

### 5.1 目标

- 在 `ghz_medium_v10` 原模型内给出真实计算曲线，替代示意曲线；
- 不再靠“目标 F 端点”构图。

### 5.2 第一版成果

- 产出 `V10_4_REAL_COST_CURVE.*`；
- 元数据写明 `type = computed_curve`；
- 曲线点来自固定样本下的 gate 扫描计算。

### 5.3 第二版加强（关键）

- 加入“同保留率随机对照”（matched-retention random control）：
  - 输出 `F_gated`；
  - 同时输出 `F_random_mean ± std`（随机抽样但保留率匹配）。

### 5.4 这一步带来的结论变化

- 可以明确区分：
  - 不是“随机丢同样比例也会得到同样高分”；
  - 高 `F` 与特定门控规则强相关；
  - 因而应归类为 post-selection amplification，而非全样本机制值。

---

## 6. 论文叙事重定位（已执行）

- 已把 GHZ 文稿中的旧示意曲线引用替换为 `V10_4_REAL_COST_CURVE.*`；
- 叙事从“追求复现 F=4”改为“审计探测/筛选规则对 F 的敏感性”；
- 明确加入随机同保留率对照，避免单曲线误读。

---

## 7. 当前真实立场（不规避版本）

1. **旧示意曲线问题属实**：此前确有 illustrative 曲线，不能再当证据主图。  
2. **v10.4 是实算曲线**：在 medium-v10 主模型内可复现、可追溯。  
3. **高 F 与规则强耦合**：振幅门控可把指标推高，随机同保留率不复现同等高度。  
4. **最稳结论不是“推翻量子”**，而是：高相关指标对保留协议高度敏感，必须把被丢弃样本和筛选规则纳入主结果。  
5. **团队当前激进假设（工作假说，不是终判）**：  
   - “量子大概率不干涉”作为方向性判断，仍需后续任务持续审计与反驳测试；  
   - 该判断当前不作为最终定理，仅作为后续实验与脚本路线的驱动假设。

---

## 8. 为什么必须保留这份档案

- 否则未来只看文件名会误解：为什么同时存在 v11/v19/v10.4 等“看起来互相冲突”的脚本；
- 实际上这些版本对应的是不同阶段的争议响应：  
  **示意曲线争议 -> 无锚点回应 -> 极端触发探索 -> 回归主模型实算 + 随机对照**。

---

## 9. 下一阶段接口

本档案之后的新任务，建议默认携带以下输入：

- 主模型脚本：`scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`
- 证据产物：`artifacts/ghz_medium_v10/V10_4_REAL_COST_CURVE.*`
- 争议背景脚本：`scripts/explore/ghz_honest_cost_curve_v11.py`、`scripts/explore/ghz_loop_explosion_v19.py`
- 本文档：`artifacts/ghz_medium_v10/V10_4_STORY_ARCHIVE.zh.md`

> 这样后续任何新版本都能回答三个问题：  
> （1）它在回应哪条质疑；（2）它与 v10 主模型的关系；（3）它改变了哪条结论口径。
