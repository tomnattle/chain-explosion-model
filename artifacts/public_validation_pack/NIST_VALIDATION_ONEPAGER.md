# NIST 验证一页纸（管理视角）

## 当前状态（红黄绿）

- **整体状态：黄偏红**
- **门禁结论：FAIL**
- **含义：主映射可用，但跨映射稳健性未通过，暂不进入 3D 主线。**

## 现在可以确定的事

- 验证体系是可信的：流程可复现、可自动判定 `PASS/FAIL`。
- “后段效果变差”不是评估器作弊造成的。
- 当前 2D 严格外推下，赢家会随映射切换，说明规则层仍是主要风险。

## 当前主要风险

- **映射依赖风险（最高）**：不同映射下赢家变化，影响对外表述稳定性。
- **外推稳定性风险**：部分模型训练内表现好，但外推表现不稳。
- **沟通风险**：若不写清“在主映射定义下”，容易被质疑过度外推。

## 本周动作（执行顺序）

1. 锁定 `MAPPING_POLICY_2D` 的版本号与生效日期。  
2. 以门禁脚本为准，固定每次迭代必须更新 `NIST_MAPPING_POLICY_CHECK.md`。  
3. 仅在 `Gate=PASS` 时才允许把对应版本纳入 3D 扩展候选。  
4. 对外文本统一使用条件句模板（已写入 `SUBMISSION_TEXT_PACK.md`）。

## 决策建议

- **现在不建议进入 3D 主线。**
- **建议继续 2D 加固，目标是先把跨映射稳健性从 FAIL 拉到 PASS。**

## 证据入口（只看这三份）

- `artifacts/public_validation_pack/NIST_VALIDATION_GOVERNANCE_REPORT.md`
- `artifacts/public_validation_pack/NIST_MAPPING_POLICY_CHECK.md`
- `artifacts/public_validation_pack/MAPPING_POLICY_2D.md`
