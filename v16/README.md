# I'm Upping My P(doom) · Integrated Linework

v16 修复 v15 新增元素与原场景风格分离的问题。画面统一为精密机械线雕：对象具有厚度、安装点、支承、线束和远近遮挡，语义动作发生在同一个三维空间中。全部道具、字形与线条仍由代码构造，不使用图片素材或背景视频。

## 本轮调整

开场和 Shinigami 段恢复 **v14 原版单眼球**，移除双眼轮廓、双瞳、寿命钟表及附加红线。[qa_eye_restore.py](qa_eye_restore.py) 比较了两版在 1.6、3.7、5.3、32.8、34.9、36.8、37.8 秒的原始 1920×1080 RGB 帧，七组 SHA256 全部一致；运行后生成本地报告 `eye_restore_validation.json`。这是编码前的精确复原检查，不能推及未抽样的所有帧或编码后的像素。

v15 的 27 个附加语义 cue 筛选为 **16 个**。11 个展板、图标或重复装饰场面回退原场景或取消附加覆盖：`sparks`、`circuits`、`hierarchy`、`risk1`、`shinigami`、`stable`、`optimizing`、`sydney`、`basilisk`、`moon`、`approval`。原歌词、主体场面与节奏继续保留。

其余场面做结构上的融合：

- **GPU / FLOPS**：取消画面上沿四枚悬浮芯片、红色斜脚和过亮双塔，改成一体机舱、嵌入式核心、散热折片、深部接头与互联线束。只有一次有限的接点显露，不再循环扫动。
- **CDR**：链表节点改为沿纵深错位的机械单元，以实体管线连接；取尾与头部脱离仍可读，取消独立指示箭头和正面卡片展板。
- **Loom**：正面分支树改为空间分岔轨道与端口；选中的一条路径逐渐显露，其他分支在不同深度展开。
- **Gato / masked / von Neumann**：任务输入、遮蔽补齐和存储总线安装到相同的承重件与线束上，减少悬浮图标。Gato 独立镜头、十字控制符号及 PTO 雨伞取消。
- **Transformer**：保留多头注意力等结构，降低连线与红粉色增益，让骨架、端点和连接关系先可辨。

所有 v15 新增的独立循环扫线均已移除；v14 原有的连续 witness 信号、冲击线、实际穿越与必要的物理接触继续使用。`semantic_director.py` 的静态检查确认没有 `draw_red_path` 调用或取模相位循环。

## 16 个筛选后的语义 cue

[semantic_score.py](semantic_score.py) 编排以下场面；它们补充 v14 已有的中文房间、Shoggoth 面具、回形针工厂、正交坐标与递归制造。

| 秒 | 场面 |
|---|---|
| 9.08–12.99 | 损失骤降轨道 |
| 64.22–65.94 | Omega 汇聚 |
| 65.94–68.185 | FLOPS 计算机舱 |
| 73.87–77.24 | MLP 前向、反向与重复 |
| 77.24–80.68 | von Neumann 存储总线与替代路径 |
| 84.78–89.995 | CDR 空间链表机械 |
| 89.995–94.06 | Gato 多任务输入通道 |
| 98.845–102.32 | 回形针封住关机工位退路 |
| 102.32–104.33 | 燃烧的引线 |
| 109.33–115.00 | Transformer 计算结构 |
| 118.645–120.18 | GPU 机舱与互联 |
| 122.54–124.04 | 分支轨道前奏 |
| 125.86–127.96 | Loom 的路径选择 |
| 127.96–129.60 | 遮蔽符片与上下文补齐 |
| 132.22–136.83 | 未知观测窗与百叶闭合 |
| 136.83–141.20 | 舞台背后的机械结构 |

## Transformer 多机位

109.82–114.10 秒的 **五个插入机位**仍围绕同一套固定空间装置展开：token 与位置编码、Q/K/V 投影、四个不同关系模式的注意力头、拼接及残差/前馈路径、纵深解码层。114.10 秒后接既有 DISOBEY 穿字飞行。

四条重复水平扫描线已删除，部件通过安装件与原机械空间连接；权重与输出按阶段显露。73.87–77.24 秒的训练另用一次前向、一次回传、一次重复表现，不与推理镜头混为同一动作。歌词中的脱轨属于艺术讽喻，不表示 Transformer 结构必然导致反抗。

## 文件与研究依赖

| 文件 | 用途 |
|---|---|
| [render.py](render.py) | 渲染入口、场景组合、逐词字形与编码 |
| [semantic_score.py](semantic_score.py) | 16 个 cue 与五个 Transformer 插入机位 |
| [semantic_director.py](semantic_director.py) | 有限语义动作与部件增益，不含新增循环扫线 |
| [integrated_semantics.py](integrated_semantics.py) | 有厚度的链表、记忆体、任务通道、遮蔽件及分支轨道 |
| [cohesive_geometry.py](cohesive_geometry.py) | GPU 机舱、核心、散热、互联与通用机械安装件 |
| [style_audit.md](style_audit.md) | v14/v15 实际成片风格对照与处理清单 |
| [style_preview_review.md](style_preview_review.md) | v16 首轮静帧复核 |

v16 在完整仓库中运行，继续依赖 `code3d/` 及前代 `v4/`–`v15/` 的公共模块。特别是 v14 的 `metaphor_geometry.py`、`metaphor_extra.py`，以及 v15 的 `semantic_geometry.py`；Transformer 几何由本目录的 `transformer_geometry.py` 提供。不要只拷贝 `v16/`。

典故研究沿用 [v15/concept_lexicon.md](../v15/concept_lexicon.md) 与 [JSON 数据](../v15/concept_lexicon.json)，包含 39 项概念、歌词时间、一手来源与解释边界。CDR 按 Lisp 的取尾操作呈现；Loom 按分支式语言模型界面呈现。Ilya 段保持未知，不捏造秘密发现。

## 渲染与预览

在项目根目录运行。环境、依赖安装、字体与后端选项见仓库根目录 README。需要 Python、ModernGL / OpenGL 3.3+、字体及 `requirements.txt` 中的依赖；请提供可使用的源音视频：

```powershell
python v16/render.py --audio "path/to/source.mp4"
```

语义静帧预览无需音轨：

```powershell
python v16/render.py --meaning-preview
```

默认输出：`output_v16/Im_Upping_My_Pdoom_Integrated_Linework_1080p.mp4`。目标为 1920×1080、30 fps、H.264 / yuv420p，源 AAC 通过 FFmpeg 直接复制。还可用 `--font`、`--backend`、`--output`、`--sample` 和 `--duration` 指定环境或渲染短片段。

## 保留内容与验证状态

完整 225 词仍按演唱逐词描线，同屏最多两词，作为三维结构存在；四次爆炸继续对齐 P(doom) 词点。Go 灾难长航线、其他穿字飞行、尾声穿越不同场景的鼓击编排保留。

154.6 秒起使用整帧定格，包含完整歌名 `I'm Upping My P(doom)` 与署名 `Made by Chiyang001`。编码设置继续复制原 AAC，不改变原声。

最终母版为 **1920×1080、30 fps、4700 帧，1,136,924,405 字节**。已完成以下验证：

- 七帧单眼原始 RGB 与 v14 完全一致；新增扫线静态检查通过。
- 225 词顺序、无提前、同屏最多两词、完整描线及空间可读性通过。
- 18 条飞行中的 17 处实际穿字成立，先可读后越面，无反向回穿；Go 在演唱窗口内穿越。
- 全片音视频解码无错误，原 AAC 位流 SHA256 一致。
- 165 个事件各提取七帧用于转场复核；实际编码的 44 帧语义联系图、GPU 四时刻序列及四张 1080p 重点帧通过[风格抽样验收](qa_encoded_meaning_review.md)。
- 最后 62 个输入帧完全一致；编码后与定格首帧的最大平均像素差为 0.119 / 255，完整歌名与署名可见。

在项目根目录可复核完整编码和片尾，生成的影音、帧图与大表均保留本地：

```powershell
python v16/build_review_events.py
python v16/validate_v16.py --events v16/review_events.json
python v16/verify_tail.py
python v16/qa_encoded_meaning.py
python v16/qa_gpu_strip.py
```

解码与音轨检查覆盖完整文件；视觉结论来自所列抽样，静帧不能单独证明全片每一帧的动态效果。

制作者：**Made by Chiyang001（炽阳001）** · [Bilibili](https://space.bilibili.com/404891612) · [GitHub](https://github.com/Chiyang001?tab=repositories)
