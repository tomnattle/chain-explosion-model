# nist_unified_semantics_audit_v1.py 质疑回应（v1）

原始质疑留档：`a.txt`、`b.txt`、`c.txt`（不改动）  
本文件只做：去重、改写成可验证命题、行动化处置。

---

## A/B/C 去重结果（唯一质疑清单）

> 说明：`b.txt` 与 `c.txt` 高度重复；`a.txt` 提供了更细的口径修正建议。  
> 以下 7 条为去重后的唯一问题。

### [U1] `external_clock_bin` 是否偏离“纯时间桶计数”
- **来源**：a,b,c（重复）
- **改写后命题**：当前 `external_clock_bin` 使用 one-to-one 最近邻匹配，可能与“同桶全计数、不做最佳匹配”的官方口径不一致。
- **状态**：`CONFIRMED`
- **影响等级**：`HIGH`
- **行动**：
  1. 新增 `external_clock_bucket_all`（纯桶计数版，不最近邻）。
  2. 保留现实现并重命名为 `external_clock_nearest_1to1`（明确其语义）。
  3. 两版本并行报告，禁止混称。

### [U2] `event_anchor_nearest` 是否属于漏洞结构模型
- **来源**：b,c（重复）
- **改写后命题**：`event_anchor_nearest` 使用事件自参照时间锚，属于 coincidence-loophole 研究模型，不应与“官方外部时钟口径”并列为同类主结果。
- **状态**：`CONFIRMED`
- **影响等级**：`HIGH`
- **行动**：
  1. 在输出 JSON 中添加 `model_role = loophole_probe`。
  2. 报告文本中从“主比较”降级为“漏洞探针”。

### [U3] `cont_norm` 与 CHSH 统计对象是否混用
- **来源**：a,b,c（重复）
- **改写后命题**：`cont_norm` 是连续相关系数类对象，不等同于二值 CHSH；若混写会造成结论越界。
- **状态**：`CONFIRMED`
- **影响等级**：`HIGH`
- **行动**：
  1. 所有报告分栏：`binary-CHSH` 与 `continuous-corr` 严格分开。
  2. 删除任何“cont_norm 即 CHSH”表述。
  3. 输出文件命名加前缀区分（`chsh_*` vs `corr_*`）。

### [U4] `cont_norm` 分母是否受配对筛选影响
- **来源**：a（独有）
- **改写后命题**：当前分母在配对后样本内计算，可能引入“筛选影响分母”的口径偏移。
- **状态**：`NEEDS_REPRO`
- **影响等级**：`MEDIUM-HIGH`
- **行动**：
  1. 新增固定分母版本：分母取 same-index 全样本单边二阶矩。
  2. 并行输出 `cont_norm_localden` 与 `cont_norm_fixedden`。
  3. 若差异超阈值（如 0.02），升级为 `CONFIRMED`。

### [U5] `same_index` 多事件同时间戳处理是否会“过度配对”
- **来源**：a（独有）
- **改写后命题**：同一 `t` 上两翼多事件时采用 `min(len(A_t),len(B_t))` 顺序配对，需明确这是“事件级”而非“trial级”定义，并统计其发生率。
- **状态**：`NEEDS_REPRO`
- **影响等级**：`MEDIUM`
- **行动**：
  1. 增加冲突统计：`multi_event_t_rate`。
  2. 输出“严格唯一 trial”对照结果（若可构建）。

### [U6] `synthetic_cos` 对照模型命名可能误导
- **来源**：b,c（重复）
- **改写后命题**：`synthetic_cos` 是构造性对照，不应被命名或叙述为“量子真实对照”。
- **状态**：`CONFIRMED`
- **影响等级**：`MEDIUM`
- **行动**：
  1. 更名为 `synthetic_local_cos_baseline`。
  2. 文档中明确“只用于管线 sanity，不用于物理真值宣判”。

### [U7] 单比特槽位过滤（2^k）是否构成后选择风险
- **来源**：b,c（重复）
- **改写后命题**：当前只保留 one-hot 槽位点击，需量化丢弃比例和分布偏差，判断是否影响主结论。
- **状态**：`NEEDS_REPRO`
- **影响等级**：`MEDIUM`
- **行动**：
  1. 输出过滤前后计数与设置分布。
  2. 加一条“宽松映射”对照（若数据支持）。

---

## 本轮汇总

- **CONFIRMED**: 4（U1,U2,U3,U6）
- **NEEDS_REPRO**: 3（U4,U5,U7）
- **FALSE_POSITIVE**: 0
- **OUT_OF_SCOPE**: 0

---

## 新增文件 `d.txt` 并入结果

`d.txt` 为方法学肯定与解释性评论，未新增可执行“质疑条目”。  
去重后不产生新的 `U*` 问题，处理如下：

- **D1 语义矩阵评价**：与现有结论一致（非新质疑）
- **D2 反事实注入评价**：与 U1/U2/U3 的验证框架一致（非新质疑）
- **D3 等效 CHSH 扫描评价**：与既有清单一致（非新质疑）
- **D4 slot 连续值/二值并行评价**：可作为文档补充，不构成缺陷条目

因此本轮计数保持不变：  
`CONFIRMED=4, NEEDS_REPRO=3, FALSE_POSITIVE=0, OUT_OF_SCOPE=0`

---

## 立即执行计划（行动化）

1. 先做 `HIGH` 条目：U1/U2/U3（结构与口径改造）。  
2. 再做 `NEEDS_REPRO`：U4/U5/U7（补指标与对照）。  
3. 新版本脚本后缀统一 `_v2`，不覆盖 `v1`。  
4. 回归验证固定三步：
   - same-index 基线一致性
   - shuffled-B 近零性
   - 外部时钟纯桶 vs 最近邻的差异量化

---

## 执行进展（本轮已完成）

- 已新增修复版脚本：`scripts/explore/nist_unified_semantics_audit_v2.py`
- 已完成 U1：
  - 新增 `external_clock_bucket_all`（纯桶 all-pairs，非最近邻）
  - 旧 `external_clock_nearest_1to1` 保留但降级为 `loophole_probe`
- 已完成 U2：
  - `event_anchor_nearest` 明确标记为 `loophole_probe`
- 已完成 U3：
  - 输出结构中明确分离 `S_binary_chsh` 与 `S_cont_*_corr`
  - 注释中声明仅 `binary_chsh` 属于 Bell-CHSH 对象

### v2 首次复跑快照（window=15）

- `same_index S_binary_chsh = 2.329417`
- `external_clock_bucket_all S_binary_chsh = 2.775687`
- `external_clock_nearest_1to1 S_binary_chsh = 2.808666`
- `event_anchor_nearest S_binary_chsh = 2.834670`

结论：纯桶口径相较最近邻口径显著回落（约 `-0.033`），与“最近邻会抬高 S”的质疑方向一致。

---

## U4/U5/U7 执行进展（v3）

- 已新增：`scripts/explore/nist_unified_semantics_audit_v3.py`
- 已输出：`results/nist_unified_semantics_audit_v3.json`

### U4（cont_norm 分母口径）结果

- 新增 `S_cont_norm_fixedden_corr`（分母固定为 same-index 基线二阶矩）。
- 在 same-index 下：
  - `S_cont_norm_corr = 2.320815`
  - `S_cont_norm_fixedden_corr = 2.320815`
- 当前数据上两者一致，说明“局部分母 vs 固定分母”的差异在 same-index 基线处不显著。

### U5（same_index 多事件同时间戳）结果

- `multi_event_t_rate = 0.0`
- 说明本次主样本在 shared timestamp 上未观测到多事件冲突，`same_index` 顺序配对不会触发该风险路径。

### U7（one-hot 过滤偏差）结果

- `drop_ratio_A = 0.06449`
- `drop_ratio_B = 0.06162`
- 过滤比例约 6%（A/B 接近），属于可量化筛选；后续应在文档中明确该过滤是数据定义步骤而非隐藏操作。

---

## v4 补强结果（对应新增漏洞修复建议）

新增脚本：`scripts/explore/nist_unified_semantics_audit_v4.py`  
结果文件：`results/nist_unified_semantics_audit_v4.json`

### F1 桶边界效应（offset scan）— 已修
- 对 `external_clock_bucket_all` 做 offset=0..14 扫描。
- 结果：`S_binary_range = 0.022401`（2.7680 ~ 2.7904）。
- 结论：存在可量化边界敏感性，但幅度有限，主结论不翻转。

### F2 same_index 严格模式（drop multi-event t）— 已修
- 增加 `same_index_strict`（丢弃多事件时间戳）。
- 本样本 `multi_event_t_rate=0.0`，故 strict 与 non-strict 一致：
  - `S_binary_chsh = 2.329417`

### F3 内置不确定性量化（bootstrap CI）— 已修
- 在 v4 内置关键模式 bootstrap（本轮 n_boot=80）：
  - same_index: `[2.2953, 2.3702]`
  - event_anchor(A): `[2.8181, 2.8546]`
  - event_anchor(B): `[2.8166, 2.8515]`

### F4 fixed_den 轻泄露疑虑（train/test split）— 已修
- 分母改为 `train half` 学习，`test half` 应用：
  - `train_pairs=64008`, `test_pairs=64008`
  - `offset0 S_cont_norm_fixedden_corr = 2.763113`
- 结论：已从“同样本直接提分母”升级为分割口径，泄露疑虑显著降低。

### F5 A/B 锚点不对称 — 已修
- 加入 `A_anchor` 与 `B_anchor` 对照：
  - `A=2.834670`, `B=2.833314`, `delta_abs=0.001356`
- 结论：不对称存在但极小，不影响主结论。

