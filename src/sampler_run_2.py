from itertools import product

from qiskit.circuit.library import QAOAAnsatz
from qiskit_aer import AerSimulator
from qaoa_circuit import qaoa_circuit
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error


def calculate_state_cost(bitstring, G):
    """
    Calculate the cost for a specific bitstring state using a NetworkX graph G.
    Assumes nodes are labeled 0, 1, ..., n-1.
    """
    cost = 0
    state = [int(bit) for bit in bitstring]
    # Convert state bits to z-values: bit 0 -> +1 and bit 1 -> -1.
    z_values = [1 - 2 * bit for bit in state]

    # For each edge in the graph, multiply the corresponding z-values.
    for i, j in G.edges():
        cost += z_values[i] * z_values[j]

    return cost

def calculate_expectation_value(counts, adj_matrix):
    total_cost = 0
    total_shots = sum(counts.values())

    for bitstring, count in counts.items():
        state_cost = calculate_state_cost(bitstring, adj_matrix)
        total_cost += state_cost * count

    return total_cost / total_shots

def sampler_run_2(beta_values, gamma_values , n_qubits, cost_hamiltonian, adj_matrix):
    noise_model = NoiseModel()

    # single_qubit_error = depolarizing_error(0.8, 1)
    # two_qubit_error = depolarizing_error(0.8, 2)
    #
    # noise_model.add_all_qubit_quantum_error(single_qubit_error, ["h", "rx", "rz"])
    # noise_model.add_all_qubit_quantum_error(two_qubit_error, ["cx", "rzz"])
    simulator = AerSimulator()
    expectation_values = np.zeros((len(beta_values), len(gamma_values)))
    # simulator = AerSimulator(noise_model=noise_model)
    sampler = Sampler(mode=simulator)
    circuits = []

    for beta in beta_values:
        for gamma in gamma_values:
            qc = qaoa_circuit([beta], [gamma], n_qubits, cost_hamiltonian)
            qc.measure_all()
            circuits.append(qc)
            #expectation_values[i, j] = calculate_expectation_value(counts, adj_matrix)
    result = sampler.run(circuits).result()
    print(result)
    cnt = 0
    for i in range(0,len(beta_values)):
        for j in range(0,len(gamma_values)):
            counts = result[cnt].data.meas.get_counts()
            cnt += 1
            expectation_values[i, j] = calculate_expectation_value(counts, adj_matrix)

    return expectation_values