from qiskit import QuantumCircuit
from qiskit.circuit.library import RZZGate
import numpy as np

def qaoa_circuit(betas, gammas, n_qubits, bqm):
    if len(betas) != len(gammas):
        raise ValueError("The number of beta and gamma parameters must be the same.")

    circuit = QuantumCircuit(n_qubits)
    circuit.h(range(n_qubits))  # Apply Hadamard gates

    for beta, gamma in zip(betas, gammas):
        # Apply Cost Hamiltonian evolution
        for qubit, coeff in bqm.linear.items():
            circuit.rz(2 * gamma * coeff, qubit)

        for (i, j), coeff in bqm.quadratic.items():
            circuit.append(RZZGate(2 * gamma * coeff), [i, j])

        # Apply Mixer Hamiltonian evolution
        for qubit in range(n_qubits):
            circuit.rx(2 * beta, qubit)
    return circuit

