# Zenodo Metadata: 《假大象与泡泡》书稿（叙事版 · 审计手记）
# Zenodo Metadata: *The Fake Elephant and the Bubble* — narrative manuscript & audit notes

## Published record / 已发布记录（上传 Zenodo 后填写）
- **Zenodo record:** （待填 TBD — 例如 `https://zenodo.org/records/XXXXXXXX`）  
- **DOI:** （待填 TBD — 例如 `https://doi.org/10.5281/zenodo.XXXXXXXX`）  
- **Companion code / 配套代码:** https://github.com/tomnattle/chain-explosion-model  

> 首次发布前可删除本节「待填」行，或保留本文件作本地清单，仅在 Zenodo 网页表单中粘贴下方 **Title / Description / Keywords**。

## Title / 标题
[EN] The Fake Elephant and the Bubble — Notes on Auditing Readout Rules in Public Data and Bell-Type Experiments (Manuscript)
[中] 假大象与泡泡 —— 公开数据、Bell/GHZ 与读数规则的审计手记（书稿）

## Description / 描述
[EN]
This deposit is the **narrative manuscript** of the *chain-explosion-model* research program, maintained under `book/` in the companion repository. It is **not** a quantum mechanics textbook and **not** a claim to overturn standard physics. The through-line is: **bubble intuition → lattice loss models → auditable `ce_*` scripts → public-record (e.g. NIST) CHSH/Bell-style audits → GHZ in-silico vs archive → ripple toy benchmarks → honest failure logs and open “possibility” chapters**.

**What is included (source of truth):** Markdown chapters, two background archives (Bell, GHZ), preface, appendix on three phrasings, afterword, and `book/02-contents.md` as the table of contents. Technical monograph and frozen battle results remain in `docs/` and `battle_results/` in the same repo.

**PDF build (optional):** From repo root, with Pandoc + XeLaTeX installed, run `.\scripts\build_book_pdf.ps1` — default output `book/_build/假大象与泡泡-书稿.pdf`.

**License note:** Manuscript-style docs in this project are typically **CC BY-NC-ND 4.0** (see repository `LICENSE-DOCS.md`); software in the repo may be under **AGPL-3.0**. Confirm the license you select on Zenodo matches the files you upload.

**Scope statement:** Narrative and audit **transparency** — headline numbers are binding only to the definitions given in each chapter or frozen artifact, not to metaphors in the preface.

[中]
本归档为 **chain-explosion-model** 研究工程的**叙事书稿**，正文源文件位于配套仓库的 **`book/`** 目录。**不是**量子力学教科书，**也无意**宣称推翻标准物理。叙事主轴为：**泡泡直觉 → 格子与损耗 → 可审计的 `ce_*` 工具 → 公开记录（如 NIST）上的 Bell/CHSH 类审计 → GHZ 档案与 in-silico → 涟漪玩具基准 → 失败与开放问题的诚实记录及构想章**。

**内容边界（以仓库为准）：** Markdown 章节、Bell/GHZ 两篇背景档案、序言、三种表述附录、后记；全书目录见 **`book/02-contents.md`**。技术专论与冻结战报仍在同仓库的 **`docs/`**、**`battle_results/`** 等处。

**PDF 生成（可选）：** 在仓库根目录安装 Pandoc 与 XeLaTeX 后执行 **`.\scripts\build_book_pdf.ps1`**，默认输出 **`book/_build/假大象与泡泡-书稿.pdf`**。

**许可提示：** 书稿类文档在仓库中通常适用 **CC BY-NC-ND 4.0**（见 **`LICENSE-DOCS.md`**）；源代码可能为 **AGPL-3.0**。请在 Zenodo 所选许可与实际上传文件一致。

**范围声明：** 侧重叙事与审计**透明度**；凡出现 CHSH 等 headline 数字，**仅以各章或冻结归档中的定义与数据来源为准**，序言比喻不构成实验判决书。

## Keywords / 关键词
- Fake Elephant / 假大象
- Bubble Model / 泡泡模型
- Readout Rules / 读数规则
- Protocol Transparency / 协议透明
- Bell Inequality / 贝尔不等式
- CHSH / CHSH
- GHZ / GHZ
- NIST Public Data / NIST 公开数据
- Reproducibility / 可复现性
- Science Communication / 科学传播
- Chinese Manuscript / 中文书稿

## Upload checklist / 上传清单（自用）
- [ ] 导出 PDF（`book/_build/…pdf`）或与 Zenodo 同步上传选定 `.md` 打包 `.zip`  
- [ ] 封面图：`book/image/cover.jpg`（若与 deposit 一并发布）  
- [ ] 在 Zenodo 填写 **Publication date**、**Version**（如 v1.0）  
- [ ] 选择 **Communities**（若适用）与 **License**  
- [ ] 发布后将本节顶部 **Zenodo record / DOI** 回填到本文件并提交 git  
