import dimod
import numpy as np
import ast

from calculate_max_value import calculate_max_value
from cost_hamiltonian import create_cost_hamiltonian_mwis
from energy_histogram import generate_mwis_histogram
from estimator_run import  estimator_run_qaoa, estimator_run_qaoa_grid
from generate_chart import generate_heatmap, draw_bitstring_distribution
from sampler_run import sampler_run
from sampler_run_2 import sampler_run_2

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
cost_mwis = create_cost_hamiltonian_mwis(graph)
# initial_beta = np.random.uniform(0, np.pi, 1)
# initial_gamma = np.random.uniform(0, 2 * np.pi, 1)
''"run by sampler'"
#expectation_values_2 = sampler_run_2(beta_values, gamma_values , n_qubits, cost_hamiltonian, graph)
# expectation_values = sampler_run(initial_beta, initial_gamma , n_qubits, cost_mwis, graph)

''"run by estimator'"
# expectation_values = estimator_run(beta_values, gamma_values , n_qubits, cost_hamiltonian)
# print(expectation_values)
# generate_heatmap(expectation_values)
# optimal_beta, optimal_gamma, optimal_energy = estimator_run_qaoa(
#     n_qubits=n_qubits,
#     p=1,
#     cost_mwis=cost_mwis
# )
# optimal_beta_2, optimal_gamma_2, optimal_energy_2 = estimator_run_qaoa(
#     n_qubits=n_qubits,
#     p=2,
#     cost_mwis=cost_mwis
# )
optimal_beta, optimal_gamma, optimal_energy = estimator_run_qaoa_grid(n_qubits,1, cost_mwis, grid_resolution=50)
optimal_beta_2, optimal_gamma_2, optimal_energy_2 = estimator_run_qaoa_grid(n_qubits,2, cost_mwis, grid_resolution=16)
print(optimal_beta, optimal_gamma, optimal_energy)
optimal_params = [(optimal_beta, optimal_gamma), (optimal_beta_2, optimal_gamma_2)]
print(optimal_gamma)
print(optimal_beta)
print(optimal_energy)
sampler = dimod.ExactSolver()
sampleset = sampler.sample(cost_mwis)
best_sample = sampleset.first.sample
best_energy = sampleset.first.energy

print("\nBest sample (bitstring with lowest energy):")
print(best_sample)
print("Best energy:")
print(best_energy)
draw_bitstring_distribution(n_qubits, optimal_beta, optimal_gamma, cost_mwis)
generate_mwis_histogram(optimal_params, n_qubits, cost_mwis, graph)