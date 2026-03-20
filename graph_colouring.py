import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict

opts = {"with_labels": True, "node_size": 300}


def generate_grid_graph(rows, cols, neighbourhood="von_neumann"):
    G = nx.grid_2d_graph(rows, cols)
    print("Number of Nodes: ", G.order())
    print("Number of Edges: ", G.size())
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


def run_perturbation_simulation(G, num_colours, num_perturbations, max_iterations):
    colouring, conflicts = run_simulation(G, num_colours, max_iterations)

    # change the colour of k random nodes
    num_nodes_perturbed = random.sample(list(G.nodes()), num_perturbations)
    for node in num_nodes_perturbed:
        current = colouring[node]
        other_colours = [c for c in range(num_colours) if c != current]
        colouring[node] = random.choice(other_colours)

    conflicts_after_perturbation = count_conflicts(G, colouring)

    recovery_history = run_simulation_from_state(G, colouring, num_colours, max_iterations)
    recovered = recovery_history[-1] == 0

    print("initial conflicts: ", conflicts)
    print("conflicts after perturbation: ", conflicts_after_perturbation)
    print("recovery history: ", recovery_history)
    print("recovered: ", recovered)

    results = {
        "initial_conflicts": conflicts,
        "conflicts_after_perturbation": conflicts_after_perturbation,
        "recovery_history": recovery_history,
        "recovered": recovered
    }

    return results


def run_simulation_from_state(G, initial_colouring, num_colours, max_iterations):
    colouring = dict(initial_colouring)  # make a copy to avoid modifying the original
    nodes = list(G.nodes())
    conflict_history = [count_conflicts(G, colouring)]

    for _ in range(max_iterations):
        conflicted_nodes = [n for n in nodes if any(colouring[n] == colouring[neighbour] for neighbour in G.neighbors(n))]
        if not conflicted_nodes:
            break
        node = random.choice(conflicted_nodes)
        neighbour_colours = [colouring[neighbour] for neighbour in G.neighbors(node)]
        colour_counts = [neighbour_colours.count(c) for c in range(num_colours)]
        min_count = min(colour_counts)
        best_colours = [c for c, cnt in enumerate(colour_counts) if cnt == min_count]
        colouring[node] = random.choice(best_colours)
        conflict_history.append(count_conflicts(G, colouring))

    return conflict_history, colouring


def plot_colouring(G, colouring):
    color_map = [colour for node, colour in sorted(colouring.items())]
    #color_map = [palette[colour] for node, colour in sorted(colouring.items())]
    plt.figure(figsize=(8, 8))
    nx.draw(G, **opts, node_color=color_map)
    plt.show()


if __name__ == "__main__":
    random.seed(43)
    G = generate_grid_graph(5, 5)
    num_colours = 3
    #palette = ["lightblue", "green", "yellow", "orange", "pink"]
    colouring = initialise_colours(G, num_colours)
    print("Initial colouring:", colouring)
    print("Initial conflicts:", count_conflicts(G, colouring))
    plot_colouring(G, colouring)
    run_simulation(G, num_colours, max_iterations=200)
    run_perturbation_simulation(G, num_colours, num_perturbations=5, max_iterations=1000)
    run_simulation_from_state(G, colouring, num_colours, max_iterations=500)
