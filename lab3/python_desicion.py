import networkx as nx
import os
from tabulate import tabulate
import time
import tqdm
import functools
from operator import mul
import array

DATA_DIR = "prepared_data"

 

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
    for n in clique:
        if not (set(clique) <= set(G[n] + [n])):
            return False
    return True

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


if __name__ == "__main__":
    results = [["file", "len_clique_greedy", "time_greedy", "len_clique_ls", "time_ls"]]
    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)
        with open(os.path.join(file_path, file + ".txt")) as f:
            data = f.read().split("\n")
            num_nodes, num_edges = int(data[0].split()[0]), int(data[0].split()[1])
            edges = data[1:]
            edges = [e.split() for e in edges if e != '']
            G = fill_graph(edges=edges, num_nodes=num_nodes)
            print(file.upper())
            time_start = time.time()
            max_clique, max_len_clique, cliques = find_max_clique(G=G, num_nodes=num_nodes, randomized=10)
            print(check_clique_for_local_search(G, max_clique))
            time_greedy = time.time() - time_start
            time_start = time.time()
            max_clique_ls, max_len_clique_ls = local_serch_max_clique(G=G, initial_clique=max_clique, max_iterations=10)
            print(check_clique_for_local_search(G, max_clique_ls))
            time_ls = time.time() - time_start
            results.append([file, max_len_clique, time_greedy, max_len_clique_ls, time_greedy + time_ls])
    print(tabulate(results))
    with open("results.txt", "w") as f:
        print(tabulate(results), file=f)

