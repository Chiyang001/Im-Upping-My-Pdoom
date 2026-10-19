# P(doom) — Impact Cut

成片：output_v7/Pdoom_Impact_Cut_1080p.mp4。

本版在v6的快速转场和连续叙事上，增加七处有蓄力、释放和余波的冲击，重做无歌词尾声，并在最后整帧定格中加入 **Made by Chiyang001**。画面仍全部由代码绘制的三维线条和字形组成。

## 爆发与张力

| 时间／秒 | 动机 | 画面动作 |
| --- | --- | --- |
| 25.685 | FOOM | 空间压紧、橙色冲击波扩张、碎片与近镜飞掠，余波进入房间 |
| 42.050 | 奇点开始 | 冷色内爆、结构向源点塌缩 |
| 49.785 | 原子重排 | 方向性键链断裂，较轻的释放 |
| 62.060 | Basilisk BOOM | 上冲的压力柱与城市冲击 |
| 103.870 | 引信 | 沿导线传递的方向性爆炸 |
| 117.505 | 安全围栏 | 板块断裂并飞入GPU阵列 |
| 131.140 | 自我升级 | 递归结构裂解，进入观察者场景 |

六段张力分别作用于吞噬夹口、优化加速、Gato牵绳、无处可逃、机械剪切和观察者。主要结构会压紧、拉长或变形，当前字形保留取景与可读空间。爆发由程序生成的压力骨架、断裂冲击波、长碎片、破板、近镜飞掠和电弧共同构成；没有添加图片素材。

## 尾声

141.2秒后使用30个实测主拍和6个实测细分攻击，九个镜头贯穿四个阶段：

1. 红色信号留下轨迹、分叉、锁定并复制为神经网络。
2. 网络包围世界，夹具闭合；世界分片被拉入侧面机械喉口，最后红线在拍上绷断。
3. 机器过载内爆、破壳、反转并递归，收紧到无穷环的交点。
4. 红色信号勾出无穷轨迹，刻出公式与制作者署名。

154.6秒起保持整帧至156.667秒。几何、背景、镜头、后期和署名一起冻结；末尾不淡黑。每个输入定格帧使用相同缓存，并检查SHA256一致性。

## 运行与检查

从项目根目录执行：

```powershell
python v7/render.py
python v7/render.py --impact-preview
python v7/render.py --sample 23 --duration 5
python v7/render.py --sample 141 --duration 16
python v7/render.py --audit
python v7/validate_v7.py --events v7/review_events.json
```

render.py为集成绘制器；impact_score.py为七处冲击和六段张力；blast_geometry.py为34,395段冲击线条；outro_director.py为尾声节奏和分镜；epilogue_geometry.py为20,779段尾声叙事实体。沿用v5的世界与道路、v6的剪辑导演、v4／code3d的歌词几何与时间轴。

规格：1920×1080、30fps、156.667秒、H.264、4×MSAA；原片AAC音轨直接复制。依赖与v6相同。

检查文件：validation.txt、framing_result.json、freeze_validation.json。最后一项核对定格输入帧完全一致；完整成片另做逐帧解码和原音轨位流比对。536个歌词活动时刻的投影检查未发现出框；该检查不代替视觉可读性复核。

最终成片934,199,945字节，完整解码与AAC位流一致性检查通过。结尾62个输入帧的SHA256完全一致，编码后抽查定格帧的平均像素差小于0.08／255，无可见位移；最终署名已从完整MP4抽帧复查。

开发者：炽阳001

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
