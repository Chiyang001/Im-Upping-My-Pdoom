# 素材与依赖说明

本仓库的 MIT 许可证适用于原创渲染代码、场景编排及原创文档。它不授予歌曲、歌词、录音、参考视频、字体或第三方依赖的权利。

- **歌曲与歌词**：本项目为《I'm Upping My P(doom)》制作程序化 MV。歌词文本与时间轴来自用户提供的制作材料；用户提供的参考链接指向 MusicPerson (Udio User) 与 osmarks 的 [P(doom) 歌词词条](https://genius.com/Musicperson-udio-user-and-osmarks-pdoom-lyrics)。相关歌词与录音的权利归其各自权利人，未纳入本项目的 MIT 授权。原始录音、参考视频及带原音轨的成片不随源码分发。复现时请自行提供有权使用的音频。
- **字体**：代码读取本机字体并提取轮廓，仓库不包含 Arial 或其他字体文件。原版使用 Windows Arial Bold；替换字体时请遵循所用字体自身的许可证。换字体可能改变字宽、构图与穿字取景，需要重新检查。
- **画面**：最新版 v17 · First Half Alchemy 的三维线框、场景与字形细节均由代码构造。`docs/` 中的预览图来自这些程序生成的画面。旧阶段的外部图片素材未收录。当前风格调整与复现方式见 [v17 制作说明](v17/README.md)。
- **Python 与工具依赖**：NumPy、ModernGL、glcontext、Pillow、fontTools、Shapely、mapbox-earcut、imageio-ffmpeg 及其 FFmpeg 二进制各自适用上游许可证；本仓库不重新许可这些组件。

概念研究沿用 v15 的 39 项词义整理，一手出处见 [v15 制作说明](v15/README.md#主要一手参考)、[概念词典](v15/concept_lexicon.md) 与 [v14 隐喻研究笔记](v14/metaphor_research.md)。v17 的前半词义呈现见 [当前制作说明](v17/README.md) 与 [前半覆盖研究](v17/first_half_coverage.md)。
