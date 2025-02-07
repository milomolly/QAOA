from qiskit_aer import AerSimulator
from src.qaoa_circuit import qaoa_circuit
from qiskit_ibm_runtime import SamplerV2 as Sampler
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error
def calculate_state_cost(bitstring, adj_matrix):
    """Calculate the cost for a specific bitstring state."""
    n = len(adj_matrix)
    cost = 0
    state = [int(bit) for bit in bitstring]

    z_values = [1 - 2 * bit for bit in state]

    for i in range(n):
        for j in range(i + 1, n):
            if adj_matrix[i][j] == 1:
                cost += z_values[i] * z_values[j]

    return cost

def calculate_expectation_value(counts, adj_matrix):
    """Calculate the expectation value of the cost Hamiltonian from measurement counts."""
    total_cost = 0
    total_shots = sum(counts.values())

    for bitstring, count in counts.items():
        state_cost = calculate_state_cost(bitstring, adj_matrix)
        total_cost += state_cost * count

    return total_cost / total_shots

def sampler_run(beta_values, gamma_values , n_qubits, cost_hamiltonian, adj_matrix):
    noise_model = NoiseModel()

    single_qubit_error = depolarizing_error(0.8, 1)
    two_qubit_error = depolarizing_error(0.8, 2)

    noise_model.add_all_qubit_quantum_error(single_qubit_error, ["h", "rx", "rz"])
    noise_model.add_all_qubit_quantum_error(two_qubit_error, ["cx", "rzz"])
    simulator = AerSimulator(noise_model=noise_model)
    sampler = Sampler(mode=simulator)
    expectation_values = np.zeros((len(beta_values), len(gamma_values)))
    for i, beta in enumerate(beta_values):
        for j, gamma in enumerate(gamma_values):
            qc = qaoa_circuit(beta, gamma, n_qubits, cost_hamiltonian)
            qc.measure_all()
            result = sampler.run([qc]).result()
            counts = result[0].data.meas.get_counts()
            expectation_values[i, j] = calculate_expectation_value(counts, adj_matrix)

    return expectation_values