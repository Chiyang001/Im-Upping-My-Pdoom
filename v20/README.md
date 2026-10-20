# I'm Upping My P(doom) · Semantic Thrust

当前为 **v20 平稳镜头修订**。所有场景、歌词时序和物件动作沿用 v20，仅去掉普通鼓点震动、瞬时焦距变化、全画面缩放，以及每一到两个词重置的摄影机叠加。当前修订已完成渲染与重新验收，下面的原版记录单独标为历史。

v20 的 **127.90–132.22 秒**仍为 masked pre-training → recursive self-upgrade 的档案输送、遮罩开启、训练扫描、输出提取与连续自造机器空间。原有定向分镜、前奏四镜头、Repeat 同轨往返、CDR 共用支架、FREE 七次重击与全笼碎裂、NVDA → Moon → Omega 实体跟拍、P(doom) 爆炸和穿字，以及持续穿入无限环的尾声继续保留。片尾不显示歌名或制作者牌。

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

## 本轮普通镜头修订

[render.py](render.py) 停止调用前半段的 `phrase_camera` 和后半段的 `pair_camera`。这些逐词组叠加机位会在短词窗口重新设置位移、方向、倾斜与焦距；当前普通段落改由 v20 原有分镜持续定向推进，不再要求每一到两个词触发机位变化。

同时去掉普通鼓点的高频眼位、倾斜与焦距扰动，以及前奏和普通画面的鼓点缩放。原有亮度节奏、场景变化、逐词描线和语义机构动作保留；FREE 的真实重击、GO 灾难、P(doom) 爆炸和尾声鼓点飞行仍由各自的专用逻辑控制。

[pair_director.py](pair_director.py) 仍提供原机构的有限动作，包含存储架退役、多模态通道拉紧、算力包失稳和舞台支承等。停用的是其摄影机叠加，场景中的部件、固定物件宿主与运动时序保持不变。前半段实体几何及其机构动作同样保留。

专用段落继续拥有优先级：FREE、NVDA / 月面 / Omega、Repeat、CDR、Transformer 和训练自升级段各有自己的运动逻辑。原穿字航线和真实场景转场保留。本轮没有另建或替换场景。

## 检查状态与范围

**当前平稳镜头修订已完成：1,284,600,419 字节，1920×1080、30 fps、4700 帧。** 225 词空间可读性和时序通过；18 段专用飞行中 17 次实际穿字，全部有穿越前可读帧且无反向回穿。全片解码、原 AAC 位流一致性检查通过，音轨 SHA256 为 `80613c12ac602d1ff19d6ba61a2b26a34e4a23b6c1efa22a2a3d6df82bb4572d`。最后 62 个编码帧全部不同，最后八帧持续运动。

[独立运镜检查](qa_smooth_camera.md) 与原始 v20 Git 源码比较了 75 个同一句内部的普通词组边界，逐词组镜头叠加实际调用为零；87 次普通鼓点测试的相机姿态和投影完全相同，11 组原有专门运镜保持实际位移。全部行首、行末及原有分镜/专用镜头转换统一排除并另记，不宣称全片无切镜或零跳变。

本轮重新生成 356 个事件的七帧联系表。68 张整合编码图的五页及开头 32 张编码取样均已观察，另检查两张 BAG 原尺寸画面。[当前成片抽样复核](qa_smooth_encoded_review.md) 明确了范围；取样与数值检测不代表逐帧人工观看全片。

### 原始 v20 的历史验收

以下记录对应修改前的 `Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4`，不代表当前修订的成片状态。

**原始 MP4 为 1,210,355,128 字节；全片解码与原 AAC 位流一致性通过。** 225 词保持原序、同屏最多两词，全部通过完整描线和空间可读性检查。18 段飞行中 17 处实际穿字，均先可读后越面，无反向回穿。最后 62 个原始输入帧及编码后帧全部不同，最后八帧持续运动；无片尾歌名或署名。

[qa_pair_coverage.py](qa_pair_coverage.py) 的原版检查对 **225 个词、166 个演唱词组**按 30 fps 取样实际 `frame_view`。检测时去掉公共世界 Z 向前移，并把瞬时鼓点抖动设为零。逐词组机位启用时，历史结果为 **166 / 166 组**有符合阈值的摄影机变化，没有无效方向或非有限投影矩阵。当前已停用这层机位，因此该统计不能作为当前修订的通过结论。

这个结果证明摄影机在活动，**不能证明每个词的含义都被表达，也不等于审美通过或逐帧观看了全片**。导演名称、阶段计数和姿态变化不能代替实际画面检查。词是否正面、完整入框、完整勾勒且达到可读尺寸，由独立的空间词检查判断；镜头再活跃，也可能把字切出画面。

[qa_upgrade_motion.py](qa_upgrade_motion.py) 确认新机器只有线几何、坐标有限，七个唱词节点对应不同动作，五段采样内均有 XYZ 位移；六个抽样读词点的字面朝向余弦为 0.866–0.979。新场景的 [25 帧集成预览复核](qa_upgrade_visual_review.md) 已观察三页联系表及重点原尺寸帧，检查机器视差、物理字面、段落交接和出口补齐。

[实际编码专项复核](qa_upgrade_encoded_review.md) 从最终 MP4 解码 127.80–132.40 秒的 25 张图片并观察全部三页联系表，另检查 128.470、129.420、130.360、132.200 秒的原生 1080p 帧。额外的 128.000 秒原生帧确认 FROM 清晰、未继承旧转场的径向模糊，也没有旧黑色机器骨架遮挡。出口结构在 132.200 秒仍可见。这共计 26 张不同解码图，其中五张检查原尺寸；复核结论仅覆盖这些取样，不等于观看了完整电影的每一帧。

原版 [build_review_events.py](build_review_events.py) 编排 **356 个检查事件**，当时的验证器为每个事件提取前后各三帧，生成 60 页联系表。全片解码与原 AAC 位流一致性由 [validate_v20.py](validate_v20.py) 单独验证。原版前奏、FREE、月面追踪和尾声的七张保护场面原始 RGB 抽样帧与 v19 完全相同；本轮普通镜头与后期缩放已调整，不沿用像素完全一致的结论。

[后半段实际编码复核](qa_pair_encoded_review.md) 检查 40 张图片、五页联系表与四张原生 HD 重点帧，确认短词机位、引线、GPU、正交轴和幕后等场面仍协调。[整合编码记录](qa_encoded_meaning_review.md) 汇总 68 张实际编码抽样的检查范围。上述均为明确范围的取样与转场检查，不是全片每一帧的人工审看记录。

## 复现

在完整仓库根目录运行。环境依赖见 [根 README](../README.md) 与 [requirements.txt](../requirements.txt)。请提供有使用权且与时间轴匹配的音视频源；原录音与字体不随源码分发，权利范围见 [第三方声明](../THIRD_PARTY_NOTICES.md)。

```powershell
python v20/render.py --audio "path/to/source.mp4"
```

默认输出：

```text
output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_Smooth_1080p.mp4
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
python v20/qa_smooth_camera.py
python v20/audit_words.py
python v20/qa_spatial_words.py v20
python v20/qa_actual_flights.py
```

完整 MP4 结束编码后，执行成片检查：

```powershell
python v20/build_review_events.py
python v20/validate_v20.py --source "path/to/source.mp4" --events v20/review_events.json
python v20/qa_upgrade_preview.py --encoded "output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_Smooth_1080p.mp4"
python v20/qa_encoded_meaning.py
python v20/verify_ending.py
```

本地报告、单帧和联系表写入 `v20/`；它们不作为生产输入随仓库分发。验证器读取本轮 `v20/` 和 `output_v20/`，具体参数以脚本的 `--help` 为准。

| 文件 | 用途 |
| --- | --- |
| [render.py](render.py)、[render_options.py](render_options.py) | 摄影机优先级、固定物件宿主、空间词排布、合成与输出 |
| [upgrade_geometry.py](upgrade_geometry.py)、[upgrade_director.py](upgrade_director.py) | 新建档案、训练与自造机器，以及逐词动作、物理字面与快速机位 |
| [pair_director.py](pair_director.py) | 保留原机构有限动作；逐词组摄影机叠加在生产入口中停用 |
| [qa_pair_coverage.py](qa_pair_coverage.py) | 原版词组摄影机活动统计；当前不再以每词组变化为验收目标 |
| [qa_upgrade_motion.py](qa_upgrade_motion.py)、[qa_upgrade_preview.py](qa_upgrade_preview.py) | 新机器结构检查、源预览和 MP4 解码取样 |
| [hook_director.py](hook_director.py)、[first_half_director.py](first_half_director.py) | 保留前奏与前半段的演唱词组编排 |
| [meaning_camera.py](meaning_camera.py)、[cdr_geometry.py](cdr_geometry.py)、[free_impact.py](free_impact.py) | 同轨 Repeat、Lisp 取尾机构与七次敲击全笼碎裂 |
| [object_pursuit.py](object_pursuit.py)、[infinity_finale.py](infinity_finale.py) | 实体追踪与持续移动的无限环尾声 |

v20 依赖完整仓库的公共模块与历史目录，包括 `code3d/`、`work/`、`v4/`–`v19/`，不要只拷贝 `v20/`。上一轮设计见 [v19 说明](../v19/README.md)，典故与实体覆盖见 [v15 概念词典](../v15/concept_lexicon.md) 和 [v17 说明](../v17/README.md)。

制作者：**炽阳001 / Chiyang001** · [Bilibili](https://space.bilibili.com/404891612) · [GitHub](https://github.com/Chiyang001?tab=repositories)
