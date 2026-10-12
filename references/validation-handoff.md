# 验收、回读与交付

## 原生检查

- 保存检查点后按每个交付配置重建，读取活动配置名称。递归检查必要特征和子草图，记录 `GetErrorCode2()` 及 warning，不只看顶层文件能打开。
- 草图约束状态、功能尺寸、实体数、包络和体积与建模简表对照；GetBodyBox 是近似包络，公差应与几何尺度对应。
- 在任务自己的副本/生成文件上将一个关键参数改变到安全值，重建并测量可预期响应，然后用 finally 恢复原式并再次验证。保存最终状态。不能因方程存在就宣称已测试可编辑。
- 需要磁盘回读验证时，保存后关闭并重新打开本任务文件再读取；已经打开的 OpenDoc6 返回不能冒充磁盘重开测试。
- 检查各成分名称、材料/配方自定义属性、配置作用域和外观。保留没有定义的物理属性状态，不用任意密度生成有误导性的“真实质量”。

## 独立 STEP 检查

按需要导出 STEP AP242 / Parasolid，记录配置名及单位。用 build123d/OCP 或可用的独立 CAD 工具回读：

```python
import build123d as b
shape = b.import_step(step_path)
solids = list(shape.solids())
assert all(s.is_valid for s in solids)
overlaps = []
for i, first in enumerate(solids):
    for j, second in enumerate(solids[i+1:], i+1):
        inter = first.intersect(second)
        volume = (sum(x.volume for x in inter) if isinstance(inter, b.ShapeList)
                  else inter.volume) if inter else 0.0
        if volume > volume_tolerance_mm3:
            overlaps.append((i, j, volume))
```

公差按模型量级和 CAD 精度定义，不盲目照搬纳米级公差。接触可能产生 Face/ShapeList，而非 Solid；不要直接假设所有 intersect 返回对象都有 `.volume`。

零重叠不代表所有界面都接触；还要测必要接触面的距离/面积。正体积交叠是否允许取决于设计，例如有意过盈不同于误放置。多材料模拟域通常应无意外交叠。记录每对异常和用途，不能只报“实体数符合”。

应验证的量：

|结构|检验|
|---|---|
|连续导电栅|整体单实体 + 中部截面条数 + 相邻净间隙|
|多层材料|各层厚度/Z 位置 + 面接触 + 两两重叠|
|放样/阵列|全包络 + 单元数量/节距 + 无误并入旧实体|
|静态装配|组件变换完整读回 + 固定状态 + 零件引用存在|
|可运动装配|配合、自由度、行程及运动范围的干涉，不能仅全部固定|

## 可视验证

使用 `$cad` 的 inspect 和 snapshot 对真实 STEP 检查。至少查看主模型等轴测和针对失误风险的顶视/侧视；只在需要时增加分解或截面。命令语法按当前技能：

```text
python <cad>/scripts/step --kind assembly <assembly.step> --mesh-tolerance .003
python <cad>/scripts/inspect refs <assembly.step> --facts --planes --positioning
python <cad>/scripts/snapshot --input <assembly.step> --output <absolute-preview.png> --camera iso
```

mesh-tolerance 要按项目尺度选择。快照会在文件名加时间戳，最终链接必须使用实际存在的路径。原生路线生成的 STEP 可作为 direct-import 输入；有 build123d 生成器的路线则遵循 CAD 技能的源文件流程。

同时检查原生视图：可用 SolidWorks `ShowNamedView2('',7)`、`ViewZoomtofit2()`、`GraphicsRedraw2()` 和 `SaveBMP` 获取原生模型预览，或使用 computer-use 查看界面。不能用渲染器美化图代替原生/真实几何检查。Matplotlib 三维透明多层面可能错误排序，不能据此判定层间相交；采用 CAD 深度缓冲快照并配合数值检测。

使用 cad-viewer 时若缺 agent:start 等启动失败，记录实测错误，交付 CLI 检查和离线预览；不要为预览故障修改安装包或未经请求换一套 CAD 主流程。

## 文件包

交付按任务需要组织：原生 SLDPRT/SLDASM、STEP/Parasolid、参数/配方/来源表、中文修改说明、验证记录和实际预览。源脚本应独立于旧项目，不包含导入即连接应用的副作用。需要 STL/3MF 时作为次级输出，不能替代精确 CAD。

- 保存最终默认配置并说明其意义；每个 STEP 标明对应配置。
- 独立原生零件与装配引用放在可共同携带的位置。复杂外部引用优先用经检查的 Pack and Go；不要声称跨机可用，除非引用检查支持。
- 枚举只读/打包时排除 `~$` 锁文件、临时失败版本、缓存和不需要的 BMP。脚本见 `native_files()`。
- 压缩包做完整性检查，必要时记录 SHA256；最终链接使用真实绝对路径。
- 最终简述“做了什么、哪些检查通过、哪些尺寸是假设、编辑范围、未完成或受限项”。默认交付中文说明，不为缺少仿真做多余风险告警。
