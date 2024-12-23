import networkx as nx
import os
from tabulate import tabulate
import time
import tqdm
import functools
from operator import mul
import array
import sys
# import graph_cliques

sys.setrecursionlimit(10000)
DATA_DIR = "prepared_data"

 

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

def create_sub_graph(G: list, nodes: list) -> list:
    sub_graph = [[] for _ in range(len(G))]
    for node in nodes: 
        for i in G[node]:
            if i in nodes:
                sub_graph[node].append(i)
    return sub_graph

def check_clique(G: list, clique: list) -> bool:
    set_nodes = set([i for i in range(len(clique)) if clique[i] == 1])
    for n in range(len(G)):
        if G[n] == []:
            continue
        if set_nodes != (set(G[n]).add(n)):
            return False
    return True 

def check_clique_for_local_search(G: list, clique: list) -> bool:
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            u, v = clique[i], clique[j]
            # Если вершины u и v не смежны, это не клика
            if v not in G[u]:
                return False
    return True
    # for n in clique:
    #     if not (set(clique) <= set(G[n] + [n])):
    #         return False
    # return True

def find_clique_from_node(node: int, G: list) -> int:
    clique = [0] * num_nodes
    clique[node] = 1
    sub_graph = create_sub_graph(G, G[node])
    while not check_clique(sub_graph, clique=clique):
        max_node = max(range(len(sub_graph)), key=lambda i: len(sub_graph[i]))
        clique[max_node] = 1
        sub_graph = create_sub_graph(sub_graph, sub_graph[max_node])
    
    return [i for i in range(len(clique)) if clique[i] == 1], len([i for i in range(len(clique)) if clique[i] == 1])
def find_max_clique(G: list, num_nodes: int, randomized: int=0) -> int:
    best_clique = []
    best_len_clique = 0
    sorted_graph = sorted(range(num_nodes), key=lambda i: len(G[i]), reverse=True)
    max_node = sorted_graph[0]
    cliques = []
    best_clique, best_len_clique = find_clique_from_node(max_node, G)
    cliques.append(best_clique)
    k = 0
    nodes = [max_node]
    for n in sorted_graph:
        if n != max_node:
            for ready_node in nodes:
                if n in G[ready_node]:
                    continue
            next_clique, next_len_clique = find_clique_from_node(n, G)
            cliques.append(next_clique)
            nodes.append(n)
            k += 1
            if best_len_clique < next_len_clique:
                best_clique = next_clique
                best_len_clique = next_len_clique
            if k == randomized:
                break
    
    return best_clique, best_len_clique, cliques

def sort_vertex(G: list) -> list:
    return sorted(range(len(G)), key=G.__getitem__, reverse=True)
def local_search(G: list, initial_clique=None):
    best_clique = initial_clique.copy()
    sorted_G = sort_vertex(G)
    for node in initial_clique:
        current_clique = initial_clique.copy()
        current_clique.remove(node)
        current_node_max = None
        for node_max in sorted_G:
            if node_max in initial_clique:
                continue
            if check_clique_for_local_search(G, current_clique + [node_max]):
                current_clique.append(node_max)
                current_node_max = node_max
                break
        if current_node_max is None:
            continue
        for node_max_n in G[current_node_max]:
            if node_max_n in initial_clique:
                continue
            if check_clique_for_local_search(G, current_clique + [node_max_n]):
                current_clique.append(node_max_n)
        if len(current_clique) > len(best_clique):
            best_clique = current_clique.copy()
    return best_clique, len(best_clique)

def local_serch_max_clique(G: list, initial_clique: list, max_iterations: int):
    best_clique = initial_clique.copy()
    current_clique = initial_clique.copy()
    for _ in tqdm.tqdm(range(max_iterations)):
        current_clique, current_score = local_search(G, best_clique)
        if current_score < len(best_clique):
            break
        best_clique = current_clique.copy()
    return best_clique, len(best_clique)

    


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

def sort_by_color(G, colors):
    degree_colors_list = [0] * len(set(colors))
    for n in colors:
        degree_colors_list[n] += 1
    degree_colors_list.sort(reverse=True)
    degree_colors_vertex = [0] * len(G)
    for v in range(len(G)):
        degree_colors_vertex[v] = degree_colors_list[colors[v]]
    return sorted(range(len(G)), key=lambda i: (len(G[i]), degree_colors_vertex[i]), reverse=True)

def branch_and_bound(G: list, current_clique: list, remaining_vertices: list, best_clique: list, colors: list, 
                     current_colors: set): 
    colors_remainig_vertices = [colors[n] for n in remaining_vertices]
    if len(current_clique) + len(set(colors_remainig_vertices)) <= len(best_clique):
        return best_clique
    new_remaining = []
    for v in remaining_vertices:
        if v in new_remaining:
            continue
        if len(G[v]) < len(best_clique):
            continue
        new_clique = current_clique + [v]
        new_colors = current_colors | {colors[v]}
        if check_clique_for_local_search(G, new_clique):
            if len(new_clique) > len(best_clique):
                best_clique = new_clique.copy()
            new_remaining = [n for n in remaining_vertices if n in G[v] and n not in new_clique 
                             and colors[n] not in new_colors 
                             and len(set(G[n]) & set(remaining_vertices)) >= len(best_clique)]
            if len(new_remaining) == 0:
                continue
            best_clique = branch_and_bound(G, new_clique, new_remaining, best_clique, colors, new_colors)
            remaining_vertices.remove(v)
    return best_clique

def find_max_clique_bnb(G: list, initial_clique: list):
    n = len(G)
    colors, num_colors = color_graph(G, len(G))
    best_clique = branch_and_bound(G, [], sort_by_color(G, colors), initial_clique, colors, set())
    return best_clique, len(best_clique)


if __name__ == "__main__":
    results = [["file", "len_clique_greedy", "time_greedy", "len_clique_ls", "time_ls", "len_clique_bnb", "time_bnb"]]
    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)
        with open(os.path.join(file_path, file + ".txt")) as f:
            data = f.read().split("\n")
            num_nodes, num_edges = int(data[0].split()[0]), int(data[0].split()[1])
            edges = data[1:]
            edges = [e.split() for e in edges if e != '']
            G = fill_graph(edges=edges, num_nodes=num_nodes)
            G_copy = G.copy()
            print(file.upper())
            time_start = time.time()
            max_clique, max_len_clique, cliques = find_max_clique(G=G, num_nodes=num_nodes, randomized=10)
            print(G == G_copy)
            print(check_clique_for_local_search(G, max_clique))
            time_greedy = time.time() - time_start
            time_start = time.time()
            max_clique_ls, max_len_clique_ls = local_serch_max_clique(G=G, initial_clique=max_clique, max_iterations=10)
            print(G == G_copy)
            print(check_clique_for_local_search(G, max_clique_ls))
            time_ls = time.time() - time_start
            time_start = time.time()
            max_clique_bnb, max_len_clique_bnb = find_max_clique_bnb(G, max_clique_ls)
            # max_clique_bnb, max_len_clique_bnb = graph_cliques.find_max_clique_bnb(G, max_clique_ls)
            print(check_clique_for_local_search(G, max_clique_bnb))
            time_bnb = time.time() - time_start
            results.append([file, max_len_clique, time_greedy, 
                            max_len_clique_ls, time_greedy + time_ls,
                            max_len_clique_bnb, time_greedy + time_ls + time_bnb])
    print(tabulate(results))
    with open("results.txt", "w") as f:
        print(tabulate(results), file=f)

