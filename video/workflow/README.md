# 忍3统一视频制作工作流 v1.2

**唯一 GitHub Actions 入口：** [Ninja 3 Video Production](../../.github/workflows/video-production.yml)。合并旧 MV 制作、短视频制作和自动回归测试；原始立绘、`mv/make_mv.py` 和分镜文件全部保留，避免功能丢失。

## 从选题到成片

1. 在 ../../memes/catalog.json 查找梗：核对 context、evidence、sources。原创反转须明确标为二创。
2. 复制 episodes/deep-abyss-meeting-v1.json 作为新一集分镜；定义每镜头 start/end、speaker、lines、voice、effect。
3. 使用仓库 assets/ 下已入库原图，核对角色身份、尺寸与透明背景，绝不以不相关的 AI 图冒充原立绘。
4. 使用 scripts/check.py 验证素材路径、分镜完整性和时长；先做小分辨率短片测试，再渲染整片。
5. 使用 scripts/render.py 输出 H.264/AAC MP4。scripts/audio.py 为六位角色选用独立中文合成音色、自动调整过长台词的语速、混合原创配乐与音效，并在讲话时压低音乐。默认 edge-tts 在线中文声音；离线机器人语音仅限测试。
6. 通过 ffprobe 检查视频及音轨编码、尺寸和时长，人工审查画面裁剪、字幕、笑点与配音。
7. 保留每集 JSON、代码提交及 CHANGELOG。不要覆盖 assets/ 原始图片，不要把临时配音称为正式配音。

## 本地运行

需要 Python 3.10+、FFmpeg、Pillow、NumPy 和中文字库（Linux 安装 fonts-noto-cjk）。自然普通话需安装 edge-tts 且运行时有网络；如明确选择离线机器人测试配音，另装 espeak-ng。网络 TTS 不可用会报错，不会偷偷改用机器人音。

在仓库根目录执行：

    python -m pip install pillow numpy edge-tts
    python video/workflow/scripts/check.py video/workflow/episodes/deep-abyss-meeting-v1.json
    python video/workflow/scripts/render.py --recipe video/workflow/episodes/deep-abyss-meeting-v1.json --quality draft --tts off --seconds 2 --output output/test.mp4
    python video/workflow/scripts/render.py --recipe video/workflow/episodes/deep-abyss-meeting-v1.json --quality final --tts edge --output output/deep-abyss-meeting-v1.mp4

## GitHub 一键渲染

在 **Actions > Ninja 3 Video Production > Run workflow** 选择：

- `video_type = short`：从 `episodes/*.json` 选择剧情短片，支持 `draft/final`；`narration = edge` 为默认自然中文，`placeholder` 为机器人测试语音，`off` 仅配乐音效。
- `video_type = mv`：使用保留的 `mv/make_mv.py` 与 `tyqittle/anime-music-library` 制作音乐视频；短片选项对 MV 不生效。

**只有这一个视频制作 Actions 工作流。** 修改 `mv/**`、`video/workflow/**` 时，同一工作流会自动运行代码静态检查、原图校验和 2 秒 MP4 回归测试；要生成完整 MP4 则手动 Run workflow。最终影片作为 Artifact 保留 30 天。不会自动上传 B 站，也不会自动把 MP4 提交到仓库。

旧 MV 脚本保留在 `mv/` 作为统一视频工作流的内部渲染模块，**不是另一个独立的视频工作流入口**。

## 质量红线

- 角色、背景图片必须实际存在于本仓库；缺素材停止渲染，不用占位假人冒充。
- 分镜无重叠、空档；字幕不能截断；不同尺寸立绘需统一画面占比。
- 原创段子和真实玩家梗分开，涉及版本机制需复核。
- 人物声线是独立中文合成音色，并非《忍3》声优原声或声音克隆。商业化/公开传播前自行核实立绘、音乐、音色服务许可。
- 目前只做精灵位移、镜头震动、文字特效与画面合成；并非 Live2D、真实口型或角色一致性图生图。

## 迭代路线

- v1.1：可视化分镜编辑、角色预览与尺寸模板
- v1.2：分层角色、眨眼、口型与表情替换
- v1.3：时间轴混音与配音对齐
- v1.4：转场模板、运动曲线和镜头节奏
- v2.0：基于真实原立绘的图生图与角色一致性检验

重大变更升级模板或工作流版本，记录 CHANGELOG，并保留可回退提交。

## 语音质量与排错（v1.2）

- **不再截断台词**：每句语音按镜头起止时间排入，若超长则在限度内用 FFmpeg `atempo` 保持音高加速；需要超过 1.7 倍时直接报错，要求修改分镜时长或文案。
- **按人物区分配音**：`scripts/audio.py` 内 `PROFILES` 提供默认中文声音/语速/音高；`characters.<角色>.voice_profile` 或镜头级 `voice_profile` 可覆盖。
- **混音**：讲话区间音乐自动 ducking（带渐变），人声有响度与峰值控制，转场音效不抢对白。
- **可查错**：每部视频旁产生 `*-audio-report.json`，逐句列出语音、时长、加速倍数和对齐位置；Actions 产物包含这个报告。
- **自动回归**：`python video/workflow/scripts/test_audio.py` 完全离线验证不裁词、语音对齐、静音模式和 PCM 时长。首次 `edge` 渲染需联网，在线服务不保证永久可用。
- **手动离线预览**：`--tts placeholder` 使用 eSpeak NG 粗略核对台词，不建议发布。
