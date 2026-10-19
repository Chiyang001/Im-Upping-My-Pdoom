# P(doom) — Code Sculpture

本版全部使用程序化三维几何绘制，没有背景图片、AI 生成图、视频背景或文字贴图。原片仅提供音轨。

成片：output3d/Pdoom_Code_Sculpture_1080p.mp4

## 视觉与动画

- 黑色空间、冰白与青绿线雕、蓝紫色结构点缀。
- 11 类线雕装置对应 34 段歌词：机械眼、回路、损失曲面、透视房间、有机曲线、原子轨道、螺旋蛇、纸夹群、计算阵列、神经网络和导火索。
- 文字从字体矢量轮廓剖分为三角形，挤出成真实三维实体；每个词有自己的空间位置与朝向，沿曲面布局。
- 歌词实体与装置共用透视相机和深度缓冲，具有几何遮挡、挤出侧面、光照、视差。
- 逐词时间驱动抬升与亮度变化；低频重音驱动脉冲；副歌加入放射爆发；纸夹群随段落增大。
- 真实 1920×1080 / 30 fps，4× MSAA，HDR 中间缓冲与轻微辉光。
- 音轨直接复制原始 AAC，不重压缩。

## 复现

在项目根目录执行 `python code3d/render.py`。
预览：`python code3d/render.py --preview`。
依赖：Python、moderngl、numpy、Pillow、fonttools、shapely、mapbox-earcut、imageio_ffmpeg。
程序使用 Windows Arial Bold 的矢量字形。需要支持 OpenGL 3.3 的显卡。
歌词时间轴保存在 work/lyrics.json，逐词参考 work/transcript.json，节奏点保存在 work/beats.json。

开发者：炽阳001
https://space.bilibili.com/404891612
https://github.com/Chiyang001?tab=repositories
