# P(doom) — LINE ARCHITECTURE

当前交付：output_v4/Pdoom_Line_Architecture_1080p.mp4

这一版完全以程序化三维线条、字形轮廓、路径和相机动画构建，不加载任何背景图片、AI图像、视频画面或字体纹理。原始视频仅提供音乐音轨。

## 制作与修订

- 34段歌词逐句配置不同空间结构与镜头，不使用上一版的公共底盘、圆盘或五种循环排版。
- 字体矢量轮廓直接变成线段，并构造前后轮廓、纵深连接、曲面字、字形建筑、纸夹链与经纬编织。
- 歌词与环境共享三维坐标、投影相机与深度缓冲；字的笔画连接到电路、轨道、承重结构、房间、织机等装置。
- 每句按当前演唱结构的实际三维包围盒确定景别，已唱完的字可以掠镜，当前唱句受画幅约束。
- 节奏从原音轨重新分析：132.003 BPM、344拍、399个主要冲击。混音频段检测用于视觉节奏，不是分离后的鼓轨。
- 强拍驱动几何闭合、坠落、断裂、剪切、爆裂与镜头切换；4次副歌分别承担不同字形结构。
- 通过多轮分镜、连续样片与独立评审修改；最新画幅抽查558个时刻，当前唱句无出画记录。
- 尾奏将字形扩张为空间网络，最后收束为无穷轨迹。

## 输出与复现

1920×1080，30fps，2分36.667秒，H.264；4×MSAA、HDR中间缓冲与细线辉光。
原始AAC音轨直接复制，未重新压缩。

在项目根目录运行：

```powershell
python v4/render.py
python v4/render.py --preview
python v4/render.py --audit
python v4/render.py --sample 20
```

主要文件：

- v4/render.py：字形、动画、节奏事件、镜头、渲染与合成。
- v4/scenes_early.py：第0–16段的环境几何。
- code3d/scenes_late_v4.py：第17–33段的环境几何。
- v4/engine.py：几何与字体路径辅助代码。
- code3d/analyze_rhythm_v3.py / rhythm_v3.json：重新生成的节奏数据。
- work/lyrics.json / transcript.json：歌词时间轴与逐词参考。
- v4/framing_audit.json：画幅抽查数据。

依赖：Python、numpy、Pillow、scipy、moderngl、fonttools、shapely、mapbox-earcut、imageio_ffmpeg。
字体轮廓来自Windows Arial Bold；所有字形在GPU中均为实际线段，没有字幕贴图。

开发者：炽阳001
Bilibili：https://space.bilibili.com/404891612
GitHub：https://github.com/Chiyang001?tab=repositories

## 最终检查

- 全片完整解码通过。
- 原始AAC音频码流SHA256完全一致。
- 558个演唱画幅抽查样本，当前唱句未超出画幅。
- 12fps动态诊断未检测到演唱段内超过0.5秒的近静止。
- 强鼓附近有对应的可检测画面波动；该项仅用于节奏诊断，不作为艺术效果高低的客观证明。
- 对照检查与连续样片已覆盖开场、副歌、左转、破围、GPU剪切等段落。
