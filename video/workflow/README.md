# 忍3短视频制作工作流 v1.0

本目录是可复用的视频生产工作流，不覆盖仓库已有的 MV 流程，也不移动原始立绘。工作目标是持续迭代《忍者必须死3》非官方搞笑短片。

## 从选题到成片

1. 在 ../../memes/catalog.json 查找梗：核对 context、evidence、sources。原创反转须明确标为二创。
2. 复制 episodes/deep-abyss-meeting-v1.json 作为新一集分镜；定义每镜头 start/end、speaker、lines、voice、effect。
3. 使用仓库 assets/ 下已入库原图，核对角色身份、尺寸与透明背景，绝不以不相关的 AI 图冒充原立绘。
4. 使用 scripts/check.py 验证素材路径、分镜完整性和时长；先做小分辨率短片测试，再渲染整片。
5. 使用 scripts/render.py 输出 H.264/AAC MP4。音轨由 scripts/audio.py 生成原创占位音乐和可选中文合成语音。
6. 通过 ffprobe 检查视频及音轨编码、尺寸和时长，人工审查画面裁剪、字幕、笑点与配音。
7. 保留每集 JSON、代码提交及 CHANGELOG。不要覆盖 assets/ 原始图片，不要把临时配音称为正式配音。

## 本地运行

需要 Python 3.10+、FFmpeg、Pillow、NumPy 和中文字库（Linux 安装 fonts-noto-cjk）。若要临时机器人配音，另装 espeak-ng。

在仓库根目录执行：

    python -m pip install pillow numpy
    python video/workflow/scripts/check.py video/workflow/episodes/deep-abyss-meeting-v1.json
    python video/workflow/scripts/render.py --recipe video/workflow/episodes/deep-abyss-meeting-v1.json --quality draft --tts off --seconds 2 --output output/test.mp4
    python video/workflow/scripts/render.py --recipe video/workflow/episodes/deep-abyss-meeting-v1.json --quality final --tts placeholder --output output/deep-abyss-meeting-v1.mp4

## GitHub 一键渲染

在 Actions > Render Ninja 3 Short Video > Run workflow 选择剧集、画质和是否使用占位配音。将检验、试渲染、正式渲染 MP4，上传 Actions Artifact 供下载（暂存 30 天）。不会自动公开上传 B 站或自动把成品提交到代码仓库。

## 质量红线

- 角色、背景图片必须实际存在于本仓库；缺素材停止渲染，不用占位假人冒充。
- 分镜无重叠、空档；字幕不能截断；不同尺寸立绘需统一画面占比。
- 原创段子和真实玩家梗分开，涉及版本机制需复核。
- 中文机器人配音仅供节奏验证；商业化/公开传播前应自行核实立绘、音乐、音色许可。
- 目前只做精灵位移、镜头震动、文字特效与画面合成；并非 Live2D、真实口型或角色一致性图生图。

## 迭代路线

- v1.1：可视化分镜编辑、角色预览与尺寸模板
- v1.2：分层角色、眨眼、口型与表情替换
- v1.3：时间轴混音与配音对齐
- v1.4：转场模板、运动曲线和镜头节奏
- v2.0：基于真实原立绘的图生图与角色一致性检验

重大变更升级模板或工作流版本，记录 CHANGELOG，并保留可回退提交。
