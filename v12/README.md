# I'm Upping My P(doom) — Flight

成片：`output_v12/Im_Upping_My_Pdoom_Flight_1080p.mp4`。

本版把爆点相机改成真正的单向飞行。相机先逼近固定字面，词体迅速扩张并从镜头两侧掠到身后，然后继续进入字后舱体，直到下一处真实转场。没有穿完倒飞回原位置，也没有转头回看背面文字。

## 穿越设计

| 爆点 | 演唱区间／秒 | 相机穿过字面／秒 |
| --- | --- | --- |
| P(doom) 1 | 23.560–24.040 | 23.985 |
| P(doom) 2 | 59.940–60.300 | 60.245 |
| P(doom) 3 | 96.300–96.680 | 96.625 |
| P(doom) 4 | 125.400–125.860 | 125.805 |

四个词先有完整可读窗口，越面时仍在演唱和显示区间内。临近镜头时允许字形超出画框、越过近裁切面，保留实际字边擦镜的尺度变化；取消旧版会抵消前冲的自动整词广角保护。

相机沿各词原有固定法线穿行，因此四次分别有前冲、抬升、下潜和斜向穿梭，滚转降低为辅助动作。实际峰速约100–109场景单位／秒；路径长度与净位移之比约1.01–1.03，体现连续前飞。每次仅有一次字面距离正→负变化，无反向穿回。

后续歌词组提前固定在飞行路线的不同深度、位置和朝向上。它们仍按演唱起音显示，镜头接近后依次掠过。位置与大小在离线规划时确定，播放时字面不跟随相机转向。规划使用同一世界行进坐标，避免读词位置重复计算位移。

奇点、原子、围栏和递归升级也采用通道飞行；引信采用快速侧上掠飞接下一个真实剪辑。保留v11的六处语义动作、v10的独立机位和既有30拍叙事尾声。

## 飞行空间

`flight_geometry.py`提供径向引擎、升降竖井、断裂舱壁和递归舱室四类固定通道。每类37k–39k线顶点，包含双层凹刻舱壁、密集机械肋骨、连续管轨、亮色侧线和外层画廊。它们固定在词体宿主周围，具有真实前后距离；相机经过时，近处结构比远处移动得快。通道沿深度继续衔接，避免穿字后变成空黑背景。

全部画面仍由代码线条和三维字形构成，无位图素材、背景视频或额外字幕层。225词顺序和起音不变，同屏最多两词；四次爆炸仍位于P(doom)词点。154.6秒起冻结整幅画面，完整歌名 **I'm Upping My P(doom)** 与 **Made by Chiyang001** 保持到片尾。

## 复现

从项目根目录执行：

```powershell
python v12/render.py
python v12/render.py --flight-preview
python v12/audit_words.py
python v12/audit_geometry.py
python v12/qa_camera_flight.py v12
python v12/qa_readable_words.py
python v12/validate_v12.py --events v12/review_events.json
python v12/verify_tail.py
```

依赖v4–v11已有几何、时间轴、字形、机位、剪辑和尾声模块。

## 检查证据

- `flight_storyboard.jpg`：九段飞行的逼近、越面和继续前飞阶段。
- `qa_camera_flight_v11.json`／`qa_camera_flight_v12.json`：旧版没有穿面，当前四个P(doom)均实际穿面且不返穿；越面前各有9／5／5／7个完整可读帧。
- `qa_readability.json`：225词均有完整可读帧；飞行段每词至少2帧完整可读，后续词未因穿面而遗失。
- `token_validation.json`：225词顺序、起音、描线帧覆盖和最大两词检查通过，四次爆点归属正确。
- `geometry_validation.json`：所有词均可读；字边逼近和越镜区间单独记录为有意的出框，非飞行段不允许额外出框或反面字形。
- `validation.txt`：完整MP4解码、原AAC位流一致性和47个剪辑／冲击事件的前后帧抽查。
- `freeze_validation.json`／`encoded_freeze_validation.json`：片尾62帧保持检查。
- `final-frame.jpg`：从最终MP4提取的完整歌名和制作者定格。
- `qa_encoded_visual.json`、`qa_encoded_flight_sheet.jpg`、`qa_encoded_follow_words.jpg`：最终母版的穿面序列、后续词和片尾抽帧复核，视觉检查通过。

1920×1080、30fps、156.667秒，H.264 CRF18、4×MSAA；原AAC直接复制。最终文件1,128,068,902字节，完整解码和AAC位流一致性通过。片尾62个输入帧完全相同，编码后最大平均像素差约0.086/255。

开发者：炽阳001

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
