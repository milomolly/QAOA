import numpy as np

from src.calculate_best_cut import calculate_best_cut
from src.cost_hamiltonian import create_cost_hamiltonian
from src.energy_histogram import generate_energy_histogram
from src.estimator_run import estimator_run
from src.generate_chart import generate_heatmap
from src.sampler_run import sampler_run

def read_edge_list(file_path):
    """
    Reads an edge list from a file and converts it to an adjacency matrix.
    """
    with open(file_path, 'r') as f:
        # Read the file and convert the string back to a list of tuples
        edges = eval(f.read().strip())

    num_nodes = max(max(edge) for edge in edges) + 1

    adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]

    for u, v in edges:
        adjacency_matrix[u][v] = 1
        adjacency_matrix[v][u] = 1  # Since the graph is undirected

    return adjacency_matrix
file_path = 'input/graph.txt'  # Update this to your file path
adj_matrix = read_edge_list(file_path)
n_qubits = len(adj_matrix)
beta_values = np.linspace(0, np.pi/2, 16)
gamma_values = np.linspace(0, np.pi, 8)
cost_hamiltonian = create_cost_hamiltonian(adj_matrix)

''"run by sampler'"
expectation_values = sampler_run(beta_values, gamma_values , n_qubits, cost_hamiltonian, adj_matrix)
''"run by estimator'"
#expectation_values = estimator_run(beta_values, gamma_values , n_qubits, cost_hamiltonian)
generate_heatmap(expectation_values)
optimal_beta, optimal_gamma = calculate_best_cut(expectation_values, beta_values, gamma_values, cost_hamiltonian, adj_matrix)
generate_energy_histogram(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian, adj_matrix)