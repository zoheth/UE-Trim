
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

在命令行中，输入以下命令：

```bash
jupyter notebook analysis.ipynb
```
- 按顺序执行 **准备就绪！** 之前的所有代码块。修改`cur_node`，即可查看依赖该节点的所有节点的依赖图，删除所有节点，或恢复操作。

- 可以参考之前步骤生成的`topology_all.txt`文件里的内容选择`cur_node`的值

- 所有删除恢复操作做了**持久化**，重启jupyter不会影响一致性。日志文件为：`logs/filesystem.log`

- 恢复操作使用栈来实现。当执行恢复操作时，总是恢复最后一次删除的目录集合，所有恢复操作不需要任何参数。



