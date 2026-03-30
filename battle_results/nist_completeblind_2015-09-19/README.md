# 战斗归档：NIST completeblind（2015-09-19 跑次）

本目录为**固定快照**：真实 HDF5 → 事件 CSV → 双协议 CHSH 对齐的一次可审计结果，便于引用与复盘；**请勿**为迎合新结论覆盖此处文件，应新建子目录并升级预注册版本号。

## 结论（当时判据）

| 门 | 结果 |
|----|------|
| 工程门 | **通过**：配对可算、量级合理 |
| 论点门 | **未通过**：`strict` 协议下 `S ≈ 2.336 > strict_max_S (2.02)` |

同批数据上仍出现 **`S_standard > S_strict`**（约 2.84 > 2.34），分叉方向与“宽窗”判据一致，但**未能**同时满足预注册的 `strict_max_S`。

## 数表摘要

- **strict**：`window = 0`（网格索引），`pairs = 136632`，`S ≈ 2.3363`
- **standard**：`window = 15`（网格索引），`pairs = 148670`，`S ≈ 2.8394`

完整数值见 `battle_result.json`。

## 文件说明

- `BATTLE_ARCHIVE.json`：归档元数据、数据来源、示例命令、git commit
- `battle_result.json`：判辞与四路 `E`、`S`
- `nist_convert_config.snapshot.json`：HDF5→CSV 参数快照（含槽位 ±1 预注册）
- `chsh_preregistered_config_nist_index.snapshot.json`：双协议配对窗与论点门快照
- `figure_chsh_alignment.png`：当时生成的四格图（若存在）

事件级 CSV 体积大，默认仍放在仓库 `data/nist_completeblind_side_streams.csv`；归档不重复拷贝 binary/巨文件，路径见 `BATTLE_ARCHIVE.json`。

## 文献/格式依据

NIST 对 HDF5 内 `clicks`/`settings` 的文字说明：  
https://www.nist.gov/document/bell-test-data-file-folder-descriptions
