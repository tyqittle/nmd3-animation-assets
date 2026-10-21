# 忍3视觉素材库 | Ninja Must Die 3

用于以后制作**代码驱动的动画、MV**：分类保存《忍者必须死3》人物立绘、皮肤、Boss、武器、壁纸与战斗参考画面。

**[打开 Pages 素材图鉴](https://tyqittle.github.io/nmd3-animation-assets/)** · [素材原图总索引](catalog/assets.json) · [可下载 CSV 索引](catalog/assets.csv)

## 新增：曼波语音音效包（2026-10-21）

> **热度纠偏：**“2026-10-21新加入仓库”不等于“2026-10刚火”。我们查到2026-10仍有“曼波配音”讲完整故事/文案的作品，而仓库这里的14个只是会喊「曼波」的旧梗变体，**并没有实现现在常用的整段朗读效果**。详见[实查报告：曼波热点和过时素材的区分](memes/research/MAMBO_TREND_AUDIT_2026-10-21.md)。



**[打开曼波专题在线试听](https://tyqittle.github.io/nmd3-animation-assets/comedy/)** · [下载14个曼波 WAV](assets/comedy/mambo/mambo-sfx-14-wav.zip) · [查看来源与使用说明](assets/comedy/mambo/README.md)

已在仓库永久收录 **14个新合成的旧式「曼波」喊声 WAV，属于2024原梗衍生，不是2026最新热梗**：日文/中文单发、双连、三连、高速、慢速、尖声、低音、回声、机械鬼畜、抽卡成功、空大失败、警告、卡顿。每个都单独保存，并有文件时长、所用中性TTS声线、SHA256和版权提示。**这不是《赛马娘》诗歌剧游戏原声或二创UP主原声，不包含声线克隆和别人录音。**

与原有24个基础搞笑音效、16种动画特效合计，整活网页当前展示 **54项（38个音效 + 16种特效）**。所有变体均有可下载 WAV 和完整 ZIP，参见 [曼波生成器](tools/generate_mambo_sfx.py) 及 [通过真实文件的声音测试](tools/test_mambo_sfx.py)。

## 新增：忍村整活音效与动态特效（2026-10-21）

**[立即打开可试听/预览的搞笑素材库](https://tyqittle.github.io/nmd3-animation-assets/comedy/)** · [24个 WAV 音效 ZIP](assets/comedy/comedy-sfx-24-wav.zip) · [16套透明特效 ZIP](assets/comedy/comedy-vfx-16-complete.zip) · [分门别类的媒体索引](assets/comedy/catalog.json)

本次实际生成并提交 **24 个原创合成搞笑音效 + 16 种透明动画特效**，每个特效同时提供透明动画 WebP、静态 PNG、16 帧 RGBA PNG 序列帧 ZIP。包含大重击、弹簧、悲伤小号、唱片刹停、尴尬虫鸣、冷笑话鼓点、问号、冷汗、烟雾、漫画冲击波、定格碎裂、彩纸、金币雨等；适合百炼烧心/焚天不烧心对比短剧和各类忍3鬼畜创作。**图片图鉴中的274张图片统计不包含这40组新音视频素材。**

全套文件均直接保存在仓库 `assets/comedy/`，独立 [使用说明](assets/comedy/README.md)、[生成脚本](tools/generate_comedy_assets.py) 与 [自动测试工作流](.github/workflows/build-comedy-kit.yml) 已收录。媒体完整性检查覆盖WAV音量、时长、序列帧数量、透明通道与哈希；并非外部热门音效录音的搬运或复刻。

## 素材库最新扩容 · 2026-10-21（已实际入库）

**[直接打开图鉴](https://tyqittle.github.io/nmd3-animation-assets/)** · [原始图片总索引](catalog/assets.json) · [怪物与 Boss](assets/bosses/) · [武器](assets/weapons/) · [角色立绘](assets/characters/skins/)

目前已核对仓库中 **274 张真实图片文件与对应的 274 张轻量 WebP 预览**。相较这轮开始时的 107 张，**净增 167 张**。已下载图片均有原始页面链接、仓库文件路径、图片尺寸和 SHA-256，并通过实际文件存在性、哈希去重及分类检查。待采集的 1 条候选**不计入**274 张。

| 素材分类 | 本轮前 | 现在 | 新增 |
|---|---:|---:|---:|
| 角色/皮肤独立图及待核对候选图 | 45 | 116 | +71 |
| 武器本体及幻化 | 30 | 73 | +43 |
| 独立 Boss 图 | 11 | 11 | 0 |
| **怪物系代表图（非独立 Boss）** | 0 | 53 | +53 |
| 壁纸、场景、宣传、特效 | 21 | 21 | 0 |
| **总计** | **107** | **274** | **+167** |

- 武器：对照 [BWIKI SSR 武器分类](https://wiki.biligame.com/nmd3/分类:武器品质SSR) 和相关维护公告，下载了赤焰龙息、百雷·拂晓、雷契·化龙、风宿·苍龙、鬼泪村正、祝融等武器本体，以及多种明确命名的幻化。新素材在 `assets/weapons/wiki/`。
- 怪物：从 [怪物档案](https://wiki.biligame.com/nmd3/怪物档案) 收录 53 张怪物系代表图，包括红龙系、青龙系、雷龙系、丹青式神系、半藏系、机械蜂系等。**这只是怪物系列图鉴封面，不是53个独立 Boss 的高清立绘**，已专门标记为 `monster_group_reference`，可以在 Boss 与怪物分类中进一步筛选。
- 角色：经 BWiki 页面图片标签、真实图片透明度、像素尺寸和重复哈希检查，新增琳、苍牙、小椒、小黑、伊鹤、戌时等角色外观立绘。其中缺少明确身份信息的候选被放到待核对分区，并未冒充已完成身份目检的角色。
- 站点：全部新文件均有 `previews/` 下对应 WebP；先加载轻量预览图，点击时再加载高清原图。搜索、滚动分批渲染与弹窗无闪动逻辑保留。
- **核验范围**：完成文件完整性、来源及自动化分类一致性检查；除明确核对过的条目外，`visual_review=pending` 代表**还没有逐张人工视觉审核**。下载成功也不等于获得商业使用授权。

维护工具：[角色采集](.github/workflows/expand-artwork.yml) · [武器采集](.github/workflows/expand-weapons.yml) · [Boss/怪物采集](.github/workflows/expand-bosses.yml) · [校验脚本](scripts/audit_assets.py) · [缩略图生成](scripts/build_previews.py)。

## 武器与 Boss 实图扩充（2026-10-21）

[直接浏览网站](https://tyqittle.github.io/nmd3-animation-assets/) · [武器文件](assets/weapons/) · [Boss 文件](assets/bosses/)

本轮已经把 **17 张武器实图和 5 张 Boss 实图** 下载并写入仓库，武器从 13 张增至 **30 张**，Boss 从 6 张增至 **11 张**。在当时的扩充阶段，整个素材图鉴达到 **107 张可读取的图片文件和 107 张对应 WebP 预览图**（人物 45、武器 30、Boss 11、壁纸 8、场景 1、宣传 10、特效 2）。

Boss 新增：**异化毒龙、八咫乌、骸骨死神、青翼龙王、残心**。武器新增：**焚天、破雾·贯羽、尽滅、三日月雷切、苍雪祝神铃、岚·不鸣之刃、龙毫笔、风月含袖、怒鲤双生、紫电白虹、如龙临渊、八岐断雷枪、丛云之霜羽**与多种百炼、三日月雷切幻化。原先误把 BWiki 公共 `WuqiBG` 圆环模板当作“百炼”武器的条目已经替换为真实武器图。

新增素材均保留来源页、原图路径、尺寸、哈希校验等字段。下载和图像格式验证已完成，**逐张人工视觉身份复核仍待完善**；尚未成功获取图片的候选不会显示为已入库素材。采集后立即生成轻量 WebP 预览，网站仍可点开未经缩小的原图。

[武器待采集目标](catalog/wiki_weapon_targets.json) · [Boss 待采集目标](catalog/wiki_boss_targets.json) · [武器采集与同步工作流](.github/workflows/expand-weapons.yml) · [Boss 采集与同步工作流](.github/workflows/expand-bosses.yml)

## 实图核对与分类修复（2026-10-21）

**[打开素材图鉴](https://tyqittle.github.io/nmd3-animation-assets/)** · [待核对与实图纠错清单](docs/VISUAL_AUDIT_2026-10-21.md) · [完整 JSON](catalog/assets.json)

**历史记录（本次扩充前）**：当时仓库有 **85 张真实图片文件**；现已增至 107 张，最新分类数量见上方。本次分类修复不会因为标注错误而删除原始素材。已发现 **3 张源名称与实际画面类型/身份不一致的素材**，在网站默认页面隔离，点击「查看待核对素材」仍可查看。

| 逻辑大类 | 扩充前已下载文件 | 扩充前正常图鉴展示 |
|---|---:|---:|
| 忍者角色 | 45 | 44 |
| 武器 | 13 | 13 |
| Boss 与怪物 | 6 | 6 |
| 场景参考 | 1 | 1 |
| 壁纸与构图 | 8 | 8 |
| 活动与宣传插画 | 10 | 8 |
| 战斗特效 | 2 | 2 |
| **合计** | **85** | **82** |

分类规则不再依赖文件名：根据实图判断「单人抠图 vs 海报复合画面」，根据 BWIKI 的「获取方式／所属忍者」区分真正流派、普通皮肤与觉醒外观。

本轮明确纠正：**青行姬·琳错配海报**、**樱火·荧错配宣传图**、**鬼斩·紫原电吉他造型待查**；以及 **魂·苍牙、雪·苍牙、玄黄·双焰、棋士·紫原** 等被误标为流派的皮肤，和 **夜叉·隼白、极刃·血影、神炎·小椒、乘霄·戌时** 等觉醒外观。

**图片文件的本地路径保持不变**。其他条目仍有逐图审核的工作，不能将本次针对重点问题的核对误称为全库人工实图验收。

详细见 [分类规范](docs/CLASSIFICATION.md) 与 [实图纠错记录](docs/VISUAL_AUDIT_2026-10-21.md)。

### 2026-10-21 新增：8 张角色图 + 7 张武器图

**[查看全部 15 张新图与直接文件链接](docs/NEW_ASSETS_2026-10-21.md)**

- **角色：** 乘霄·戌时、双焰·小椒、雷兽·阿力、神炎·小椒、不知火·舞、夜叉·隼白、极刃·血影、贺新焰·双焰小椒。
- **武器：** 伏溟九渊、尽滅·共逐风、风月含袖·流泠、巨阙·缚日、怒鲤双生·寂鲤并蒂、百雷·拂晓·龙泓、百炼。
- 新原图位于 `assets/characters/skins/`、`assets/characters/2026-10-expansion/`、`assets/weapons/2026-10-expansion/`、`assets/weapons/wiki/`。
- 新增 [89 项角色和皮肤候选采集目标](catalog/wiki_illustration_targets.json)、[18 项武器候选采集目标](catalog/wiki_weapon_targets.json)。新武器**焚天**目前列在待采集目标中，在该批次**尚未完成下载验证**；现已在本轮武器扩充中取得实际图片并入库。

### 2026-10-20 上一批补充：+23 张实际图片

10 张人物：觉醒小夜、小夜基础、棋士紫原、血影挥刃、霜刃伊鹤、雷羿银枭、剑心卫鲤、猫太老板娘、冰羽兮兰、樱火荧。另有 12 张场景/视觉参考图和 1 张丛云之霜羽·织芒武器图。

**素材用途区分：** 带透明通道的完整人物立绘较适合进一步分层；武器图可能只有单独武器，也可能包含装饰特效。宣传画中如有人物或大字，不应当成纯净背景。格式校验不等于逐张人工检查内容，切勿默认所有图片都是高清、完整、可商用的独立立绘。

## 图片在 GitHub 仓库内的目录

- [人物与皮肤](assets/characters/)
- [Boss 与怪物](assets/bosses/)
- [武器](assets/weapons/)
- [场景与壁纸](assets/backgrounds/)

网页从 `catalog/assets.json` 读取**已下载**记录；点击即可查看仓库内的图片源文件，而不是跳去外站加载。

### 图鉴流畅度升级（2026-10-21）

- **预览与原图分离**：`scripts/build_previews.py` 以 Pillow 生成保持原比例与透明度的 420×560 以内 WebP，写入 `previews/assets/`；**原图文件及 catalog 路径不变**。85 张预览共约 **3.63 MB**，相较 40.05 MB 原图数据量降低约 **90.9%**（仅指完整预览集的文件体积，并非实测首屏耗时）。
- **首屏与滚动**：先绘制最多 24 条卡片，滚动接近底部时追加下一批，图片懒加载并异步解码，避免首次重排全部卡片。
- **搜索与筛选**：搜索输入 120 ms 防抖；预计算检索文本和排序索引，减少多余工作。
- **高清弹窗**：固定查看区域；先加载并解码高清图，完成后显示，关闭弹窗时让过期请求失效，避免重复点击后图片闪动或错位。
- **自动维护**：[预览生成工作流](.github/workflows/build-previews.yml) 在 `assets/**`、`catalog/assets.json` 或生成脚本变更时重新生成并提交预览图；预览缺失时网页可回退到原图。

性能校验：使用浏览器开发者工具 Network 对比 `previews/assets/…webp` 与 `assets/…png` 请求；移动端滚动应按需增加卡片。网络速度、GitHub Pages 缓存及浏览器性能仍会影响实际加载体验。


## 检查、再次采集

```bash
python -m pip install -r requirements.txt
python scripts/fetch_assets.py
python scripts/audit_assets.py
```

- [采集与校验工作流](.github/workflows/collect-images.yml)
- [皮肤立绘发现流程](.github/workflows/expand-artwork.yml)
- [武器原图发现流程](.github/workflows/expand-weapons.yml)
- [本轮入库明细与链接](docs/NEW_ASSETS_2026-10-21.md)
- [素材分类规范和保留原路径原则](docs/CLASSIFICATION.md)
- [分类一致性校验](scripts/validate_taxonomy.py)
- [动画素材处理规范](docs/ANIMATION_GUIDE.md)

源站可能限制抓取，受限或下载失败的图片不会冒充已入库图片。后续优先补充独立动画层、可抠像完整立绘、无字高清背景、Boss 模型与刀光粒子素材。


## 忍3短视频热点与梗库（2026-10-21 更新）

**[在线浏览 101 条忍3梗](https://tyqittle.github.io/nmd3-animation-assets/memes/)** · [梗索引 JSON](memes/catalog.json) · [梗库说明](memes/README.md) · [来源目录](memes/SOURCES.md)

素材库现有 101 条可用于短视频、配音、MV 的文本素材，原有 68 条（34 条出处明确、21 条社区参考、13 条原创构思），现新增 33 条（跨圈短视频、10 月游戏官方与玩家话题、原创联动）。每条附角色、背景、笑点和镜头设计；链接到原始资料而不是私自复制第三方视频或梗图。支持通过网站按角色、梗类型和出处等级筛选。**[2026-10-21新增热点与镜头详情](memes/HOTSPOTS_2026-10-21.md)**，新增选题附有效期和来源，不将原创二创伪装成玩家公认热梗。

## 版权

本仓库为非官方个人参考资料库，图片版权属于原权利人。网页可见不意味着获授权公开复制、再分发或商用。仓库目前为 **Public**；如需仅私人使用，可在 GitHub Settings 调整为 Private。见 [版权说明](docs/RIGHTS.md)。


## 2026-10-21 新短剧工程：小椒卖焚天

**[《小椒卖焚天：百炼烧心 vs 焚天不烧心》独立工程](video/projects/xiaojiao-fentian-shop/README.md)** · [分镜与渲染程序](video/projects/xiaojiao-fentian-shop/render.py) · [生产清单](video/projects/xiaojiao-fentian-shop/project.json)

【2026-10-21重制】37秒竖屏忍村市井对比短剧：小黑贪便宜用百炼，经历非双焰角色接锤、回锤后蓄力1.5秒和出手时机的「烧心」，再试带双段短暂无敌与定身连招的焚天，感叹「贵是贵了点，但用着不烧心」，小椒认真立规矩。工程引用仓库小椒、小黑、百炼及焚天四份原图，缺图拒绝渲染；售价关系为虚构，不比较真实武器伤害高低。由通用视频制作工作流渲染为MP4并自动生成质检联络图、配音日志；**此处说明工程已入库，不表示已经目检或确认MP4渲染成功**。

## 忍3视频制作流程（v2.0 · 不绑定画面模板）

**[查看创作自由版完整制作规范](video/workflow/README.md)** · [GitHub Actions 通用视频生产入口](.github/workflows/video-production.yml) · [作品目录](video/projects/)

工作流只规定 **创意规划 → 素材审核 → 本作品分镜/声音设计 → 可选预览 → 独立渲染 → 技术/人工质检 → 交付**，不再规定“必须拍哪一类片子”或固定构图、人物站位、对话框、片头、背景音乐和转场。

每部作品有独立的项目配置和渲染程序；Actions 通过输入项目路径执行，不再从固定短片/MV下拉列表中选择。旧深渊短片和 Shadow Protocol MV 仅作为两个**不同渲染器的历史示例**保留，不能当做统一创作模板。自动测试允许无角色、无对白、无字幕甚至没有音轨的独立视频工程通过。

