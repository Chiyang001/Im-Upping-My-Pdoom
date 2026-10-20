# I'm Upping My P(doom) · Kinetic Hook

v19 从首帧开始展示点火机构，前奏用四个快速镜头串起火种、导轨、线圈与虹膜；前半段根据演唱词组重新切换机位。Repeat 用同一轨道的前行、倒走和再次启动表现反复；CDR 段重建为真正有前后关系的 Lisp 取尾机构；FREE 改成七次连续重击，最后一次使整个牢笼碎裂飘散。

所有图形仍是代码绘制的三维线条，没有图片、贴图、背景视频或另加的解说字幕。歌词沿用原演唱时间轴，词形由线条逐步勾勒并安装在场景空间中。v18 的 NVDA → Moon → Omega 物件追踪、单眼造型与持续移动的无限环尾声继续保留；片尾不显示歌名或制作者牌。

## 前奏：1.42 秒内的四个镜头

[hook_director.py](hook_director.py) 用同一枚火种、同一条实际导轨和同一组机器结构建立因果关系。开场第一帧就有发光胶囊与精细加工线条；第一句歌词开始前不显示任何歌词文字。

| 时间 | 镜头与动作 |
| --- | --- |
| 0.00–0.24 | 胶囊、轴承和导轨齿的近距离特写，随火种启动。 |
| 0.24–0.69 | 横向跟移；导轨、胶囊与后方机壳形成不同速度的视差。 |
| 0.69–1.14 | 从低处反看火种越过感应线圈，线圈被依次点亮。 |
| 1.14–1.42 | 向开启的机械虹膜快速前冲，接入第一句的单眼场景。 |

机器由胶囊接缝、紧固孔、双轨、机壳、绕组和有深度的虹膜组成。四个镜头观看同一套物件，物件不会随摄影机切换而重新贴到画面中心。

## 前半段：按词组推进镜头

[first_half_score.py](first_half_score.py) 从逐词时间轴建立前 73.87 秒的 **83 个演唱词组**与 **4 个无词动作段**，由 [first_half_director.py](first_half_director.py) 根据具体场景切换镜头：电路强调横移和层次，控制机构采用较低视角，稳定训练观察机械行程，检验段从上方观察接缝再向下穿出。

每个词组通常含一到两个词。新增机位包含侧向、升降、向前接近与快速离开，切换跟随唱词节点。FREE 连续敲击、NVDA 物件跟拍和已有穿字的接近／越面阶段交由专用镜头保护，避免新增切位破坏动作。最终按 30 fps 检查前半段 2,217 帧，**63 / 83 组采用新增机位**，另四个无词机位均激活；所有摄影机矩阵有限。83 是编排定义数，不能当作新增切镜数。

无词处也有动作：35.52–38.12 秒检查单眼的深层边缘后离开，72.90–73.87 秒沿检验接缝驶出。原有蘑菇、月面、算力、机械蛇、训练和原子机构由新的视角重新组织，保持它们和歌词的对应关系。

## Repeat 与 CDR

[meaning_camera.py](meaning_camera.py) 将 Repeat 的反复落实到摄影机的实际位置：73.87–75.90 秒沿固定神经轨前行，75.90–76.30 秒倒走原路，76.30 秒起再次启动并接入原有穿字。反复发生在同一轨道上；越字之后的附加移动限制在字面切向，保持原有单向越面关系。

CDR 指 Lisp 的取尾操作，典故依据见 [v15 概念词典](../v15/concept_lexicon.md) 与 [本轮设计复核](repeat_cdr_design_review.md)。[cdr_geometry.py](cdr_geometry.py) 删除旧上下两排悬浮矩形盒，改成同一根弯曲三轨桁架上的四个 cons 单元：开放托架容纳 CAR 首元素，深管口与导体承接 CDR 尾指针，选择叉沿尾部依次前进。神经导体从上方贯通，体现歌词从旧符号路线向密集神经计算的转向。

各部件采用固定宿主坐标，镜头先观察头尾分离，再从侧下方跟随尾指针进入深处；88.62 秒后的空隙继续驶过机构。新结构为 **20,042 个线顶点、零三角面**，不使用悬浮图标或旧重复盒体。

## FREE：七次重击，整个牢笼碎裂

[free_impact.py](free_impact.py) 在 56.20–58.43 秒内建立完整机械牢笼。看不见的力先后敲击不同位置，每次都有瞬时压弯、反弹、结构震颤和摄影机后坐；金属永久凹陷逐次积累。

前六次敲击在 **56.380、56.615、56.840、57.070、57.295、57.525 秒**，最后一次在 **57.745 秒**，全部对应实测鼓点。最后一击使竖杆、顶底横梁、侧架、后部支承、轴承和横锁一起断裂，转为 **366 个机械碎片**；没有继续保留完整的大框架。

碎片从被敲弯后的真实源位置散开，保持杆段、套圈和锁件的形状，各自旋转、沿 XYZ 飞离并受重力下落。主体为 29,850 个线顶点，使用一个动态 GPU 批次绘制。摄影机先后坐，再快速进入散开的碎片之间。压力波随每次实际敲击重新计时，不是重复播放同一段开门动画；画面里没有拳头或手掌图案。

## 检查状态

**完整 MP4 已完成，1,195,362,504 字节；全片解码、原 AAC 位流一致性与编码后专项画面复核通过。** 已为 294 个事件各提取七帧，生成 49 页原分辨率联系表；总览图按 JPEG 尺寸上限缩小，分页保留完整检查尺寸。

- 225 个歌词词项保持原顺序，同屏最多两个词；无提前出现、漏词或无法完整勾勒的词。全部词项通过正面、完整入框与至少 28 像素的空间可读性检查。
- 18 段飞行通过越面、越面前可读和无反向回穿检查，其中 17 段实际穿字；GO 保持演唱窗口内越面。
- [Repeat / CDR 专项复核](repeat_cdr_design_review.md) 检查了 8 个相关词与 16 帧源预览。Repeat 在约 77.180 秒穿字一次，无反向重穿；旧悬浮盒体已删除。
- [FREE 源检查及最终集成预览](qa_free_impact_review.md) 通过七次鼓点核对、401 个有限姿态检查和 15 帧完整 HD 预览。全部 366 个碎片离开原位，最大碎片轴向跨度低于 2.64 单位；FREE 在破裂中可读，抽样白色裁切峰值为 0.819%。
- [FREE 实际编码复核](qa_free_encoded_review.md) 检查 24 张成片解码图、三张分页联系表与三张原生 1080p 重点帧。六次预击的击前／击中／回弹与最终全笼碎散均可辨，FREE 在破裂中可读，碎片随后让出前冲通道。实际编码抽样白色裁切峰值为 0.5594%。
- [前奏与前半实际编码复核](qa_hook_encoded_review.md) 解码前奏全部 43 帧：43 帧均不同，最低亮线覆盖率为 19.34%，无空白或静止等待。另复核 24 张前半抽样与九张原生 HD 重点帧，包括两段无词运镜。
- [Repeat / CDR 编码复核](qa_encoded_repeat_cdr_review.md) 检查 16 张成片抽样与四张原生 HD 图片，确认旧悬浮盒删除、共用支架与尾指针存在真实视差。
- [整合编码画面记录](qa_encoded_meaning_review.md) 汇总 48 张实际编码抽样及专项复核的范围。最后 62 个原始和编码后帧均不同，最后八帧也持续运动；无标题、署名、缓存定格或时间钳制。七张未修改后半段与尾声原始 RGB 抽样帧和 v18 完全相同。单眼造型保留，机位与构图按本轮要求改变。

## 复现

从完整仓库根目录运行。Python、ModernGL / OpenGL 3.3+ 与其他依赖见 [根 README](../README.md) 和 [requirements.txt](../requirements.txt)。请自行提供有使用权、且与时间轴匹配的音视频源；原曲录音和字体不随源码分发，歌词时间参考的权利说明见 [第三方声明](../THIRD_PARTY_NOTICES.md)。

```powershell
python v19/render.py --audio "path/to/source.mp4"
```

默认输出：

```text
output_v19/Im_Upping_My_Pdoom_Kinetic_Hook_1080p.mp4
```

目标规格为 **1920×1080、30 fps、4700 帧、H.264 / yuv420p**。源 AAC 使用 `-c:a copy` 直接复制。可通过 `--font`、`--backend` 和 `--output` 指定环境；局部样片示例：

```powershell
python v19/render.py --audio "path/to/source.mp4" --sample 56.2 --duration 2.23 --output "free-sample.mp4"
```

生成本轮分镜预览无需音轨：

```powershell
python v19/render.py --meaning-preview
python v19/qa_free_preview.py
python v19/qa_repeat_cdr.py
```

预览保存在 `v19/` 的联系表、分页图和单帧图片中。可运行源检查：

```powershell
python v19/audit_words.py
python v19/qa_spatial_words.py v19
python v19/qa_actual_flights.py
python v19/qa_free_impact.py
python v19/qa_preserved_scenes.py
```

完整 MP4 完成后运行最终检查入口：

```powershell
python v19/build_review_events.py
python v19/validate_v19.py --source "path/to/source.mp4" --events v19/review_events.json
python v19/qa_encoded_meaning.py
python v19/qa_free_encoded.py
python v19/qa_encoded_repeat_cdr.py
python v19/verify_ending.py
```

验证器 `validate_v19.py` 读取本轮 `v19/` 和 `output_v19/`；以脚本实际默认值和参数帮助为准。

| 文件 | 用途 |
| --- | --- |
| [render.py](render.py)、[render_options.py](render_options.py) | 整合镜头、固定物件宿主、歌词空间排布、后处理与输入输出 |
| [hook_director.py](hook_director.py) | 四个前奏镜头与同一套点火机构 |
| [first_half_score.py](first_half_score.py)、[first_half_director.py](first_half_director.py) | 演唱词组切位、无词段落动作与前半物件编排 |
| [meaning_camera.py](meaning_camera.py)、[cdr_geometry.py](cdr_geometry.py) | 同轨反复运镜与 Lisp 取尾机构 |
| [free_impact.py](free_impact.py) | 七次受力、渐进凹陷、完整牢笼碎裂与局部镜头位移 |
| [object_pursuit.py](object_pursuit.py)、[infinity_finale.py](infinity_finale.py) | 保留 v18 的实体追踪和持续移动的无限环尾声 |

v19 依赖完整仓库的公共模块与历史目录，包括 `code3d/`、`work/`、`v4/`–`v18/`，不要只拷贝 `v19/`。过往典故研究见 [v15 概念词典](../v15/concept_lexicon.md)，前半实体设计见 [v17 说明](../v17/README.md)，物件追踪与无限环的原始设计见 [v18 说明](../v18/README.md)。

制作者：**炽阳001 / Chiyang001** · [Bilibili](https://space.bilibili.com/404891612) · [GitHub](https://github.com/Chiyang001?tab=repositories)
