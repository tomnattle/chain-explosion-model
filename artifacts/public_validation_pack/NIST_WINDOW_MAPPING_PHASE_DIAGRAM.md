# NIST window × gauge-mapping 相图

- 数据: `data/nist_completeblind_side_streams.csv`
- windows: `[0.0, 1.0, 2.0, 5.0, 10.0, 15.0]`
- gauge mappings: `identity, flip_A_setting1, flip_B_setting1, flip_A1_B1, flip_all_A, flip_all_B`
- 图像: `artifacts/public_validation_pack/fig6_nist_window_mapping_phase_diagram.png`

## 配对规模

- window=0.0: paired events=136632
- window=1.0: paired events=137498
- window=2.0: paired events=138353
- window=5.0: paired events=140822
- window=10.0: paired events=144800
- window=15.0: paired events=148696

## S 值矩阵

| gauge \\ window | 0.0 | 1.0 | 2.0 | 5.0 | 10.0 | 15.0 |
|---|---:|---:|---:|---:|---:|---:|
| identity | 2.336276 | 2.578770 | 2.680187 | 2.800230 | 2.829113 | 2.812912 |
| flip_A_setting1 | 1.657874 | 1.404872 | 1.294207 | 1.149392 | 1.073856 | 1.050633 |
| flip_B_setting1 | 1.657601 | 1.406977 | 1.296098 | 1.147536 | 1.077330 | 1.050199 |
| flip_A1_B1 | -1.655842 | -1.398250 | -1.281672 | -1.116799 | -1.014974 | -0.962926 |
| flip_all_A | -2.336276 | -2.578770 | -2.680187 | -2.800230 | -2.829113 | -2.812912 |
| flip_all_B | -2.336276 | -2.578770 | -2.680187 | -2.800230 | -2.829113 | -2.812912 |

## 读取建议

- 观察同一行随 window 的变化，判断配对窗口敏感性。
- 观察同一列随 gauge 的变化，判断编码约定敏感性。
- 若两向都敏感，说明当前结论仍依赖分析管线细节。
