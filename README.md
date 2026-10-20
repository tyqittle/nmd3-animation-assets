# 忍者必须死3 · 动画素材库

面向后续代码动画 / MV 制作的真实远程 Git 素材库。按角色、Boss、武器、背景归档，并保留来源链接、尺寸与 SHA256。

## 实际入库状态（2026-10-20）

**已成功下载、验证并提交 25 张图片文件**；候选来源记录共 26 条：

| 类别 | 已入库 | 来源候选 |
|---|---:|---:|
| 角色、皮肤 | 12 | 12 |
| Boss / 怪物 | 6 | 6 |
| 武器道具 | 1 | 1 |
| 背景 / 壁纸 | 6 | 7 |
| **总计** | **25** | **26** |

暂未入库：`wallpaper_purple_combat_01`（源站返回 HTTP 403）。没有用空白图、占位图或 AI 图冒充它。

**特别说明**：图片虽然已按格式验证，但还未逐张人工检查主体、裁切、是否完整立绘和是否带背景。部分角色图片只有 465px 高或 512px 方图，更适合作为候选参考；不能保证 25 张全部达到高质量动画要求。

## 直接浏览

- [角色](assets/characters/)：12 张
- [Boss / 怪物](assets/bosses/)：6 张
- [武器](assets/weapons/)：1 张
- [背景](assets/backgrounds/)：6 张
- [素材索引 JSON](catalog/assets.json) / [表格 CSV](catalog/assets.csv)
- [预览图鉴页面](index.html)：可用静态 HTTP 服务 / GitHub Pages 打开
- [自动采集工作流](.github/workflows/collect-images.yml)：重新采集可通过 Actions 手动启动

## 本地脚本

```bash
pip install -r requirements.txt
python scripts/fetch_assets.py
python scripts/audit_assets.py
```

下载脚本不会绕过图片来源网站的访问限制；源站不可用的文件会保留未下载状态。

## 未来动画的素材标准

优先使用可抠像的高清全身立绘；对于有遮挡的角色，先拆分身体、四肢、衣服、飘带图层，再通过代码做关键帧、骨骼、镜头与特效运动。网页缩略图和头像只能作为视觉参考，不能充当全身动画成品。

## 版权说明

本仓库并非《忍者必须死3》官方项目，美术资源版权归原权利人。目前仓库可见性为 **Public**，图片公开再分发的授权并未核实；如仅个人使用，建议在 GitHub Settings 中设置为 Private。来源与说明见 [docs/RIGHTS.md](docs/RIGHTS.md)。
