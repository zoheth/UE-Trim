import argparse
import os
import re
import json
from collections import defaultdict
import pickle
import networkx as nx

parser = argparse.ArgumentParser(description="Processing command line arguments")
parser.add_argument(
    "--ue_path",
    type=str,
    required=True,
    help="Path to Unreal Engine root directory, e.g. D:\\UE\\UnrealEngine-5.1.0-release",
)
parser.add_argument(
    "--consider_all_dependencies",
    default=True,
    action=argparse.BooleanOptionalAction,
    help="Consider all dependencies (default: True)",
)

args = parser.parse_args()

source_path = os.path.join(args.ue_path, "Engine", "Source")
plugins_path = os.path.join(args.ue_path, "Engine", "Plugins")
platforms_path = os.path.join(args.ue_path, "Engine", "Platforms")

consider_all_dependencies = args.consider_all_dependencies

build_files = []
for dirpath, dirnames, filenames in os.walk(source_path):
    for filename in filenames:
        if filename.casefold().endswith(".build.cs"):
            build_files.append(os.path.join(dirpath, filename))

plugin_files = []
for dirpath, dirnames, filenames in os.walk(plugins_path):
    for filename in filenames:
        if filename.casefold().endswith(".uplugin"):
            plugin_files.append(os.path.join(dirpath, filename))

platforms_build_files = []
for dirpath, dirnames, filenames in os.walk(platforms_path):
    for filename in filenames:
        if filename.casefold().endswith(".build.cs"):
            platforms_build_files.append(os.path.join(dirpath, filename))

pattern = re.compile(
    r"ModuleRules.*?PublicDependencyModuleNames\.AddRange\((.*?)\);", re.DOTALL
)

module_dependencies = defaultdict(list)
super_modules = defaultdict(list)
module_names = set()

super_modules_info = {}


def process_build_file(build_file, super_name):
    with open(build_file, "r", encoding="UTF-8") as f:
        content = f.read()
    base_name = os.path.basename(filename)
    module_name = base_name.split(".")[0]
    module_names.add(module_name)
    super_modules[super_name].append(module_name)

    matches = pattern.findall(content)
    dependencies = []
    if consider_all_dependencies:
        dependencies = re.findall(r'"([^"]*)"', content)
    elif matches:
        dependencies = matches[0]
        dependencies = re.findall(r'"(.*?)"', dependencies)
    
    # Add class inheritance dependencies
    class_inheritance_pattern = r'class\s+\w+\s*:\s*(\w+)'
    inheritance_matches = re.findall(class_inheritance_pattern, content)
    dependencies.extend(inheritance_matches)
    if inheritance_matches:
        print(inheritance_matches)
    
    module_dependencies[super_name] = list(
        set(module_dependencies[super_name] + dependencies)
    )


for build_file in build_files:
    path_parts = build_file.split(os.sep)
    super_name = path_parts[6]
    super_modules_info[super_name] = {"Dir": os.sep.join(path_parts[:7])}
    process_build_file(build_file, super_name)

for build_file in platforms_build_files:
    path_parts = build_file.split(os.sep)
    super_name = '_'.join([path_parts[5], path_parts[8]])
    super_modules_info[super_name] = {"Dir": os.sep.join(path_parts[:9])}
    process_build_file(build_file, super_name)

for plugin_file in plugin_files:
    wark_path = os.path.dirname(plugin_file)
    super_name = os.path.basename(wark_path)
    super_modules_info[super_name] = {"Dir": wark_path}
    try:
        with open(plugin_file, "r", encoding="UTF-8") as f:
            plugin_content = json.load(f)
        super_modules_info[super_name].update(
            {
                "FriendlyName": plugin_content.get("FriendlyName", None),
                "Category": plugin_content.get("Category", None),
                "Description": plugin_content.get("Description", None),
            }
        )
    except json.decoder.JSONDecodeError:
        pass
        # print(f"Error decoding JSON for file: {plugin_file}")

    # Find all .build.cs files in the same directory
    for dirpath, dirnames, filenames in os.walk(wark_path):
        for filename in filenames:
            if filename.casefold().endswith(
                ".build.cs"
            ):  # Case-insensitive file extension check
                build_file = os.path.join(dirpath, filename)
                process_build_file(build_file, super_name)

for super_name, modules in super_modules.items():
    for module_name, dependencies in module_dependencies.items():
        for dependent_module in dependencies:
            if dependent_module in modules:
                index = dependencies.index(dependent_module)
                dependencies[index] = super_name


G = nx.DiGraph()

for module_name in module_dependencies.keys():
    module_names.add(module_name)
    G.add_node(module_name)

if not os.path.exists("logs"):
    os.makedirs("logs")
if not os.path.exists("data"):
    os.makedirs("data")

with open("logs/gen_graph_output.log", "w") as f:
    for module_name, dependencies in module_dependencies.items():
        for dependency in dependencies:
            if dependency in module_names:  # Check if the dependency is a module.
                G.add_edge(module_name, dependency)
                print(f"{module_name} -> {dependency}", file=f)

with open("data/graph_all.pickle", "wb") as f:
    pickle.dump(G, f)

with open("data/modules_info.pickle", "wb") as f:
    pickle.dump(super_modules_info, f)
