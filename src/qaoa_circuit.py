from qiskit import QuantumCircuit


def qaoa_circuit(beta, gamma, n_qubits, cost_hamiltonian):

    circuit = QuantumCircuit(n_qubits)
    circuit.h(range(n_qubits))

    for pauli, coeff in zip(cost_hamiltonian.paulis, cost_hamiltonian.coeffs):
        # Get the label; note the string ordering is assumed consistent with how the Hamiltonian was built.
        label = pauli.to_label()
        # Find which qubits have a non-identity (i.e. "Z") operator.
        qubits = [i for i, p in enumerate(label) if p == "Z"]

        if len(qubits) == 0:
            # This is an identity term; can be ignored since it only contributes a global phase.
            continue
        elif len(qubits) == 1:
            # For a single-qubit Z term, the unitary exp(-i*gamma*coeff*Z) is implemented as RZ(2*gamma*coeff)
            circuit.rz(2 * gamma * coeff.real, qubits[0])
        elif len(qubits) == 2:
            # For a two-qubit ZZ term, apply the RZZ gate.
            circuit.rzz(2 * gamma * coeff.real, qubits[0], qubits[1])
        else:
            # In case of unexpected multi-qubit terms, one could extend this section.
            raise ValueError("Unsupported term with more than 2 qubits in the cost Hamiltonian.")

    # Mixer: Apply RX rotations to each qubit.
    for qubit in range(n_qubits):
        circuit.rx(2 * beta, qubit)

    return circuit
