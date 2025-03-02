from qiskit import QuantumCircuit

def qaoa_circuit(beta, gamma, n_qubits, cost_hamiltonian):
    """Create the QAOA circuit."""
    circuit = QuantumCircuit(n_qubits)
    circuit.h(range(n_qubits))
    for pauli, coeff in zip(cost_hamiltonian.paulis, cost_hamiltonian.coeffs):
        print(pauli, coeff)
        qubits = [i for i, p in enumerate(pauli.to_label()) if p == "Z"]
        if len(qubits) == 2:
            circuit.rzz(2 * gamma * coeff.real, qubits[0], qubits[1])
    for qubit in range(n_qubits):
        circuit.rx(2 * beta, qubit)
    return circuit