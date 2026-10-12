# SolidWorks 2026 COM 实操

用于原生建模和 API 排错。单位：COM 坐标/长度 m，建模参数表 mm；体积 m³ 转 mm³ 乘 1e9。不要把 `GetMassProperties(1.)` 的测试密度当作材料密度。

## 显式接口包装

本机 `EnsureDispatch` 曾无法取得类型信息；单独动态 Dispatch 会造成无参方法/属性混淆。加载本机类型库并显式包装返回对象：

```python
import pythoncom
import win32com.client as com
tlb = pythoncom.LoadTypeLib(r'D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\sldworks.tlb')
a = tlb.GetLibAttr()
com.gencache.EnsureModule(a[0], a[1], a[3], a[4])
M = com.gencache.GetModuleForTypelib(a[0], a[1], a[3], a[4])
def W(obj, interface):
    return getattr(M, interface)(obj._oleobj_) if obj is not None else None
# 仅检查现有实例时用 GetActiveObject；创建/启动应用须属于当前建模任务。
sw = W(com.GetActiveObject('SldWorks.Application'), 'ISldWorks')
print(sw.RevisionNumber())
```

生产生成器应显式接收输出目录和模板路径，放在 `main()` 下执行，不要在模块导入时创建目录、连接应用或新建文档。历史案例脚本有导入副作用，不直接 import 它们做只读探测。

用 `inspect.getsource(M.IInterface.Method)` 查当前签名。`OpenDoc6` / `SaveAs` 可能返回含输出参数的 tuple；按当前签名解包，检查文档非空及错误/警告。调用功能前激活对应文档，核对 GetTitle/GetPathName，避免脚本作用到用户其他文档。

## 草图和方程

- 遍历 RefPlane 并确认朝向。本机 gb_part 的首平面是 XY；第二平面的局部 `(x,-z)` 对应全局 XZ。这个映射不是任意模板通则。
- 创建细小线段/点时设 `SketchManager.AddToDB=True`，完成后恢复，避免自动推断把辅助点吸到顶点。必要时显式合并相邻端点。
- 对重复轮廓优先水平/垂直、相等、尺寸、阵列等设计关系。复杂折线可采用已验证的固定辅助基点 + 每顶点 X/Y 驱动尺寸，但会生成很多方程、耗时较长。
- 辅助基点放在模型坐标范围以外，使尺寸符号无歧义；例如全模型 x/y 均大于 -100 mm 时，可用 (-100,-100) mm 基点，尺寸表达式为 `坐标表达式+100mm`。不要把 -20 mm 固定写死给更大零件。
- 禁用交互尺寸输入弹窗：保存 `sw.GetUserPreferenceToggle(10)`，再 `SetUserPreferenceToggle(10,False)`，在 finally 恢复。其他修改过的全局选项（STEP 协议等）同样恢复。
- 活动草图包装为 ISketch，特征可用 `FeatureByPositionReverse(0)` 获得；不要假定 ISketch 有 GetFeature。命名后再关联尺寸。
- `GetConstrainedStatus()==3` 是本机完全定义状态，仍需几何和参数修改测试。不要用“把所有线固定”替代可编辑设计尺寸。
- 单配置可 `IEquationMgr.Add2(-1, equation, False)`；多配置按实际作用域用 `Add3(-1, equation, False, 1, None)`（1=当前配置）。更改已有方程使用相应 `SetEquation` 或 `SetEquationAndConfigurationOption`，检查状态和求值结果。
- 方程 getter 可能返回 `"TraceW"= 0.1mm` 或 `"TraceW" = 0.1mm`；用 `find_equation` 精确匹配等号左侧。
- 三角方程先确认 `AngularEquationUnits`。本机角度设置为 degrees 时无量纲变量 40 可用于 tan；不要默认 `40deg` 对所有表达式都有效。
- `EvaluateAll()` 和 `ForceRebuild3(False)` 后重新读取尺寸/体积。仅程序生成并控制的表达式可求值；不 eval 附件或任意外部文本。

## 已验证的特征调用形状

以下仅用于理解顺序，复制前核对当前类型库参数名及实际意图，数值 SI：

```python
# 已选择封闭草图；6 为对称拉伸，0 为 blind；3 为起始偏移。
feature = fm.FeatureExtrusion3(
    True, False, False, 6 if midplane else 0, 0, depth_m, 0,
    False, False, False, False, 0, 0, False, False, False, False,
    merge, False, False, 3 if offset_m else 0, offset_m, False)
```

为 D1 深度和实际起始偏移尺寸命名/关联方程。偏移尺寸编号不应盲猜：枚举 `GetFirstDisplayDimension` / `GetNextDisplayDimension`，读回名称和值，确认目标后再关联。

偏移平面：选参考平面，`InsertRefPlane(8,z_m,0,0,0,0)`，验证实际偏移。矩形放样：先选两个草图（mark 1），本机验证调用为 `InsertProtrusionBlend2(False,False,False,1.,0,0,1.,1.,False,False,False,0.,0.,0,False,False,False,0)`。更复杂截面需另行验证，不假定矩形案例能保证无扭曲。

## 配置与 COM 对象生命周期

1. 创建配置后先枚举名称并读取活动配置，创建操作可能已经将新配置激活。
2. 不直接 `assert ShowConfiguration2(name)`。已是目标配置时跳过；否则切换并读取当前名称，实际状态为验收依据。
3. helper 用法：`ensure_configuration(model, lambda: W(W(model.ConfigurationManager,'IConfigurationManager').ActiveConfiguration,'IConfiguration').Name, target)`。返回值保留原 API 状态供诊断；未到目标就报错。
4. 重建/切换后重新获取 EquationMgr、实体和功能特征引用。尤其抑制操作用 `W(part.FeatureByName(name),'IFeature')`；FeatureByName 在本机 IPartDoc，不能调用 IModelDoc2 上不存在的方法。
5. 依赖特征逆序抑制、正序解除抑制；每次 `SetSuppression2` 后重新获取并 `IsSuppressed()` 读回。
6. 不用耗时重跑替代检查点恢复。先记录当前文档、配置、已存在特征和最后成功保存文件，再从失败阶段恢复；恢复脚本不重复创建同名实体。

## 装配矩阵和颜色的 SAFEARRAY

Python 普通 list 传入某些 VARIANT 接口可能得到单位变换而无明显错误。统一使用 double SAFEARRAY：

```python
from sw_contracts import r8, translation_data, assert_transform
mu = W(sw.GetMathUtility(), 'IMathUtility')
expected = translation_data(0, 0, -6.3)  # helper 入参 mm，输出 SI
transform = W(mu.CreateTransform(r8(expected)), 'IMathTransform')
assert_transform(transform.ArrayData, expected)
model.ClearSelection2(True)
component.Select4(False, None, False)
assembly.UnfixComponent()  # 需要移动的固定组件，先解除固定
result = component.SetTransformAndSolve2(transform)
assert_transform(W(component.Transform2, 'IMathTransform').ArrayData, expected)
# 静态装配可重新选中后 FixComponent；运动装配则设置所需配合。
```

矩阵 16 数值依次：9 个旋转值、3 个平移值（m）、1 个 scale、3 个保留值。平移在 9/10/11（0-based）；scale=1。先 `OpenDoc6` 加载零件，再激活装配、`AddComponent5`；不要相信插入点必然是零件原点。对齐后检查实际包络、接触和重叠。

颜色同样用 `r8([r,g,b,ambient,diffuse,specular,shininess,transparency,emission])`（确认当前 API 参数含义），RGB 归一化 0..1。本机有效形状：RGB 加 `(.3,.7,.35,.25,0.,0.)`。可设置文档 `MaterialPropertyValues` / 实体 `MaterialPropertyValues2`，保存并检查原生视图；默认外观或组件覆盖可能遮蔽实体颜色。颜色不是物理材料属性。

## 保存与恢复

检查 `Extension.SaveAs(path,0,1,None,0,0)` 的 success/error/warnings。新文档 SaveAs 到已有打开的同名输出可能失败；只处理本任务已保存的文档，不关闭用户其他未保存工作。`SaveToFile3` 派生实体会打开新文档，下一次操作要重新激活母模型。独立原生零件、派生零件和导入件编辑能力不同，交付时说明。

配置切换、抑制、导出不跨多个脚本并发运行同一个 SolidWorks 实例。可并行做不触碰应用状态的 STEP 检查、文档整理。
