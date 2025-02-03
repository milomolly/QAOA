from qiskit_aer import AerSimulator
from src.qaoa_circuit import qaoa_circuit
from qiskit.primitives import Estimator
import numpy as np


def estimator_run(beta_values, gamma_values , n_qubits, cost_hamiltonian):
    simulator = AerSimulator()
    estimator = Estimator()
    expectation_values = np.zeros((len(beta_values), len(gamma_values)))
    for i, beta in enumerate(beta_values):
        for j, gamma in enumerate(gamma_values):
            qc = qaoa_circuit(beta, gamma, n_qubits, cost_hamiltonian)
            expectation = estimator.run([qc], [cost_hamiltonian]).result().values[0]
            expectation_values[i, j] = expectation
    return expectation_values