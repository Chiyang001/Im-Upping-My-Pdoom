# I'm Upping My P(doom) — Meaning in Motion

**纯代码三维线稿 MV · 空间歌词 · FPV 穿越 · 语义隐喻**

A procedural 3D wireframe music video built with Python and ModernGL. Lyrics are physical geometry in the scene; the camera flies through words, machines and visual metaphors.

![片尾画面](docs/cover.jpg)

由 **炽阳001 / Chiyang001** 制作。当前版本为 **v15 · Meaning in Motion**：所有场景由代码线条与字形轮廓构造，无图片背景或预渲染场景素材。

## 画面设计

- **225 词空间歌词**：按演唱逐词描线，每次最多两个词；字形有厚度、骨架与细节，处于固定三维空间。
- **18 段飞行、17 段实际穿字**：推进、俯冲、侧掠、上升与转向结合，四次爆炸落在 P(doom) 的歌词窗口。
- **概念成为场面动作**：在既有九段隐喻上加入 27 段附加编排，覆盖损失曲线、寿命交易、算力与总线、Lisp 链表、Gato 多任务、急停台、遮蔽 token 和分支未来等。39 项词义与一手出处见 [概念词典](v15/concept_lexicon.md)。
- **Transformer 多分镜**：五个插入机位依次观察 token、位置信息、Q/K/V、四头注意力、残差与前馈、纵深解码；同一词的演唱过程中，装置与镜头持续改变。
- **灾难长镜头与鼓点尾声**：Go 穿越包含色散、震动和结构坍塌；无歌词尾声沿 30 个鼓点穿过九组空间，单向推进 585 个世界单位。
- **完整片尾**：154.6 秒起整帧定格，显示 `I'm Upping My P(doom)` 与 `Made by Chiyang001`。

![隐喻分镜](docs/storyboard.jpg)

## 快速复现

已验证环境：**Windows、Python 3.13、支持 OpenGL 3.3 的显卡**。原始成片为 1920×1080、30 fps、4700 帧，约 2 分 37 秒。渲染速度取决于显卡与 CPU，完整渲染会产生约 GB 级 MP4。

```powershell
git clone https://github.com/Chiyang001/Im-Upping-My-Pdoom.git
cd Im-Upping-My-Pdoom
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

先生成静帧分镜，**无需音频**：

```powershell
.\.venv\Scripts\python.exe v15/render.py --meaning-preview
```

结果保存到 `v15/meaning_storyboard.jpg` 及同目录单帧图片。字体默认寻找本机 Arial Bold，也可显式指定可用的 `.ttf` / `.otf` 文件。

渲染完整 MV，请自行提供与本项目时间轴匹配、可使用的原曲音频或视频（MP4 / M4A 中的 AAC 音轨）：

```powershell
.\.venv\Scripts\python.exe v15/render.py --audio "D:\Music\source.mp4"
```

默认输出：`output_v15/Im_Upping_My_Pdoom_Meaning_in_Motion_1080p.mp4`。音轨使用 `-c:a copy`，不会重新压缩。歌曲、原片及成片音视频未随源码分发；输入音轨需适合直接复制到 MP4 容器。

先渲染一小段：

```powershell
.\.venv\Scripts\python.exe v15/render.py --audio "D:\Music\source.mp4" --sample 30 --duration 3 --output "output_v15/sample.mp4"
```

可配置 `--audio`、`--font`、`--output`、`--backend`，或设置 `PDOOM_AUDIO`、`PDOOM_FONT`、`PDOOM_OUTPUT`、`PDOOM_BACKEND` 环境变量。命令行参数优先；显式相对路径按启动命令的目录解析。`--help` 无需启动 GPU。

```powershell
python v15/render.py --help
python v15/render.py --font "C:\Windows\Fonts\arialbd.ttf" --meaning-preview
```

Linux 无显示服务时可以尝试 `--backend egl` 并指定系统字体；Linux / macOS 未做完整成片验收。字体替换会改变字宽和穿字构图，应重新检查歌词可读性。仓库不包含字体文件。

## 代码结构

本项目逐版迭代，最新版继续使用较早目录中的稳定模块，因此克隆时应保留完整目录结构。

| 位置 | 用途 |
| --- | --- |
| `v15/render.py`、`render_options.py` | 最新渲染入口、输入输出与字体配置 |
| `v15/semantic_geometry.py`、`semantic_score.py`、`transformer_geometry.py` | 附加语义线雕、39项研究与Transformer流程 |
| `v14/metaphor_geometry.py`、`metaphor_extra.py` | 沿用的九段隐喻线雕与时序动作 |
| `v15/flight_camera.py` | 穿字航线与摄影机数学 |
| `v13/` | Go 灾难动画、尾声长航线、字形细节 |
| `v10/`、`v11/`、`v12/` | 分镜、激进镜头与飞行空间 |
| `v9/` | 逐词编排、爆点与剪辑调度 |
| `v4/`、`v5/`、`v7/`、`v8/`、`code3d/` | 几何引擎、早期场景、世界层与摄影机基础 |
| `work/lyrics.json`、`work/transcript.json` | 歌词和逐词时间参考 |
| `code3d/rhythm_v3.json` | 检测节奏、鼓点与冲击数据 |
| `v11/compositions.json` | 最新渲染仍需读取的构图保护数据 |

早期制作与修正脚本一并保留作开发记录；其中部分历史脚本依赖未分发的图片、影音或额外分析工具。**复现最终版本请使用 `v15/render.py`**。核心依赖见 `requirements.txt`；重新做早期节奏分析或语音转录时，相关脚本还需 SciPy、faster-whisper 等可选依赖。

## 检查与制作记录

无需 GPU 的检查：

```powershell
python -m compileall -q code3d work v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15
python v15/audit_words.py
python v15/flight_camera.py
```

空间可读性与实际飞行检查需要字体和 OpenGL：

```powershell
python v15/qa_spatial_words.py v15
python v15/qa_actual_flights.py
```

已有母版验证了完整解码、原 AAC 位流一致性、新增多镜头和语义动作的事件前后七帧以及 62 帧片尾定格。上述数字对应制作时的原字体和原音轨，修改字体或时序后需要重新验收。详细设计与一手概念来源见 [v15 制作说明](v15/README.md)；历史本地成片记录见 [制作历史](docs/LOCAL_RENDER_HISTORY.md)。生成日志、QA 大表、影音和帧图默认由 `.gitignore` 排除。

## 开源与作者

原创代码与原创文档采用 [MIT License](LICENSE)。歌曲、歌词、录音、字体和第三方依赖的权利说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

**炽阳001 / Chiyang001**

- [Bilibili](https://space.bilibili.com/404891612)
- [GitHub](https://github.com/Chiyang001?tab=repositories)
