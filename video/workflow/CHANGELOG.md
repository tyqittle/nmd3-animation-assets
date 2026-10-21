# 忍3视频制作工作流更新记录

## v2.0 — 2026-10-21：彻底拆开「制作流程」和「视频模板」

- 统一工作流仅负责质量与执行阶段，不再要求固定剧情、人物、台词、配色、比例或复用同一套画面布局。
- 新增 `video/workflow/scripts/production.py`：从每个作品独立的 `project.json` 读取准备依赖、需要核对的素材、可选预览、正式渲染命令及单片可选的技术质量指标。
- Actions 入口删除固定 `short/mv` 和固定剧集选择，改为传入作品清单路径，并在独立项目的自由渲染程序上执行通用验证。
- 旧漫画短片和 MV 作为**两个相互独立的历史示例**，保留全部原始脚本与素材；MV 脚本加入 `--seconds` 和 `--output` 以便自行控制预览。
- 新增 `test_production.py` 验证无字幕/无角色/无音轨/不同渲染器的视频也可走同一流程。
- `README.md` 改为先说明制作步骤、艺术自主权与项目格式，防止未来再次把示例视觉误当规范。


## v1.2 — 2026-10-21：修复中文语音、节奏和混音

- 默认成片配音改为在线自然普通话（edge-tts），为隼白、小黑、苍牙、阿力、琳、血影设置不同声音；原声克隆不在此工作流能力范围。
- 修复 eSpeak 配音长于镜头时直接截断尾字的问题：从尾字硬裁改为基于 atempo 的完整保留和镜头约束，超时必报错。
- 调整对白响度与 BGM ducking，降低配乐遮挡台词的情况。
- 给每支 MP4 生成逐句 audio-report.json，包括时间戳和变速倍数。
- 新增离线回归测试；GitHub Actions 在产片时校验逐句对白数量和无裁切。
- Edge TTS 需联网；在线服务报错不会静默伪装成自然配音。


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
