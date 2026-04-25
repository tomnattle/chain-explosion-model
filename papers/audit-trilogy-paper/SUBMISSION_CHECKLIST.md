# Trilogy Audit 投稿核对清单

> 用于第三篇（Bell + GHZ 综合审计）提交前最终核对。

## A. 稿件完整性

- [x] 英文主稿可独立阅读：`draft.en.md`
- [x] 外发摘要已冻结：`ABSTRACT_FINAL.en.md`
- [x] 标题与摘要均定位为“方法学审计框架”，非本体宣言
- [x] 明确区分“支持结论”与“不支持外推”

## B. 证据链与可复现

- [x] Bell DOI 已写入：`10.5281/zenodo.19763028`
- [x] GHZ DOI 已写入：`10.5281/zenodo.19763473`
- [x] GitHub 仓库地址已写入正文与附录
- [x] Claim-to-Artifact 映射表已完整填写且无占位项

## C. 核心数字与边界

- [x] Bell 关键数字一致：`2.336276 -> 2.839387`，`Delta=+0.503111`
- [x] Bell CI 关键数字一致：`CI95_standard=[2.820420, 2.857413]`
- [x] GHZ 关键数字一致：best fine-stage `F=0.085396`，未达 `F=4`
- [x] 无“终结非局域性/替代理论已成立”类超证据表述

## D. Singles 诊断定位

- [x] `C_norm = coincidences / sqrt(singles_A * singles_B)` 已写入
- [x] Singles 相关段落定位为“可检验归一化路径假设”
- [x] 明确声明该路径不是 CHSH/GHZ 等价证明

## E. 提交前最后检查

- [ ] 术语统一表已对齐：`../TERMINOLOGY.md`
- [x] 章节内文件路径与 DOI 可点击且正确
- [ ] Data Locality Check：原始数据与证据路径均为仓库内相对路径，Clone 后可直接复现
- [x] PDF 已生成并可预览
- [x] Zenodo 元数据备份已准备
