# 本机配置与复用范围

以下是已验证的 Windows 配置，不代表其他机器必然相同；升级或迁移后先检查路径、模板及 API 主版本。

|项目|已验证值|
|---|---|
|SolidWorks|Design Premium 2026 SP2.1；RevisionNumber 34.2.1|
|程序|`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe`|
|类型库|同目录 `sldworks.tlb`|
|零件模板|`C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot`|
|装配模板|同目录 `gb_assembly.asmdot`|
|Python|`C:\Program Files\Python314\python.exe`，含 pywin32|
|独立几何检查|build123d 0.11.1 / OCP；确认当前解释器有这些模块|
|CAD CLI|`C:\Users\Dell\.codex\skills\cad\scripts\step`、`inspect`、`snapshot`|

读取 PDF 可使用工作区依赖工具提供的 Python / pypdf / pdfplumber；不要假定系统 Python 具有这些包。使用工具返回路径，不固定缓存包版本。

SolidWorks COM 类型库 GUID：`{83A33D31-27C5-11CE-BFD4-00400513BB57}`，LCID 0，major 34，minor 0。常量库 GUID：`{4687F359-55D0-4CD3-B6CF-2EB42C11F989}`。用本机生成的类型信息查方法签名，不凭记忆补参数。

本技能提炼自本机叠层传感器与 Hossain DIW 应变计任务。已验证原生草图、拉伸、矩形放样、命名方程、配置、带颜色静态装配和 STEP 检查；不把过去有重叠的层状阵列分支当作通过案例。

本机案例索引，仅用于回查证据，技能正常使用不依赖它们：

- `C:\Users\Dell\Desktop\juntong-fan\hossain_strain_gauges_20261008\outputs\reports\native_validation.json`
- 同目录 `step_validation.json`、`assembly_validation.json`、`appearance.json`。
- 该案例验证过 6 个原生零件、2 个装配；线宽 0.10→0.12→0.10 mm 的导体体积 2.0085→2.3542→2.0085 mm³。这些是回归证据，不是新模型默认尺寸。

本机曾安装的 CAD Viewer 0.3.9 缺 `agent:start`。每次使用按当前 `cad-viewer` 技能检查/启动；如果仍失败，报告错误并用 CAD CLI 快照完成预览，不手写虚假端口链接。快照流程不依赖交互查看器启动成功。
