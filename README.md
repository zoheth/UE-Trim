
---

## 安装依赖

在仓库的根目录下，打开命令行窗口，然后输入以下命令安装依赖：

```bash
pip install -r requirements.txt
```
---
## 一、运行gen_graph_v2.py脚本，获得依赖图与一些模块信息

`gen_graph_v2.py`脚本有两个命令行参数：

1. `--ue_path`: 必需的参数，需要指定Unreal Engine的根目录。例如：`D:\UE\UnrealEngine-5.1.0-release`
2. `--consider_all_dependencies`: 可选的参数，默认值为True。若为False则只考虑私有依赖。

在命令行中，使用以下命令运行脚本：

```bash
python gen_graph_v2.py --ue_path "D:\UE\UnrealEngine-5.1.0-release"
```

---
## 二、运行 jupyter note

在命令行中，输入以下命令开启不同的notebook，**不同的notebook之间没有依赖关系**：

```bash
jupyter notebook analysis.ipynb
```
- 按顺序执行 **准备就绪！** 之前的所有代码块。修改`cur_node`，即可查看依赖该节点的所有节点的依赖图，删除所有节点，或恢复操作。

- 可以参考之前步骤生成的`topology_all.txt`文件里的内容选择`cur_node`的值

- 所有删除恢复操作做了**持久化**，重启jupyter不会影响一致性。日志文件为：`logs/filesystem.log`

- 恢复操作使用栈来实现。当执行恢复操作时，总是恢复最后一次删除的目录集合，所有恢复操作不需要任何参数。

## 三、UBT模块可视化

**step1**

修改UBT源码，修改文件`Engine\Source\Programs\UnrealBuildTool\Configuration\UEBuildModule.cs`中的`public HashSet<UEBuildModule> GetDependencies(bool bWithIncludePathModules, bool bWithDynamicallyLoadedModules)`函数。在返回Modules之前添加以下内容。
```csharp
// Writing module dependencies to a file
string filePath = "C:\\ModuleDependencies.txt";
using (StreamWriter writer = new StreamWriter(filePath, true)) // true to append data to the file
{
	writer.WriteLine("[" + this.Name + "]");

	writer.WriteLine("Directory: " + ModuleDirectory);

	writer.WriteLine("Dependencies:");
	foreach (UEBuildModule module in Modules)
	{
		writer.WriteLine("- " + module.Name);
	}
	writer.WriteLine();
}
```

**step2**

运行引擎根目录下的`GenerateProjectFiles.bat`。运行脚本后信息将写入`C:\\ModuleDependencies.txt`，即修改源码时指定的位置，可以更换成任意路径。 <br>
注意！！！不要反复运行！获取到`ModuleDependencies.txt`之后及时注释掉更改的内容。

**step3**

将`ModuleDependencies.txt`文件置于`ubt_data`目录下，然后运行
```bash
python gen_ubt_data.py
```

**step4**

可视化模块之间的依赖

```bash
# 用图的形式可视化 重要模块 之间的依赖：
jupyter notebook visualization.ipynb

# 用文本的形式可视化 所有模块 之间的依赖：
jupyter notebook visualization2.ipynb
```


