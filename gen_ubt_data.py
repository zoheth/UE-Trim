import networkx as nx
import difflib
import pickle


def parse_module_dependencies(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    modules = {}
    current_module = None
    reading_deps = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current_module = line[1:-1]
            if current_module not in modules:
                modules[current_module] = {
                    "Directory": None,
                    "Dependencies": set(),  # Use a set to prevent duplicates
                }
            reading_deps = False
        elif line.startswith("Directory: "):
            if current_module:
                modules[current_module]["Directory"] = line.split("Directory: ")[1]
        elif line.startswith("Dependencies:"):
            reading_deps = True
        elif reading_deps and current_module:
            dep = line[2:]  # Remove the '- ' prefix
            modules[current_module]["Dependencies"].add(dep)

    return modules


def create_dependency_graph(dependencies):
    G = nx.DiGraph()

    for module, details in dependencies.items():
        for dep in details["Dependencies"]:
            G.add_edge(module, dep)

    return G


modules_info = parse_module_dependencies("ubt_data/ModuleDependencies.txt")
G = create_dependency_graph(modules_info)


def parse_desc_file(desc_file_path):
    with open(desc_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    descriptions = {}
    for line in lines:
        node, desc = line.split(":", 1)
        descriptions[node.strip()] = desc.strip()

    return descriptions


def find_most_similar_key(key, keys_list):
    """Find the most similar key in a list of keys."""
    matches = difflib.get_close_matches(key, keys_list, n=1)
    if matches:
        return matches[0]
    return None


# Parsing the desc.txt file
desc_data = parse_desc_file("ubt_data/Desc.txt")

# Add descriptions to the modules_info dictionary
for module_name, module_data in modules_info.items():
    closest_match = find_most_similar_key(module_name, desc_data.keys())
    if closest_match:
        module_data["Desc"] = desc_data[closest_match]
nx.write_gexf(G, "ubt_data/graph_full.gexf")
nodes_to_remove = [node for node, degree in G.in_degree() if degree > 10]
G.remove_nodes_from(nodes_to_remove)
nx.write_gexf(G, "ubt_data/graph.gexf")
subgraphs = {}
for node in G.nodes():
    predecessors = set(nx.ancestors(G, node))
    successors = set(nx.descendants(G, node))
    related_nodes = predecessors.union(successors, {node})
    subgraph = G.subgraph(related_nodes)
    subgraphs[node] = subgraph

with open("ubt_data/modules_info.pkl", "wb") as f:
    pickle.dump(modules_info, f)
