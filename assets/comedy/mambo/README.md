# 曼波音效专包 · 14 个新制作的语音版本

**[打开忍村整活素材站 →「曼波专题」](../../../comedy/)** · [下载全部14个 WAV](mambo-sfx-14-wav.zip) · [素材元数据](catalog.json)

这批不只是“曼波风格的电子音”，有明确念出“曼波！”和“マンボ！”的语音。使用普通中日双语神经 TTS 新生成声源，再做速度、音高、回声、机械故障和原创提示音处理，实际文件为 WAV。

**不是《赛马娘》诗歌剧游戏原声，也不是UP主的音效包、翻唱、声线克隆或原角色配音。** 很多剪辑合集带有“未经授权禁止转载”，本包不复制这些原音轨。命名“曼波”只是表达网络声音梗的用法，并不保证与原版原声相同。使用时仍须遵守语音服务和剪辑平台的规则。

## 文件清单

| 文件 | 声音内容 | 推荐的忍3搞笑场景 |
|---|---|---|
| mambo_ja_single.wav | 日语单发 | 小椒突然登场 |
| mambo_ja_double.wav | 日语双连 | 两连空大、双重呆滞 |
| mambo_zh_single.wav | 中文单发 | 中文短剧反应音 |
| mambo_zh_triple.wav | 中文三连 | 连续抽歪、失败循环 |
| mambo_fast.wav | 高速1.45倍 | 技能狂按、鬼畜加速 |
| mambo_slow.wav | 慢放0.74倍 | 时间凝固、反应迟钝 |
| mambo_helium.wav | 尖声变调 | 可爱人物反差 |
| mambo_deep.wav | 低音变调 | Boss沉重出场 |
| mambo_echo.wav | 带延迟回声 | 一个人喊全村听 |
| mambo_robot.wav | 机械颤音 | 机械Boss、鬼畜卡壳 |
| mambo_win.wav | 上行喜报提示音 | 抽卡出货 |
| mambo_fail.wav | 下行失败提示音 | 百炼没接锤、抽卡歪 |
| mambo_alarm.wav | 警报声 | 残血、Boss来袭 |
| mambo_stutter.wav | 短促复读卡顿 | 抽搐鬼畜 |

音频均为PCM 16-bit、32kHz、单声道，可导入剪映、PR、达芬奇、FFmpeg。全部 ZIP 完整打包下载，元数据包含独立文件路径、声源语言、声音处理方法、时长、字节大小与 SHA256 校验。

## 参考链接（不是声音采样来源）

- [B站：诗歌剧活全家音效合集——投稿标注未经作者授权禁止转载](https://www.bilibili.com/video/BV13T421k732/)
- [爱给：曼波音效变体归类参考](https://www.aigei.com/sound/class/man_bo_bu_1/)

实际声音使用普通中性声音模型 zh-CN-XiaoxiaoNeural 和 ja-JP-NanamiNeural 的全新念词录制及程序变速变调；非游戏或UP主录音。素材元数据以 original_game_voice=false 明确区分。工具链受TTS服务条款约束，不能自动宣称无条件商用授权。

## 生成、验证和后续扩容

源码：[generate_mambo_sfx.py](../../../tools/generate_mambo_sfx.py) · [test_mambo_sfx.py](../../../tools/test_mambo_sfx.py) · [GitHub自动构建](../../../.github/workflows/build-mambo-sfx.yml)。

    python -m pip install "numpy>=1.26,<3" "edge-tts>=7,<8"
    python tools/generate_mambo_sfx.py --output assets/comedy/mambo
    python tools/test_mambo_sfx.py

本包独立于原来24个基础音效及16种透明特效，视频制作工作流只需按本次创意选择声音，不会强制其他视频使用同一音效或模版。
