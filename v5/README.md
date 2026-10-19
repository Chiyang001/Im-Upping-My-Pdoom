# P(doom) — THE LIVING MACHINE

最新成片：output_v5/Pdoom_Living_Machine_1080p.mp4

本版围绕“同一颗红色信号进入、唤醒、逃离并最终被机器编织”的连续旅程重做。保留歌词线构字、真实三维深度和原始音轨；不使用背景图片、AI生成图片、背景视频或文字贴图。

## 连续叙事

1. 字迹与电路唤醒机器，线路折成训练损失断崖，字架变成权力桥梁。
2. 桥梁闭合成吞噬机构，红色信号沿输送线路进入喉口。
3. FOOM引发扩张，城市升起并封成语言房间；触须与眼睛露出。
4. 瞳孔内部延续为训练工厂，道路被奇点拖弯，加速结构解体为原子链。
5. 原子线连接为Sydney牢笼，逃离线路继续通向算力城市。
6. 蛇形结构、月球轨道与计算峡谷相连，进入短暂的安全检查区。
7. 网络反馈、旧架坠落、道路换向与缺失桥柱形成连续逃离路径。
8. Gato拉索接触红色信号，字形拉紧、松脱，纸夹工厂围住出口，信号拖成导火索。
9. 栅栏碎片进入剪切的服务器阵列，并向织机输送经纬。
10. 织机递归生成机器，观察孔露出开场的眼睛，剧场与城市属于同一具机器外壳；最终收束为无穷轨迹。

## 本轮主要变化

- 移除逐词/逐行强制镜头回正，使用38个关键帧构成C1连续镜头路径，世界行程0→250。
- 持续世界包含基础设施、机器城市、不同尺度碎片、长数据带及共享连接点的道路、信号、机器骨架和记忆结构。
- 每个节点拥有固定的世界位置；前一段结构继续移动，后一段结构提前进入远景。淡入淡出由节点自己的时间窗决定。
- 语义结构承担前景和画面边界：Maw/Chinese room放大进入镜头；纸夹工厂撤掉通用直线廊道，改由纸夹链和夹具包围通路。
- 字形会折叠、拉伸并过镜，已唱行降低亮度，避免多句重叠争抢。
- 背景细线采用分层光照与合成；近处主要结构保留真实深度遮挡。
- 背景的主次、色彩、宽高比例和变形随章节连续变化，而非始终铺同一层绿色网架。
- 原音轨重新分析的132.003 BPM /399个主要冲击继续驱动具体结构动作。

## 运行

在项目根目录执行：

```powershell
python v5/render.py
python v5/render.py --preview
python v5/render.py --audit
python v5/render.py --sample 18
```

主要源码：v5/render.py、camera_path.py、world_layers.py、story_geometry.py。
沿用的几何辅助与字形：v4/engine.py、v4/scenes_early.py、code3d/scenes_late_v4.py。
时间轴：work/lyrics.json、work/transcript.json；节奏：code3d/rhythm_v3.json。

输出：原生1920×1080、30fps、156.667秒、H.264、4×MSAA，原始AAC音轨直接复制。
依赖：Python、moderngl、numpy、Pillow、scipy、fonttools、shapely、mapbox-earcut、imageio_ffmpeg。

## 最终检查

- 成片大小：1,031,727,032字节。
- 全片逐帧解码通过；原音轨与输出音轨的AAC位流SHA256完全一致，记录见validation.txt。
- 536个歌词活动时刻的投影边界检查未发现出框，记录见final_framing_result.json。此项仅检查投影边界，不代替视觉可读性复核。
- 完成吞噬／语言房间、Gato／纸夹工厂、奇点、GPU栅栏、织机与结尾的连续画面复核；修复奇点字形镜像、相邻行争抢与未来字形遮挡。
- 叙事、世界空间与镜头分别由三个子代理参与制作和复核。空间覆盖与运动诊断用于定位问题，不作为超越参考片的艺术评价。

开发者：炽阳001
Bilibili：https://space.bilibili.com/404891612
GitHub：https://github.com/Chiyang001?tab=repositories
