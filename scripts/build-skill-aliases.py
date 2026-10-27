# -*- coding: utf-8 -*-
"""生成主包的别名包（马甲）。

线上有一批历史 slug（airebao / airibao / aitop 等）早就发布过，内容都是同一份
「AITOP 资讯助手」的旧版。它们的作用是分发入口与搜索覆盖，包名和展示名各不相同，
正文没必要各自维护一份——跟着主包走就行。

所以这里以主包中文版（frontend/public/aitop-skill/SKILL.md）为唯一正文来源，
只换 frontmatter 的 name/description 和一级标题（= 索引页的 displayName），
保持每个马甲自己的展示名不变、内容随主包升级。

X-AITOP-Client 仍报 aitop-skill/1.x：马甲与主包是同一个 skill，后端统计应当
合并到主入口，不按安装入口拆开。

同一份脚本还负责另一类包：**slug 被他人占用后的品牌前缀替代包**。社区源允许
不同 namespace 存在同名 slug，所以 `ai-news` 这类通用名发布得出去，但搜索和
`skillhub install ai-news` 会命中别人的包。给它们换一个带品牌前缀的 slug，
正文照搬原包，用户才装得到。

用法：python scripts/build-skill-aliases.py
"""
import io
import os
import re
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "frontend", "public")
MAIN = os.path.join(PUB, "aitop-skill", "SKILL.md")
ZIP_TIME = (2026, 8, 5, 0, 0, 0)

# (slug, 展示名). 展示名沿用线上已有值，避免把历史上积累的搜索认知冲掉。
ALIASES = [
    ("airebao", "AI新闻 AI TOP NEWS"),
    ("airibao", "全球AI新闻【官方 AITOP.NEWS】"),
    ("aitop", "AIHOT AITOP日报"),
]

# (原 slug, 替代 slug)。原 slug 在社区源上已被他人占用，这里只改包名与展示名，
# 正文照搬原包；只投放中文站，英文版（ai-news-en 等）没有被占用，不受影响。
RENAMES = [
    ("ai-news", "airebao-news"),
    ("ai-daily", "airebao-daily"),
    ("ai-tools", "airebao-tools"),
]

# 替代包的展示名前缀：与 ai-news 等原包在索引页上同名会分不出来
RENAME_PREFIX = "AI热报"

DESCRIPTION = (
    "查询、搜索和展开 AITOP 的 AI 行业动态与每日精编日报。"
    "用于“今天 AI 圈发生了什么”、近期模型/产品/论文/行业动态、指定关键词搜索、"
    "AITOP 日报、资讯详情、来源核对和原文引用等请求。"
)


def split_main(text):
    """拆掉主包的 frontmatter 与一级标题，返回剩余正文。"""
    body = text
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4:].lstrip("\n")
    lines = body.split("\n")
    out = []
    dropped = False
    for ln in lines:
        if not dropped and ln.startswith("# "):
            dropped = True
            continue
        out.append(ln)
    return "\n".join(out).lstrip("\n")


def render(body, slug, display):
    # 正文整体沿用主包，包括正文里指向主包安装页的自我更新链接和 X-AITOP-Client
    # 标识：马甲内容等同主包，把用户引导到主包入口是正确的，不需要改写。
    return (
        "---\n"
        "name: %s\n"
        "description: %s\n"
        "---\n\n"
        "# %s\n\n%s" % (slug, DESCRIPTION, display, body)
    )


def render_rename(raw, old_slug, new_slug):
    """把卫星包整体换一个 slug：frontmatter 的 name、安装页自我更新链接跟着改，
    其余正文（含 X-AITOP-Client）原样保留。

    自我更新链接必须改：它写的是 `https://airebao.com/skills/<slug>/`，留着原值
    会把用户引导回那个装不到的旧入口。
    """
    head = ""
    body = raw
    name = old_slug
    desc = ""
    display = old_slug
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            head = raw[:end]
            m = re.search(r"^name:\s*(.+)$", head, re.M)
            if m:
                name = m.group(1).strip()
            m = re.search(r"^description:\s*(.+)$", head, re.M)
            if m:
                desc = m.group(1).strip()
            body = raw[end + 4:].lstrip("\n")

    m = re.search(r"^#\s+(.+)$", body, re.M)
    if m:
        display = m.group(1).strip()
        body = body[:m.start()] + "# %s %s" % (RENAME_PREFIX, display) + body[m.end():]

    old_link = "https://airebao.com/skills/%s/" % old_slug
    new_link = "https://airebao.com/skills/%s/" % new_slug
    assert old_link in body, "%s 正文里找不到自我更新链接 %s" % (old_slug, old_link)
    body = body.replace(old_link, new_link)

    return (
        "---\n"
        "name: %s\n"
        "description: %s\n"
        "---\n\n%s" % (new_slug, desc, body)
    )


def pack(zip_path, text):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo("SKILL.md", date_time=ZIP_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, text.encode("utf-8"))


def main():
    with io.open(MAIN, encoding="utf-8", newline="") as f:
        body = split_main(f.read())

    # 主包正文必须是原始形态：一级标题已从 body 剥离，且 X-AITOP-Client 仍报
    # 主入口，说明没有被某个马甲的渲染结果污染。
    assert not body.startswith("# "), "正文里还留着一级标题"
    assert "aitop-skill/" in body, "主包正文里找不到 X-AITOP-Client 标识"

    print("[别名包] 源: frontend/public/aitop-skill/SKILL.md")
    for slug, display in ALIASES:
        md = render(body, slug, display)
        d = os.path.join(PUB, "skills", slug)
        os.makedirs(d, exist_ok=True)
        with io.open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        pack(os.path.join(d, "SKILL.zip"), md)

        assert md.startswith("---\nname: %s\n" % slug), "%s 的 frontmatter 不对" % slug
        assert "\n# %s\n" % display in md, "%s 的一级标题没写对" % slug
        print("  %-10s %-28s %6d chars" % (slug, display, len(md)))

    print("\n%d 个别名包 -> frontend/public/skills/" % len(ALIASES))

    print("\n[替代包] slug 被他人占用，改品牌前缀重新投放")
    for old_slug, new_slug in RENAMES:
        src_md = os.path.join(PUB, "skills", old_slug, "SKILL.md")
        with io.open(src_md, encoding="utf-8", newline="") as f:
            md = render_rename(f.read(), old_slug, new_slug)

        d = os.path.join(PUB, "skills", new_slug)
        os.makedirs(d, exist_ok=True)
        with io.open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        pack(os.path.join(d, "SKILL.zip"), md)

        assert md.startswith("---\nname: %s\n" % new_slug), "%s frontmatter 不对" % new_slug
        assert "https://airebao.com/skills/%s/" % new_slug in md, "%s 的更新链接没换" % new_slug
        assert "https://airebao.com/skills/%s/" % old_slug not in md, "%s 仍指向旧入口" % new_slug
        print("  %-14s <- %-11s %6d chars" % (new_slug, old_slug, len(md)))

    print("\n%d 个替代包 -> frontend/public/skills/" % len(RENAMES))


if __name__ == "__main__":
    main()
