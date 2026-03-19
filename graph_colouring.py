import networkx as nx
import matplotlib.pyplot as plt
import random

opts = {"with_labels": True}


def generate_grid_graph(rows, cols, neighbourhood="von_neumann"):
    G = nx.grid_2d_graph(rows, cols)
    return nx.convert_node_labels_to_integers(G)


def initialise_colours(G, num_colours):
    return {node: random.randint(0, num_colours - 1) for node in G.nodes()}


def count_conflicts(G, colouring):
    conflicts = 0
    for u, v in G.edges():
        if colouring[u] == colouring[v]:
            conflicts += 1

    return conflicts


def list_conflicted_nodes(G, colouring):
    conflicted_nodes = set()
    for u, v in G.edges():
        if colouring[u] == colouring[v]:
            conflicted_nodes.add(u)
            conflicted_nodes.add(v)

    return conflicted_nodes


def plot_colouring(G, colouring):
    color_map = [colour for node, colour in sorted(colouring.items())]
    plt.figure(figsize=(8, 8))
    nx.draw(G, **opts, node_color=color_map)
    plt.show()


if __name__ == "__main__":
    random.seed(42)
    G = generate_grid_graph(5, 5)
    num_colours = 3
    colouring = initialise_colours(G, num_colours)
    print("Initial colouring:", colouring)
    print("Initial conflicts:", count_conflicts(G, colouring))
    plot_colouring(G, colouring)
