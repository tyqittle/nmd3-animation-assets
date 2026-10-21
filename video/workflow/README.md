# 忍3视频制作工作流 v2.0 — 流程固定，创作自由

**本文件只约束如何可靠地完成一次视频制作，不约束视频长什么样。** 不必照搬上一个作品的角色站位、对话框、字幕、转场、节奏、片头或配色。

GitHub Actions 入口：[Ninja 3 Video Production](../../.github/workflows/video-production.yml)。
通用流程执行器：[production.py](scripts/production.py)。
创意可选素材：[24种原创基础音效 + 14种新配音「曼波」音效 + 16种透明特效](../../assets/comedy/README.md)（[在线试听/预览](../../comedy/)）；不强制任何视频使用这些元素。曼波音效仅是原创TTS变体，不能误标成《赛马娘》游戏配音。

**质量验收指南：** [QUALITY_REVIEW.md](QUALITY_REVIEW.md)。成片技术检查和实际画面审查分开，避免以高分辨率、可播放替代真实的创意和动作质量。

## 必须遵循的是制作流程，不是视频模板

1. **创意目标**：为**当前这一部**确定表达意图、受众、整体情绪、时长和输出格式；允许剧情、战斗、MV、搞笑、鬼畜、静音、竖屏或实验影像。
2. **素材核实**：选择或制作独立的角色、Boss、武器、背景、音乐、音效；核对画面身份、来源、授权、分辨率与透明度。需要图生图时记录真正的参考原图；不冒充成功。
3. **为作品设计分镜和声音**：可以采用脚本、文字镜头表、关键帧、时间线、动画工程、剪辑表；只要求表达清晰、视听节奏合理，不强制人物对白、固定镜头结构或某种视觉样式。
4. **独立制作与渲染**：每部作品选自己的工具链和渲染程序，允许 Pillow、Blender、AE、FFmpeg、OpenCV、Live2D、音画剪辑或其他程序。预览可由作品自主定义，也允许只提交正式输出。
5. **质检**：自动检查视频文件存在且可解码、时长有效；音轨/尺寸/时间范围仅按当前作品声明的条件验收。人工审查素材错配、裁切、节奏、对白完整性、画面质量与版权问题。
6. **交付和迭代**：保存该作品的工程、命令、来源、最终视频和质检记录；发现问题返回对应制作步骤修复，而不是统一改成另一种模板。

### 绝不能强加给所有作品的东西

- 固定片头、片尾、进度条、对话框、角色位置、文字系统、转场、字体、调色或特效。
- 固定背景音乐、配音、声线、角色数、镜头数、时长、比例、帧率、编码工具或讲述方式。
- 必须使用某个现有的 `episodes/*.json`、`video/workflow/scripts/render.py` 或 `mv/make_mv.py`。
- “为了自动化方便”将独立作品变成仅替换人名和背景的同一段代码。

## 新增视频的技术接口

每个独立作品创建 `video/projects/<作品目录>/project.json`。它告诉流程“怎样制作这部片”，**不规定任何画面内容或风格**。

示例（请实现自己的项目脚本；下面的 `my-project/render.py` 不是仓库已存在的文件）：

~~~json
{
  "schema_version": "1",
  "id": "my-project",
  "title": "完全自主设计的忍3视频",
  "required_files": ["ninja/video/projects/my-project/render.py"],
  "setup": [["python", "-m", "pip", "install", "numpy"]],
  "render": {
    "preview": {
      "argv": ["python", "ninja/video/projects/my-project/render.py",
               "--preview", "--output", "{output}"],
      "output": "output/{id}-preview.mp4"
    },
    "final": {
      "argv": ["python", "ninja/video/projects/my-project/render.py",
               "--output", "{output}"],
      "output": "output/{id}-final.mp4",
      "checks": {"audio_required": true, "min_seconds": 5}
    }
  }
}
~~~

技术规则：`render.final` 必须声明，`render.preview` 可选。`argv` 是参数数组，不经 shell；可用 `{output}`、`{id}`、`{repo}`、`{workspace}`。项目自己的代码和资源从工作区读取，生成文件放在工作区 `output/`，可以用 MP4、MOV、WebM、MKV。`setup` 是可选依赖安装命令，不给所有作品强行绑定一个动画引擎。

可选自动检查项：`audio_required`、`min_seconds`、`max_seconds`、`min_width`、`min_height`。**不存在必需的角色名单、字幕形式、声音类别、视频宽高比或统一构图。** 特殊的本地软件、图形环境或依赖需要单独为对应项目配置执行环境。

## GitHub Actions：一个入口，所有创作

进入 [Ninja 3 Video Production](../../.github/workflows/video-production.yml) → Run workflow。

- `project`：填写你这部作品的项目文件路径，例如 `video/projects/shadow-protocol-mv/project.json`。不再有固定的短片/MV类型下拉框，不再预选剧集。
- `stage = preview`：试渲染（如项目提供）；`final`：直接生成最终版；`all`：从试渲染到最终成片并做技术校验。
- 自动上传 `output/` 里的文件作为 Actions Artifact（保留30天），不会擅自发布到其他平台。

本地工作区示例（当前目录是存放 `ninja/` 与可选 `music/` 的共同父目录）：

~~~bash
python ninja/video/workflow/scripts/production.py --stage validate-all
python ninja/video/workflow/scripts/production.py --project video/projects/shadow-protocol-mv/project.json --stage preview
python ninja/video/workflow/scripts/production.py --project video/projects/deep-abyss-meeting/project.json --stage all
~~~

## 旧代码的地位：可选示例，不是生产规范

- [深渊复盘会](../projects/deep-abyss-meeting/project.json) 的旧 `render.py` 包含固定文字框和角色摆放，仅供其本身继续运行。
- [Shadow Protocol MV](../projects/shadow-protocol-mv/project.json) 用完全独立的 `mv/make_mv.py` 制作音乐节奏影像，可单独运行和预览。
- `scripts/audio.py` 是配音合成与混音**可选模块**，静音、纯音乐及真人配音作品无需使用。
- `episodes/*.json` 是旧漫画短片特定格式，不作为新作品的数据结构要求。
- 技术性流程测试在 `scripts/test_production.py`；旧配音测试在 `scripts/test_audio.py`。

### 怎样判断修复有效

**新增一个画面语言完全不同的视频，不需要修改总工作流，也不用复制旧镜头脚本。** 只需该作品自己的项目文件 + 自己的制作工具，便能使用相同的校验、预览（可选）、正式输出和交付机制。工作流绝不替作品做审美选择。
