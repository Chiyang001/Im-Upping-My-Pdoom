# I'm Upping My P(doom) — Rupture

成片：`output_v11/Im_Upping_My_Pdoom_Rupture_1080p.mp4`。

本版把爆炸从中心发散的碎片改为相机也进入冲击：爆前短促预载，爆后高速轨道侧穿、俯冲、强滚转和回甩，再平滑接回原分镜。保留v10的32个独立机位、225词逐唱呈现、四次P(doom)词点爆炸、31处声乐快切、30拍尾声和完整歌名／署名定格。

## 爆点相机

`impact_camera.py`覆盖四次P(doom)和另外五处语义爆发。四个副歌分别采用不同方向的螺旋侧穿、抬升滚转、斜切工厂和织机俯冲。相机围绕爆点时固定的词体宿主移动，词的平面保持原有物理朝向，不跟着镜头转。

实际渲染相机测量，四次P(doom)的相对眼位偏移约20.8／19.3／20.2／14.8单位，轨道转角约41.6／46.3／51.4／53.6°，滚转约64／71／75／79°；峰值滚转速度约417–515°/s。每次约1.0–1.2秒内平滑回到原机位路径。

镜头经过俯拍轴时允许连续大幅转动，检查未发现非剪辑点单帧超过60°的视图翻跳。峰值时文字会随物理场景倾斜甚至短促接近倒置；爆点前后保留完整清楚的阅读帧。

## 六处动作加强

`aggression_score.py`为六段歌词建立独立的有限时动作：

| 语义动作 | 时段／秒 | 画面动作 |
| --- | --- | --- |
| Loss 下坠 | 10.02–12.28 | 镜头下切、侧倾，等高线塌陷 |
| 齿间吞噬 | 19.98–22.17 | 推入狭缝，交错齿列前探、压紧 |
| Accelerating | 46.92–48.63 | 冲入通道，近场斜梁高速穿过 |
| Sharp left turn | 81.62–84.72 | 急转反打，外弯轨道擦镜 |
| Disobey | 113.58–116.54 | 擦过关节，机器两侧反向错裂 |
| RLHF askew | 121.45–123.80 | 倾斜穿过芯片，机架逐层错位 |

`rupture_geometry.py`新增全线条的长三角断板、立体背边、刻线与近场桁架。爆炸前沿的空间扭曲、碎片飞行和断板展开幅度增加；场景主线略加粗以提高反差。没有使用图像素材或背景视频。

爆点构图保护只在短促动作中打开镜头视场，不因一次大动作缩小整段歌词。几何断裂仅作用于结构，不改变歌词时序和字符形状。

## 复现与证据

从项目根目录执行：

```powershell
python v11/render.py
python v11/render.py --ferocity-preview
python v11/audit_words.py
python v11/audit_geometry.py
python v11/validate_v11.py --events v11/review_events.json
python v11/verify_tail.py
```

渲染器继续依赖v4–v10现有几何、时间轴、机位、剪辑与尾声模块。

- `strike_storyboard.jpg`：九次冲击各六个阶段的预览；`action_storyboard.jpg`：六处歌词动作的进程。
- `token_validation.json`：225词顺序、起音和帧覆盖通过，每次最多两词，四爆点均在P(doom)词窗内。
- `geometry_validation.json`：225词均有完整可读帧；完整显示的非剪辑词帧无出框、背面或过薄字形，最低字框高33.19px，最小正面朝向余弦0.647。
- `qa_camera_first.json`、`qa_view_continuity.json`：真实相机位移、角度、速度、词窗和相邻视图连续性审计。
- `validation.txt`：全片解码与原AAC位流一致性；47个剪辑或冲击事件各7帧抽查。
- `freeze_validation.json`、`encoded_freeze_validation.json`：154.6秒开始整帧冻结，最后62个输入帧完全相同。
- `final-frame.jpg`：从最终MP4抽取，完整歌名 **I'm Upping My P(doom)** 与 **Made by Chiyang001**。
- `qa_encoded_pdoom_sheet.jpg`、`qa_encoded_action_sheet.jpg`：最终编码母版的18个代表帧，爆点攻击／峰值／恢复和六处动作峰值均已复核。

1920×1080、30fps、156.667秒，H.264 CRF18、4×MSAA，原AAC直接复制。最终文件1,097,551,838字节；全片解码通过，AAC位流与原片完全相同。编码后62个定格帧的最大平均像素差约0.086/255。

开发者：炽阳001

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
