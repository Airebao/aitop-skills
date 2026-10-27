# -*- coding: utf-8 -*-
"""重建 dist：frontmatter 同时保留 name+description（服务端要求）与 slug/version/displayName/summary/license。

一母两版（airebao.com 中文站 / aitop.news 英文站），每个 slug 出两份包：
`<slug>-<version>` 是中文版，`<slug>-<version>-en` 是英文版。dist 目录名带版本号，
所以两版靠包名后缀区分而不是靠目录——SkillHub 的索引按包名收敛，同名会互相覆盖。

用法：python scripts/_sk_build_dist.py
"""
import io
import os
import re
import json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = os.path.join(REPO, "scripts", "build-skills.py")
SRC_SAT = os.path.join(REPO, "frontend", "public", "skills")
SRC_MAIN = os.path.join(REPO, "frontend", "public", "aitop-skill")
LICENSE = "MIT"

EDITIONS = {"zh": "", "en": "-en"}

# 手工维护、不在 SKILLS 条目里的卫星包
EXTRA = ["ai-editorial", "ai-changelog"]

# 主包的别名（马甲）：正文跟着主包走，只有包名和展示名不同，且只投放中文站。
# 它们由 scripts/build-skill-aliases.py 产出，没有 en 子目录，所以只在 zh 这一轮打包。
ALIASES = ["airebao", "airibao", "aitop"]

# 原 slug 被他人占用后的品牌前缀替代包，同样只投放中文站（英文版未被占用）。
# 原包继续发（发布是成功的），替代包负责让用户真正装得到。
RENAMES = ["airebao-news", "airebao-daily", "airebao-tools"]

with io.open(BS, "r", encoding="utf-8", errors="replace") as f:
    src = f.read()
AITOP_VERSION = re.search(r'^VERSION\s*=\s*"([^"]+)"', src, re.M).group(1)
VERSION = ".".join((AITOP_VERSION.split(".") + ["0", "0"])[:3])
DIST = os.path.join(REPO, "dist", "skillhub-" + VERSION)

# 解析 SKILLS 条目
start = src.index("SKILLS = [")
body = src[start:]
idxs = [m.start() for m in re.finditer(r'"slug":\s*"', body)] + [len(body)]
sat = []
for i in range(len(idxs) - 1):
    blk = body[idxs[i]:idxs[i + 1]]

    def g(key, b=blk):
        m = re.search(r'"%s":\s*"((?:[^"\\]|\\.)*)"' % key, b)
        return m.group(1) if m else None

    if g("slug") and g("title"):
        sat.append({"slug": g("slug"), "displayName": g("title"), "summary": g("description")})

# (包名 slug, SKILL.md 所在目录)
packages = []
for ed, suffix in EDITIONS.items():
    main_src = SRC_MAIN if ed == "zh" else os.path.join(SRC_MAIN, ed)
    packages.append(("aitop-skill", main_src, ed, suffix))
    for s in sat:
        sat_src = os.path.join(SRC_SAT, s["slug"]) if ed == "zh" else os.path.join(SRC_SAT, s["slug"], ed)
        packages.append((s["slug"], sat_src, ed, suffix))
    # ai-editorial 不在 build-skills.py 的 SKILLS 里（接口形状 /articles 不属于任何
    # 母版，由 scripts/build-manual-skills.py 单独产出），但它同样要进 dist。
    for extra in EXTRA:
        x_src = os.path.join(SRC_SAT, extra) if ed == "zh" else os.path.join(SRC_SAT, extra, ed)
        packages.append((extra, x_src, ed, suffix))
    if ed == "zh":
        for alias in ALIASES + RENAMES:
            packages.append((alias, os.path.join(SRC_SAT, alias), ed, suffix))

os.makedirs(DIST, exist_ok=True)

report = []
skipped = []
for slug, src_dir, ed, suffix in packages:
    src_md = os.path.join(src_dir, "SKILL.md")
    if not os.path.exists(src_md):
        skipped.append("%s/%s" % (ed, slug))
        continue

    with io.open(src_md, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    # 取原文的 name / description（保留服务端要求的字段原值）
    old_name = slug
    old_desc = ""
    display = slug
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            head = raw[:end]
            m = re.search(r"^name:\s*(.+)$", head, re.M)
            if m:
                old_name = m.group(1).strip()
            m = re.search(r"^description:\s*(.+)$", head, re.M)
            if m:
                old_desc = m.group(1).strip()
            raw = raw[end + 4:].lstrip("\n")
    m = re.search(r"^#\s+(.+)$", raw, re.M)
    if m:
        display = m.group(1).strip()

    # displayName 带上版本归属，否则索引页上两版同名分不出来
    display_out = display if ed == "zh" else "%s (EN)" % display

    outdir = os.path.join(DIST, "%s-%s%s" % (slug, VERSION, suffix))
    os.makedirs(outdir, exist_ok=True)
    package_slug = slug + suffix

    # 服务端必需: name + description；社区索引: slug/version/displayName/summary/license
    fm = (
        "---\n"
        "name: %s\n"
        "slug: %s\n"
        "version: %s\n"
        "displayName: %s\n"
        "summary: %s\n"
        "license: %s\n"
        "edition: %s\n"
        "description: %s\n"
        "---\n\n" % (old_name + suffix, package_slug, VERSION, display_out,
                     (old_desc or display).replace("\n", " ").strip(), LICENSE,
                     ed, old_desc.replace("\n", " ").strip())
    )
    with io.open(os.path.join(outdir, "SKILL.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(fm + raw)

    meta = {"slug": package_slug, "version": VERSION, "edition": ed,
            "displayName": display_out, "summary": old_desc or display, "license": LICENSE}
    with io.open(os.path.join(outdir, "_meta.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    report.append(meta)

if skipped:
    print("缺少 SKILL.md 已跳过:", ", ".join(skipped))

with io.open(os.path.join(DIST, "results.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump({"version": VERSION, "editions": list(EDITIONS), "packages": report},
              f, ensure_ascii=False, indent=2)
    f.write("\n")

print("rebuilt:", len(report), "->", DIST)
for r in report:
    print("  %-6s %-14s %s" % (r["edition"], r["slug"], r["displayName"]))
