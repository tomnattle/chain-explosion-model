# Chain Explosion Model

杩欐槸涓€涓洿缁曠鏁ｃ€佸眬鍩熴€佸彲瀹¤浼犳挱妯″瀷鏋勫缓鐨勭爺绌跺瀷浠ｇ爜浠撳簱銆傚畠涓嶆槸閲忓瓙鍔涘鏁欑涔︼紝涔熶笉鏄爣鍑嗛噺瀛愮悊璁虹殑鐩存帴鏇夸唬璇佹槑锛涘畠鏇村儚涓€涓妸鍋囪鍐欒繘浠ｇ爜銆佹妸瀹為獙鍐欒繘褰掓。銆佹妸杈圭晫鍐欒繘鏂囨。鐨勭爺绌跺伐绋嬨€? 
This is a research-oriented code repository built around a discrete, local, and auditable propagation model. It is neither a quantum mechanics textbook nor a direct proof against standard quantum theory; it is better understood as a research program that encodes hypotheses into code, experiments into archives, and limits into documentation.

杩欎釜浠撳簱鐪熸鐨勯噸鐐逛笉鏄浂鏁ｇ殑鍙岀紳鑴氭湰锛岃€屾槸涓ゆ涓ヨ們鐨?CHSH / NIST 褰掓。瀹為獙銆傚叾瀹?`ce_*`銆乣verify_*`銆乣discover_*`銆乣explore_*`銆乣critique_*` 鑴氭湰锛屼富瑕佹壙鎷呭熀纭€寤烘ā銆佹暟鍊兼敮鎾戝拰杈圭晫瀹¤鐨勪綔鐢ㄣ€? 
The true center of this repository is not the scattered double-slit scripts, but two serious CHSH / NIST archival experiments. The other `ce_*`, `verify_*`, `discover_*`, `explore_*`, and `critique_*` scripts mainly serve as foundational modeling, numerical support, and boundary-audit layers.

## Contents

1. [Reading Guide](#reading-guide)
2. [Quick Start Paths](#quick-start-paths)
3. [What This Repository Contains](#what-this-repository-contains)
4. [The Two Major Experiments](#the-two-major-experiments)
5. [Why The Project Has Value](#why-the-project-has-value)
6. [Recommended Reading Order](#recommended-reading-order)
7. [Quick Note](#quick-note)

## Reading Guide

濡傛灉浣犲彧鎯冲揩閫熺悊瑙ｈ繖涓」鐩紝寤鸿鍏堣杩欎唤鍏ュ彛鏂囨。锛屽啀璇绘€绘枃妗?[PROJECT_TECHNICAL_MONOGRAPH.md](D:/workspace/golang/nakama/chain-explosion-model/docs/PROJECT_TECHNICAL_MONOGRAPH.md)銆傚悗鑰呮寜鈥滃儚涓€鏈功鈥濈殑鏂瑰紡缁勭粐鍐呭锛屽寘鍚憳瑕併€佺珷鑺傘€佸師鐞嗐€佸叕寮忋€佸疄楠屻€佺粨鏋滀笌杈圭晫銆? 
If you want a fast understanding of the project, start with this entry document and then read the full monograph [PROJECT_TECHNICAL_MONOGRAPH.md](D:/workspace/golang/nakama/chain-explosion-model/docs/PROJECT_TECHNICAL_MONOGRAPH.md). The monograph is organized like a book, with an abstract, chapters, principles, formulas, experiments, results, and interpretive limits.

If you want to see the author's intuitive picture of propagation and measurement before diving into the technical structure, read [MODEL_INTUITION.md](D:/workspace/golang/nakama/chain-explosion-model/docs/MODEL_INTUITION.md). That file is intentionally separated from the result documents so that intuition and conclusion are not conflated.

## Quick Start Paths

If you want different ways to enter the repository, use one of these:

- Fast overview: [PROJECT_TECHNICAL_MONOGRAPH.md](D:/workspace/golang/nakama/chain-explosion-model/docs/PROJECT_TECHNICAL_MONOGRAPH.md)
- Author's model picture: [MODEL_INTUITION.md](D:/workspace/golang/nakama/chain-explosion-model/docs/MODEL_INTUITION.md)
- Bell / CHSH protocol layer: [BELL_PROTOCOL_NOTE.md](D:/workspace/golang/nakama/chain-explosion-model/docs/BELL_PROTOCOL_NOTE.md)
- Archived battle results: [battle_results/README.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/README.md)

## What This Repository Contains

杩欎釜浠撳簱鍖呭惈涓夌被鏍稿績鍐呭锛氱涓€绫绘槸绂绘暎浼犳挱妯″瀷鏈韩锛岀浜岀被鏄洿缁曞弻缂濄€佹祴閲忋€佸欢杩熼€夋嫨鍜岀浉鍏虫€х殑鍩虹瀹為獙锛岀涓夌被鏄潰鍚?CHSH / NIST 闂鐨勪袱杞弗鑲冨綊妗ｄ笌瑙ｉ噴鏀舵潫銆? 
This repository contains three core layers: first, the discrete propagation model itself; second, foundational experiments on double-slit behavior, measurement, delayed choice, and correlations; third, two rounds of serious archival work and interpretive closure around CHSH / NIST questions.

- `chain_explosion_numba.py` / 楂樻€ц兘浼犳挱鍐呮牳  
  `chain_explosion_numba.py` / high-performance propagation kernels
- `ce_engine_v2.py`, `ce_engine_v3_coherent.py` / 鏇村畬鏁寸殑瀹為獙寮曟搸  
  `ce_engine_v2.py`, `ce_engine_v3_coherent.py` / fuller experimental engines
- `ce_00_*` 鍒?`ce_10_*` / 鍩虹鐜拌薄瀹為獙  
  `ce_00_*` to `ce_10_*` / foundational phenomenon experiments
- `verify_*`, `discover_*`, `explore_*` / 楠岃瘉銆佸彂鐜颁笌鎺㈢储灞? 
  `verify_*`, `discover_*`, `explore_*` / verification, discovery, and exploration layers
- `battle_results/` / 涓ゆ涓ヨ們瀹為獙鐨勫綊妗ｅ尯  
  `battle_results/` / archival zone for the two serious experiments

## The Two Major Experiments

绗竴娆′弗鑲冨疄楠屼綅浜?`battle_results/nist_completeblind_2015-09-19/`銆傚畠鍥寸粫鍏紑 completeblind 鏁版嵁寤虹珛浜嗕粠 HDF5銆佷簨浠?CSV銆侀厤瀵瑰崗璁€丆HSH 璁＄畻鍒?JSON 褰掓。鐨勫畬鏁撮摼璺紝骞舵槑纭褰曚簡鈥滃伐绋嬮€氳繃銆佽鐐规湭閫氳繃鈥濈殑缁撹銆? 
The first major experiment is located at `battle_results/nist_completeblind_2015-09-19/`. It builds a full chain from HDF5 to event CSV, pairing protocols, CHSH computation, and JSON archiving over public completeblind data, and explicitly records the conclusion that the engineering path passed while the thesis gate failed.

绗簩娆′弗鑲冨疄楠屼綅浜?`battle_results/nist_round2_v2/`銆傚畠杩涗竴姝ュ鐞嗕簡甯冨眬鍏煎鎬с€佹槧灏勬晱鎰熸€с€佸崗璁竟鐣屽拰瑙ｉ噴鏀舵潫闂锛屽洜姝ゆ瘮绗竴杞洿鍍忎竴浠芥寮忕爺绌跺綊妗ｃ€? 
The second major experiment is located at `battle_results/nist_round2_v2/`. It goes further by addressing layout compatibility, mapping sensitivity, protocol boundaries, and interpretive closure, making it closer to a formal research archive than the first round.

## Why The Project Has Value

杩欎釜椤圭洰鏈€鏈変环鍊肩殑鍦版柟锛屼笉鏄畠绠€鍗曞０绉拌В閲婁簡閲忓瓙鐜拌薄锛岃€屾槸瀹冩妸涓€濂楁浛浠ｆ€т紶鎾彊浜嬫帹杩涘埌浜嗗彲杩愯銆佸彲瀹¤銆佸彲澶辫触銆佸彲褰掓。鐨勭▼搴︺€傚挨鍏堕噸瑕佺殑鏄紝澶辫触缁撴灉涔熻淇濈暀涓嬫潵浜嗭紝鑰屼笉鏄鏂囨。鎺╃洊銆? 
The strongest value of this project is not that it simply claims to explain quantum-like phenomena, but that it advances an alternative propagation narrative to the point where it is executable, auditable, falsifiable, and archivable. Crucially, failed results are also preserved rather than hidden by the documentation.

## Recommended Reading Order

寤鸿鎸夎繖涓『搴忛槄璇伙細鏈枃浠躲€佹€绘枃妗ｃ€丅ell 鍗忚璇存槑銆佷袱杞?battle 褰掓。锛屽啀鍥炲ご鐪嬪熀纭€鑴氭湰銆傝繖鏍蜂富绾垮拰鏀嚎涓嶄細娣峰湪涓€璧枫€? 
The recommended reading order is: this file, the full monograph, the Bell protocol note, the two battle archives, and only then the foundational scripts. This keeps the main line and supporting branches from being confused.

1. [PROJECT_TECHNICAL_MONOGRAPH.md](D:/workspace/golang/nakama/chain-explosion-model/docs/PROJECT_TECHNICAL_MONOGRAPH.md)
2. [MODEL_INTUITION.md](D:/workspace/golang/nakama/chain-explosion-model/docs/MODEL_INTUITION.md)
3. [BELL_PROTOCOL_NOTE.md](D:/workspace/golang/nakama/chain-explosion-model/docs/BELL_PROTOCOL_NOTE.md)
4. [battle_results/README.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/README.md)
5. [battle_results/nist_completeblind_2015-09-19/README.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_completeblind_2015-09-19/README.md)
6. [battle_results/nist_round2_v2/README.md](D:/workspace/golang/nakama/chain-explosion-model/battle_results/nist_round2_v2/README.md)

## Quick Note

褰撳墠浠撳簱閲屼粛鏈変竴閮ㄥ垎鏃ф枃妗ｅ瓨鍦ㄤ腑鏂囩紪鐮佹薄鏌撶幇璞★紝杩欎細褰卞搷涓撲笟灞曠ず鏁堟灉銆傛柊鐨勫叆鍙ｆ枃妗ｅ拰鎬绘枃妗ｅ凡缁忔寜涓嫳鍙岃缁撴瀯閲嶅啓锛屽悗缁嫢缁х画浼樺寲锛屽缓璁妸 battle 瀛愮洰褰曞唴鐨勫叧閿枃妗ｄ篃缁熶竴娓呮礂涓?UTF-8 鍙岃鐗堟湰銆? 
Some older documents in the repository still show Chinese encoding corruption, which hurts the professional presentation of the project. The new entry document and monograph have already been rewritten in a bilingual structure, and a good next step would be to normalize the key battle-subdirectory documents into clean UTF-8 bilingual versions as well.

