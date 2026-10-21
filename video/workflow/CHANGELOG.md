# 忍3视频制作工作流更新记录

## v1.1 — 2026-10-21：三个视频 Actions 合并为一个

- 统一入口：`.github/workflows/video-production.yml`（Ninja 3 Video Production）。
- 合并原先 `render-mv.yml`（音乐 MV）、`render-short-video.yml`（剧情短片）和 `check-short-video.yml`（自动回归测试），删除三份独立 Actions 配置。
- 单个工作流可选 `short` / `mv`；推送和 PR 变更时复用一个回归验证任务，不重复触发三套工作流。
- 保留 `mv/make_mv.py`、`video/workflow/scripts/`、`video/workflow/episodes/` 和所有仓库角色原图，不破坏已有作品。
- 统一从 Actions 下载 MP4 Artifact，仓库主 README 与视频说明同步修改。

# v1.0 的历史记录保留

## v1.0 — 2026-10-21

- 新建独立的 video/workflow/ 目录，保留旧 mv/ 工作流和现有素材结构。
- 首个可编辑剧集示例：48 秒《忍村深渊复盘会：谁把闪交了？》。
- 制定角色原图校验、连续分镜、程序动画、占位配音、H.264/AAC MP4 渲染与验证流程。
- 增加手动触发的 GitHub Actions 入口和下载成片的 Artifact。
- 现阶段为 sprite animation + 漫画分镜，不声称已经实现逐帧角色动作或原声克隆。

## 下一轮待验证

- GitHub Actions 首次完整渲染及 48 秒视频实际画面。
- 对照原始立绘逐张核查裁切、透明通道与角色身份。
- 改进配音自然度和文字换行；通过新版本提交逐步优化。
