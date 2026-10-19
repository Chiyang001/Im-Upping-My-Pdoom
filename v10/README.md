# I'm Upping My P(doom) — Multi Angle

成片：`output_v10/Im_Upping_My_Pdoom_Multi_Angle_1080p.mp4`。

这一版针对前视远景同质的问题，重写声乐段32个分镜的绝对机位。保留31处人声快切、逐词起音、四次P(doom)爆发和30拍叙事尾声。所有画面继续由代码线条和真实三维字形构成。

## 分镜设计

- 开场用虹膜近景建立观察者，再切52–54°电路侧跟、Loss俯拍、桥底仰拍和齿间POV。
- 稳定训练台采用顶视，奇点从下方斜潜，加速段穿过轨道；原子段靠近轨道球面和键链，保留连续的几何结构。
- 再进入侧向牢笼、低位Basilisk、算力架、审批器局部、反馈机顶视和抽出逻辑卡近景。
- Gato从指桥下方看抓索，纸夹工厂切俯拍，Killswitch靠近空控制台，再穿过正交轴和机械背部。
- 末段从围栏底部仰拍切芯片区域近景、织机俯拍、递归孔穿越；观察者镜头返回大幅虹膜，最后拉开为整座剧场。

每镜使用独立的相机位置、观察目标、焦距和定向路径。镜头跟随一件固定装置的世界行进，不根据正在演唱的单词重新对中。歌词固定挂在本镜头的实体平面上，分别具有地板、斜向载板、侧壁或悬梁姿态；没有每帧转向相机的billboard。近景的背景线条降低曝光，让装置局部成为主体。构图保护只对整个镜头作静态词体缩放，保留原定镜头焦距和景别。

## 保留的节奏与文字约束

225个词与完整歌词一一对应，每次最多显示一到两个正在演唱的词；没有未来词预显或整句残留。四个P(doom)词点爆炸为23.620、59.985、96.335、125.460秒，源点跟随该词的实际三维中心。FOOM与Basilisk Boom位置不再触发爆炸。五处其他语义爆发、快速转场和30拍尾声继续保留。

154.6秒冻结完整画面到156.667秒，同时显示完整歌名 **I'm Upping My P(doom)** 和 **Made by Chiyang001**。

## 复现

从项目根目录执行：

```powershell
python v10/render.py
python v10/render.py --angles-preview
python v10/audit_words.py
python v10/audit_geometry.py
python v10/validate_v10.py --events v10/review_events.json
python v10/verify_tail.py
```

渲染依赖已有v4–v9的线条几何、时间轴、爆点、剪辑和尾声模块；`shot_grammar.py`是本版新增机位及文字宿主设计，`render.py`完成集成。

## 检查证据

- `token_validation.json`：30fps扫描，225词全部有完整描线帧，无漏词、无提前出现，同屏最多2词，四次爆发均位于P(doom)演唱区间内。
- `geometry_validation.json`：所有完整描线且清晰显示的非转场词帧，0投影出框、0反向或过薄字面；225词均有完整可读取景。最低字框高33.19px，最小正面朝向余弦0.870。
- `angle_storyboard.jpg`：31个声乐代表镜头的取景联系表。
- `validation.txt`：完整MP4解码通过，AAC位流SHA256与原片完全相同；47个剪辑或冲击事件，各检查前后7帧。
- `freeze_validation.json`：片尾62个输入帧完全相同。
- `encoded_freeze_validation.json`：编码后62帧保持，最大平均像素差0.081/255以内。
- `final-frame.jpg`：从最终MP4提取的歌名及署名定格。

1920×1080、30fps、156.667秒；H.264 CRF18、4×MSAA，原AAC直接复制。文件1,096,676,161字节。

开发者：炽阳001

Bilibili：https://space.bilibili.com/404891612

GitHub：https://github.com/Chiyang001?tab=repositories
