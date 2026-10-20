# v19 发布源码静态复核

复核只读取生产源码、Git 跟踪／未忽略文件清单及 JSON；没有修改生产代码或正在编码的文件。

- 从 `v19/render.py` 按实际本地搜索目录递归检查 **49 条本地导入、43 个不同 Python 源文件**。全部目标存在，并已跟踪或处于未忽略、可随 `git add v19` 纳入发布的状态；没有导入仅存在于忽略目录中的模块。
- `v19/compositions.json`、`v19/edit_events.json`、`v19/review_events.json`、`v19/word_timeline.json` 四份运行／检查时间轴全部存在，JSON 可解析，`.gitignore` 的 `!v*/...` 例外规则允许它们纳入发布。
- 生产模块没有用户桌面、临时目录或其他特定开发电脑的绝对路径。唯一 Windows 盘符字面值为 `render_options.py` 的可选 `C:/Windows` 系统字体候选；已有环境变量、`--font` 及 Linux/macOS 候选路径支持，不是必须使用的机器路径。
- 检查 v19 的 Python 与 Markdown，未发现遗留的 `validate_v18`、`output_v18` 或旧 v18 验证入口。历史研究与设计说明的 v18 文档链接属于正常版本引用。
- 修正文档首页把七次 FREE 敲击误写成六次的问题。README 的生产入口、输出路径和最终验证入口均指向 v19。

这些结果验证发布候选文件的静态完整性；正式暂存、提交及推送由主任务完成。媒体、字体、生成的联系表和本地 QA JSON 仍按现有规则留在本地。
