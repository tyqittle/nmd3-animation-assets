# 忍3视觉素材库 | Ninja Must Die 3

用于以后制作**代码驱动的动画、MV**：分类保存《忍者必须死3》人物立绘、皮肤、Boss、武器、壁纸与战斗参考画面。

**[打开 Pages 素材图鉴](https://tyqittle.github.io/nmd3-animation-assets/)** · [素材原图总索引](catalog/assets.json) · [可下载 CSV 索引](catalog/assets.csv)

## 武器与 Boss 实图扩充（2026-10-21）

[直接浏览网站](https://tyqittle.github.io/nmd3-animation-assets/) · [武器文件](assets/weapons/) · [Boss 文件](assets/bosses/)

本轮已经把 **17 张武器实图和 5 张 Boss 实图** 下载并写入仓库，武器从 13 张增至 **30 张**，Boss 从 6 张增至 **11 张**。整个素材图鉴现在有 **107 张可读取的图片文件和 107 张对应 WebP 预览图**（人物 45、武器 30、Boss 11、壁纸 8、场景 1、宣传 10、特效 2）。

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


## 新增：忍3梗与鬼畜短视频素材库（2026-10-21）

**[在线浏览 68 条忍3梗](https://tyqittle.github.io/nmd3-animation-assets/memes/)** · [梗索引 JSON](memes/catalog.json) · [梗库说明](memes/README.md) · [来源目录](memes/SOURCES.md)

本轮整理 68 条可用于后续短视频、配音、MV 的文本素材，包括 **34 条有明确出处、21 条社区参考、13 条明确标注的原创二创点子**。每条附角色、背景、笑点和镜头设计；链接到原始资料而不是私自复制第三方视频或梗图。支持通过网站按角色、梗类型和出处等级筛选。

## 版权

本仓库为非官方个人参考资料库，图片版权属于原权利人。网页可见不意味着获授权公开复制、再分发或商用。仓库目前为 **Public**；如需仅私人使用，可在 GitHub Settings 调整为 Private。见 [版权说明](docs/RIGHTS.md)。

## 唯一视频制作工作流（V1.1）

**[Ninja 3 Video Production — GitHub Actions 唯一视频制作入口](.github/workflows/video-production.yml)**

- [工作流说明、分镜与版本记录](video/workflow/README.md)
- [《忍村深渊复盘会》48 秒分镜 JSON](video/workflow/episodes/deep-abyss-meeting-v1.json)
- [工作流更新记录](video/workflow/CHANGELOG.md)

制作入口可选 **短视频**（搞笑动画/剧情）或 **MV**（原音乐剪辑），同一个 Actions 工作流负责渲染 MP4。修改脚本和分镜时也由这个工作流自动运行 2 秒回归测试。原来的三个视频 Actions 文件已合并取消，立绘和 MV 脚本保留。
