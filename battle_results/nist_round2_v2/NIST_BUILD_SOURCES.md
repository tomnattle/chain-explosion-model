# NIST 官方构建参数 — 检索线索（Round 2 冻结用）

文档已说明：HDF5 由压缩 timetag **经程序**转为当前 `clicks`/`settings` 形式；**半径、相对 sync 的 delay** 等来自分析程序输入（曾提及 yaml、`build_file_txt.py`、Bitbucket `bell_analysis_code`）。

## 入口链接（需人工下载/写信索取）

- Bell Test Research Software and Data（总入口）：  
  https://www.nist.gov/pml/applied-physics-division/bell-test-research-software-and-data  
- Data / folder 说明（含 cw45 / HDF5 槽位编码文字）：  
  https://www.nist.gov/document/bell-test-data-file-folder-descriptions  
- 处理数据下载（AWS）：  
  https://www.nist.gov/pml/applied-physics-division/bell-test-research-software-and-data/repository-bell-test-research-2  

## 联系

- `[redacted-email]`（官方文档所列）

## 写入 v2 时必须冻结的字段（示例）

- `config/alice/radius`, `config/bob/radius`（HDF5 内已有，但与「选 click 的窗」是否一致需对照 yaml）  
- `config/*/bitoffset`, `config/*/pk`  
- **16 槽 → 逻辑 ±1（或 detector 基）** 的最终规则须来自论文/代码，**不能**仅沿用 v1 的 0–7 / 8–15 占位而不声明版本  

将摘要以 `official_build.parameter_freeze` 填入 `chsh_preregistered_config_nist_v2_TEMPLATE.json` 的定稿副本，并 **新子目录归档**。
