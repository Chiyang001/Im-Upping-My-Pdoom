# I'm Upping My P(doom) — Seismic Flight

成片：`output_v13/Im_Upping_My_Pdoom_Seismic_Flight_1080p.mp4`。

本版强化GO末尾的灾难穿越、尾声的连续多场景长飞行、非爆点穿字及文字自身的三维细节。全部画面继续用代码线条和字形几何构成，保留原AAC音轨。

## GO地震穿越

GO演唱窗94.060–94.860秒，字形先清楚呈现，再在约94.798秒实际穿过镜头。镜头持续前进，依次经过95.230的断层喉、95.435的坠落拱和95.680的上升裂隙，95.910接入下一处真实转场。

`disaster_flight.py`提供固定GO字面上的三轴飞行、短促镜头震动、色散和结构坍塌。震动叠在前进路线之上，不替代真实平移。场景的左右构件反向错位、地层下沉、通道骨架震颤；字形本身保留固定物理宿主。94.300／95.230／95.435／95.680沿用原音轨检测鼓点，穿字点接近94.783的节拍。

实际渲染检查：GO有18个完整可读帧；仅一次正面→背面的穿越，无反向穿回；相对字面飞行路径约187.5单位、净位移149.5单位，叠加灾难震动后的峰速约241单位／秒。

## 其他穿字及不同空间

在四处P(doom)和既有语义爆发外，增加六处独立飞行：

| 歌词／动作 | 穿字约时刻／秒 | 空间变化 |
| --- | --- | --- |
| DROP | 10.925 | 从Loss断崖进入悬梁与电路 |
| ACCELERATING | 48.580 | 通道推进并穿向原子结构 |
| REPEAT | 77.180 | 反馈回路、逻辑卡与计算架 |
| DISOBEY | 114.940 | 机械关节错裂、围栏、GPU |
| ASKEW | 122.485 | 分层机架、织机与递归孔 |
| SHOW | 140.425 | 剧场、观察眼与递归出口 |

飞行时后续歌词按组固定在航线的不同深度，仍只在各自演唱起音显示。相机接近时字形扩张并贴镜掠过；词面不逐帧转向相机。保留原31处声乐转场和独立机位，单向飞行在合适的真实转场交接。

## 尾声长航线

`outro_flight.py`从141.2秒开始建立连续航线，沿Z方向前进585单位，真实曲线路程约703单位，左右跨越约62单位、上下跨越约49单位。30个原曲鼓点给前进速度增加推力，不采用前冲再弹回的相机动作。

九组固定世界空间依次为神经通路、复制阵列、神经脊柱、轨道牢笼、撕裂世界板、屈曲肋骨、碎片翻转、递归房间和无穷出口，保持“复制→捕获世界→坍塌→闭环”的叙事。既有EPILOGUE几何按固定矩阵分布在路线中；连续舱壁和红色引导轨迹把房间连接起来，近处结构与远景产生实际视差。

153.415秒起收速，153.95秒抵达原定片尾机位。标题153.95–154.30描线，署名154.08–154.45描线；154.6秒开始冻结整幅画面到156.667秒。最终完整显示 **I'm Upping My P(doom)** 和 **Made by Chiyang001**。

## 五种字形细节

`typography_details.py`增加PCB铜线和焊盘、断层板层、经纬织线、挤出骨架、扫描截层。线条按真实字划内部的奇偶交点裁切，原始字面轮廓保留，字腔不填死。GO另有多层深字腔和长侧肋，近穿时能看到背缘厚度。

## 复现

从项目根目录执行：

```powershell
python v13/render.py
python v13/render.py --v13-preview
python v13/audit_words.py
python v13/qa_spatial_words.py v13
python v13/qa_actual_flights.py
python v13/build_review_events.py
python v13/validate_v13.py --events v13/review_events.json
python v13/verify_tail.py
```

渲染器继续依赖v4–v12的几何、字形、时间轴、机位、飞行通道和原尾声资产。

## 验证

- `token_validation.json`：225词顺序及起音正确，无提前或漏词，每次最多两词，四处P(doom)爆炸仍位于正确词窗内。
- `qa_spatial_words_v13.json`：每词至少1帧完整描线、正面、全字框入画且字高至少28px。
- `qa_actual_flights.json`：16段飞行中15段实际穿字，均先可读后越面，无同段回穿；引信采用侧上掠过。
- `qa_outro_continuity.json`：尾声585单位单向推进，9个固定场景实际经过，连续轨迹无跳变、末状态冻结。
- `go_storyboard.jpg`、`newwords_storyboard.jpg`、`outrolong_storyboard.jpg`：源画面设计复核。
- `qa_encoded_go.jpg`、`qa_encoded_outro.jpg`：从最终编码母版独立抽取的24个代表帧。
- `validation.txt`：完整解码通过，AAC位流SHA256与原片相同；89个剪辑、穿面、地震或尾声节拍事件各抽前后7帧。
- `freeze_validation.json`、`encoded_freeze_validation.json`：最后62个输入帧完全相同，编码后最大平均像素差约0.119/255。

成片1920×1080、30fps、156.667秒，H.264 CRF18、4×MSAA；文件1,255,528,646字节。

开发者：炽阳001

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
