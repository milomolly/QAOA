from qiskit.quantum_info import SparsePauliOp

def create_cost_hamiltonian(adj_matrix):
    n = len(adj_matrix)
    terms = []
    coeffs = []
    for i in range(n):
        for j in range(i + 1, n):
            if adj_matrix[i][j] == 1:
                z_i = ["I"] * n
                z_i[i] = "Z"
                z_i[j] = "Z"

                terms.append(("".join(z_i[::-1]), 1.0))
                coeffs.append(1.0)

    return SparsePauliOp.from_list(terms)