# v20 发布源码复核

结论：本轮静态发布检查与最终相机覆盖复查通过。检查只读取生产文件、
Git 文件清单与 JSON，并生成本地 QA 报告；没有修改生产代码或操作 Git。

- 从 `v20/render.py` 按生产搜索目录递归解析 **53 条本地导入、46 个不同
  Python 源文件**。全部目标存在，且已跟踪或未被忽略、可随发布纳入。
  新增的 `upgrade_geometry.py`、`upgrade_director.py`、`pair_director.py`
  及其依赖均在可发布源码中，没有依赖忽略目录里的临时模块。
- `work/lyrics.json`、`work/transcript.json`、`code3d/rhythm_v3.json`、
  `v11/compositions.json` 及 v20 的 `compositions.json`、`edit_events.json`、
  `review_events.json`、`word_timeline.json` 全部存在、可解析且允许发布。
  `pair_director.py` 和 `first_half_score.py` 使用与各自源码同目录的词时间轴。
- 生产依赖没有必须使用的开发者桌面、临时目录或个人绝对路径。唯一
  Windows 盘符字面值是可选的 `C:/Windows` 系统字体候选；已有 `--font`、
  `PDOOM_FONT` 及 Linux/macOS 字体候选。音频、输出和 OpenGL 后端同样支持
  命令行或环境变量配置。音乐、字体和生成媒体按现有规则留在本地。
- README、第三方声明和 v20 Markdown 的 **53 个本地链接目标**均存在，
  没有指向仅本机保留的忽略文件。
- 最终代码重新执行 `python v20/qa_pair_coverage.py --version v20`：
  **225 个词、166 个词组全部观察到实际相机变化**；扣除了共同向前世界
  位移和瞬时鼓点抖动，没有低变化词组、连续弱变化词串或无效投影矩阵。
  检查依据真实相机结果，不把导演阶段名称当作运动证据。

最终 `render.py` SHA-256：
`7acf3c765b853560946092b411ccd57a7e68b7e31a251dae30431be37912ab66`。

本地完整记录为 `release_source_audit.json` 与 `qa_pair_coverage.json`。
这些生成报告不是生产依赖，也不需要加入源码仓库。相机数值检查不替代
歌词可读性或视觉审查；成片的专项视觉记录分别见
[新训练场景](qa_upgrade_encoded_review.md)与
[后半段词组镜头](qa_pair_encoded_review.md)。
