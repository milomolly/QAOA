import matplotlib.pyplot as plt
import os

from qiskit.primitives import Estimator
from qiskit_aer import AerSimulator

from src.qaoa_circuit import qaoa_circuit


def generate_heatmap(expectation_values, folder="output/graph", filename="heatmap.png"):
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)
    # Full path to save the file
    filepath = os.path.join(folder, filename)
    # Generate the heatmap and save it
    plt.figure(figsize=(16, 8))
    plt.xlabel(r"$\gamma / \pi$")
    plt.ylabel(r"$\beta / \pi$")
    plt.imshow(expectation_values, aspect='auto', origin='lower',
               extent=[0, 2, 0, 1], cmap='RdYlBu')
    plt.colorbar(label=r"$\langle \beta, \gamma | C | \beta, \gamma \rangle$")
    plt.title("QAOA Cost Hamiltonian Expectation Values")
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

def generate_distribution(counts,filename, folder="output/graph"):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    plt.figure(figsize=(12, 6))
    plt.bar(counts.keys(), counts.values())
    plt.xlabel("Bitstring")
    plt.ylabel("Frequency")
    plt.title("Measurement Outcomes for the Optimal QAOA Circuit")
    plt.xticks(rotation=90)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()


def draw_bitstring_distribution(n_qubits, optimal_beta, optimal_gamma, cost_hamiltonian, shots=1024):
    # Initialize the simulator.
    simulator = AerSimulator()

    # Build the QAOA circuit using optimal parameters.
    qc = qaoa_circuit(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian)
    qc.measure_all()  # Append measurement to all qubits.

    # Execute the circuit on the simulator.
    result = simulator.run(qc, shots=shots).result()
    counts = result.get_counts()

    # Plot the measurement distribution as a bar chart.
    plt.figure(figsize=(10, 6))
    bitstrings = list(counts.keys())
    frequencies = list(counts.values())
    max_bitstring = max(counts, key=counts.get)
    print("Bitstring with maximum frequency:", max_bitstring, "with count:", counts[max_bitstring])

    plt.bar(bitstrings, frequencies, color='blue', edgecolor='k')
    plt.xlabel("Bitstring")
    plt.ylabel("Frequency")
    plt.title("Bitstring Distribution")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()