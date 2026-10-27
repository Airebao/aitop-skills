# AI热报 / AITOP Skills

多源 AI 资讯聚合 + AI 评分平台（[airebao.com](https://airebao.com) 中文站 / [aitop.news](https://aitop.news) 英文站）的全套 Skill 包。

一个后端、两套门面：**中文站 airebao.com（品牌「AI热报」）** 与 **英文站 aitop.news（品牌「AITOP」）**。同一份能力按站点分成两版发布，包名区分靠 `-en` 后缀。

- 版本：**1.7.0**
- 包总数：**44**（中文 25 / 英文 19）
- 发布平台：[SkillHub](https://skillhub.cn/skills/user_507a5056)

## 目录结构

```
skills/<slug>/SKILL.md      # Skill 正文，目录名 = SkillHub 上的 slug
skills/<slug>/_meta.json    # slug / version / displayName / summary / license
scripts/                    # 生成这些包的脚本（可本地复现）
index.json                  # 机器可读清单
```

`skills/` 下的目录名与 SkillHub 上的 slug **1:1 对应**，所以从 SkillHub 装的包，可以直接从这个仓库取同一份源文件。

## 安装

从 SkillHub 装（推荐）:

```bash
skillhub install aitop-skill        # 中文主包
skillhub install aitop-skill-en     # 英文主包
skillhub install ai-news            # 单个卫星包
```

直接从本仓库取用：把 `skills/<slug>/SKILL.md` 放进你的 skill 目录即可，包内已写明 Base URL、请求头与参数约定。

## 接入约定

每个包都需要携带三个请求头：

```http
X-AITOP-Client: <slug>/1.7.0        # 包名 + 版本，服务端据此统计
X-AITOP-Install: <安装 ID>        # 匿名安装标识，首次使用时写死
User-Agent: <真实 UA>              # 默认的 curl/x.y.z 会被拒
```

用户提供了订阅 key 时再加 `X-AITOP-Key: <key>`（`ak_` 开头），带上后详情不再截断、信源列表完整。

几点容易踩的：

- 中文站包的 Base URL 是 `https://airebao.com/api/public`，英文站包是 `https://aitop.news/api/public`。
- 数据台类接口（模型库 / 融资库 / 政策台 / 榜单）每次请求都带 `lang`，中文站用 `lang=zh`、英文站用 `lang=en`，双语字段会折叠成单语。
- `GET /changelog` 不接受 `lang` 参数，英文版包已跳过请求本地化。
- 详情接口返回的 `readMore.url` 指向站内完整版；任一 `*Truncated` 为 `true` 时必须附上它并说明是摘录。

## 包清单

### 中文站（airebao.com，25 个）

| slug | 展示名 | 版本 | 英文对应 |
|---|---|---|---|
| `ai-asean` | 东南亚 AI 简报 | 1.7.0 | 有（`ai-asean-en`） |
| `ai-changelog` | AI热报 更新日志 | 1.7.0 | 有（`ai-changelog-en`） |
| `ai-daily` | AI 日报 | 1.7.0 | 有（`ai-daily-en`） |
| `ai-editorial` | AI 深度长文 | 1.7.0 | 有（`ai-editorial-en`） |
| `ai-funding` | AI 投融资与政策 | 1.7.0 | 有（`ai-funding-en`） |
| `ai-funding-db` | AI 融资数据表 | 1.7.0 | 有（`ai-funding-db-en`） |
| `ai-labs` | 大厂一手动态 | 1.7.0 | 有（`ai-labs-en`） |
| `ai-model-db` | 大模型参数与价格库 | 1.7.0 | 有（`ai-model-db-en`） |
| `ai-models` | 大模型发布追踪 | 1.7.0 | 有（`ai-models-en`） |
| `ai-news` | AI 新闻速览 | 1.7.0 | 有（`ai-news-en`） |
| `ai-papers` | AI 论文速递 | 1.7.0 | 有（`ai-papers-en`） |
| `ai-policy-desk` | AI 政策台 | 1.7.0 | 有（`ai-policy-desk-en`） |
| `ai-rank` | AI 周榜 | 1.7.0 | 有（`ai-rank-en`） |
| `ai-rising` | AI 上升热榜 | 1.7.0 | 有（`ai-rising-en`） |
| `ai-tools` | AI 工具发现 | 1.7.0 | 有（`ai-tools-en`） |
| `ai-topic` | AI 话题深挖 | 1.7.0 | 有（`ai-topic-en`） |
| `ai-topics` | AI 内容选题雷达 | 1.7.0 | 有（`ai-topics-en`） |
| `ai-weekly` | AI 一周回顾 | 1.7.0 | 有（`ai-weekly-en`） |
| `airebao` | AI新闻 AI TOP NEWS | 1.7.0 | 无 |
| `airebao-daily` | AI热报 AI 日报 | 1.7.0 | 无 |
| `airebao-news` | AI热报 AI 新闻速览 | 1.7.0 | 无 |
| `airebao-tools` | AI热报 AI 工具发现 | 1.7.0 | 无 |
| `airibao` | 全球AI新闻【官方 AITOP.NEWS】 | 1.7.0 | 无 |
| `aitop` | AIHOT AITOP日报 | 1.7.0 | 无 |
| `aitop-skill` | AI热报 资讯助手 | 1.7.0 | 有（`aitop-skill-en`） |

### 英文站（aitop.news，19 个）

| slug | 展示名 | 版本 |
|---|---|---|
| `ai-asean-en` | ASEAN AI briefing (EN) | 1.7.0 |
| `ai-changelog-en` | AITOP changelog (EN) | 1.7.0 |
| `ai-daily-en` | AI daily briefing (EN) | 1.7.0 |
| `ai-editorial-en` | AITOP editorial articles (EN) | 1.7.0 |
| `ai-funding-db-en` | AI funding records (EN) | 1.7.0 |
| `ai-funding-en` | AI funding and policy news (EN) | 1.7.0 |
| `ai-labs-en` | Official AI lab updates (EN) | 1.7.0 |
| `ai-model-db-en` | AI model specifications and prices (EN) | 1.7.0 |
| `ai-models-en` | Model release tracker (EN) | 1.7.0 |
| `ai-news-en` | AI news digest (EN) | 1.7.0 |
| `ai-papers-en` | AI research digest (EN) | 1.7.0 |
| `ai-policy-desk-en` | AI policy desk (EN) | 1.7.0 |
| `ai-rank-en` | AI weekly charts (EN) | 1.7.0 |
| `ai-rising-en` | Rising AI topics (EN) | 1.7.0 |
| `ai-tools-en` | AI product discovery (EN) | 1.7.0 |
| `ai-topic-en` | AI topic explorer (EN) | 1.7.0 |
| `ai-topics-en` | AI editorial angle finder (EN) | 1.7.0 |
| `ai-weekly-en` | AI week in review (EN) | 1.7.0 |
| `aitop-skill-en` | AITOP news assistant (EN) | 1.7.0 |

## 本地复现

包不是手写的，由脚本从结构化定义生成。`scripts/` 里是完整管线：

```bash
python scripts/build-skills.py          # 卫星包 + 双版本（zh/en）
python scripts/build-manual-skills.py  # 主包 / ai-editorial / ai-changelog
python scripts/build-skill-aliases.py  # 历史马甲包 + 被占用 slug 的替代包
python scripts/_sk_build_dist.py       # 汇总出可发布产物
```

`EDITIONS` 里定义了两个站点的 site / brand / lang，所有正文里的站点链接与品牌署名都按版渲染，不存在写死的域名。

## License

MIT
