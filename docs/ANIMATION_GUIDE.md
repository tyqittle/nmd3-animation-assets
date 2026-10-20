# 将素材用于代码动画 / MV

## 1. 来源与筛选

优先真正的角色全身立绘和动作大图，不把官网宣传横幅、小尺寸头像冒充人物可动素材。先检查原始来源、实际像素和裁剪区域，再决定能否用作视频镜头。

## 2. 下载与核查

```bash
pip install -r requirements.txt
python scripts/fetch_assets.py
python scripts/audit_assets.py
```

`catalog/assets.json` 的 `download_status=downloaded` 仅是下载程序写出的结果；实际使用仍应核查图片文件存在、内容正确和透明度。

## 3. 动画工作流

角色和背景独立分层，补全被遮挡的四肢；采用骨骼动画、关键帧/逐帧、镜头运动、樱花与墨迹粒子、景深和音频节拍检测。每个镜头都应绑定明确图层与素材 ID。针对动作镜头优先 60 FPS 渲染并导出 H.264/AAC 兼容 MP4。

## 4. 素材命名

`assets/<类别>/<素材ID>.<扩展名>`。保留素材原始直链、来源网页、像素尺寸、校验 SHA256，编辑副本单独保存，不覆盖原图。
