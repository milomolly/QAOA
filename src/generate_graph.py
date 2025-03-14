import networkx as nx
import random

n = [5, 10, 15, 20]

for i in n:
    p = 0.5
    for j in range(30):
        # Generate the random graph
        graph = nx.erdos_renyi_graph(i, p)

        # Create an array of integer weights for each vertex
        weights = []
        for node in graph.nodes():
            weight = random.randint(1, 100)  # random integer weight between 1 and 100
            graph.nodes[node]['weight'] = weight
            weights.append(weight)

        # Prepare a file name for the output
        file_name = f"input/graph{i}_{j + 1}.txt"

        # Write the weight array and edge list to the file
        with open(file_name, "w") as file:
            file.write("Vertex Weights Array:\n")
            file.write(str(weights) + "\n")
            file.write("\nEdge List:\n")
            file.write(str(list(graph.edges())))
