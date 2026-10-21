# 忍3整活音效 × 透明特效素材库

> 2026-10-21 起维护。**保存的是真实音频和可编辑图像序列，不是空链接、第三方网站中转或音效名称清单。**

入口：[可试听/预览/下载的整活素材站](../../comedy/) · [结构化素材清单](catalog.json) · [生成源码](../../tools/generate_comedy_assets.py) · [媒体完整性测试](../../tools/test_comedy_assets.py)

## 经典「曼波！」短叫素材包（2026-10-21新入库，梗本身源于2024）

**[在线试听「曼波专题」](../../comedy/)** · [完整14个 WAV](mambo/mambo-sfx-14-wav.zip) · [文件及来源说明](mambo/README.md) · [JSON元数据](mambo/catalog.json)

这批是另行生成并永久入库的 **14 个有「曼波！」念词的 WAV，定位为旧梗基础素材，不代表2026最新热点**，适合曼波单发、二连、三连、加速、慢放、抽卡出货、空大失败等场景。使用中性中文/日文 TTS 重新念词并加工，**不是游戏诗歌剧原声、声优仿声或第三方热门短视频原音轨**。所以它们与以下24种自制基础音效、16种透明动画是并列分类；网站合计38音效 + 16动画共54条，其中14个曼波是经典短叫变体，与2026年常见的「曼波配音朗读完整文案」不是同一回事。[热点核对报告](../../memes/research/MAMBO_TREND_AUDIT_2026-10-21.md)。总览元数据通过网页组合两个 catalog 读取，避免下次重建基础音效时删除曼波条目。

## 真正入库的格式

| 素材 | 数量 | 文件 | 编辑用途 |
|---|---:|---|---|
| 搞笑音效 | 24 | sfx/ 音频 WAV；comedy-sfx-24-wav.zip | 直接导入剪映、PR、达芬奇、FFmpeg |
| 搞笑动画 | 16 | vfx/ 动画 WebP | 网站循环预览，部分软件可导入 |
| 静态贴图 | 16 | vfx/ 静态 PNG（RGBA） | 字幕边、漫画辅助 |
| 透明序列帧 | 16 套 × 16 帧 | vfx/ *_frames.zip | 可透明叠加的逐帧动画 |
| 一键特效包 | 1 | comedy-vfx-16-complete.zip | 打包全部动画、静态图、序列帧 |

音频：WAV、32kHz、单声道、16-bit PCM，剪辑时可转换到 48kHz。动画：360×360 RGBA，12fps，16 帧、1.33 秒，首尾允许全透明以实现渐入渐出。

音效包括重击 Boom、敲头 Bonk、弹簧、答错、悲伤小号、唱片刹停、尴尬虫鸣、讽刺鼓点、金币叮、键盘狂按、塑料胜利号、倒吸气等。特效包括冲击波、问号、冷汗、怒气青筋、速度线、闪光、火花、烟雾、定格碎裂、彩纸、爱心、聚光灯、警报、感叹号、尘土和金币雨。

## 推荐忍3搞笑短剧场景

- **百炼烧心**：接锤失败叠问号 + 弹簧蹦；等待蓄力配悬念滴答；Boss挪位空大，先唱片刹停再冷场虫鸣。
- **焚天不烧心**：亮相用聚光圈 + 闪光；定身连招用漫画冲击波 + 大重击。
- **抽卡歪了**：错误双响 / 悲伤小号 + 大冷汗；抽中 UP 则用金币雨 / 庆祝彩纸 + 塑料胜利号。
- **鬼畜动作**：阿力弹簧蹦与尘土节奏剪辑；打脸反转用重击后突然静音。
- **制作原则**：先让音效落在反应点，不要把所有效果堆在同一秒；笑点的前后空拍同样重要。

## 如何导入剪辑软件

1. 下载 WAV 或透明 PNG 序列帧 ZIP，解压到本地。
2. 把声音放在角色转身、打断、失败等关键节点，背景音乐适当降低。
3. 将连续命名的 000.png 至 015.png 按 12fps 作为一条图像序列导入，叠加在人物图层上方。
4. WebP 主要用于网站循环预览；并非所有剪辑软件支持透明 WebP。最稳妥的编辑格式是 ZIP 内的 RGBA PNG 序列。

示例（在第 4 秒给已有声轨的 input.mp4 叠加漫画冲击波以及重击音效）：

    ffmpeg -i input.mp4 -framerate 12 -i comic_impact_%03d.png -i comic_boom.wav \
    -filter_complex "[1:v]format=rgba,setpts=PTS-STARTPTS+4/TB[vfx];[0:v][vfx]overlay=x=(W-w)/2:y=(H-h)/2:eof_action=pass[vid];[2:a]adelay=4000|4000[sfx];[0:a][sfx]amix=inputs=2:duration=first:normalize=0[aud]" \
    -map "[vid]" -map "[aud]" -c:v libx264 -pix_fmt yuv420p -c:a aac output.mp4

## 来源、授权和风险

本批音效从头使用 numpy 合成算法生成，没有下载任何热门影视短视频原声、明星语音、鬼畜视频音频或 BGM；视觉特效由 Pillow 逐帧编程生成，不是从第三方视频截取。音效名称指代剪辑上的类似用法，不能冒充经典原版的音色/版权。

本仓库尚无统一 LICENSE 文件，不应推定第三方可自动商用或任意再分发。忍3游戏人物、武器、音乐的权利也不受本包影响。以后如要加入 Freesound 等平台的外部声音，必须记录原上传者、链接及独立音频许可证（常见为 CC0 / CC BY / CC BY-NC，条款各有差异）。

## 生成和验证

    python -m pip install "numpy>=1.26,<3" "Pillow>=11,<13"
    python tools/generate_comedy_assets.py --output assets/comedy
    python tools/test_comedy_assets.py

GitHub Actions：[Build Original Comedy SFX and VFX](../../.github/workflows/build-comedy-kit.yml)。扩容时修改生成器里的 SFX / VFX 项目清单以及各项绘制或合成算法，工作流会自动重新生成、测试并发布实际媒体。无须修改通用视频工作流的创作风格要求。
