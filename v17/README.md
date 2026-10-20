# I'm Upping My P(doom) · First Half Alchemy

v17 丰富前半段 0–73.87 秒的实体词义，让蘑菇袋、机械蛇、算力登月、控制工位、对话机构和训练装置进入既有三维世界。道具具有厚度、支承、接头与纵深；全部由代码线条构造，不使用图片、背景视频或额外解释字幕。原版单眼球与后半段机械线雕、Transformer 多机位和穿字镜头继续保留。

## 实际编排

[first_half_score.py](first_half_score.py) 新增 **14 个 FIRST_HALF_CUES**；[semantic_score.py](semantic_score.py) 同时沿用 v16 的 **16 个语义 cue**。两套时间区间可以重叠，例如登月场面与 Omega 汇聚。具体动作由 [first_half_director.py](first_half_director.py) 和 [semantic_director.py](semantic_director.py) 驱动，以下描述对应当前实现。

| 时间 / cue | 实体与动作 |
| --- | --- |
| 5.70–9.08 · circuits | 有接头的机械线束与分叉触点，一条接点结构有限显露。 |
| 12.99–16.20 · control | 龙门、缆索、控制台与夹持端；控制台下降，夹持端上升，呈现控制关系的张力。 |
| 16.20–22.19 · dialogue | 对话符片装在机械收纳结构中，穿梭件横向传递，咬合件先压缩再放开。 |
| 22.19–24.12 · risk | 机械虹膜与细丝收紧，P(doom) 原爆点之后扩张、退场。 |
| 24.12–26.06 · foom | 两个纵深机床工位依次显露，新生机件抬升，承接爆炸后的高速飞行。 |
| 27.80–29.68 · shrooms | 中文房间出口方向的敞口袋、提绳和支承台，袋中三株蘑菇有伞盖、柄与菌褶；输送梁接入右侧分拣机，菌丝一次显露为上方菌褶拱顶。 |
| 38.19–41.16 · stable | 训练台、层级工步与活塞完成一次下压、回位。 |
| 41.16–44.79 · singularity | 两段纵深制造工位与机械臂，子结构显露并沿上方、深处移动。 |
| 44.79–48.645 · optimization | 起伏误差地形、固定轨道与球形接点；接点沿轨前进，连接既有 ACCELERATING 飞行。 |
| 48.645–52.56 · atoms | 组装架与三维晶格；两组晶格横向移动并旋转四分之一周，机械臂提供装配环境。 |
| 52.56–58.43 · sydney | 对话穿梭件一次向右、向深处传递；出口锁闩随后打开。 |
| 60.30–62.34 · basilisk | 固定支承上的分节机械蛇、楔形头与下颌；下颌有一次有限位移。 |
| 62.34–65.94 · orbital | 左侧算力机组沿高度和纵深递进，上升轨连接右上月面泊位，有托盘与轮组的计算核心沿同一实体轨道一次上行。 |
| 68.20–73.87 · inspection | 局部检验夹具与样件，后方更大范围的工厂结构逐渐显露。 |

这些动作通过固定场景宿主和既有摄影机路线连接，保留逐词字形在空间中的位置。新编排使用有限进度控制显露和位移，不加入独立循环红扫线。

## 三个重点物件

**袋子与蘑菇。** [organic_geometry.py](organic_geometry.py) 构造袋口、褶皱、提绳、承重件以及多方向的菌盖、菌柄和菌褶。它们放在 ROOM 穿字之后仍可见的出口方向，让 bag 与 shrooms 有可认出的实体关系。单主袋装在载台上，右侧规则分拣机通过实体梁连接；同源菌丝长成上方大伞菌褶拱顶，延续困惑意象。没有右侧悬浮副袋。

**Basilisk。** 同一模块用连续分节躯体、颈部、楔形头、下颌和锚固件形成机械蛇。蛇是歌词思想实验与社群梗的原创具象表达；当前动作是有限下颌位移。研究笔记中提出的回望、回折因果索和轨道收紧不属于当前已实现动作。

**NVDA → Moon → Omega。** [orbital_geometry.py](orbital_geometry.py) 提供七层线雕：位移球面、不同尺度凹坑、月缘、递进算力机组、立体升轨、晶圆与核心、安装泊位。月球具有真实三维起伏，算力设施带机壳、散热折片、互联与嵌入式核心。62.34 秒起它们共用固定宿主；64.22 秒后与沿用的 Omega 汇聚场面重叠，继续接向 FLOPS 机舱。NVDA 的登月意象表达夸张上冲的歌词双关。

## 研究与实现边界

典故研究沿用 v15 的 [39 项概念词典](../v15/concept_lexicon.md) 与 [JSON 数据](../v15/concept_lexicon.json)。[前半段覆盖研究](first_half_coverage.md) 和 [设计数据](first_half_coverage.json) 进一步记录词窗、出处、原画面缺口及创意提案。

研究文档是设计提案，不能据此认定每个拟议动作都已实现。当前优化段的轨道保持固定；原子段表现晶格移动和旋转；检验段呈现局部夹具与更大工厂的尺度关系。拟议中的轨道改道、夹爪从原梁抽出晶格后留下缺口、量规侧翻等动作，均不作为当前完成项。实际部件、时序与变换以两个 director 的代码为准。

歌曲中的中文房间、技术奇点、智能爆炸、Basilisk 与 Omega 具有不同的思想实验、假说或虚构背景。画面用于艺术表达。Ilya 段仍保持未知；原单眼不叠加第二只眼、寿命时钟或数字。

## 保留内容与回归

新增前半段场面沿用 v16 的视觉语言。后半段 MLP、Gato、Transformer 多机位、GPU 一体机舱、Loom 分支、P(doom) 爆点、Go 灾难穿越以及鼓点长尾继续保留。歌词仍按演唱逐词描线，同屏最多两个词。

已经完成的源画面与数学检查：

- [qa_preserved_scenes.py](qa_preserved_scenes.py) 生成 `preserved_scenes_validation.json`：顺序加载 v16、v17，并清理项目模块缓存后，14 个原始 RGB 帧 SHA256 全部完全一致。单眼时刻为 1.6、3.7、5.3、32.8、34.9、36.8、37.8 秒；后半时刻为 75、92.5、111.7、119.7、125.5、145.4、155 秒。该结果限于所列抽样帧。
- [qa_spatial_words.py](qa_spatial_words.py) 生成 `qa_spatial_words_v17.json`：225 词原序一致，最多两词，无提前出现；每词至少有一帧完整描线、正面、全字框入画且高度不少于 28 px。
- [qa_actual_flights.py](qa_actual_flights.py) 生成 `qa_actual_flights.json`：18 段飞行中 17 段实际穿字，全部在越面前有可读帧，无反向回穿；Go 在演唱窗口内约 94.798 秒越面。
- [orbital_geometry.py](orbital_geometry.py) 生成 `orbital_geometry_audit.json`：七层、49,072 线顶点、零面片，局部边界及歌词中央走廊检查通过。

最终母版为 **1920×1080、30 fps、4700 帧，1,150,459,346 字节**，完整编码检查已完成：

- 全片音视频解码无错误；AAC 位流 SHA256 与原文件一致。
- 192 个事件各提取前后三帧及事件帧，用于转场复核。
- 实际编码的 64 个画面和六张 1080p 原图通过[风格与词义抽样验收](qa_encoded_meaning_review.md)。
- 最后 62 个输入帧完全相同；编码后与定格首帧的最大平均像素差为 0.119 / 255。
- 最终管线与道具调整后的 14 帧原眼与后半精确保留检查再次通过。

解码和音轨检查覆盖完整文件；视觉结论来自所列抽样，不把静帧检查当成全片每一帧动态效果的证明。生成的媒体和详细 JSON 报告保留本地，不随源码分发。

原声继续通过 `-c:a copy` 复制。154.6 秒起整帧定格，保留完整歌名 `I'm Upping My P(doom)` 和 `Made by Chiyang001`。

## 复现

从完整仓库根目录运行，环境与依赖安装见 [根 README](../README.md)。需要字体、Python、ModernGL / OpenGL 3.3+ 及 `requirements.txt` 中的依赖。请自行提供可使用且与本项目时间轴匹配的源音视频：

```powershell
python v17/render.py --audio "path/to/source.mp4"
```

语义分镜预览无需音轨：

```powershell
python v17/render.py --meaning-preview
```

预览保存在 `v17/meaning_storyboard.jpg`、分页面与同目录单帧图片。默认成片路径为 `output_v17/Im_Upping_My_Pdoom_First_Half_Alchemy_1080p.mp4`，目标格式为 1920×1080、30 fps、H.264 / yuv420p，源 AAC 直接复制。也可用 `--font`、`--backend`、`--output`、`--sample` 和 `--duration` 指定环境或渲染短片段。

```powershell
python v17/qa_preserved_scenes.py
python v17/qa_spatial_words.py v17
python v17/qa_actual_flights.py
python v17/build_review_events.py
python v17/validate_v17.py --events v17/review_events.json
python v17/verify_tail.py
python v17/qa_encoded_meaning.py
```

| 文件 | 用途 |
| --- | --- |
| [render.py](render.py)、[render_options.py](render_options.py) | 场景组合、字形、镜头、输入输出与编码 |
| [first_half_score.py](first_half_score.py)、[first_half_director.py](first_half_director.py) | 14 段前半编排与有限动作 |
| [first_half_geometry.py](first_half_geometry.py) | 控制、对话、训练、制造、优化、晶格和检验装置 |
| [organic_geometry.py](organic_geometry.py) | 蘑菇袋、菌褶、机械蛇及承重件 |
| [orbital_geometry.py](orbital_geometry.py) | 月面地形、上升算力、晶圆、轨道和泊位 |
| [semantic_score.py](semantic_score.py)、[semantic_director.py](semantic_director.py) | 沿用的 16 段语义编排与 Transformer 插入机位 |
| [qa_preserved_scenes.py](qa_preserved_scenes.py) | 隔离模块缓存、顺序 GL 上下文的原始画面精确保留检查 |

v17 继续依赖完整旧目录中的公共模块，包括 `code3d/` 与 `v4/`–`v16/`，以及 `work/` 中的歌词、逐词时间和节奏数据。不要只拷贝 `v17/`。历史研究、静态审计及预览记录用于解释制作过程；最终复现入口为 `v17/render.py`。

制作者：**Made by Chiyang001（炽阳001）** · [Bilibili](https://space.bilibili.com/404891612) · [GitHub](https://github.com/Chiyang001?tab=repositories)
