import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict

opts = {"with_labels": True, "node_size": 300}


# function to generate a grid graph
def generate_grid_graph(rows, cols, neighbourhood="von_neumann"):
    G = nx.grid_2d_graph(rows, cols)
    print("Number of Nodes: ", G.order())
    print("Number of Edges: ", G.size())
    return nx.convert_node_labels_to_integers(G)


# randomly assign a colour to each node from the available colours
def initialise_colours(G, num_colours):
    return {node: random.randint(0, num_colours - 1) for node in G.nodes()}


# count the number of conflicted nodes in the graph
def count_conflicts(G, colouring):
    conflicts = 0
    # for each edge in graph, if the 2 nodes are same colour, then conflict
    for u, v in G.edges():
        if colouring[u] == colouring[v]:
            conflicts += 1

    return conflicts


# return a set of nodes that are in conflict
def list_conflicted_nodes(G, colouring):
    conflicted_nodes = set()
    for u, v in G.edges():
        if colouring[u] == colouring[v]:
            conflicted_nodes.add(u)
            conflicted_nodes.add(v)

    return conflicted_nodes


# function to update the colour of a node based on the colours of its neighbours
def update_node(G, node, colouring, num_colours):
    # count how many neighbours are using each colour
    neighbour_colours = [colouring[neighbour] for neighbour in G.neighbors(node)]
    colour_counts = defaultdict(int)
    for colour in neighbour_colours:
        colour_counts[colour] += 1

    # find the minimum count and the colours that have that count
    min_count = min(colour_counts.get(c, 0) for c in range(num_colours))
    best_colours = [c for c in range(num_colours) if colour_counts.get(c, 0) == min_count]

    # randomly choose one of the best colours
    colouring[node] = random.choice(best_colours)

    return colouring


# run the simulation from a random initial state
def run_simulation(G, num_colours, max_iterations):
    # randomly assign initial colours to each node and record initial conflicts
    colouring = initialise_colours(G, num_colours)
    conflict_history = [count_conflicts(G, colouring)]

    for iteration in range(max_iterations):
        conflicted_nodes = list_conflicted_nodes(G, colouring)
        # if no conflicts remain, solution found
        if not conflicted_nodes:
            #print(f"Solution found in {iteration} iterations")
            break

        # pick a random conflicted node and update its colour
        node_to_update = random.choice(list(conflicted_nodes))
        colouring = update_node(G, node_to_update, colouring, num_colours)
        # record the number of conflicts after the update
        conflict_history.append(count_conflicts(G, colouring))

    #print(f"Iteration {max_iterations}: Conflicts = {conflict_history[-1]}")

    return colouring, conflict_history


# function to run the perturbation experiment
def run_perturbation_experiment(G, num_colours, num_perturbations, max_iterations):
    # first run the baseline simulation to get a solution
    colouring, conflict_history = run_simulation(G, num_colours, max_iterations)
    print("Number of colours: ", num_colours)

    # if the baseline simulation did not solve, skip the perturbation test
    if conflict_history[-1] != 0:
        print("Baseline did not solve, skipping perturbation test")
        return None

    iterations_to_solve = len(conflict_history) - 1
    print("Initial Conflicts: ", conflict_history[0])
    print("Iterations to solve: ", iterations_to_solve)

    # change the colour of k random nodes
    num_nodes_perturbed = random.sample(list(G.nodes()), num_perturbations)
    for node in num_nodes_perturbed:
        current = colouring[node]
        # choose any colour other than the current colour of the node
        other_colours = [c for c in range(num_colours) if c != current]
        colouring[node] = random.choice(other_colours)

    conflicts_after_perturbation = count_conflicts(G, colouring)
    print("Nodes perturbed: ", num_perturbations)
    print("Conflicts after perturbation: ",conflicts_after_perturbation)

    # recover from the perturbed state and see if it can return to a solution
    _, recovery_history = run_simulation_from_state(G, colouring, num_colours, max_iterations)
    recovered = recovery_history[-1] == 0
    iterations_to_recover = len(recovery_history) - 1
    print("Recovered: ", recovered)
    print("Iterations to recover: ", iterations_to_recover)

    results = {
        "initial_conflicts": conflict_history[-1],
        "conflicts_after_perturbation": conflicts_after_perturbation,
        "recovered": recovered,
        "recovery_history": recovery_history
    }

    return results


# runs the simulation starting from a given state (used for recovery after perturbation)
def run_simulation_from_state(G, initial_colouring, num_colours, max_iterations):
    colouring = dict(initial_colouring)  # make a copy to avoid modifying the original
    nodes = list(G.nodes())
    conflict_history = [count_conflicts(G, colouring)]

    for _ in range(max_iterations):
        conflicted_nodes = list_conflicted_nodes(G, colouring)
        # if no conflicts remain, solution found
        if not conflicted_nodes:
            break

        # pick a random conflicted node and update its colour using the same rule as run_simulation
        node = random.choice(list(conflicted_nodes))
        colouring = update_node(G, node, colouring, num_colours)

        conflict_history.append(count_conflicts(G, colouring))

    return colouring, conflict_history


# estimates the chromatic number of the graph using a greedy colouring algorithm
def get_chromatic_number(G):
    colouring = nx.coloring.greedy_color(G, strategy="largest_first")
    num_colours_used = len(set(colouring.values()))

    return num_colours_used


# draws the graph with nodes coloured according to the given colouring
def plot_colouring(G, colouring):
    color_map = [colour for node, colour in sorted(colouring.items())]
    #color_map = [palette[colour] for node, colour in sorted(colouring.items())]
    plt.figure(figsize=(8, 8))
    nx.draw(G, **opts, node_color=color_map)
    plt.show()


# plots the conflict history for different numbers of colours to show how quickly the algorithm solves
def plot_conflicts(G, num_colours, max_iterations):
    plt.figure(figsize=(10, 5))
    for colours in num_colours:
        _, conflict_history = run_simulation(G, colours, max_iterations)
        plt.plot(conflict_history, label=f"{colours} colours")

    plt.xlabel("Iteration")
    plt.ylabel("Number of Conflicts")
    plt.title("Conflict Reduction over time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    random.seed(42)
    G = generate_grid_graph(10, 10)
    num_colours = 3
    #palette = ["lightblue", "green", "yellow", "orange", "pink"]
    colouring = initialise_colours(G, num_colours)
    #print("Initial colouring:", colouring)
    #print("Initial conflicts:", count_conflicts(G, colouring))
    #plot_colouring(G, colouring)
    #run_simulation(G, num_colours, max_iterations=500)
    #for k in [1, 2, 3, 4, 5, 6, 7, 8]:
        #run_perturbation_experiment(G, num_colours, num_perturbations=k, max_iterations=1000)
    run_perturbation_experiment(G, num_colours, num_perturbations=4, max_iterations=1000)
    #plot_conflicts(G, num_colours=[2, 3, 4, 5, 6, 7, 8, 9, 10], max_iterations=200)


