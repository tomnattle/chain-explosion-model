# Session Archive — 2026-04-25（Zenodo 链接已对齐至 papers_final 双语审计版，2026-04-26）

## 今日目标

- 解决 OSF generalist 停止收稿后的发布路径问题。
- 在同一天完成 2 篇论文公开发布。
- 在前两篇基础上完成第三篇（终章）写作、打包并公开发布。

## 完成结果（当前引用 / papers_final 双语 PDF）

以下三条为仓库与 `README` 的**正式引用**；此前其他 Zenodo 记录号仅作历史会话参考，勿与当前版混用。

### 1) Bell / CHSH 分母审计

- 记录页：`https://zenodo.org/records/19784937`
- DOI：`https://doi.org/10.5281/zenodo.19784937`
- 状态：Published / Open

### 2) GHZ `medium-v10` 仿真审计（V10.4）

- 记录页：`https://zenodo.org/records/19785022`
- DOI：`https://doi.org/10.5281/zenodo.19785022`
- 状态：Published / Open

### 3) 审计三部曲（综合篇）

- 记录页：`https://zenodo.org/records/19785083`
- DOI：`https://doi.org/10.5281/zenodo.19785083`
- 状态：Published / Open

## 今日关键产物文件

### Bell

- `papers/bell-audit-paper/bell-audit-paper-v1.pdf`
- `papers/bell-audit-paper/bell-audit-paper-v1.1.pdf`
- `papers/open-review/ZENODO_BELL_V1_METADATA_BACKUP_2026-04-25.md`

### GHZ

- `papers/ghz-threebody-paper/ghz-threebody-paper-v1.pdf`
- `papers/ghz-threebody-paper/ghz-threebody-paper-v1.1.pdf`
- `papers/open-review/ZENODO_GHZ_V1_METADATA_PREP_2026-04-25.md`

### Trilogy

- `papers/audit-trilogy-paper/draft.en.md`
- `papers/audit-trilogy-paper/ABSTRACT_FINAL.en.md`
- `papers/audit-trilogy-paper/SUBMISSION_CHECKLIST.md`
- `papers/audit-trilogy-paper/audit-trilogy-paper-v1.pdf`
- `papers/audit-trilogy-paper/audit-trilogy-paper-v1.1.pdf`
- `papers/audit-trilogy-paper/audit-trilogy-paper-v1.2.pdf`
- `papers/open-review/ZENODO_TRILOGY_V1_METADATA_PREP_2026-04-25.md`

## 今日完成的结构化工作

1. 诊断发布通道：确认 Zenodo 可直接替代 OSF generalist 的当日开放需求。  
2. 处理环境问题：`activate_conda.ps1` 目标环境缺失，切换至 `base` 环境安装 `pandoc` + `tectonic`。  
3. 生成 PDF：完成 Bell / GHZ / Trilogy 三线 PDF 产出与迭代。  
4. 元数据标准化：形成 Bell/GHZ/Trilogy 三份 Zenodo 表单备份文件。  
5. 论文终稿收束：第三篇采用“方法学审计框架”定位，补齐：
   - claim-to-artifact 映射表  
   - 边界声明（支持/不支持）  
   - singles-aware diagnostics 与 `2\sqrt{2}` 路径表述  
6. 终稿锁定检查：核验 DOI 链接、关键图证路径、最终 PDF 可用性。

## 风险与处理记录

- 风险：过度外推为本体论结论。  
  - 处理：统一降级为 method-level claims，并保留 non-supported extrapolations。  
- 风险：发布页 DOI 字段误用（新版本草稿要求填外部 DOI）。  
  - 处理：明确“已有 DOI”字段使用规则，采用 Zenodo 正确流程。  
- 风险：无 PDF 阻塞发布。  
  - 处理：先确保可发布文件集合，后补 PDF；最终当日补齐 PDF。

## 当前状态结论

- 三篇 DOI 已全部上线，公开可访问，发布链闭环完成。
- 今日核心任务“当日完成发布并开放”已超额完成。

## 建议的下一步（明日）

- 新建 `papers/open-review/TRILOGY_INDEX.md`，统一汇总三篇标题/DOI/一句话摘要。
- 将三篇 DOI 回写到主入口文档（如 `papers/README.md` 与 `papers/open-review/README.md`）。
- 准备一版 100-150 词英文外联摘要，用于专家私信和邮件首段。
