import numpy as np
import ast

from calculate_max_value import calculate_max_value
from cost_hamiltonian import create_cost_hamiltonian
from energy_histogram import generate_mwis_histogram
from estimator_run import estimator_run
from generate_chart import generate_heatmap
from sampler_run import sampler_run
import networkx as nx


def read_graph(file_path):

    with open(file_path, 'r') as f:
        lines = f.readlines()

    vertex_weights = None
    edge_list = None

    # Parse the file lines to extract vertex weights and edge list
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("Vertex Weights Array:"):
            vertex_weights = ast.literal_eval(lines[i + 1].strip())
        elif line.startswith("Edge List:"):
            edge_list = ast.literal_eval(lines[i + 1].strip())

    if vertex_weights is None or edge_list is None:
        raise ValueError("Graph file format is incorrect. Expected both vertex weights and edge list.")

    # Use the number of vertex weights as the number of nodes
    num_nodes = len(vertex_weights)

    # Create an adjacency matrix for the undirected graph
    adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]
    for u, v in edge_list:
        adjacency_matrix[u][v] = 1
        adjacency_matrix[v][u] = 1  # Graph is undirected

    # Create a graph from the numpy array
    graph_np = np.array(adjacency_matrix)
    graph = nx.from_numpy_array(graph_np)

    # Assign the vertex weights as node attributes
    node_weight_dict = {i: weight for i, weight in enumerate(vertex_weights)}
    nx.set_node_attributes(graph, node_weight_dict, 'weight')

    return graph
file_path = 'input/graph.txt'  # Update this to your file path
graph = read_graph(file_path)
n_qubits = len(graph)
beta_values = np.linspace(0, np.pi/2, 16)
gamma_values = np.linspace(0, np.pi, 8)
cost_hamiltonian = create_cost_hamiltonian(graph)

''"run by sampler'"
expectation_values = sampler_run(beta_values, gamma_values , n_qubits, cost_hamiltonian, graph)
''"run by estimator'"
#expectation_values = estimator_run(beta_values, gamma_values , n_qubits, cost_hamiltonian)
generate_heatmap(expectation_values)
optimal_beta, optimal_gamma = calculate_max_value(expectation_values, beta_values, gamma_values, cost_hamiltonian, graph)
generate_mwis_histogram(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian, graph)