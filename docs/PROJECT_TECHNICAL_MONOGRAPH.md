# Chain Explosion Model Technical Monograph
# Chain Explosion Model 鎶€鏈€绘枃妗?
## Abstract

鏈枃妗ｅ皢 `chain-explosion-model` 浣滀负涓€涓畬鏁寸爺绌跺璞℃潵浠嬬粛锛岃€屼笉鏄妸瀹冨綋鎴愪竴缁勯浂鏁ｈ剼鏈€傛枃妗ｇ殑鐩爣鏄鏄庤繖濂椾唬鐮佺殑妯″瀷鍘熺悊銆佸疄楠岀粨鏋勩€佷袱娆′弗鑲冨疄楠岀殑鍗忚涓庣粨鏋溿€佷互鍙婅繖浜涚粨鏋滃湪瑙ｉ噴灞備笂鐨勮竟鐣屻€? 
This document presents `chain-explosion-model` as a coherent research object rather than as a loose collection of scripts. Its purpose is to explain the model principles, the experimental structure, the protocols and outcomes of the two major experiments, and the interpretive boundaries of those outcomes.

浠庣爺绌朵环鍊间笂鐪嬶紝杩欎釜浠撳簱鐨勯噸瑕佹€т笉鍦ㄤ簬瀹冪洿鎺ュ甯冧簡鏌愮鏈€缁堢墿鐞嗙粨璁猴紝鑰屽湪浜庡畠鎶婁竴濂楁浛浠ｆ€т紶鎾亣璁炬帹杩涘埌浜嗗彲浠ヨ杩愯銆佽妫€楠屻€佽褰掓。銆佷篃鍙互琚惁瀹氱殑闃舵銆傚挨鍏堕毦寰楃殑鏄紝浠撳簱淇濆瓨浜嗗け璐ョ粨鏋滀笌闄愬埗鏉′欢锛岃€屼笉鏄彧淇濈暀鏈夊埄鍙欎簨銆? 
From a research-value perspective, the importance of this repository does not lie in declaring a final physical verdict, but in advancing an alternative propagation hypothesis to the stage where it can be run, tested, archived, and also refuted. What is especially valuable is that the repository preserves failure cases and limiting conditions rather than only favorable narratives.

鏈€绘枃妗ｉ噰鐢ㄢ€滃儚涓€鏈功鈥濈殑缁撴瀯缂栧啓锛屽寘鍚墠瑷€寮忓鍏ャ€佹ā鍨嬬珷鑺傘€佸叕寮忕珷鑺傘€佸疄楠岀珷鑺傘€佸浘绀虹储寮曘€佺粨鏋滆В閲婁笌杈圭晫璇存槑銆傝繖鏍峰啓鐨勭洰鐨勶紝鏄璇昏€呭嵆浣夸笉鍏堟墦寮€婧愮爜锛屼篃鑳藉厛寤虹珛涓€鏉℃竻鏅颁富绾裤€? 
This monograph is written in a book-like structure, including a preface-style introduction, model chapters, formula chapters, experiment chapters, a figure index, result interpretation, and statements of boundary. The goal is to let a reader build a clear conceptual thread even before opening the source code.

Because the project also carries a strong author-side intuition about how propagation should be pictured, that intuition is documented separately in [MODEL_INTUITION.md](D:/workspace/golang/nakama/chain-explosion-model/docs/MODEL_INTUITION.md). The separation is deliberate: the intuition note preserves the visual and conceptual picture, while this monograph stays focused on implementation structure, experiments, and interpretive limits.

## Table of Contents

1. [Abstract](#abstract)
2. [Chapter 1. Project Positioning](#chapter-1-project-positioning)
3. [Chapter 2. Architecture of the Codebase](#chapter-2-architecture-of-the-codebase)
4. [Chapter 3. The Core Model](#chapter-3-the-core-model)
5. [Chapter 4. Measurement as Local Intervention](#chapter-4-measurement-as-local-intervention)
6. [Chapter 5. Phase, Coherence, and Visibility](#chapter-5-phase-coherence-and-visibility)
7. [Chapter 6. Foundational Experiment Tree](#chapter-6-foundational-experiment-tree)
8. [Chapter 7. CHSH Protocol Logic](#chapter-7-chsh-protocol-logic)
9. [Chapter 8. Major Experiment I: NIST Completeblind Archive](#chapter-8-major-experiment-i-nist-completeblind-archive)
10. [Chapter 9. Major Experiment II: Round 2 / NIST v2 Closure](#chapter-9-major-experiment-ii-round-2--nist-v2-closure)
11. [Chapter 10. Figure and Artifact Index](#chapter-10-figure-and-artifact-index)
12. [Chapter 11. Interpretive Boundaries](#chapter-11-interpretive-boundaries)
13. [Chapter 12. Optimization Proposal](#chapter-12-optimization-proposal)

## Suggested Reading Paths

- If you want the shortest book-like route: Chapter 1 -> Chapter 3 -> Chapter 7 -> Chapter 8 -> Chapter 9 -> Chapter 11
- If you want the author's inner picture first: read [MODEL_INTUITION.md](D:/workspace/golang/nakama/chain-explosion-model/docs/MODEL_INTUITION.md), then return here
- If you only care about the archive-level conclusion structure: jump directly to Chapter 8, Chapter 9, and Chapter 11

---

## Chapter 1. Project Positioning
## 绗竴绔?椤圭洰瀹氫綅

杩欎釜椤圭洰棣栧厛鏄竴涓爺绌跺伐绋嬶紝鍏舵鎵嶆槸涓€涓ā鎷熶粨搴撱€傚畠閫氳繃浠ｇ爜鍘昏〃杈句竴绉嶆牳蹇冨垽鏂細鏌愪簺鐪嬩笂鍘婚渶瑕佸鏉傞噺瀛愬彊浜嬬殑鐜拌薄锛屾槸鍚﹁兘澶熷湪鏄惧紡鐨勫眬鍩熴€佺鏁ｃ€佸洜鏋滀紶鎾鏋朵腑鑾峰緱鏁板€间笂鐨勯噸寤恒€佽繎浼兼垨鏇夸唬琛ㄨ堪銆? 
This project is first a research engineering effort and only secondarily a simulation repository. Through code, it expresses a core question: whether some phenomena that seem to require a complex quantum narrative can instead be numerically reconstructed, approximated, or reformulated within an explicit local, discrete, and causal propagation framework.

涓庢櫘閫氱殑鏁欏婕旂ず涓嶅悓锛岃繖涓粨搴撳苟涓嶆弧瓒充簬鈥滃仛鍑哄嚑寮犲儚鏍风殑鍥锯€濄€傚畠杩涗竴姝ヨ姹傚疄楠屾湁鏄庣‘鍙傛暟銆佹湁鍙噸澶嶆墽琛岃矾寰勩€佹湁缁撴瀯鍖栦骇鐗┿€佹湁闂ㄦ鍒ゆ柇锛屽苟鏈€缁堣兘澶熺暀涓嬪綊妗ｃ€傚洜姝ゅ畠鏇村儚涓€涓爺绌惰鍒掔殑浠ｇ爜鍖栧疄鐜般€? 
Unlike ordinary educational demos, this repository is not satisfied with merely producing a few plausible plots. It further requires clear parameters, reproducible execution paths, structured artifacts, threshold-based judgments, and durable archives. For that reason, it is better seen as the coded implementation of a research program.

杩欎釜瀹氫綅鍐冲畾浜嗘枃妗ｇ粨鏋勫繀椤婚噸鏂版帓搴忋€備富绾夸笉搴旇鏄嚑鍗佷釜鑴氭湰閫愪釜骞抽摵锛岃€屽簲璇ユ槸鈥滄ā鍨嬪師鐞?-> 鐜拌薄瀹為獙 -> CHSH 鍗忚闂 -> 涓ゆ涓ヨ們瀹為獙 -> 瑙ｉ噴杈圭晫鈥濄€傛湰鎬绘枃妗ｅ氨鏄緷鐓ц繖鏉′富绾挎潵閲嶅啓鐨勩€? 
This positioning determines that the documentation must be reordered. The main line should not be a flat list of dozens of scripts, but rather 鈥渕odel principles -> phenomenon experiments -> CHSH protocol questions -> two serious experiments -> interpretive boundaries.鈥?This monograph is rewritten according to precisely that line.

---

## Chapter 2. Architecture of the Codebase
## 绗簩绔?浠ｇ爜鏋舵瀯

浠撳簱鐨勬牳蹇冧唬鐮佸彲鍒嗕负鍥涗釜灞傛锛氫紶鎾唴鏍搞€佸疄楠屽紩鎿庛€佸疄楠岃剼鏈€佸綊妗ｄ笌瀹¤宸ュ叿銆傜悊瑙ｈ繖涓垎灞傞潪甯搁噸瑕侊紝鍥犱负瀹冨喅瀹氫簡姣忎竴涓枃浠跺湪鐮旂┒閾句腑鐨勫湴浣嶃€? 
The core code of the repository can be divided into four layers: propagation kernels, experimental engines, experiment scripts, and archival/audit tooling. Understanding this hierarchy is crucial because it determines the role each file plays in the research chain.

绗竴灞傛槸浼犳挱鍐呮牳锛屼富瑕佺敱 `chain_explosion_numba.py` 缁勬垚銆傝繖閲屽疄鐜颁簡鏈€鍏抽敭鐨勭鏁ｉ偦鍩熶紶鎾鍒欙紝鍖呮嫭鍙岀紳浼犳挱銆佸惛鏀舵帺鑶滀紶鎾€佸垎鏀紶鎾拰甯︾浉浣嶇殑鐗堟湰銆傝繖涓€灞傜殑鐗圭偣鏄珮棰戙€佸眬閮ㄣ€佸亸鏁板€煎唴鏍搞€? 
The first layer is the propagation kernel, mainly implemented in `chain_explosion_numba.py`. It contains the key discrete neighborhood update rules, including double-slit propagation, absorber-mask propagation, split propagation, and phase-carrying variants. This layer is high-frequency, local, and numerically kernel-oriented.

绗簩灞傛槸瀹為獙寮曟搸锛屼唬琛ㄦ枃浠舵槸 `ce_engine_v2.py` 鍜?`ce_engine_v3_coherent.py`銆傝繖涓€灞傚湪鍐呮牳涔嬩笂澧炲姞浜嗘洿瀹屾暣鐨勫疄楠岄€昏緫锛屼緥濡傚姝ヤ紶鎾€佺浉浣嶆紨鍖栥€侀殢鏈鸿矾寰勩€佺粺璁℃彁鍙栧拰鏇村鏉傜殑瀵规瘮鍒嗘瀽銆? 
The second layer is the experimental engine, represented by `ce_engine_v2.py` and `ce_engine_v3_coherent.py`. This layer builds on top of the kernels with fuller experimental logic such as multi-step propagation, phase evolution, random paths, statistical extraction, and more complex comparative analysis.

绗笁灞傛槸瀹為獙鑴氭湰锛屽寘鎷?`ce_*`銆乣verify_*`銆乣discover_*`銆乣explore_*` 鍜?`explore_critique_*` 绯诲垪銆傚畠浠妸妯″瀷鏀捐繘涓嶅悓闂涓祴璇曪細浠庡弻缂濆彲瑙佸害锛屽埌鍚告敹寮忔祴閲忥紝鍐嶅埌 Bell/CHSH 鍜屽崗璁晱鎰熸€с€? 
The third layer consists of experiment scripts, including the `ce_*`, `verify_*`, `discover_*`, `explore_*`, and `explore_critique_*` series. These scripts place the model into different problem settings: from double-slit visibility to absorption-style measurement, and then to Bell/CHSH and protocol sensitivity.

绗洓灞傛槸褰掓。涓庡璁″伐鍏凤紝涓昏鍖呮嫭 `run_unified_suite.py`銆乣suite_artifacts.py` 鍜?`experiment_dossier.py`銆傝繖涓€灞傜殑浠峰€煎湪浜庯紝瀹冩妸鍗曟杩愯浠庘€滀复鏃惰緭鍑衡€濇彁鍗囦负鈥滃彲褰掓。鐮旂┒宸ヤ欢鈥濄€? 
The fourth layer is the archival and audit tooling, mainly including `run_unified_suite.py`, `suite_artifacts.py`, and `experiment_dossier.py`. The value of this layer is that it upgrades a single run from a 鈥渢emporary output鈥?into an 鈥渁rchivable research artifact.鈥?
---

## Chapter 3. The Core Model
## 绗笁绔?鏍稿績妯″瀷

杩欏妯″瀷鐨勫熀鏈璞′笉鏄爣鍑嗛噺瀛愭尟骞咃紝鑰屾槸浜岀淮鏍肩偣涓婄殑鍦洪噺锛屼粨搴撳鏁颁綅缃皢鍏惰В閲婁负鈥滆兘閲忊€濇垨鈥滃己搴︹€濄€傚湪鏈€鍩虹鐗堟湰涓紝浼犳挱杩囩▼鍙互鐞嗚В涓烘瘡涓牸鐐规妸鑷韩鏉冮噸鍒嗗彂缁欏懆鍥磋嫢骞叉牸鐐癸紝鍚屾椂涔樹互琛板噺鍥犲瓙銆? 
The basic object of the model is not a standard quantum amplitude but a field quantity on a two-dimensional lattice, interpreted in most places in the repository as 鈥渆nergy鈥?or 鈥渋ntensity.鈥?In the most basic version, propagation can be understood as each lattice site distributing its weight to neighboring sites while being multiplied by a damping factor.

璁?\(E_t(x,y)\) 琛ㄧず鏃跺埢 \(t\) 鐨勬牸鐐瑰満閲忥紝\(A\)銆乗(B\)銆乗(S\) 鍒嗗埆琛ㄧず涓讳紶鎾柟鍚戙€佸弽鍚戜紶鎾柟鍚戝拰渚у悜浼犳挱鏂瑰悜鐨勬潈閲嶏紝\(\lambda\) 琛ㄧず涓€姝ヤ紶鎾殑琛板噺鍥犲瓙銆傞偅涔堜竴涓吀鍨嬫洿鏂板彲鍐欎负锛? 
Let \(E_t(x,y)\) denote the lattice field at time \(t\), let \(A\), \(B\), and \(S\) denote the weights of forward, backward, and lateral propagation, and let \(\lambda\) denote the one-step damping factor. Then a typical update can be written as:

\[
E_{t+1}(x,y)
=
\lambda\Big(
A E_t(x-1,y)
 B E_t(x+1,y)
 S E_t(x,y-1)
 S E_t(x,y+1)
 \frac{S}{2}E_t(x-1,y-1)
 \frac{S}{2}E_t(x-1,y+1)
 \frac{S}{2}E_t(x+1,y-1)
 \frac{S}{2}E_t(x+1,y+1)
\Big).
\]

杩欏苟涓嶆槸瀵逛唬鐮侀€愯鐨勫瓧闈㈣浆鍐欙紝鑰屾槸瀵瑰叾鏍稿績浼犳挱鎬濇兂鐨勬暟瀛︽娊璞°€傜湡姝ｇ殑浠ｇ爜杩樺彔鍔犱簡闅滅鐭╅樀銆佸惛鏀剁煩闃点€佹湁闄愬尯鍩熸帰娴嬪櫒鍜屽垎鏀紶鎾瓑鏉′欢銆? 
This is not a literal line-by-line transcription of the code, but a mathematical abstraction of its core propagation idea. The actual code further overlays barrier matrices, absorber masks, finite-region detectors, and split-propagation conditions.

鍙岀紳缁撴瀯閫氳繃甯冨皵闅滅鐭╅樀 `barrier` 瀹炵幇銆傛暣鍒楁尅鏉块€氬父鍏堣缃负闃绘尅锛屽啀鍦ㄤ袱鏉＄紳鐨勪綅缃墦寮€绐楀彛锛屼娇浼犳挱浠呰兘绌胯繃鎸囧畾鍑犱綍鍖哄煙銆傝繖鎰忓懗鐫€鍙岀紳鍥炬牱骞朵笉鏄澶栫粯鍒跺嚭鏉ョ殑锛岃€屾槸浠庢洿鏂拌鍒欏拰鍑犱綍绾︽潫涓秾鐜板嚭鏉ョ殑銆? 
The double-slit structure is implemented through a boolean barrier matrix `barrier`. A full barrier column is usually initialized as blocked, and then two slit regions are reopened as windows so that propagation may pass only through designated geometric regions. This means the double-slit pattern is not manually drawn afterward, but emerges from the update rule plus geometric constraints.

---

## Chapter 4. Measurement as Local Intervention
## 绗洓绔?娴嬮噺浣滀负灞€鍩熶粙鍏?
浠撳簱鍦ㄦ蹇典笂鏈€椴滄槑鐨勯€夋嫨涔嬩竴锛屾槸灏介噺鎶娾€滄祴閲忊€濊繕鍘熶负浼犳挱閾句腑鐨勫眬鍩熻繃绋嬶紝鑰屼笉鏄洿鎺ユ妸瀹冭涓洪潪灞€鍩熷潔缂┿€傚叿浣撳疄鐜颁笂锛屾祴閲忓彲浠ヨ〃鐜颁负缂濆悗鍚告敹銆佹湁闄愬尯鍩熸崯鑰椼€侀槇鍊兼帰娴嬫垨浜嬩欢淇濈暀瑙勫垯銆? 
One of the most distinctive conceptual choices in the repository is to reduce 鈥渕easurement,鈥?as much as possible, to a local process within the propagation chain rather than treating it immediately as nonlocal collapse. In implementation, measurement may appear as post-slit absorption, finite-region loss, threshold detection, or event-retention rules.

濡傛灉鐢?\(\eta(x,y)\) 琛ㄧず鏌愪釜浣嶇疆鐨勫惛鏀舵瘮渚嬶紝閭ｄ箞涓€涓畝鍗曠殑灞€鍩熷惛鏀惰繃绋嬪彲鍐欐垚锛? 
If \(\eta(x,y)\) denotes the absorption ratio at a given position, then a simple local absorption process can be written as:

\[
\tilde{E}_t(x,y)=\big(1-\eta(x,y)\big)E_t(x,y).
\]

闅忓悗锛孿(\tilde{E}_t(x,y)\) 鍐嶈閫佸叆涓嬩竴姝ヤ紶鎾€傝繖鏍蜂竴鏉ワ紝鈥滄祴閲忊€濅笉鍐嶆槸涓€涓彧鑳藉湪瑙ｉ噴灞傝璋冪敤鐨勬湳璇紝鑰屽彉鎴愪簡浠ｇ爜涓殑鏄惧紡鏈哄埗锛屽彲浠ヨ寮哄急鎵弿銆佷綅缃壂鎻忓拰灏哄鎵弿銆? 
After that, \(\tilde{E}_t(x,y)\) is passed into the next propagation step. In this way, 鈥渕easurement鈥?is no longer a term invoked only at the interpretive level, but becomes an explicit coded mechanism that can be scanned by strength, position, and size.

姝ｅ洜涓烘祴閲忓湪杩欓噷琚満鍒跺寲锛屼粨搴撴墠鑳借繘涓€姝ヨ璁鸿繛缁彉鍖栥€佸欢杩熸彃鍏ャ€佹湁闄愬昂瀵稿惛鏀跺櫒涓庡浘鏍烽€€鐩稿共涔嬮棿鐨勫叧绯汇€傝繖涔熸槸 `ce_04_*` 鍒?`ce_07_*` 浠ュ強閮ㄥ垎 `discover_*` 鑴氭湰鐨勭悊璁鸿捣鐐广€? 
Because measurement is mechanized in this way, the repository can further discuss the relationship between continuous change, delayed insertion, finite-size absorbers, and pattern decoherence. This is the theoretical starting point of `ce_04_*` through `ce_07_*` and part of the `discover_*` scripts.

---

## Chapter 5. Phase, Coherence, and Visibility
## 绗簲绔?鐩镐綅銆佺浉骞蹭笌鍙搴?
鍦ㄦ洿楂樺眰鐨勮剼鏈腑锛屼粨搴撲笉鍙紶鎾兘閲忥紝杩樹細浼犳挱鐩镐綅銆傝嫢鎶婂骞呰涓?\(\psi_t(x,y)=\sqrt{E_t(x,y)}e^{i\phi_t(x,y)}\)锛岄偅涔堜笉鍚岃矾寰勫埌杈惧悓涓€鏍肩偣鏃跺彲鍙戠敓澶嶆暟鍙犲姞锛岃€屾柊鐨勮兘閲忓垯鍙敱妯″钩鏂瑰緱鍒般€? 
In higher-level scripts, the repository propagates not only energy but also phase. If the complex amplitude is written as \(\psi_t(x,y)=\sqrt{E_t(x,y)}e^{i\phi_t(x,y)}\), then different paths arriving at the same lattice site may interfere through complex superposition, and the new energy may be obtained from the squared magnitude.

\[
E_{t+1}(x,y)=|\psi_{t+1}(x,y)|^2.
\]

杩欎竴姝ヤ娇寰椾粨搴撳彲浠ヨ璁衡€滅浉浣嶅叧鑱旀槸鍚︿繚鐣欌€濃€滅浉浣嶅満濡備綍涓庡己搴﹀満鍏卞悓婕斿寲鈥濈瓑闂銆備笉杩囨枃妗ｄ笂蹇呴』鏄庣‘锛岃繖浠嶇劧鏄竴涓ā鍨嬪畾涔夊嚭鏉ョ殑鐩镐綅浼犳挱鏈哄埗锛岃€屼笉鏄鏍囧噯閲忓瓙鐩镐綅缁撴瀯鐨勫畬鏁翠弗鏍煎鍑恒€? 
This step allows the repository to discuss questions such as whether phase correlation is preserved and how a phase field evolves together with an intensity field. However, the documentation must be explicit that this is still a model-defined phase propagation mechanism, not a complete rigorous derivation of the standard quantum phase structure.

鍙岀紳鍥炬牱涓渶閲嶈鐨勯噺涔嬩竴鏄彲瑙佸害锛屼粨搴撲腑甯哥敤鐨勮〃杈炬槸锛? 
One of the most important quantities in double-slit patterns is the visibility, and the repository often uses the expression:

\[
V=\frac{I_{\max}-I_{\min}}{I_{\max}+I_{\min}}.
\]

杩欓噷鐨?\(I_{\max}\) 涓?\(I_{\min}\) 閫氬父浠庡睆骞曞己搴︽洸绾跨殑宄颁笌璋蜂及璁″緱鍒般€傝繖涓畾涔夋湰韬緢缁忓吀锛屼絾鍦ㄤ粨搴撲腑鐨勬剰涔夊苟涓嶅彧鏄弿杩版潯绾癸紝鑰屾槸浣滀负涓€涓法鑴氭湰鍏变韩鎸囨爣锛岀敤鏉ヨ繛鎺ヨ窛绂汇€佽€﹀悎銆佸惛鏀朵笌鍗忚鍙樺寲銆? 
Here, \(I_{\max}\) and \(I_{\min}\) are usually estimated from peaks and valleys in the screen-intensity curve. The definition itself is classical, but its role in the repository is broader than fringe description: it functions as a shared cross-script metric connecting distance, coupling, absorption, and protocol variation.

---

## Chapter 6. Foundational Experiment Tree
## 绗叚绔?鍩虹瀹為獙鏍?
濡傛灉鎶婃暣涓粨搴撶敾鎴愪竴妫垫爲锛岄偅涔堝熀纭€瀹為獙鏄爲骞诧紝鑰屼袱娆′弗鑲冨疄楠屾槸闀垮嚭鏉ョ殑涓ゆ潯涓绘灊銆傚熀纭€瀹為獙棣栧厛寤虹珛浼犳挱鐩磋锛岀劧鍚庢妸鈥滄祴閲忊€濆拰鈥滅浉鍏虫€р€濋€愭鏈哄埗鍖栵紝鏈€鍚庢墠杩涘叆 CHSH 灞傘€? 
If the entire repository is drawn as a tree, then the foundational experiments form the trunk, while the two major experiments are the two main branches growing from it. The foundational experiments first establish propagation intuition, then progressively mechanize 鈥渕easurement鈥?and 鈥渃orrelation,鈥?and only afterward move into the CHSH layer.

`ce_00_double_slit_demo.py` 鏄渶鍩虹鐨勫弻缂濈ず鎰忚剼鏈€傚畠閲囩敤鐨勫吀鍨嬪弬鏁板寘鎷?`WIDTH = 300`銆乣HEIGHT = 200`銆乣A = 1.0`銆乣S = 0.25`銆乣B = 0.05`銆乣LAMBDA = 0.85`銆乣SLIT_WIDTH = 6` 鍜?`STEPS = 300`銆傝繖绫诲弬鏁颁綋鐜板嚭璇ユā鍨嬬殑鍩烘湰鎬ф牸锛氬墠鍚戜紶鎾崰涓诲锛屼晶鍚戣€﹀悎鎻愪緵鎵╂暎涓庡共娑夊嚑浣曪紝鍙嶅悜椤硅緝灏忚€岄潪瀹屽叏涓洪浂銆? 
`ce_00_double_slit_demo.py` is the most basic double-slit illustration script. Its typical parameters include `WIDTH = 300`, `HEIGHT = 200`, `A = 1.0`, `S = 0.25`, `B = 0.05`, `LAMBDA = 0.85`, `SLIT_WIDTH = 6`, and `STEPS = 300`. These parameters already express the basic temperament of the model: forward propagation dominates, lateral coupling provides diffusion and interference geometry, and the backward term is small rather than strictly zero.

`ce_01_visibility_vs_screen_distance.py` 杩涗竴姝ョ爺绌跺彲瑙佸害涓庝紶鎾窛绂荤殑鍏崇郴銆傝鑴氭湰浣跨敤 `A = 1.0`銆乣S = 0.3`銆乣B = 0.05`銆乣LAMBDA = 0.90`銆乣STEPS = 400` 浠ュ強涓€缁?`SCREEN_DISTANCES`銆傝繖鏉″疄楠岀嚎鍦ㄤ粨搴撲腑寰堥噸瑕侊紝鍥犱负鈥滃彲瑙佸害闅忎紶鎾窛绂昏“鍑忊€濇槸妯″瀷璇曞浘寮鸿皟鐨勫彲妫€楠岀壒寰佷箣涓€銆? 
`ce_01_visibility_vs_screen_distance.py` goes further by studying the relation between visibility and propagation distance. It uses `A = 1.0`, `S = 0.3`, `B = 0.05`, `LAMBDA = 0.90`, `STEPS = 400`, and a set of `SCREEN_DISTANCES`. This experimental line is important because 鈥渧isibility decays with propagation distance鈥?is one of the model鈥檚 intended testable signatures.

`ce_04_*` 鍒?`ce_07_*` 鎶婃祴閲忔晥搴旀帹杩涙垚涓€涓彲鎵弿瀵硅薄锛岃€?`ce_08_*` 鍒?`ce_10_*` 鍒欐妸鏀矾浼犳挱銆佺浉浣嶅拰鐩稿叧鎬у甫鍏ユā鍨嬨€傝繖鎰忓懗鐫€ CHSH 灞備笉鏄獊鐒跺嚭鐜扮殑锛岃€屾槸浠庝竴绯诲垪杈冧綆灞傚疄楠屼笂闀垮嚭鏉ョ殑銆? 
`ce_04_*` through `ce_07_*` promote measurement effects into something that can be scanned parametrically, while `ce_08_*` through `ce_10_*` bring branch propagation, phase, and correlation into the model. This means the CHSH layer does not appear abruptly, but grows out of a sequence of lower-level experiments.

---

## Chapter 7. CHSH Protocol Logic
## 绗竷绔?CHSH 鍗忚閫昏緫

杩涘叆 Bell / CHSH 闂鍚庯紝浠撳簱鍏虫敞鐨勯噸鐐逛笉鍐嶅彧鏄浘鏍凤紝鑰屾槸鈥滀簨浠跺浣曢厤瀵光€濆拰鈥滀粈涔堟牱鐨勪簨浠惰繘鍏ョ粺璁♀€濄€傝繖涓€姝ラ潪甯稿叧閿紝鍥犱负浠撳簱鐨勬牳蹇冨垽鏂箣涓€灏辨槸锛氬崗璁湰韬細鏀瑰彉缁撴灉锛岃€屽崗璁笌鏈綋缁撹涓嶈兘琚交鏄撴贩鍚屻€? 
Once the repository enters the Bell / CHSH problem, the focus shifts from patterns to how events are paired and which events are allowed into the statistics. This step is crucial, because one of the central claims of the repository is that protocol itself changes the result, and protocol should not be casually conflated with ontological conclusion.

鍦?`explore_chsh_experiment_alignment.py` 涓紝鏈€灏忎簨浠舵牸寮忔槸 `side, t, setting, outcome`銆傚叾涓?`side` 鍖哄垎 A/B 涓ょ考锛宍setting` 鍙栧€间负 0 鎴?1锛宍outcome` 瑙勮寖鍒?\(\pm 1\)銆? 
In `explore_chsh_experiment_alignment.py`, the minimal event format is `side, t, setting, outcome`. Here `side` distinguishes the A/B wings, `setting` takes values 0 or 1, and `outcome` is normalized to \(\pm 1\).

閰嶅閫昏緫鏄繖鏍风殑锛氳嫢 A 渚т簨浠舵椂闂翠负 \(t_A\)锛孊 渚т簨浠舵椂闂翠负 \(t_B\)锛屼笖婊¤冻 \(|t_A-t_B|\le w\)锛屽垯鍦ㄧ獥鍙?\(w\) 鍐呴€夋嫨鏈€杩戙€佹湭琚崰鐢ㄧ殑 B 浜嬩欢涓庝箣閰嶅銆傝繖鏍峰緱鍒扮殑 paired 鏍锋湰闆嗗悎闅忓悗琚敤浜庤绠楀洓绉嶈缃粍鍚堜笂鐨勭浉鍏抽噺銆? 
The pairing logic is as follows: if the time of an A-side event is \(t_A\), the time of a B-side event is \(t_B\), and \(|t_A-t_B|\le w\), then within the window \(w\) the nearest unused B event is paired with it. The resulting paired sample set is then used to compute the correlations on the four setting combinations.

鐩稿叧閲忕殑鏍囧噯琛ㄨ揪寮忎负锛? 
The standard expression for the correlations is:

\[
E=\frac{N_{++}+N_{--}-N_{+-}-N_{-+}}{N_{\mathrm{total}}}.
\]

CHSH 缁勫悎閲忓垯鍐欐垚锛? 
The CHSH combination is then written as:

\[
S=E(a,b)+E(a,b')+E(a',b)-E(a',b').
\]

浠撳簱涓殑 `strict` 涓?`standard` 骞朵笉淇敼杩欎釜鍏紡锛岃€屾槸淇敼杩涘叆鍏紡鐨勯厤瀵圭獥鍙ｏ紝涔熷氨淇敼浜?paired 鏍锋湰闆嗐€傝繖绉嶁€滄敼鍗忚鑰屼笉鏀瑰叕寮忊€濈殑鍋氭硶锛屾鏄粨搴?CHSH 鐮旂┒绾挎渶鏍稿績鐨勫伐绋嬫€濇兂銆? 
The repository鈥檚 `strict` and `standard` protocols do not modify this formula; they modify the pairing window that determines which samples enter the formula. This 鈥渃hanging the protocol without changing the formula鈥?is the central engineering idea of the repository鈥檚 CHSH research line.

---

## Chapter 8. Major Experiment I: NIST Completeblind Archive
## 绗叓绔?閲嶅ぇ瀹為獙涓€锛歂IST Completeblind 褰掓。鎴?
绗竴娆′弗鑲冨疄楠屼綅浜?`battle_results/nist_completeblind_2015-09-19/`銆傝繖涓嶆槸浠撳簱鍐呴儴鑷敓鎴愭暟鎹笂鐨勬紨绀猴紝鑰屾槸閽堝鍏紑 completeblind 鏁版嵁寤虹珛鐨勪竴鏉″畬鏁村綊妗ｉ摼銆傚畠鐨勯噸瑕佹€у湪浜庯紝瀹冪涓€娆℃妸浠撳簱鐨?CHSH 璁鸿瘉鎺ㄥ悜浜嗗閮ㄦ暟鎹棶棰樸€? 
The first major experiment is located at `battle_results/nist_completeblind_2015-09-19/`. This is not an internal demonstration on self-generated data, but a full archival chain built against public completeblind data. Its importance lies in the fact that it is the first time the repository鈥檚 CHSH reasoning is pushed toward an external-data problem.

绗竴娆″疄楠岀殑棰勬敞鍐岄厤缃敱 `chsh_preregistered_config_nist_index.json` 缁欏嚭銆傚叧閿棬妲涘寘鎷?`strict.window = 0.0`銆乣standard.window = 15.0`銆乣strict_max_S = 2.02`銆乣standard_min_S = 2.0` 鍜?`require_standard_S_gt_strict_S = true`銆傝繖鎰忓懗鐫€姝よ疆瀹為獙骞朵笉婊¤冻浜庣湅鍒?`S > 2`锛岃€屾槸瑕佹眰涓ユ牸鍗忚涓嬬殑 \(S\) 浠嶈鍘嬪湪涓婄晫闄勮繎銆? 
The preregistered configuration for the first experiment is given by `chsh_preregistered_config_nist_index.json`. The key thresholds include `strict.window = 0.0`, `standard.window = 15.0`, `strict_max_S = 2.02`, `standard_min_S = 2.0`, and `require_standard_S_gt_strict_S = true`. This means the experiment is not satisfied merely by seeing `S > 2`; it also requires the strict-protocol value of \(S\) to remain pressed near the upper bound.

鏍规嵁褰掓。缁撴灉鏂囦欢 `battle_result.json`锛宻trict 鍗忚涓嬬殑缁撴灉涓猴細`pair_count = 136632`锛宍Eab = 0.9989774338237003`锛宍Eabp = 0.9980977239045323`锛宍Eapb = 0.9979612207190944`锛宍Eapbp = 0.65876052027544`锛屼互鍙?`S = 2.336275858171887`銆? 
According to the archival result file `battle_result.json`, the strict-protocol result is: `pair_count = 136632`, `Eab = 0.9989774338237003`, `Eabp = 0.9980977239045323`, `Eapb = 0.9979612207190944`, `Eapbp = 0.65876052027544`, and `S = 2.336275858171887`.

standard 鍗忚涓嬬殑缁撴灉涓猴細`pair_count = 148670`锛宍Eab = 0.9918413278942186`锛宍Eabp = 0.9703577587147753`锛宍Eapb = 0.9473404037508701`锛宍Eapbp = 0.07015227532787607`锛屼互鍙?`S = 2.8393872150319877`銆? 
Under the standard protocol, the result is: `pair_count = 148670`, `Eab = 0.9918413278942186`, `Eabp = 0.9703577587147753`, `Eapb = 0.9473404037508701`, `Eapbp = 0.07015227532787607`, and `S = 2.8393872150319877`.

杩欐瀹為獙鐨勪粨搴撶骇鍒ゅ畾鏄?`engineering_pass = true`锛屼絾 `thesis_pass = false`銆傚け璐ュ師鍥犻潪甯告槑纭細  
The repository-level judgment for this experiment is `engineering_pass = true`, but `thesis_pass = false`. The reason for failure is very explicit:

\[
S_{\mathrm{strict}}=2.336276 > 2.02.
\]

杩欎竴鐐归潪甯搁噸瑕侊紝鍥犱负瀹冭鏄庣涓€娆′弗鑲冨疄楠屾渶鏈変环鍊肩殑鍦版柟锛屼笉鏄€滃畠鑳滃埄浜嗏€濓紝鑰屾槸鈥滃畠鎶婂け璐ョ粨璁轰篃褰掓。浜嗏€濄€備粠鐮旂┒鏂规硶璁鸿搴︾湅锛岃繖姣斿崟绾睍绀烘垚鍔熷浘鍍忔洿鏈夊垎閲忋€? 
This is very important, because it shows that the greatest value of the first serious experiment is not that 鈥渋t won,鈥?but that it archived a failed conclusion as well. From the standpoint of research methodology, this carries more weight than merely displaying successful images.

---

## Chapter 9. Major Experiment II: Round 2 / NIST v2 Closure
## 绗節绔?閲嶅ぇ瀹為獙浜岋細Round 2 / NIST v2 鏀舵潫瀹為獙

绗簩娆′弗鑲冨疄楠屼綅浜?`battle_results/nist_round2_v2/`銆傚畠鐨勬剰涔変笉鍙槸鍐嶈窇涓€閬嶆暟鍊硷紝鑰屾槸鍦ㄧ涓€杞熀纭€涓婃妸甯冨眬鍏煎鎬с€佸伐绋嬫槧灏勬晱鎰熸€у拰瑙ｉ噴杈圭晫闂闆嗕腑澶勭悊鎺夛紝鍥犳鏇存帴杩戜竴浠芥寮忕殑鐮旂┒鏀舵潫鏂囨。銆? 
The second major experiment is located at `battle_results/nist_round2_v2/`. Its meaning is not merely to rerun the numbers, but to concentrate on layout compatibility, engineering-mapping sensitivity, and interpretive boundaries on top of the first round, making it closer to a formal research-closure document.

P3 甯冨眬妫€鏌ョ粰鍑轰簡涓€涓叧閿簨瀹烇細training HDF5 涓?completeblind HDF5 骞朵笉鍏变韩鍚屼竴濂楀彲鐩存帴澶嶇敤鐨?grid-side-streams 缁撴瀯銆俙p3_compare_report.json` 琛ㄦ槑 training 鏁版嵁 `grid_side_streams_compatible = false`锛岃€?completeblind 鏁版嵁 `grid_side_streams_compatible = true`銆傝繖涓€姝ラ樆姝簡鏈粡瀹¤鐨勬í鍚戠被姣斻€? 
The P3 layout check yields a key fact: the training HDF5 and completeblind HDF5 do not share a directly reusable grid-side-streams structure. `p3_compare_report.json` shows that the training data have `grid_side_streams_compatible = false`, while the completeblind data have `grid_side_streams_compatible = true`. This step prevents unaudited horizontal analogy.

绗簩杞?engineering 閰嶇疆鐢?`chsh_preregistered_config_nist_round2_engineering.json` 瀹氫箟銆傚叧閿尯鍒湪浜庯細`strict.window = 0.0`锛宍standard.window = 10.0`锛屽苟涓?thesis gate 浣跨敤 `fork_only` 妯″紡锛屽彧瑕佹眰 `S_standard > S_strict`锛岃€屼笉鍐嶆部鐢ㄧ涓€杞殑 `strict_max_S = 2.02` 绾︽潫銆? 
The second-round engineering configuration is defined in `chsh_preregistered_config_nist_round2_engineering.json`. The key differences are that `strict.window = 0.0`, `standard.window = 10.0`, and the thesis gate uses `fork_only` mode, requiring only `S_standard > S_strict` rather than reusing the first-round constraint `strict_max_S = 2.02`.

绗簩杞樉寮忔瘮杈冧簡涓ょ杈撳嚭鏄犲皠锛歚legacy` 涓?`parity`銆傚湪 `ROUND2_ENGINEERING_BATTLE_REPORT.json` 涓紝legacy 鏄犲皠缁欏嚭 `S_strict = 2.336275858171887` 鍜?`S_standard = 2.8445681666863845`锛沺arity 鏄犲皠缁欏嚭 `S_strict = 2.3274283887643272` 鍜?`S_standard = 2.83617087618962`銆? 
The second round explicitly compares two output mappings: `legacy` and `parity`. In `ROUND2_ENGINEERING_BATTLE_REPORT.json`, the legacy mapping yields `S_strict = 2.336275858171887` and `S_standard = 2.8445681666863845`; the parity mapping yields `S_strict = 2.3274283887643272` and `S_standard = 2.83617087618962`.

杩欎袱绉嶆槧灏勪箣闂寸殑宸紓鏄湁闄愯€岀ǔ瀹氱殑锛屾暟鍊间笂琛ㄧ幇涓?`delta_S_strict = -0.00884746940755976` 涓?`delta_S_standard = -0.008397290496764409`銆傝繖璇存槑宸ョ▼鏄犲皠浼氭敼鍙樼粨鏋滐紝浣嗗湪绗簩杞攣瀹氭鏋朵笅锛屾柟鍚戞€у垎鍙夌粨璁哄苟娌℃湁琚帹缈汇€? 
The difference between the two mappings is finite and stable, numerically expressed as `delta_S_strict = -0.00884746940755976` and `delta_S_standard = -0.008397290496764409`. This shows that engineering mapping does change the result, but under the locked second-round framework the directional fork conclusion is not overturned.

鏇村叧閿殑鏄紝绗簩杞繕鎶婂悓涓€鏁版嵁閲嶆柊鏀惧洖绗竴杞?thesis gate 涓嬪洖鏀俱€傜粨鏋滆 `ROUND2_UNDER_ROUND1_GATE.json`锛屽叾涓?legacy 涓?parity 閮戒粛鐒舵槸 `thesis_pass = false`锛屽洜涓?strict 渚х殑 \(S\) 渚濇棫楂樹簬 2.02銆傝繖鏍蜂竴鏉ワ紝绗簩杞苟娌℃湁鈥滅鏀圭涓€杞け璐ョ粨璁衡€濓紝鑰屾槸鍦ㄦ柊鐨勫彊浜嬫鏋朵笅棰濆澧炲姞浜嗕竴灞?engineering closure銆? 
More importantly, the second round also replays the same data under the first-round thesis gate. The result, shown in `ROUND2_UNDER_ROUND1_GATE.json`, is that both legacy and parity still have `thesis_pass = false`, because the strict-side \(S\) remains above 2.02. In this way, the second round does not 鈥渞ewrite away鈥?the first-round failure, but adds an additional engineering closure under a new narrative frame.

---

## Chapter 10. Figure and Artifact Index
## 绗崄绔?鍥剧ず涓庝骇鐗╃储寮?
杩欎釜椤圭洰鐨勫浘绀哄凡缁忓瓨鍦ㄤ簬浠撳簱涓紝鏂扮殑鏂囨。宸ヤ綔涓嶆槸閲嶆柊鐢熸垚瀹冧滑锛岃€屾槸鎶婂畠浠噸鏂扮紪鎺掕繘涓€鏉℃洿娓呮櫚鐨勯槄璇昏矾寰勩€傚熀纭€瀹為獙灞傜殑閲嶈鍥惧寘鎷細`ce_00_double_slit_demo.png`銆乣interference_decay.png`銆乣measurement_effect.png`銆乣finite_absorber.png`銆乣delayed_choice.png`銆乣measurement_phase_diagram.png`銆乣entanglement_simulation.png` 鍜?`entanglement_with_phase.png`銆? 
The figures for this project already exist in the repository, and the task of the new documentation is not to regenerate them, but to reassemble them into a clearer reading path. Important figures from the foundational experiment layer include `ce_00_double_slit_demo.png`, `interference_decay.png`, `measurement_effect.png`, `finite_absorber.png`, `delayed_choice.png`, `measurement_phase_diagram.png`, `entanglement_simulation.png`, and `entanglement_with_phase.png`.

Bell / CHSH 灞傜殑閲嶈鍥惧寘鎷細`chsh_strict_protocol.png`銆乣chsh_strict_vs_postselected.png`銆乣chsh_closure_protocol.png`銆乣chsh_local_wave_closure_full.png`銆乣chsh_experiment_alignment.png`銆乣threshold_detector_clicks.png` 鍜?`bell_chsh_two_tracks.png`銆傝繖浜涘浘鍍忓叡鍚屾瀯鎴愪簡鍗忚鏁忔劅鎬с€佸璁′笌缁撴灉瀵归綈鐨勮瑙夎瘉鎹€? 
Important figures from the Bell / CHSH layer include `chsh_strict_protocol.png`, `chsh_strict_vs_postselected.png`, `chsh_closure_protocol.png`, `chsh_local_wave_closure_full.png`, `chsh_experiment_alignment.png`, `threshold_detector_clicks.png`, and `bell_chsh_two_tracks.png`. Together, these images form the visual evidence for protocol sensitivity, auditing, and result alignment.

褰掓。灞傜殑閲嶈 JSON 浜х墿鍖呮嫭锛氱涓€娆″疄楠岀殑 `battle_result.json`锛岀浜屾瀹為獙鐨?`ROUND2_ENGINEERING_BATTLE_REPORT.json`銆乣ROUND2_UNDER_ROUND1_GATE.json` 鍜?`p3_compare_report.json`銆傝繖浜涙枃浠舵槸鐪熸鐨勨€滅‖缁撴灉鈥濓紝鍥犱负闃堝€煎垽鏂拰缁撹閿佸畾閮芥渶缁堣惤鍦ㄨ繖閲屻€? 
Important JSON artifacts from the archival layer include the first experiment鈥檚 `battle_result.json`, and the second experiment鈥檚 `ROUND2_ENGINEERING_BATTLE_REPORT.json`, `ROUND2_UNDER_ROUND1_GATE.json`, and `p3_compare_report.json`. These files are the true 鈥渉ard results,鈥?because the threshold judgments and conclusion locks ultimately live there.

---

## Chapter 11. Interpretive Boundaries
## 绗崄涓€绔?瑙ｉ噴杈圭晫

杩欎釜椤圭洰鐨勪竴澶т紭鐐癸紝鏄畠骞朵笉鎶婃墍鏈夋暟鍊肩幇璞￠兘鑷姩涓婂崌涓烘湰浣撶粨璁恒€備粨搴撲腑鐨?`explore_critique_*` 绯诲垪銆乣BELL_PROTOCOL_NOTE.md` 浠ュ強绗簩杞敹鏉熸枃妗ｏ紝閮藉湪涓嶆柇鎻愰啋锛氱幇璞°€佸崗璁€佽В閲婏紝鏄笁涓笉鍚屽眰娆°€? 
One of the major strengths of this project is that it does not automatically elevate every numerical phenomenon into an ontological conclusion. The repository鈥檚 `explore_critique_*` series, `BELL_PROTOCOL_NOTE.md`, and the second-round closure documents all repeatedly remind us that phenomenon, protocol, and interpretation are three different levels.

鍩轰簬褰撳墠浠ｇ爜鍜屽綊妗ｏ紝杈冧负瀹夊叏鐨勮娉曟槸锛氳繖濂楃鏁ｅ眬鍩熸ā鍨嬭兘澶熷湪鑻ュ共鍦烘櫙涓嬬敓鎴愮被骞叉秹銆佺被娴嬮噺鎵板姩鍜岀被鐩稿叧鎬х粨鏋勶紱CHSH 缁撴灉瀵归厤瀵圭獥鍙ｃ€佹槧灏勫拰浜嬩欢淇濈暀瑙勫垯鍗佸垎鏁忔劅锛涗袱杞弗鑲冨疄楠屽凡缁忔妸鈥滃伐绋嬮€氳繃鈥濆拰鈥滆鐐归€氳繃鈥濆垎灞傚啓娓呮銆? 
Based on the current code and archives, a relatively safe statement is that this discrete local model can generate interference-like patterns, measurement-like disturbances, and correlation-like structures in several scenarios; CHSH results are highly sensitive to pairing windows, mappings, and event-retention rules; and the two major experiments have already separated 鈥渆ngineering passed鈥?from 鈥渢hesis passed鈥?in explicit form.

鐩稿簲鍦帮紝褰撳墠浠撳簱骞朵笉鑳界洿鎺ユ敮鎸佸涓嬭娉曪細瀹冨凡缁忔帹缈绘爣鍑嗛噺瀛愮悊璁猴紝瀹冨凡缁忎粠鏍肩偣妯″瀷涓ユ牸鎺ㄥ嚭鐙箟鐩稿璁猴紝鎴栬€呭畠宸茬粡鍑€熷唴閮ㄦ暟鍊肩粨鏋滆瘉鏄庝簡鏌愮涓€鑸摬瀛︽剰涔変笂鐨勯潪灞€鍩熸垨灞€鍩熸湰浣撶粨璁恒€? 
Correspondingly, the current repository cannot directly support statements such as: it has overthrown standard quantum theory, it has rigorously derived special relativity from a lattice model, or it has proven some general philosophical conclusion about locality or nonlocality purely from its internal numerical results.

浠庡鏈啓浣滅殑瑙掑害鐪嬶紝鐪熸浣块」鐩樉寰楁垚鐔熺殑锛屼笉鏄帾杈炴縺杩涳紝鑰屾槸杈圭晫娓呮銆傝繖涓粨搴撴渶鍊煎緱鐝嶆儨鐨勫湴鏂逛箣涓€锛屽氨鏄畠宸茬粡寮€濮嬩富鍔ㄥ啓鍑鸿繖浜涜竟鐣屻€? 
From the standpoint of scholarly writing, what makes a project look mature is not aggressive rhetoric, but clear boundaries. One of the most valuable aspects of this repository is that it has already begun to write those boundaries explicitly.

---

## Chapter 12. Optimization Proposal
## 绗崄浜岀珷 浼樺寲鏂规

涓轰簡璁╄繖涓」鐩€氳繃鏂囨。鏇村厖鍒嗗湴浣撶幇浠峰€硷紝鎴戝缓璁皢鏂囨。绯荤粺鍥哄畾涓轰笁灞傘€傜涓€灞傛槸鍏ュ彛灞傦紝鍗冲綋鍓嶇殑 `README.md`锛屽畠璐熻矗鐢ㄥ敖閲忕煭鐨勭瘒骞呭憡璇夎鑰呪€滆繖涓」鐩槸浠€涔堛€侀噸鐐瑰湪鍝噷銆佽鍏堣浠€涔堚€濄€? 
To let the value of this project emerge more fully through documentation, I recommend fixing the documentation system into three layers. The first layer is the entry layer, namely the current `README.md`, whose role is to tell the reader in as little space as possible what the project is, where the center lies, and what should be read first.

绗簩灞傛槸鎬绘枃妗ｅ眰锛屽嵆鏈枃浠躲€傚畠搴旈暱鏈熶繚鎸佲€滃儚涓€鏈功鈥濈殑缁撴瀯锛岀ǔ瀹氭壙鎷呮ā鍨嬪師鐞嗐€佹暟瀛﹁〃杈俱€佸疄楠屼富绾裤€佺粨鏋滆〃涓庤В閲婅竟鐣岀殑鍔熻兘锛屽苟鎴愪负寮曠敤鏃剁殑涓昏鏂囨。鍏ュ彛銆? 
The second layer is the monograph layer, namely this file. It should permanently keep a book-like structure, stably carrying the roles of model principles, mathematical expressions, the main experimental line, result tables, and interpretive boundaries, and serve as the primary document entry for citation.

绗笁灞傛槸 battle 瀛愮洰褰曚腑鐨勫疄楠屽綊妗ｅ眰銆傚悗缁渶鍊煎緱缁х画浼樺寲鐨勶紝涓嶆槸澧炲姞鏇村闆舵暎鑴氭湰锛岃€屾槸鎶?`battle_results` 涓嬬殑鍏抽敭鏂囨。缁熶竴鏀瑰啓鎴?UTF-8銆佸弻璇€佺粨鏋勫寲琛ㄨ堪锛岃涓よ疆涓ヨ們瀹為獙鐪熸鍏峰鈥滃彲瀵瑰鎻愪氦鈥濈殑璐ㄦ劅銆? 
The third layer is the experimental archival layer inside the `battle_results` subdirectories. The most worthwhile future optimization is not to add more scattered scripts, but to rewrite the key documents under `battle_results` into UTF-8, bilingual, and structurally organized form, so that the two major experiments truly acquire the quality of something ready for external presentation.

鍚屾椂锛屽缓璁澶栧鍔犱竴涓€滃浘琛ㄦ€荤储寮曗€濇枃妗ｏ紝鎶婃牳蹇?PNG銆丣SON銆侀厤缃枃浠跺拰缁撹瀵瑰簲璧锋潵銆傝繖鏍峰仛浼氭瀬澶у寮哄彲妫€绱㈡€э紝涔熸湁鍒╀簬鍚庣画杞垚 PDF銆佹姇閫掕鏄庢垨椤圭洰灞曠ず銆? 
At the same time, I recommend adding a separate 鈥渕aster figure and artifact index鈥?document that links core PNGs, JSON files, configuration files, and conclusions. This would greatly improve retrievability and would also help with later conversion to PDF, submission packets, or project presentation.

---

## Conclusion
## 缁撹

濡傛灉鎶婅繖涓粨搴撶湅浣滀竴鏈功锛岄偅涔堝畠涓嶆槸涓€鏈甯冩渶缁堢瓟妗堢殑涔︼紝鑰屾槸涓€鏈睍绀哄浣曟妸涓€绉嶆浛浠ｆ€ф満鍒惰鐪熸帹杩涘埌鈥滃彲杩愯銆佸彲瀹¤銆佸彲褰掓。銆佷篃鍙け璐モ€濈殑涔︺€傚畠鐪熸鐨勫垎閲忥紝涓嶅湪鍙ｅ彿锛岃€屽湪宸ヤ欢銆? 
If this repository is read as a book, then it is not a book announcing a final answer, but a book showing how an alternative mechanism can be seriously advanced to the point of being executable, auditable, archivable, and also capable of failing. Its real weight lies not in slogans, but in artifacts.

鍦ㄨ繖涓剰涔変笂锛屾湰娆℃枃妗ｄ紭鍖栫殑鐩爣骞朵笉鏄浛椤圭洰澶稿紶缁撹锛岃€屾槸甯姪椤圭洰鎶婄湡姝ｆ湁浠峰€肩殑涓滆タ鏄鹃湶鍑烘潵锛氭ā鍨嬮€昏緫銆佸疄楠岃矾寰勩€佹暟鍊肩粨鏋溿€佽竟鐣屾剰璇嗭紝浠ュ強涓ゆ涓ヨ們瀹為獙鐣欎笅鐨勭爺绌剁棔杩广€? 
In that sense, the goal of this documentation optimization is not to exaggerate the project鈥檚 conclusions, but to reveal what is genuinely valuable in it: the model logic, the experimental path, the numerical results, the awareness of limits, and the research trace left behind by the two major experiments.

