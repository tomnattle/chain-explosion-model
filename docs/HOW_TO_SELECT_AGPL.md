# Hosting platform license pickers (AGPL + CC BY-NC-ND) / 平台许可证选项说明

This note explains how to **find the right row** when a site’s search box does not match SPDX strings like `AGPL-3.0-or-later` or `CC-BY-NC-ND-4.0`.

---

## Software: AGPL-3.0-or-later / 软件：AGPL-3.0-or-later

Your repository already ships the **full GNU Affero General Public License v3** text in `LICENSE`, and the project intent is **AGPL-3.0-or-later** (see `NOTICE` and `REUSE.toml`).

## Why search fails / 为什么搜不到 “AGPL-3.0-or-later”

Many UIs only list **short names** or **SPDX IDs without the `-or-later` suffix**. Typing `AGPL-3.0-or-later` into a license search box often returns **no match**.

Use these keywords instead / 请改用这些关键词：

- `Affero`
- `AGPL`
- `GNU Affero`
- ` Affero General Public`

## GitHub / GitHub

1. Open **Settings → General → License** (or add `LICENSE` via the license template picker).
2. Choose **GNU Affero General Public License v3.0**.
3. If you need the explicit “or later” wording, keep using the standard recommended license header in `NOTICE` / per-file SPDX (`AGPL-3.0-or-later`) — GitHub’s dropdown label may still show `AGPL-3.0`.

Reference: SPDX identifier list — `AGPL-3.0-or-later` is valid even if the UI shows a shorter label.

## Zenodo / Zenodo

1. In the deposit form, pick **GNU Affero General Public License v3 (AGPL-3.0)** or the closest **GNU Affero** entry.
2. Add a one-line clarification in the description:

   `Software license: AGPL-3.0-or-later (see repository LICENSE + NOTICE).`

## Narrative docs: CC BY-NC-ND 4.0 / 文稿与叙述性文档：CC BY-NC-ND 4.0

Manuscripts and narrative materials under `papers_final/` and `docs/` are **CC BY-NC-ND 4.0** (see `LICENSE-DOCS.md`, SPDX `CC-BY-NC-ND-4.0`).

### Why search fails / 为什么搜不到 `CC BY-NC-ND 4.0` 或 `LICENSE-DOCS.md`

Platforms rarely index your repo filename. They list the **legal name** of the deed, not `LICENSE-DOCS.md`. The SPDX id `CC-BY-NC-ND-4.0` also often **does not** appear as a searchable token.

Use these keywords instead / 请改用这些关键词：

- `Creative Commons`
- `Attribution`
- `NonCommercial` or `Non-Commercial`
- `NoDerivatives` or `No Derivatives`
- `4.0` and `International`

### What to pick / 应选哪一项

Choose the entry whose full label matches (or is closest to):

**Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International**

Abbreviations you may see: **CC BY-NC-ND 4.0**, **CC-BY-NC-ND-4.0**.

Do **not** pick BY-NC-SA, BY-SA, or “NC” without “ND” unless you intend to change the license.

### Zenodo / Zenodo

1. Open the **License** (or **Rights**) field and browse the **Creative Commons** family.
2. Select **CC BY-NC-ND 4.0** / **Attribution-NonCommercial-NoDerivatives 4.0 International**.
3. If the deposit is **one record for the whole repo** and the form allows **only one** license, either:
   - pick the license that matches the **primary** artifact you are archiving, and add a short line in **Description** for the other part (e.g. software AGPL vs manuscripts CC), **or**
   - split software and manuscripts into **separate deposits** so each record’s license matches its files.

### GitHub / GitHub

The default **Add license** template list may not include all CC variants. For the **repo** license, many projects keep **AGPL** as the root `LICENSE` and state **CC BY-NC-ND for `papers_final/`** in `NOTICE` / `LICENSE-DOCS.md` (as this repo does). That is normal for **dual-licensed** trees.

---

## Canonical files in this repo / 本仓库权威文件

- `LICENSE` — full AGPLv3 license text
- `NOTICE` — human-readable dual licensing summary
- `LICENSE-DOCS.md` — CC BY-NC-ND 4.0 for narrative docs/manuscripts
- `REUSE.toml` — SPDX annotations for software vs docs paths
