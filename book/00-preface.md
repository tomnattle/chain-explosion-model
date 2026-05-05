# 序言

## 假大象

假如光是一头大象。

几百年来，所有人都在摸这头大象，写下各自的测量结果。有人摸到了象腿，写出了经典力学；有人摸到了象耳，写出了波动方程；有人摸到了象鼻，写出了量子力学。每一套描述都是真实的，但没有人见过完整的大象。

我没有摸过真正的大象。我只是一个对未知好奇、对哲学感兴趣、对人类未来有一点危机感的普通人。我没有受过正规的物理学训练，我不低于任何人，也不高于任何人。我只是想做一件事：画一头假大象，让所有测量真大象的工具来测量我画的这头，看看哪些能通过，哪些不能。

通过的，说明我在那个维度画对了一些东西。没通过的，说明我的假大象在那里有缺陷——也可能问题不在「谁错了」，而在于：**记录与统计协议是否足够透明**：如何把连续响应映射成离散结果、事件如何配对、分母如何选取。

这些层面值得被认真审视；它与工程上可复现、预先固定规则的审计式阅读是同一类诚实，而不是对具体实验者的人身否定。

**文稿导航（卷前与第一单元）**  
阅读顺序建议：`00-preface.md`（本序言）→ `01-appendix-three-phrasings.md`（三种口语、离散核，可选）→ 第1–3章正文（见 `02-contents.md` 路径）→ 第4章起遵 `00-unified-writing-scheme.md`；**Bell / GHZ 背景档案**见 `06-archive-bell.md`、`07-archive-ghz.md`。全书目录与章节文件见 `02-contents.md`。

**零基础读者**：章首不再设大块「导读框」，以免打断叙事；**专业词在正文里第一次需要处用一句话带过**即可。若你只想跟故事、不深究脚本，抓住各章主线仍读得下去；**想决定读到哪里为止**，可看**第2、5、14章**末尾的**分层路标**（见 `book/REVISION_PLAN_NARRATIVE_LAYERING.md` 方案说明）。

## 全书读法与边界（写在前面一次）

为避免**频繁打断**你的注意力，下列各条**在序言里写清一次**；**章内正文不再逐段复述**，除非当下句子离开这一条就会必然被误读。

1. **非法典**：本书不是「已写进教科书并由共同体盖棺定论」的定理汇编；推理、类比与数值示例**可错、可改**，以各章写明的定义、协议与数据来源为准。
2. **非本体论推销**：插图或口语里的「透明果冻」「连续背景」「介质」等，是为**眼睛与推演**服务的脚手架；**不**据此宣称「真空中存在机械以太」或替某种宇宙图景下判决书。
3. **非人身、非阴谋**：讨论的是记录、协议与统计对象是否透明，**不是**对具体实验者或机构的人身否定。
4. **与「反科学」脱钩**：声明边界，是为了**少误读**、把力气用在可复核的步骤上，而不是示弱或讨好。

涉及 Bell、GHZ 与公开数据的部分，我会把**模型内的数值实验**与**对公开记录与协议的审计式讨论**分开写清。公开测量文件对「连续物理图像」而言往往是**不完备的**；本书在承认这一点的前提下，仍讨论同一记录上**不同统计对象**会讲出怎样不同的故事。书中若出现 CHSH 等具体数值，**以各章对统计定义与数据来源的说明为准**，避免把序言里的比喻直接当成实验判决书。

我不回避失败：书里有章节与后记，诚实记录没通过与仍开放的部分。

这本书不挑战任何人。现有的物理学公式是人类几百年积累的智慧，我无意推翻它们。「推翻」这个词带着一种对抗的气息，而我内心没有对抗。我只是提供另一种语言——一种从球面波出发的语言——让有兴趣的人自己判断它是否有用。

我大概率是错的。这无法避免。

我的身体是宇宙元素的一次临时组合，我的思想是这次组合短暂产生的一点涟漪。人类一直在尝试认识自己，一直在修订昨日暂定的自画像——这本身就是我们存在的方式。我们是宇宙暂时借用的一种形态，我们和宇宙彼此包含。

所以这本书不是答案，是一次涟漪。它扩散出去，碰到什么，产生什么新的涟漪，我无法预知，也不需要预知。书里有未完成的地方，有开放的问题，有诚实的边界。我把这条口子挖开，后面的事交给后来者。



王　辉  
2026年5月4日



---

# Preface

## A fake elephant

Imagine light is an elephant.

For centuries, everyone has been touching this elephant and recording their findings. Some felt the leg and wrote classical mechanics. Some felt the ear and wrote wave equations. Some felt the trunk and wrote quantum mechanics. Every description is real — but no one has seen the whole elephant.

I have never touched the real elephant. I am an ordinary person — curious about the unknown, drawn to philosophy, quietly worried about the human future. I have no formal physics training. I am not below anyone, and I am not above anyone. I simply want to do one thing: draw a fake elephant, and use every tool designed to measure the real one to test my drawing.

Where the measurements pass, I may have gotten something right. Where they fail, my drawing may have a flaw — or the issue may not be “who is wrong,” but whether the **record and statistical protocol are transparent enough**: how continuous responses are mapped to discrete outcomes, how events are paired, and how denominators are chosen.

Those layers deserve scrutiny; they belong to the same kind of honesty as reproducible, preregistered audit-style reading, not a personal verdict on any experimenter.

**Navigating the front matter (through Part I)**  
Suggested reading order: `00-preface.md` (this file) → `01-appendix-three-phrasings.md` (three phrasings of the model; optional) → Chapters 1–3 via the paths listed in `02-contents.md` → from Chapter 4 onward, follow `00-unified-writing-scheme.md`. **Bell / GHZ background archives**: `06-archive-bell.md`, `07-archive-ghz.md`. The full table of contents and chapter files: `02-contents.md`.

**If you are not a physicist**: there are **no** large chapter-opening “for general readers” boxes anymore — jargon is glossed **in-line** when it first matters. If you want to decide **how deep to read**, see the short **layer cues** at the ends of **Chapters 2, 5, and 14**, and **`book/REVISION_PLAN_NARRATIVE_LAYERING.md`**.

## How to read this book — boundaries stated once

To avoid **constant footnotes** that pull you out of the narrative, the following is stated **once in this preface**; the main text **does not repeat** it paragraph by paragraph unless a sentence would otherwise be misread.

1. **Not a textbook of finished laws** — claims, analogies, and numbers can be wrong or revised; trust the definitions, protocols, and data sources spelled out in each chapter.
2. **Not selling an ontology** — visual aids (“clear jelly,” “continuous backdrop,” “medium”) are scaffolding for intuition and calculation, **not** a claim that mechanical ether fills the vacuum or that a final picture of reality is settled.
3. **Not ad hominem** — scrutiny targets transparency of records and statistics, **not** personal verdicts on experimenters or labs.
4. **Not “anti‑science” by posture** — boundaries exist to **reduce misreading** and keep effort on auditable steps.

Where Bell, GHZ, and public data appear, I separate **in-model numerical experiments** from **audit-style discussion of public records and protocols**. Published measurement files are often **incomplete as a full continuous picture**; still, the book asks what **different statistical objects** say when applied to the **same** record. Any headline CHSH-style numbers are **binding only to the definitions and data sources stated in each chapter**, not to metaphors in this preface.

I do not avoid failure: chapters and the afterword record what did not pass and what remains open.

This book challenges no one. The existing equations of physics represent centuries of human wisdom. I have no intention of overturning them. The word “overturn” carries a combative energy I do not feel. I only offer another language — a language that starts from spherical waves — and let interested readers judge for themselves whether it is useful.

I am most likely wrong. That cannot be avoided.

My body is a temporary arrangement of the universe’s elements. My thoughts are a small ripple produced by that arrangement, briefly. Humanity has always tried to understand itself, always revised yesterday’s working pictures — and that is simply how we exist. We are a form the universe borrows for a while. We and the universe contain each other.

So this book is not an answer. It is a ripple. Where it spreads, what it touches, what new ripples it creates — I cannot know, and I do not need to know. There are unfinished parts here, open questions, honest boundaries. I dig this opening. What comes next belongs to those who follow.



Hui Wang  
May 4, 2026