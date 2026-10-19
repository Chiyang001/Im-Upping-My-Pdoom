# P(doom) — Kinetic Story

成片：output_v8/Pdoom_Kinetic_Story_1080p.mp4。

本版按歌词单元重新剪辑，增加镜头运动速度与空间穿行。保留v7的七处爆发、歌词张力、30拍尾声，以及最后 **Made by Chiyang001** 的整帧定格。

## 叙事密度与运动

- 人声段31处转场、32个镜头；中位镜头时长4.43秒，最长7.49秒。
- 31个镜头涉及一到两条歌词；FOOM进入房间的一个镜头含FOOM末尾0.375秒、Chinese room与shoggoth两句，为三句衔接。没有连续四句以上不切的段落。
- 开场新增眼睛→电路→训练损失断崖→权力桥→吞噬口，拆掉原先22.19秒长镜头。
- 其余新增眼睛、加速、原子、算力、安全审批、废弃装置、CDR、Gato、无人值守控制台、正交机器、GPU、递归升级与剧场切点。
- 转场持续3–6帧；新机位持续移动，并保留转场后的空间方向。每个镜头以横移、升降或推拉为主要动作，目标随同一路径前移，不使用互不相关的多轴抖动。
- 非转场的合成镜头轨迹速度中位约1.72单位／秒，v7约1.21；前景与道路的连续世界行程提高至1.65倍，歌词锚点、道路、信号与尾迹使用同一距离。
- 每镜头的取景余量在渲染前固定求解，播放时不逐词回正或自动追字。536个演唱活动采样未发现字形投影出框；此项不代替视觉可读性复核。

这些数据用于检查剪辑和取景，不是完播率的实测结论。

## 源码与复现

从项目根目录执行：

```powershell
python v8/render.py
python v8/render.py --edits
python v8/render.py --audit
python v8/audit_pacing.py
python v8/validate_v8.py --events v8/review_events.json
```

- edit_director_v8.py：31处语义剪辑、快速镜头轨迹、场景归属与歌词保护。
- camera_path_v8.py：统一提速的世界行程，保留原有歌词时钟与音轨。
- render.py：三维线条、字形、镜头、爆发、尾声和成片输出。
- pacing_audit.json：每镜头所涉歌词、时长和非转场运动速度。
- compositions.json、framing_result.json：镜头固定取景参数与字形边界审计。
- validation.txt、freeze_validation.json：全片解码、原音轨位流与最后定格检查。

几何与尾声沿用v4／code3d／v5／v7的代码模块。没有使用图片、背景视频或文字纹理。规格为1920×1080、30fps、156.667秒、H.264、4×MSAA，原始AAC音轨直接复制。

最终成片947,425,684字节。全片解码与AAC位流一致性检查通过；最后62个输入帧完全相同，编码后抽查平均像素差低于0.057／255。两个子代理从完整成片复核开场、FOOM、加速／原子、白纸转场、PTO／引信、观察者／剧场和尾声入口，未发现持续模糊遮词、整词丢失或剪后回弹；最终署名已从完整MP4复查。

开发者：炽阳001

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
