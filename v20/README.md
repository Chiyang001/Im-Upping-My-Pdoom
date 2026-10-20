# I'm Upping My P(doom) · Semantic Thrust

v20 重做 **127.90–132.22 秒**的 masked pre-training → recursive self-upgrade：删除中央同心环与小型机器人展示，改为档案输送、遮罩开启、训练扫描、输出提取与连续自造机器的实际空间。镜头更接近机构，沿横向、纵向和深度快速移动；唱词推动具体机械动作。

新增的后半段词组导演把歌词中的退役、左转、释放、失控、引线和幕后等含义转为摄影机的运动任务。前奏四镜头、前半段词组机位、Repeat 同轨往返、CDR 共用支架、FREE 七次重击与全笼碎裂、NVDA → Moon → Omega 实体跟拍，以及持续穿入无限环的尾声继续保留。片尾不显示歌名或制作者牌。

所有图形仍由代码生成三维线条。没有图片、贴图或背景视频；字体轮廓也转为实际线几何，按原演唱时间逐词勾勒。

## 这次重建的场景

[upgrade_geometry.py](upgrade_geometry.py) 构建 **23 组部件、21,236 个线顶点、零三角面**。档案页、遮罩、训练梳、输出导体、升降抓取器与打印桁架属于同一条有物理连接的加工路线。不同阶段靠真实前后关系形成视差。

[upgrade_director.py](upgrade_director.py) 使用以下唱词节点驱动动作：

| 唱词 | 起点 | 场景与镜头 |
| --- | ---: | --- |
| From | 127.90 | 档案页沿输送线进入；镜头斜向下降并接近进料口。 |
| masked | 128.08 | 两侧遮罩沿固定机架退出，露出数据区域。 |
| pre-training | 128.56 | 快切至训练机构的侧上方；训练梳与样本沿连接导体扫描。 |
| days | 129.18 | 与机身连接的刻度链逐步累积；镜头在同一条轨迹中加速横移、降低。 |
| to | 129.60 | 升降夹具提取训练输出；摄影机随提取方向向上移动。 |
| recursive | 129.98 | 打印臂向输出轨折展，种子机器制造首个后继机构；镜头掠过加工正面。 |
| self-upgrade | 130.56 | 切回已有单向穿字路径；更深、更复杂的后继机器沿实际飞行路线生成。 |

三个后继机构具有不同拓扑：基础门架、增加打印轴的深桁架，以及展开翼板的宽幅机器；并非把相同图标重复放大。它们是“用自身输出制造更强后继系统”的视觉隐喻，并不声称是训练系统的工程原理图。典故研究沿用 [v15 概念词典](../v15/concept_lexicon.md)。

首六个词安装在固定机器表面，安装平面的朝向不依赖当前摄影机。词组按原几何范围缩放至机械字面，仍保持逐词出现。SELF-UPGRADE 交回原有实际穿字字面及越面路径。132.20 秒附近另设固定的出口桁架，使摄影机越字后仍有前景导轨与后继翼板经过镜头，随后接入下一句。

预览曾发现主体偏小、机构偏暗及出口接近空白；最终版本收近机位约 20–25%、增强机器层次，并补齐出口结构。这些修订已进入生产代码，详见 [结构与动作复核](qa_upgrade_design.md) 和 [集成预览复核](qa_upgrade_visual_review.md)。

## 按一到两个词推进

[pair_director.py](pair_director.py) 将新增后半段机位绑定至逐词时间轴。每句有持续的物理运动意图，各词组是沿这个意图的连续观察：

- von Neumann 段跟随存储架退役、下沉与退出；Sharp left turn 接近岔路并沿左支线驶离。
- Gato 段观察多模态通道的拉紧与释放；纸夹段跟随材料进入模具、掠过输出端。
- Killswitch / PTO 从高处开关下降至缺席的操作位置；引线段沿同一条燃烧导体向终点前进。
- Orthogonality 分别沿能力轴上升、沿独立目标轴横移；GPU / RLHF 检查机芯、跟随反馈并随失控回路倾斜。
- Loom 跟随被选中的分支；Ilya / show 从见证窗口进入幕后，改变角度以显露上方支承与牵线。

新增动作直接修改原机构的存储架、通道、算力包及舞台支承。物件宿主锚定于原始编排坐标，避免摄影机移动时整套机构也贴着镜头移动。135.80–136.90 与 140.60–141.20 秒的无词间隙也安排离开窗口、驶入上方结构的运镜。

专用段落继续拥有优先级：FREE、NVDA / 月面 / Omega、Repeat、CDR、Transformer 和本轮新建场景各有自己的运动逻辑。已有穿字的接近、越面与短暂稳定阶段受保护；允许的后续附加位移限制于字面切向，保持单向穿越关系。

## 检查状态与范围

**完整 MP4 已完成，1,210,355,128 字节；全片解码与原 AAC 位流一致性通过。** 225 词保持原序、同屏最多两词，全部通过完整描线和空间可读性检查。18 段飞行中 17 处实际穿字，均先可读后越面，无反向回穿。最后 62 个原始输入帧及编码后帧全部不同，最后八帧持续运动；无片尾歌名或署名。

[qa_pair_coverage.py](qa_pair_coverage.py) 对 **225 个词、166 个演唱词组**按 30 fps 取样实际 `frame_view`。检测时去掉公共世界 Z 向前移，并把瞬时鼓点抖动设为零，以免把共同前进或抖动算成分镜设计。最终 **166 / 166 组**在局部位移、视向、倾斜、焦距或词组边界中观察到符合阈值的摄影机变化，没有无效方向或非有限投影矩阵。相同检测方法在 v19 中得到 146 组，其余 20 组需要额外场景动作或视觉复核。

这个结果证明摄影机在活动，**不能证明每个词的含义都被表达，也不等于审美通过或逐帧观看了全片**。导演名称、阶段计数和姿态变化不能代替实际画面检查。词是否正面、完整入框、完整勾勒且达到可读尺寸，由独立的空间词检查判断；镜头再活跃，也可能把字切出画面。

[qa_upgrade_motion.py](qa_upgrade_motion.py) 确认新机器只有线几何、坐标有限，七个唱词节点对应不同动作，五段采样内均有 XYZ 位移；六个抽样读词点的字面朝向余弦为 0.866–0.979。新场景的 [25 帧集成预览复核](qa_upgrade_visual_review.md) 已观察三页联系表及重点原尺寸帧，检查机器视差、物理字面、段落交接和出口补齐。

[实际编码专项复核](qa_upgrade_encoded_review.md) 从最终 MP4 解码 127.80–132.40 秒的 25 张图片并观察全部三页联系表，另检查 128.470、129.420、130.360、132.200 秒的原生 1080p 帧。额外的 128.000 秒原生帧确认 FROM 清晰、未继承旧转场的径向模糊，也没有旧黑色机器骨架遮挡。出口结构在 132.200 秒仍可见。这共计 26 张不同解码图，其中五张检查原尺寸；复核结论仅覆盖这些取样，不等于观看了完整电影的每一帧。

本轮 [build_review_events.py](build_review_events.py) 编排 **356 个检查事件**，最终验证器已为每个事件提取前后各三帧，生成 60 页联系表。全片解码与原 AAC 位流一致性由 [validate_v20.py](validate_v20.py) 单独验证。前奏、FREE、月面追踪和尾声的七张保护场面原始 RGB 抽样帧与 v19 完全相同。

[后半段实际编码复核](qa_pair_encoded_review.md) 检查 40 张图片、五页联系表与四张原生 HD 重点帧，确认短词机位、引线、GPU、正交轴和幕后等场面仍协调。[整合编码记录](qa_encoded_meaning_review.md) 汇总 68 张实际编码抽样的检查范围。上述均为明确范围的取样与转场检查，不是全片每一帧的人工审看记录。

## 复现

在完整仓库根目录运行。环境依赖见 [根 README](../README.md) 与 [requirements.txt](../requirements.txt)。请提供有使用权且与时间轴匹配的音视频源；原录音与字体不随源码分发，权利范围见 [第三方声明](../THIRD_PARTY_NOTICES.md)。

```powershell
python v20/render.py --audio "path/to/source.mp4"
```

默认输出：

```text
output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4
```

目标规格：**1920×1080、30 fps、4700 帧、H.264 / yuv420p**。源 AAC 使用 `-c:a copy` 复制；`--font`、`--backend` 和 `--output` 可以覆盖环境默认值。局部样片：

```powershell
python v20/render.py --audio "path/to/source.mp4" --sample 127.9 --duration 4.5 --output "upgrade-sample.mp4"
```

无需音轨的源预览与检查：

```powershell
python v20/render.py --meaning-preview
python v20/qa_upgrade_preview.py
python v20/qa_upgrade_motion.py
python v20/qa_pair_coverage.py --version v20
python v20/audit_words.py
python v20/qa_spatial_words.py v20
python v20/qa_actual_flights.py
```

完整 MP4 结束编码后，执行成片检查：

```powershell
python v20/build_review_events.py
python v20/validate_v20.py --source "path/to/source.mp4" --events v20/review_events.json
python v20/qa_upgrade_preview.py --encoded "output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4"
python v20/qa_encoded_meaning.py
python v20/verify_ending.py
```

本地报告、单帧和联系表写入 `v20/`；它们不作为生产输入随仓库分发。验证器读取本轮 `v20/` 和 `output_v20/`，具体参数以脚本的 `--help` 为准。

| 文件 | 用途 |
| --- | --- |
| [render.py](render.py)、[render_options.py](render_options.py) | 摄影机优先级、固定物件宿主、空间词排布、合成与输出 |
| [upgrade_geometry.py](upgrade_geometry.py)、[upgrade_director.py](upgrade_director.py) | 新建档案、训练与自造机器，以及逐词动作、物理字面与快速机位 |
| [pair_director.py](pair_director.py) | 新增后半词组机位、无词间隙驶离与原机构的有限动作 |
| [qa_pair_coverage.py](qa_pair_coverage.py) | 实际摄影机姿态检测，剔除公共世界位移与瞬时鼓点抖动 |
| [qa_upgrade_motion.py](qa_upgrade_motion.py)、[qa_upgrade_preview.py](qa_upgrade_preview.py) | 新机器结构检查、源预览和 MP4 解码取样 |
| [hook_director.py](hook_director.py)、[first_half_director.py](first_half_director.py) | 保留前奏与前半段的演唱词组编排 |
| [meaning_camera.py](meaning_camera.py)、[cdr_geometry.py](cdr_geometry.py)、[free_impact.py](free_impact.py) | 同轨 Repeat、Lisp 取尾机构与七次敲击全笼碎裂 |
| [object_pursuit.py](object_pursuit.py)、[infinity_finale.py](infinity_finale.py) | 实体追踪与持续移动的无限环尾声 |

v20 依赖完整仓库的公共模块与历史目录，包括 `code3d/`、`work/`、`v4/`–`v19/`，不要只拷贝 `v20/`。上一轮设计见 [v19 说明](../v19/README.md)，典故与实体覆盖见 [v15 概念词典](../v15/concept_lexicon.md) 和 [v17 说明](../v17/README.md)。

制作者：**炽阳001 / Chiyang001** · [Bilibili](https://space.bilibili.com/404891612) · [GitHub](https://github.com/Chiyang001?tab=repositories)
