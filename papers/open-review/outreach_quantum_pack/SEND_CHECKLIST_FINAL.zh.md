# 外发执行清单（最终版）

用途：把“可发”变成“发得稳”，避免因为措辞或附件问题被直接忽略。

## A. 发前 10 分钟核对

- [ ] 闸门状态是 PASS：`papers/open-review/outreach_quantum_pack/GATE_STATUS.json`
- [ ] 使用真实桥接图：`artifacts/reports/ncc_singles_bridge_real.png`
- [ ] 使用真实桥接报告：`artifacts/reports/ncc_singles_bridge_real.json`
- [ ] 邮件只问 1 个问题，不扩展本体论
- [ ] 正文控制在 180 词以内，保留 4 个关键数字：
  - strict window/pairs: `0.25 / 136632`
  - standard window/pairs: `15.0 / 148670`
  - CHSH strict S: `2.327428`
  - CHSH standard S: `2.836171`

## B. 附件/链接策略

- [ ] 主链接只放仓库：<https://github.com/tomnattle/chain-explosion-model>
- [ ] 图只提 1 张主图：`artifacts/reports/ncc_singles_bridge_real.png`
- [ ] 数据只提 1 个主 JSON：`artifacts/reports/ncc_singles_bridge_real.json`
- [ ] 不在首封里塞太多历史材料（避免阅读负担）

## C. 邮件内容红线

- [ ] 不写“已推翻”“已证明主流错误”
- [ ] 不写“你必须认可我们的模型”
- [ ] 必须包含边界句：  
      `This normalization bridge is not by itself a CHSH-equivalence proof.`
- [ ] 语气保持“请教一个可复验技术问题”

## D. 发送顺序（建议）

1. Scott Aaronson（先理论边界）  
2. Stephanie Wehner（再操作层规范性）  
3. John Martinis（附上 `C_norm -> E(Δ)` 桥接图后发）

对应模板文件：  
`papers/open-review/outreach_quantum_pack/EMAILS_TOP3_QUANTUM_LEADS.en.md`

桥接图与报告（Martinis 版建议必附）：  
- `artifacts/reports/cnorm_e_delta_bridge_real.png`  
- `artifacts/reports/cnorm_e_delta_bridge_real.md`

## E. 发送后记录（必须做）

- [ ] 在 `papers/open-review/TARGET_EXPERTS.md` 记录“发送时间、主题、唯一问题”
- [ ] 10-14 天后仅跟进 1 次
- [ ] 收到回复后 48 小时内记录“采纳/不采纳 + 理由”

## F. 一键复跑命令（留底）

```powershell
./scripts/explore/run_quantum_outreach_preflight.ps1 `
  -Hdf5Path "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5"
```
