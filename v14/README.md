# I'm Upping My P(doom) · Hidden Machine

v14 在 v13 的穿越镜头基础上，把歌词中的关键概念做成会运转、会改变周围空间的线框机械。画面由 Python 构造三维线条、字形轮廓与几何，交给 OpenGL 渲染；不使用图片素材或背景视频。歌词继续随演唱逐词出现，并作为镜头实际穿过的空间结构。

## 九段隐喻动作

| 时间 | 歌词概念 | 场面动作 |
|---|---|---|
| 26.06–29.68 | Chinese room | 输入符片经过规则阵列和往复搬运机构，转为输出符片；封闭房间内保留空椅子和规则桌。镜头穿入符号处理空间。 |
| 29.68–31.83 | Shoggoth | 笑脸壳向两侧打开，显露后方的异质触须、器官和牵引线；转弯后的庞大身体接住穿越镜头。 |
| 80.68–84.78 | Sharp left turn | 红色能力骨架从青色约束笼中急转脱离，原有笼体留在旧方向，表现能力与约束没有一同泛化。 |
| 95.91–98.85 | Paperclips | 连续三个工位把家具、资源球送入输送与成形装置；资源缩减，回形针群沿前方路线填满空间。 |
| 104.54–109.40 | Orthogonality | 能力脊柱向上延展，独立的目标机构仍锁定回形针；直角框架表现能力与最终目标的独立维度。 |
| 115.00–116.88 | Post-Chinchilla | 空心机芯收紧，四股数据流进入紧密晶格，展示模型体量与数据投入的重新配比。 |
| 120.18–122.54 | RLHF goes askew | 前段的笑脸和神经丛再次出现，反馈耦合环偏轴转动，面具打开；既有视觉母题变成失稳的反馈机构。 |
| 127.96–131.46 | Recursive self-upgrade | 装配框、机械臂和三代结构依次生成，焊接弧光伴随新一代机械成形，形成“机器制造下一代机器”的空间链。 |
| 132.22–135.68 | What did Ilya see? | 层叠观测窗与百叶结构开启、错位，中央保持未知；不展示或捏造任何所谓秘密发现。 |

这些场面是歌词的艺术化解释。中文房间属于哲学论证，回形针和递归升级属于思想实验或假设，sharp left turn 属于风险模型，笑脸 Shoggoth 属于文化隐喻；它们均不被表述为已经发生的事实。Chinchilla 的研究结果也不等于安全边界必然失效。

## 镜头与节奏

- 新增 `CHINESE ROOM`（27.280 s）与 `MASK REVEAL`（30.580 s）两处穿字事件，让镜头从歌词进入对应机械空间。
- 保留四处 P(doom) 歌词爆点和已有的非爆点穿字路线；相机使用真实空间位移，配合转向、俯冲和局部色散。
- 保留 Go 末尾的灾难式长穿越，以及尾声连续穿越不同场景的 30 点鼓击编排。
- 154.6 s 起整帧定格，显示完整歌名 `I'm Upping My P(doom)` 和 `Made by Chiyang001`。

## 输出与复现

输出：`output_v14/Im_Upping_My_Pdoom_Hidden_Machine_1080p.mp4`。

编码设置：1920 × 1080、30 fps、约 156.667 s，H.264 / yuv420p、CRF 18、faststart。音频映射原片音轨，使用 FFmpeg `-c:a copy` 复制原 AAC 位流，不重新编码。

在项目根目录运行：

```powershell
python v14/render.py --audio "path/to/source.mp4"
```

隐喻分镜静帧预览：

```powershell
python v14/render.py --metaphor-preview
```

主要新增源码为 `metaphor_geometry.py`、`metaphor_extra.py`，由 `render.py` 调度各段动作与穿越。渲染继续依赖 v4–v13 中的字形、几何、歌词时间轴、分镜和飞行模块。完整研究、逐词时间及表意边界见 `metaphor_research.md` 和 `metaphor_research.json`。

开源入口另支持 `--font`、`--output`、`--backend` 与对应 `PDOOM_*` 环境变量；详情见仓库根目录 README。未分发原曲录音与字体文件，静帧预览不需要音轨。

## 成片验证

- `validation.txt`：完整解码通过；原片与成片 AAC 位流 SHA256 一致。129 个剪辑、飞行、语义动作、鼓点事件分别抽取前后七帧，保存为 `transition_contact_page_*.jpg`。
- `token_validation.json`、`qa_spatial_words_v14.json`：225 词顺序与起音正确，无提前、漏词，每次最多两词；每词至少一帧完整描线、正面且全字框入画，字高至少 28px。
- `qa_actual_flights.json`：18 段飞行中 17 段实际穿字，均先可读后越面，无反向回穿；FUSE 保持侧掠。Go 实际穿面约为 94.798 秒。
- `qa_encoded_metaphors.jpg`、`qa_metaphor_visual_review.json`：从最终 MP4 抽取七场、四阶段的 28 帧独立复核，面具真身、资源转换、数据汇聚与递归制造均可辨认。
- `freeze_validation.json`、`encoded_freeze_validation.json`：154.6 秒后的 62 个输入帧完全相同；编码后平均像素差最大约 0.119/255，完整标题与署名均在定格中。

最终文件为 1,168,144,622 字节，4700 帧。上一版 v13 成片保留在 `output_v13/`。

复核命令：

```powershell
python v14/audit_words.py
python v14/qa_spatial_words.py v14
python v14/qa_actual_flights.py
python v14/build_review_events.py
python v14/validate_v14.py --events v14/review_events.json
python v14/verify_tail.py
python v14/qa_encoded_metaphors.py
```

## 一手参考

- [Searle：Minds, Brains, and Programs](https://cse.buffalo.edu/~rapaport/Papers/Papers.by.Others/Searle/searle80.html)：中文房间的符号操作论证。
- [Ouyang 等：Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)：RLHF 的实际训练方法，区别于“笑脸面具”的艺术隐喻。
- [Soares：Capabilities generalization and the sharp left turn](https://www.alignmentforum.org/posts/GNhMPAWcfBCASy8e6/a-central-ai-alignment-problem-capabilities-generalization)：能力泛化而约束未同步泛化的风险模型。
- [Bostrom：The Superintelligent Will](https://nickbostrom.com/superintelligentwill.pdf)：正交性、工具性动机与回形针目标示例。
- [Hoffmann 等：Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)：Chinchilla 的参数与数据分配研究。
- [I. J. Good：Speculations Concerning the First Ultraintelligent Machine](https://gwern.net/doc/ai/1966-good.pdf)：机器设计更强机器的早期假设。

制作者署名：Made by Chiyang001（炽阳001）。

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
