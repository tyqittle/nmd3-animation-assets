# 忍3视觉素材库 | Ninja Must Die 3

用于以后制作**代码驱动的动画、MV**：分类保存《忍者必须死3》人物立绘、皮肤、Boss、武器、壁纸与战斗参考画面。

**[打开 Pages 素材图鉴](https://tyqittle.github.io/nmd3-animation-assets/)** · [素材原图总索引](catalog/assets.json) · [可下载 CSV 索引](catalog/assets.csv)

## 实图核对与分类修复（2026-10-21）

**[打开素材图鉴](https://tyqittle.github.io/nmd3-animation-assets/)** · [待核对与实图纠错清单](docs/VISUAL_AUDIT_2026-10-21.md) · [完整 JSON](catalog/assets.json)

本仓库仍保存 **85 张真实图片文件**，不会因为分类错误就删除原始素材。已发现 **3 张源名称与实际画面类型/身份不一致的素材**，在网站默认页面隔离，点击「查看待核对素材」仍可查看。

| 逻辑大类 | 已下载文件 | 正常图鉴展示 |
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
- 新增 [89 项角色和皮肤候选采集目标](catalog/wiki_illustration_targets.json)、[18 项武器候选采集目标](catalog/wiki_weapon_targets.json)。新武器**焚天**目前列在待采集目标中，**还没有经过下载校验的原图**，不计入实图数量。

### 2026-10-20 上一批补充：+23 张实际图片

10 张人物：觉醒小夜、小夜基础、棋士紫原、血影挥刃、霜刃伊鹤、雷羿银枭、剑心卫鲤、猫太老板娘、冰羽兮兰、樱火荧。另有 12 张场景/视觉参考图和 1 张丛云之霜羽·织芒武器图。

**素材用途区分：** 带透明通道的完整人物立绘较适合进一步分层；武器图可能只有单独武器，也可能包含装饰特效。宣传画中如有人物或大字，不应当成纯净背景。格式校验不等于逐张人工检查内容，切勿默认所有图片都是高清、完整、可商用的独立立绘。

## 图片在 GitHub 仓库内的目录

- [人物与皮肤](assets/characters/)
- [Boss 与怪物](assets/bosses/)
- [武器](assets/weapons/)
- [场景与壁纸](assets/backgrounds/)

网页从 `catalog/assets.json` 读取**已下载**记录；点击即可查看仓库内的图片源文件，而不是跳去外站加载。

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


## 新增：忍3梗与鬼畜短视频素材库（2026-10-21）

**[在线浏览 68 条忍3梗](https://tyqittle.github.io/nmd3-animation-assets/memes/)** · [梗索引 JSON](memes/catalog.json) · [梗库说明](memes/README.md) · [来源目录](memes/SOURCES.md)

本轮整理 68 条可用于后续短视频、配音、MV 的文本素材，包括 **34 条有明确出处、21 条社区参考、13 条明确标注的原创二创点子**。每条附角色、背景、笑点和镜头设计；链接到原始资料而不是私自复制第三方视频或梗图。支持通过网站按角色、梗类型和出处等级筛选。

## 版权

本仓库为非官方个人参考资料库，图片版权属于原权利人。网页可见不意味着获授权公开复制、再分发或商用。仓库目前为 **Public**；如需仅私人使用，可在 GitHub Settings 调整为 Private。见 [版权说明](docs/RIGHTS.md)。

## 忍3短视频制作工作流（V1.0）

- [查看可持续迭代的视频制作工作流](video/workflow/README.md)
- [编辑48秒《忍村深渊复盘会》分镜 JSON](video/workflow/episodes/deep-abyss-meeting-v1.json)
- [版本与迭代记录](video/workflow/CHANGELOG.md)
- [GitHub Actions 一键渲染 MP4](.github/workflows/render-short-video.yml)

该流程与原来的 MV 渲染工作流相互独立；从本仓库实际素材生成 MP4，先试渲染、再质检，不再依赖浏览器网页录制。
