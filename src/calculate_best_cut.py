from qiskit_aer import AerSimulator
from qaoa_circuit import qaoa_circuit
import numpy as np
from generate_chart import generate_distribution


def calculate_best_cut(expectation_values, beta_values, gamma_values, cost_hamiltonian, adj_matrix,
                       output_file="output/bestcut.txt"):
    with open(output_file, "w") as f:
        optimal_indices = np.unravel_index(np.argmin(expectation_values), expectation_values.shape)
        optimal_beta = beta_values[optimal_indices[0]]
        optimal_gamma = gamma_values[optimal_indices[1]]
        simulator = AerSimulator()
        n_qubits = len(adj_matrix)

        f.write(f"Optimal beta: {optimal_beta / np.pi:.4f}π\n")
        f.write(f"Optimal gamma: {optimal_gamma / np.pi:.4f}π\n")

        optimal_circuit = qaoa_circuit(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian)

        optimal_circuit.measure_all()
        result = simulator.run(optimal_circuit, shots=1024).result()
        counts = result.get_counts()

        best_bitstring = max(counts, key=counts.get)
        f.write(f"Best bitstring: {best_bitstring}\n")

        def calculate_cut_value(bitstring, G):
            cut_value = 0
            # Iterate over each edge in the graph
            for i, j in G.edges():
                # If the bits for the connected nodes differ, increment the cut value.
                if bitstring[i] != bitstring[j]:
                    cut_value += 1
            return cut_value

        best_cut_value = calculate_cut_value(best_bitstring, adj_matrix)
        f.write(f"Best cut value: {best_cut_value}\n")
        total_frequency = sum(counts.values())
        f.write(f"Total frequency: {total_frequency}\n")
        generate_distribution(counts)
        f.write("Distribution chart generated successfully.\n")
        return optimal_beta, optimal_gamma
