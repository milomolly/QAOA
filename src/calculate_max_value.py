from qiskit_aer import AerSimulator
from qaoa_circuit import qaoa_circuit
import numpy as np
from generate_chart import generate_distribution


def calculate_max_value(optimal_beta, optimal_gamma, cost_hamiltonian, G,
                        output_file="output/best_mwis.txt"):
    with open(output_file, "w") as f:
        # Find optimal parameters (assuming minimization of expectation value)
        # optimal_indices = np.unravel_index(np.argmin(expectation_values), expectation_values.shape)

        simulator = AerSimulator()
        n_qubits = len(G.nodes())

        # Case 1: 4D expectation_values (two sets of beta and gamma)
        # if len(optimal_indices) == 4:
        #     best_beta1_idx, best_gamma1_idx, best_beta2_idx, best_gamma2_idx = optimal_indices
        #     optimal_beta = [beta_values[best_beta1_idx], beta_values[best_beta2_idx]]
        #     optimal_gamma = [gamma_values[best_gamma1_idx], gamma_values[best_gamma2_idx]]
        #
        #     f.write(f"Optimal beta 1: {optimal_beta[0] / np.pi:.4f}π\n")
        #     f.write(f"Optimal gamma 1: {optimal_gamma[0] / np.pi:.4f}π\n")
        #     f.write(f"Optimal beta 2: {optimal_beta[1] / np.pi:.4f}π\n")
        #     f.write(f"Optimal gamma 2: {optimal_gamma[1] / np.pi:.4f}π\n")
        #
        # # Case 2: 2D expectation_values (one set of beta and gamma)
        # elif len(optimal_indices) == 2:
        #     best_beta1_idx, best_gamma1_idx = optimal_indices
        #     optimal_beta = [beta_values[best_beta1_idx]]
        #     optimal_gamma = [gamma_values[best_gamma1_idx]]
        #
        #     f.write(f"Optimal beta: {optimal_beta[0] / np.pi:.4f}π\n")
        #     f.write(f"Optimal gamma: {optimal_gamma[0] / np.pi:.4f}π\n")
        #
        # else:
        #     raise ValueError("Unexpected number of indices in optimal_indices")

        # Generate QAOA circuit with the optimal parameters
        optimal_circuit = qaoa_circuit(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian)

        # Measure all qubits and run the circuit
        optimal_circuit.measure_all()
        result = simulator.run(optimal_circuit, shots=1024).result()
        counts = result.get_counts()

        # Choose the bitstring that appears most frequently
        best_bitstring = max(counts, key=counts.get)
        f.write(f"Best bitstring: {best_bitstring}\n")

        def calculate_mwis_value(bitstring, graph, selected_bit):
            """
            Calculate the total weight for vertices selected (based on selected_bit) and
            return None if the independent set constraint is violated.
            """
            total_weight = 0
            for node in graph.nodes():
                if bitstring[node] == selected_bit:
                    total_weight += graph.nodes[node].get("weight", 1.0)
            # Verify the independent set constraint:
            for i, j in graph.edges():
                if bitstring[i] == selected_bit and bitstring[j] == selected_bit:
                    return None  # Invalid: adjacent vertices are both selected
            return total_weight

        # Compute total weights for both interpretations
        value_for_0 = calculate_mwis_value(best_bitstring, G, '0')
        value_for_1 = calculate_mwis_value(best_bitstring, G, '1')

        # Compare and choose the interpretation with the larger total weight
        if value_for_0 is None and value_for_1 is None:
            f.write("The best bitstring does not represent a valid independent set under either interpretation.\n")
        elif value_for_0 is None:
            f.write(f"Interpreting bit '1' as selected, maximum independent set value: {value_for_1}\n")
        elif value_for_1 is None:
            f.write(f"Interpreting bit '0' as selected, maximum independent set value: {value_for_0}\n")
        else:
            if value_for_0 >= value_for_1:
                f.write(f"Interpreting bit '0' as selected, maximum independent set value: {value_for_0}\n")
            else:
                f.write(f"Interpreting bit '1' as selected, maximum independent set value: {value_for_1}\n")

        total_frequency = sum(counts.values())
        f.write(f"Total frequency: {total_frequency}\n")

        # Generate the appropriate distribution chart
        # if len(optimal_indices) == 4:
        #     generate_distribution(counts, "distribution2")  # For two sets of parameters
        #     f.write("Distribution_2 chart generated successfully.\n")
        # else:  # len(optimal_indices) == 2
        generate_distribution(counts, "distribution")  # For one set of parameters
        f.write("Distribution chart generated successfully.\n")

        return optimal_beta, optimal_gamma


# Placeholder for generate_distribution_2 (to be implemented)
def generate_distribution_2(counts):
    """
    Generate a distribution chart for the case with two sets of optimal parameters.
    This could be similar to generate_mwis_histogram from the previous response.
    """
    # Example: You could adapt generate_mwis_histogram here or define a simpler version
    pass
