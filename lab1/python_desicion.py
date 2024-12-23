import networkx as nx
import os
from tabulate import tabulate
import time

DATA_DIR = "data/prepared_data"

 
def check_resutls(G: list, colors: list) -> bool:
    num_nodes = len(colors)
    for n in range(num_nodes):
        for i in G[n]:
            if colors[n] == colors[i]:
                return False
    return True

def check_color(neigh: list, colors: list, current_color: int) -> bool:
    for n in neigh:
        if colors[n] == current_color:
            return True
    return False

def color_graph(G: list, num_nodes: int) -> int:
    colors = [-1] * num_nodes
    current_color = 0
    sorted_graph = sorted(range(num_nodes), key=lambda i: len(G[i]), reverse=True)
    while -1 in colors:
        for n in sorted_graph:
            if colors[n] == -1 and not check_color(G[n], colors=colors, current_color=current_color):
                colors[n] = current_color
        current_color += 1
    return colors, len(set(colors))


def fill_graph(edges: list, num_nodes: int) -> list:
    G = [[] for _ in range(num_nodes)]
    for e in edges:
        G[int(e[0]) - 1].append(int(e[1]) - 1)
        G[int(e[1]) - 1].append(int(e[0]) - 1)
    for n in range(num_nodes):
        G[n] = list(set(G[n]))
    return G

def check_graph(G: list, num_nodes: int, num_edges: int) -> bool:
    if len(G) != num_nodes:
        return False
    edges = sum([len(e) for e in G])
    for n in range(num_nodes):
        for neigh in G[n]:
            if n not in G[neigh]:
                return False
    return True


if __name__ == "__main__":
    results = [["file", "colors", "time", "check_result"]]
    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)
        with open(os.path.join(file_path, file + ".txt")) as f:
            data = f.read().split("\n")
            num_nodes, num_edges = int(data[0].split()[0]), int(data[0].split()[1])
            edges = data[1:]
            edges = [e.split() for e in edges if e != '']
            G = fill_graph(edges=edges, num_nodes=num_nodes)
            print(check_graph(G, num_nodes=num_nodes, num_edges=num_edges))
            time_start = time.time()
            colors, num_colors = color_graph(G, num_nodes=num_nodes)
            time_alg = time.time() - time_start
            results.append([file, num_colors, time_alg, check_resutls(G, colors=colors)])
    print(tabulate(results))
    with open("results.txt", "w") as f:
        print(tabulate(results), file=f)

