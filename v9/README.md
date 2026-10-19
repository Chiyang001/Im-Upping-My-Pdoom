# I'm Upping My P(doom) — Word Impact

成片：output_v9/Im_Upping_My_Pdoom_Word_Impact_1080p.mp4。

本版把副歌的爆炸重音移到P(doom)，并重做歌词呈现：225个词按演唱起音出现，每次最多一到两个词。最终定格同时显示完整歌名 **I'm Upping My P(doom)** 与 **Made by Chiyang001**。

## P(doom) 爆点

| 副歌 | P(doom)演唱区间／秒 | 爆点／秒 |
| --- | --- | --- |
| 1 | 23.560–24.040 | 23.620 |
| 2 | 59.940–60.300 | 59.985 |
| 3 | 96.300–96.680 | 96.335 |
| 4 | 125.400–125.860 | 125.460 |

识别稿将P(doom)拆成p和-do，已合并校正。爆炸源点使用独立词体的真实三维中心；四处按方向、色彩与强度递进。原FOOM 25.685秒和Basilisk Boom 62.060秒的爆炸已移除；FOOM处保留快速匹配转场。奇点、原子、引信、围栏与升级的五处语义爆发继续保留。

## 随词构图

- 未唱到的字形完全不绘制；取消未来词鬼影、整句支架、完整字形预描与旧句残留。
- 单词或双词组使用独立的三维轮廓、背边和局部支架，按组重新定位、缩放并附着于场景中的不同装置。
- 双词组内每个词仍在自己的演唱起音出现，前词在第二词唱出时可以保留；下一组开始后上一组移除。
- 跨不同文字曲面的配对拆成单词，避免继承旧整行坐标后左右反序。
- 关键词使当前装置夹紧、扩张、剪切、编织或观察，场景动作跟随当前词。
- 225词与原歌词规范化后一一对应；按30fps扫描无漏词或提前出现，每词都有完整描线的画面，同屏最大两词。520个有词的取景采样未发现投影出框。

这套检查约束词序、时间和边界；另从完整成片复核了四次P(doom)、旧Boom位置、开场、Chinese room、PTO／引信与结尾问句，未发现整行鬼影、跨行反序或持续截词。

## 最终定格

无穷符号缩小上移，完整歌名以单行三维线稿刻在其下，署名独立一行。标题在154.10秒前完整、署名在154.45秒前完整。154.6秒开始冻结整帧，保持到156.667秒；末尾不淡黑。

## 源码与复现

从项目根目录执行：

```powershell
python v9/render.py
python v9/render.py --words-preview
python v9/render.py --audit
python v9/audit_words.py
python v9/validate_v9.py --events v9/review_events.json
```

- word_score.py：校正演唱时间、单词／双词编组、严格可见时间窗和空间入退场。
- impact_score_v9.py：四处P(doom)爆点及五处其他语义爆发。
- end_title.py：完整歌名、署名和无穷图形的最终布局。
- edit_director_v9.py：保留31处人声快切，FOOM处改为匹配剪辑。
- render.py：独立词体、场景动作、冲击波、尾声与成片集成。
- word_timeline.json、token_validation.json：逐词时间、词序、帧覆盖与爆点归属证据。
- framing_result.json、validation.txt、freeze_validation.json：取景、完整解码、音轨位流与定格检查。

保留v8的快速镜头和v7的30拍尾声，全部画面由代码线条构成。1920×1080、30fps、156.667秒，H.264、4×MSAA；原始AAC音轨直接复制。

最终成片975,034,597字节。全片解码与原AAC位流一致性检查通过；最后62个输入帧完全相同，编码后定格抽查平均像素差低于0.059／255。完整歌名与署名已从最终MP4抽帧确认。

开发者：炽阳001

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
