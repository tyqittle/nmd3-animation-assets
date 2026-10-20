# 忍3视觉素材库 / Ninja Must Die 3

为后续**代码驱动的动画、MV**整理《忍者必须死3》的角色立绘、皮肤、Boss、武器与场景。

**[打开 GitHub Pages 素材图鉴](https://tyqittle.github.io/nmd3-animation-assets/)**

## 真实文件盘点（2026-10-20）

| 分类 | 已入库 |
|---|---:|
| 人物与皮肤 | **29** |
| Boss 与怪物 | **6** |
| 武器 | **5** |
| 场景和壁纸 | **7** |
| **总计** | **47 张** |

- 每张已入库的文件都通过了格式有效性检查，并在主索引里记录来源、尺寸、哈希。
- 本轮新增的 22 张素材包含隼白、琳、苍牙、伊鹤、小椒、紫原、银枭等人物的 **620×780 原始大小图**，以及一张 **2560×1480 壁纸**。
- 索引包含 48 条候选记录，其中 1 条因外站返回 HTTP 403 尚未下载。网页默认**只展示实际已保存的 47 张图片**，不会把坏链当图。
- 本轮自动审计确认 0 个二进制重复文件。
- 格式检验并不等于画面内容人工审核：部分早期资源像素偏小，且未全部确认是否为干净全身立绘。

## 资源目录

- [角色 / 皮肤](assets/characters/) — 29
- [Boss / 怪物](assets/bosses/) — 6
- [武器](assets/weapons/) — 5
- [背景 / 壁纸](assets/backgrounds/) — 7
- [图片总索引](catalog/assets.json)（带宽、高、SHA256、来源）
- [表格索引](catalog/assets.csv)
- [待发现的皮肤列表](catalog/wiki_illustration_targets.json)（不是入库数量）

## 图鉴功能

网站可按角色/Boss/武器/背景筛选，按中文名称搜索，只看较高清图或带透明通道的图。点击图片可大图预览，查看仓库原图与原始来源。

## 自动采集与去重

```bash
python -m pip install -r requirements.txt
python scripts/fetch_assets.py
python scripts/audit_assets.py
```

- [下载和校验工作流](.github/workflows/collect-images.yml)
- [皮肤立绘发现工作流](.github/workflows/expand-artwork.yml)

BWIKI 可能对高频请求返回 HTTP 567。发现脚本遵守请求限制：受限时不绕过限制，只保存成功取得并通过内容格式验证的图片。后续应低频、分批采集，或改用已验证的图片原始直链。

## 后续做动画

参考 [动画素材处理指南](docs/ANIMATION_GUIDE.md)。对于可做动画的角色立绘，下一步是分离人物与特效、补齐被遮挡部分、分层组织衣摆/头发/武器，并使用关键帧与骨骼运动，而不是简单将整张图平移。

## 版权

本仓库为非官方个人参考资料库，艺术作品版权归各自权利方。素材公开可见不意味着已获再分发或商业授权。仓库当前为 **Public**，请自行确认所需许可；仅用于个人工作的情况下可以考虑设为 Private。详情见 [版权说明](docs/RIGHTS.md)。
