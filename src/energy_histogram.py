import os

import matplotlib.pyplot as plt
import numpy as np
from qiskit_aer import AerSimulator

from src.qaoa_circuit import qaoa_circuit


def calculate_cut_value(bitstring, adj_matrix):
    """Calculate the Max-Cut value for a given bitstring."""
    cut_value = 0
    for i in range(len(adj_matrix)):
        for j in range(i + 1, len(adj_matrix)):
            if adj_matrix[i][j] == 1 and bitstring[i] != bitstring[j]:
                cut_value -= 1
    return cut_value


def generate_energy_histogram(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian, adj_matrix):
    simulator = AerSimulator()
    optimal_circuit = qaoa_circuit(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian)
    optimal_circuit.measure_all()
    result = simulator.run(optimal_circuit, shots=1024).result()
    counts = result.get_counts()
    qaoa_energies = []
    for bitstring, freq in counts.items():
        energy = calculate_cut_value(bitstring, adj_matrix)
        qaoa_energies.extend([energy] * freq)

    """ generate random sample ( -1,1 for each spin ) """
    num_random_samples = 1024
    random_energies = []
    for _ in range(num_random_samples):
        random_bitstring = np.random.choice([0, 1], size=n_qubits)
        random_energies.append(calculate_cut_value(random_bitstring, adj_matrix))

    plt.figure(figsize=(12, 6))
    plt.hist(qaoa_energies, bins=20, alpha=0.7, label="QAOA Optimal Parameters", edgecolor='k', color='blue')
    plt.hist(random_energies, bins=20, alpha=0.7, label="Random Sampling", edgecolor='k', color='red')

    plt.xlabel("Energy (Cut Value)")
    plt.ylabel("Frequency")
    plt.title("Comparison of Energy Distribution: QAOA vs. Random Sampling")
    plt.legend()
    plt.grid(True)
    folder = "output/graph"
    filename = "energy_histogram.png"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
