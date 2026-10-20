# Repeat 与 CDR：v19 场景和运镜复核

本记录对应 `meaning_camera.py`、`cdr_geometry.py` 和 `semantic_director.py`；不涉及前奏、FREE、前半段其他分镜。

## 语义边界

歌词作者在 [逐句解释](https://docs.osmarks.net/rev/b3140e5/p%28doom%29_song_objectively_correct_interpretation) 中明确指出 `cdr` 是 Lisp 的操作，联系旧符号 AI / 专家系统语境。这里延续已有 `v15/concept_lexicon.md` 的核实结果，不将它解释为工程审查。CAR 原子、CDR 取尾、密集神经路线旁路是这一段的空间比喻；不是在声称现代神经网络不能进行链表操作。

## 场景设计

- 删除上排、下排所有旧 `cdr_cells`、`cdr_links`、`cdr_head`、`cdr_rest` 的绘制，也删除旧通用挂架。旧重复矩形盒不再出现。
- 四个 cons 单元固定在同一根弯曲的三轨桁架上：CAR 用开放三角托架容纳四面体原子，CDR 用深圆形管口承接指向下一单元的尾指针。二者通过开放 Y 形骨架承载，避免重复双圆盒体的磁带外形。
- 取尾选择叉沿同一条尾导体单向运动；旧首元素退出自己的托架，另一束细密神经导体从上方贯通。所有部件用同一个 `semantic_host('cdr',87.1,...)` 的固定物理坐标，只有真实选择机构发生局部运动。
- 镜头先低幅横移读出 Without / a / single，再随尾指针向侧方、下方与深处驶入。88.62 秒之后的空隙继续快速越过支架，没有回到原机位再淡出。

新机构共 **20,042 个线顶点，0 个三角面**；沿用青色金属、白色导体与原场景的精密紧固件，没有图片、贴图或独立图标素材。

## Repeat 运镜

73.87–75.90 秒沿固定神经轨扫描，75.90–76.30 秒快速倒走原路；76.30 秒起再沿相同轨道启动，同时衔接现有 FEEDBACK REPEAT 穿字镜头。前、后、重复三段属于同一组物理网络，删除了旧 `mlp-exit` 复制网络。

Repeat 附加位移在字面切向平面内，保持原飞行的法向穿越位置；保留飞行的 up 向量，不以绕中心旋转代替平移。

## 实际 v19 渲染器检查

运行 `python v19/qa_repeat_cdr.py`，检查实际生产 `frame_view`、实际 `token_matrix`，并生成 16 帧预览。该检查未使用开发期 `--baseline-injection` 适配器。

- 两句共 8 个词均在完整勾勒后有正面、完整入框、高于 28 像素的可读帧。
- Repeat 实体字面在 **77.179984 秒**穿越一次，未发生反向重穿。
- 查看 `qa_repeat_cdr_page_1.jpg` 与 `qa_repeat_cdr_page_2.jpg`：Forward / backward 的同轨往返、Repeat 启动、CDR 公共弯曲支架与快速穿行均可辨认；旧矩形浮动排列没有残留。

以上是源渲染预览和几何检查。完成编码后，另对 16 帧及 4 张原生 HD 细节图完成 [实际成片抽样复核](qa_encoded_repeat_cdr_review.md)，结论为 PASS。
