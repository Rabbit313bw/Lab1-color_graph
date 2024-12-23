import networkx as nx
import os
from tabulate import tabulate
import time

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

def find_clique_from_node(node: int, G: list) -> int:
    clique = [-1] * num_nodes
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
    best_clique, best_len_clique = find_clique_from_node(max_node, G)
    k = 0
    nodes = [max_node]
    for n in sorted_graph:
        if n != max_node:
            for ready_node in nodes:
                if n in G[ready_node]:
                    continue
            next_clique, next_len_clique = find_clique_from_node(n, G)
            nodes.append(n)
            k += 1
            if best_len_clique < next_len_clique:
                best_clique = next_clique
                best_len_clique = next_len_clique
            if k == randomized:
                break
    
    return best_clique, best_len_clique
    


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
    results = [["file", "len_clique", "time"]]
    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)
        with open(os.path.join(file_path, file + ".txt")) as f:
            data = f.read().split("\n")
            num_nodes, num_edges = int(data[0].split()[0]), int(data[0].split()[1])
            edges = data[1:]
            edges = [e.split() for e in edges if e != '']
            G = fill_graph(edges=edges, num_nodes=num_nodes)
            print(file)
            time_start = time.time()
            max_clique, max_len_clique = find_max_clique(G=G, num_nodes=num_nodes, randomized=10)
            time_alg = time.time() - time_start
            results.append([file, max_len_clique, time_alg])
    print(tabulate(results))
    with open("results.txt", "w") as f:
        print(tabulate(results), file=f)

