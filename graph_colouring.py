import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict

opts = {"with_labels": True, "node_size": 300}


def generate_grid_graph(rows, cols, neighbourhood="von_neumann"):
    G = nx.grid_2d_graph(rows, cols)
    return nx.convert_node_labels_to_integers(G)


def initialise_colours(G, num_colours):
    return {node: random.randint(0, num_colours - 1) for node in G.nodes()}


def count_conflicts(G, colouring):
    conflicts = 0
    # for each edge in graph, if the 2 nodes are same colour, then conflict
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


def update_node(G, node, colouring, num_colours):
    neighbour_colours = (colouring[neighbour] for neighbour in G.neighbors(node))
    colour_counts = defaultdict(int)
    for colour in neighbour_colours:
        colour_counts[colour] += 1
    best_colour = min(range(num_colours), key=lambda c: colour_counts.get(c, 0))
    colouring[node] = best_colour

    return colouring


def run_simulation(G, num_colours, max_iterations):
    colouring = initialise_colours(G, num_colours)
    conflict_history = [count_conflicts(G, colouring)]
    for iteration in range(max_iterations):
        conflicted_nodes = list_conflicted_nodes(G, colouring)
        if not conflicted_nodes:
            print(f"Solution found in {iteration} iterations!")
            break
        node_to_update = random.choice(list(conflicted_nodes))
        colouring = update_node(G, node_to_update, colouring, num_colours)
        conflict_history.append(count_conflicts(G, colouring))

    print(f"Iteration {iteration + 1}: Conflicts = {conflict_history[-1]}")

    return colouring, conflict_history


def plot_colouring(G, colouring):
    color_map = [colour for node, colour in sorted(colouring.items())]
    #color_map = [palette[colour] for node, colour in sorted(colouring.items())]
    plt.figure(figsize=(8, 8))
    nx.draw(G, **opts, node_color=color_map)
    plt.show()


if __name__ == "__main__":
    random.seed(42)
    G = generate_grid_graph(5, 5)
    num_colours = 3
    #palette = ["lightblue", "green", "yellow", "orange", "pink"]
    colouring = initialise_colours(G, num_colours)
    print("Initial colouring:", colouring)
    print("Initial conflicts:", count_conflicts(G, colouring))
    plot_colouring(G, colouring)
    run_simulation(G, num_colours, max_iterations=200)
