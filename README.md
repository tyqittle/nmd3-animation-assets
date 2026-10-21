# 忍3视觉素材库 | Ninja Must Die 3

用于以后制作**代码驱动的动画、MV**：分类保存《忍者必须死3》人物立绘、皮肤、Boss、武器、壁纸与战斗参考画面。

**[打开 Pages 素材图鉴](https://tyqittle.github.io/nmd3-animation-assets/)** · [素材原图总索引](catalog/assets.json) · [可下载 CSV 索引](catalog/assets.csv)

## 已入库的真实图片（2026-10-20）

| 类别 | 已保存 |
|---|---:|
| 角色立绘与人物参考 | 39 |
| Boss / 怪物 | 6 |
| 武器 | 6 |
| 壁纸、场景和战斗宣传参考图 | 19 |
| **实际图片文件总计** | **70** |

**这 70 张图片已由 GitHub Actions 下载并提交到 Git 仓库**，不依赖图片来源网站实时加载。下载程序验证图像格式，并记录文件大小、尺寸和 SHA-256；自动审计未检出二进制完全相同的重复图。全目录共有 71 条来源记录，尚有 1 条旧背景候选因源站 HTTP 403 未入库。

### 本轮补充：+23 张实际图片

* **10 张人物**：觉醒小夜、小夜基础、棋士紫原、血影挥刃、霜刃伊鹤、雷羿银枭、剑心卫鲤、猫太老板娘、冰羽兮兰、樱火荧。
* **12 张场景/视觉参考**：包括聚核裂变、掠天玄甲、集结正当时、宴红堂、神炎铸赤心等；其中两张为 **2560 × 1440** 壁纸。
* **1 张独立武器图**：丛云之霜羽·织芒。

新增原图放在 `assets/characters/2026expansion/`、`assets/backgrounds/2026expansion/`、`assets/weapons/2026expansion/`。

**素材用途区分：** 人物中较适合后续分层的是带透明通道的立绘；`backgrounds` 中既有横版壁纸，也有带人物和文字的宣传图，后者仅适合作为风格、特效或镜头参考，不能当纯净可复用的空场景。格式校验不等于逐张人工确认内容，**不要默认所有角色都是高清完整全身立绘**。

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
- [动画素材处理规范](docs/ANIMATION_GUIDE.md)

源站可能限制抓取，受限或下载失败的图片不会冒充已入库图片。后续优先补充独立动画层、可抠像完整立绘、无字高清背景、Boss 模型与刀光粒子素材。


## 新增：忍3梗与鬼畜短视频素材库（2026-10-21）

**[在线浏览 68 条忍3梗](https://tyqittle.github.io/nmd3-animation-assets/memes/)** · [梗索引 JSON](memes/catalog.json) · [梗库说明](memes/README.md) · [来源目录](memes/SOURCES.md)

本轮整理 68 条可用于后续短视频、配音、MV 的文本素材，包括 **34 条有明确出处、21 条社区参考、13 条明确标注的原创二创点子**。每条附角色、背景、笑点和镜头设计；链接到原始资料而不是私自复制第三方视频或梗图。支持通过网站按角色、梗类型和出处等级筛选。

## 版权

本仓库为非官方个人参考资料库，图片版权属于原权利人。网页可见不意味着获授权公开复制、再分发或商用。仓库目前为 **Public**；如需仅私人使用，可在 GitHub Settings 调整为 Private。见 [版权说明](docs/RIGHTS.md)。
