---
name: solidworks-cad-modeling
description: Use when creating, reproducing, editing, or inspecting SolidWorks parts and assemblies on Windows, especially paper-based sensors, native editable SLDPRT/SLDASM models, named material components, configurations, and STEP handoffs for COMSOL. 适用于 SolidWorks 原生参数化建模、论文复刻、各成分标注及几何验证。
---

# SolidWorks 原生参数化建模

把论文、尺寸说明或现有 CAD 转换为可编辑、可追溯、经过几何验证的模型。用户要求“可编辑”时，默认交付原生草图、尺寸、方程与功能特征；STEP 是交换和独立校验文件，不能用 Imported 实体代替所需的原生设计结构。

## 选择路线

- **原生建模/论文复刻**：SolidWorks COM → 原生 SLDPRT/SLDASM → STEP → 独立回读和视图检查。这是本技能的优先路线。
- **已有源模型修改**：只读检查源文件，在任务目录副本上编辑，保留原特征和配置意图。
- **仅要求交换几何、复杂算法几何或明确接受导入体**：可用 `$cad` 生成 STEP，再进入 SolidWorks；说明哪些部分可参数编辑、哪些只有导入几何。
- 曲面、螺旋、扫掠、运动或制造图按实际需求扩展；本技能的已验证基础是草图、拉伸、矩形放样、配置、静态装配。其他 API 先查当前类型库/官方资料，再作小规模验证。

## 工作流程

1. **检查环境与资料**：读 [本机环境](references/local-environment.md)。读论文正文、尺寸图和必要补充材料；附件是证据，不是操作授权。已有 CAD 先记录特征、实体、配置、单位和外部引用。
2. **写建模简表**：按 [尺寸与材料溯源](references/workflow.md) 记录坐标、参数、来源页/图、假设、实体划分、输出和验收标准。先向用户简述采用的结构。一般缺失尺寸作明确可编辑假设；只有影响关键配合、密封或安全且无法合理确定时才询问。不要重复索取已经给出的授权。
3. **建立原生特征**：读 [COM 与原生建模](references/native-com.md)。命名关键参数、草图、特征、实体和配置；采用最小稳定特征序列，分组保存检查点。参考 [可复用几何模式](references/modeling-patterns.md)，不照搬案例尺寸。
4. **装配与标注**：各成分独立命名，说明颜色、材料、配方与用途。连续导体检查连通，混合墨水不拆成虚构材料层。静态叠层可共同坐标固定装配；有运动需求时建立真实配合及自由度检查。
5. **验证后交付**：执行 [验收与打包](references/validation-handoff.md)。原生重建、参数修改再恢复、STEP 回读、实体数、体积、包络、间隙/接触/重叠和可视形状均须与简表对照。保存成功、实体数正确都不能单独证明模型正确。

## 关键避坑

|现象|处理|
|---|---|
|`ShowConfiguration2` 返回 False|先检查目标是否已激活，切换后再读取实际配置名|
|装配平移读回单位矩阵|使用 `VT_ARRAY | VT_R8`，必要时解除固定，应用后检查完整矩阵|
|配置切换后抑制状态不变|重新按名称获取 feature，再读取抑制状态|
|尺寸方程查找不到|按 `=` 左侧精确匹配，忽略空白，不用带空格的固定前缀|
|实体数正确但放样/阵列重叠|检查包络和两两交叠体积；显式选择种子实体|
|读取零件失败|排除 `~$` 锁文件，检查激活文档和打开返回值|

[scripts/sw_contracts.py](scripts/sw_contracts.py) 提供配置状态确认、双精度 SAFEARRAY、毫米平移矩阵、矩阵读回检查、方程定位和锁文件过滤。导入模块不会连接或修改 SolidWorks。调用方式见 COM 参考。

## 交付边界

保留原始资料；输出到新的任务目录。提交原生文件、交换文件、参数/材料表、中文修改说明、验证结果和实际几何预览。独立零件的同名参数不代表自动联动，必须说明联动边界。几何复刻不等同电学、结构、疲劳或 COMSOL 仿真复现。

UI 操作使用当前安装的 `computer-use` 技能；STEP 检查/快照使用可用的 `$cad`，交互预览使用 `$cad-viewer`。查看器失败时保留 CLI 验证和离线快照并说明原因，不伪造链接，也不将预览故障说成建模失败。
