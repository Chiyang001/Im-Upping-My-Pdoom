# I'm Upping My P(doom) · Object Pursuit

v18 让摄影机跟随场景里的具体物件：追上登月载荷，掠过月面，再转向 Omega 汇聚点；在 FREE 处让看不见的巨力打裂牢笼，摄影机随冲击后坐并向前穿出。末尾改成追逐火种、穿过立体无限环、进入深处虹膜的连续镜头。按照本轮要求，取消旧版整帧定格、歌曲标题和制作者文字。

所有新结构仍由代码绘制三维线条，不使用图片、背景视频或额外说明字幕。v17 的词义道具、原单眼、Transformer 分镜与既有穿字段落继续作为基础；本轮主动修改的镜头和结尾不属于旧版逐像素保留范围。

## 物件与摄影机共用同一世界

[render.py](render.py) 将原摄影机封装为 `authored_frame_view`。`semantic_host` 只读取这个基础摄影机来固定物件宿主，随后 `frame_view` 再叠加物件追踪、FREE 冲击和新尾声。物件不会因为摄影机开始追踪而反过来贴在镜头上，也不会逐帧追随屏幕中心。

[object_pursuit.py](object_pursuit.py) 使用实际绘制的升轨节点、载荷位置、固定月球中心和独立 Omega 宿主。歌词附着面继承物件坐标，不根据观看方向生成正对镜头的牌子。

| 时间 | 追踪对象与镜头行为 |
| --- | --- |
| 62.34–63.26 | 跟随实际算力托盘上行，目光略领先载荷，沿高度、侧向和纵深接近。 |
| 63.26–64.06 | 月面成为前景参照物；镜头在凹坑起伏前作斜向掠过，独立改变 X、Y、Z。 |
| 64.06–64.22 | 用 160 ms 横跨两处实体之间的空间，从月面甩向 Omega。 |
| 64.22–65.94 | 追随独立汇聚点，球形焦点增长并接向后续算力场面。 |

本地 `qa_object_pursuit.json` 对 62.34–65.94 秒进行了 864 次数学采样：世界坐标路径长 **174.84 单位**，X / Y / Z 跨度分别为 **45.20 / 32.23 / 34.68 单位**，坐标均为有限值。检查也确认此段没有重新穿过前一处 P(doom) 字面；60.245 秒的原爆点不在新追踪区间内。这些数据用于确认实际平移与路径隔离，不代替画面验收。

其他段落也加入与实体方向一致的平移：蘑菇袋沿承载方向递送，镜头跟随；优化段追随轨道车的实际路径；原子段随晶格横向转移。它们保留原有场景和合理留白，不额外叠加悬浮图标。

## FREE：看不见的重击

[free_impact.py](free_impact.py) 提供 `build_free_impact`、`sample_free_impact` 与 `draw_free_impact`。牢笼由带纵深支承的框架、成组半杆、轴承、套箍、横锁、锁栓和金属碎屑组成，接在原对话空间里。没有完整拳头、手掌图案或独立循环扫线。

- 56.20 秒起建立完整牢笼，57.56 秒起预压。
- **57.745 秒**的实测鼓点触发主重击。受力点附近的杆件先变形，随后向上下及纵深撕开；外侧完整杆保留尺度参照。
- **57.970 秒**发生锁件回弹。弯折和振铃逐渐衰减，不将整套动作重置循环。
- 锁栓与碎屑从锁和杆件的接触位置飞出；短暂压力弧随主击消散。
- 摄影机先沿宿主局部 Z 后坐，再叠加 X、Y、Z 位移穿入开口，承接 58.43 秒的下一段。动作不只依靠滚转或画面抖动。

原牢笼环境和旧对话锁闩在新牢笼接管时退下，避免两套重叠的杆件破坏受力关系。

## ∞：继续向前的结尾

[infinity_finale.py](infinity_finale.py) 用固定世界坐标构建有厚度的扭转带、刻线、横肋、紧固细节与交叉支承。两个环瓣在交叉处相隔 **6.4 个局部单位**，形成真实前后关系；不是数层重叠的平面无限符号。

152.50 秒起，末段鼓点依次引出无限环的整体、近侧轨道和交叉口。摄影机追逐同一枚火种沿右侧环瓣转向，经过交叉口后继续进入后方虹膜。虹膜后面有深喉部，最后一帧之前仍保持向前移动。旧长尾房间逐步交接，旧火种与尾迹随新镜头接管退下，避免同时出现两个视觉焦点。

本轮不在 154.6 秒冻结时间或复用帧缓存，也不绘制片尾标题、署名牌。制作者信息保留在项目文档中。

## 检查状态

本轮源画面已经通过 [FREE 与追踪预览复核](qa_action_preview.md)。[无限环与尾声预览复核](qa_finale_preview.md) 提出的旧火种交接修正已接入渲染器。预览检查针对实际渲染图片，不把代码参数当作视觉效果的证明。

时间轴保持 **225 个歌词词项、原顺序、同屏最多两个词**。全部词项通过完整描线、正面朝向、入画和空间可读性检查，`to` 的月面安装角度修正已通过最终回归。现有 18 段飞行检查已通过越面、越面前可读和无反向回穿检查，其中 17 段包含实际穿字；GO 仍在演唱窗口内越面。

**完整 MP4 已完成，1,161,046,765 字节；全片解码与原 AAC 位流一致性检查通过。** 原音轨使用 `-c:a copy`。完成 207 个事件的转场抽帧；[编码后动作复核](qa_encoded_action_review.md) 检查了 44 张编码抽样图和七张额外的 1080p 重点帧，确认 FREE 破笼、NVDA 追踪、月面掠过与 Omega 汇聚的实际效果。

[编码后尾声复核](qa_finale_encoded.md) 检查六个阶段与最后八帧。最后 62 个原始输入帧和编码后帧均为 **62 / 62 不同**，最后八帧的相邻差值也全部大于零；无冻结、时间钳制、歌名或制作者铭牌。七张原单眼和六张未修改的后半段原始 RGB 抽样帧与 v17 逐像素相同。视觉结论限于说明中列明的实际抽样，不代表逐帧人工观看全部画面。

## 复现

从完整仓库根目录运行，Python、ModernGL / OpenGL 3.3+ 与其他依赖见 [根 README](../README.md) 和 `requirements.txt`。请自行提供具有使用权、且与本项目时间轴匹配的音视频源。字体使用本机系统字体，默认优先系统粗体无衬线；字体与原歌曲不随源码分发。

```powershell
python v18/render.py --audio "path/to/source.mp4"
```

默认输出：

```text
output_v18/Im_Upping_My_Pdoom_Object_Pursuit_1080p.mp4
```

目标规格为 **1920×1080、30 fps、4700 帧、H.264 / yuv420p**，源 AAC 直接复制。通过 `--font`、`--backend` 和 `--output` 指定环境，也可用 `--sample`、`--duration` 渲染局部。

生成本轮动作分镜预览无需音轨：

```powershell
python v18/render.py --meaning-preview
```

预览输出到 `v18/meaning_storyboard.jpg`、分页图和同目录单帧图片。可依次运行专项检查与最终编码检查：

```powershell
python v18/qa_object_pursuit.py
python v18/qa_preserved_scenes.py
python v18/qa_spatial_words.py v18
python v18/qa_actual_flights.py
python v18/build_review_events.py
python v18/validate_v18.py --source "path/to/source.mp4" --events v18/review_events.json
python v18/qa_encoded_meaning.py
python v18/verify_ending.py
```

| 文件 | 用途 |
| --- | --- |
| [render.py](render.py)、[render_options.py](render_options.py) | 基础摄影机与追踪隔离、词形组合、后处理、输入输出和编码 |
| [object_pursuit.py](object_pursuit.py) | 载荷、月面、Omega 的真实物件坐标与追踪路径 |
| [free_impact.py](free_impact.py) | 牢笼线稿、有限重击、杆件失效和宿主局部镜头位移 |
| [infinity_finale.py](infinity_finale.py) | 立体无限环、火种路径、虹膜和持续移动的尾声 |
| [first_half_director.py](first_half_director.py)、[semantic_director.py](semantic_director.py) | 前半物件动作、歌词语义和场景交接 |
| [qa_object_pursuit.py](qa_object_pursuit.py) | 追踪路径、实体距离与旧爆点隔离检查 |

v18 继续依赖完整旧目录中的公共模块，包括 `code3d/`、`work/`、`v4/`–`v17/`；请保留旧版完整目录，不要只拷贝 `v18/`。典故研究继续引用 v15 的 [39 项概念词典](../v15/concept_lexicon.md)，前半实体词义设计见 [v17 说明](../v17/README.md)。旧版成片与制作记录保留，v18 的复现入口为本目录 `render.py`。

制作者：**炽阳001 / Chiyang001** · [Bilibili](https://space.bilibili.com/404891612) · [GitHub](https://github.com/Chiyang001?tab=repositories)
