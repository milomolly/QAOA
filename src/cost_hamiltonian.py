from qiskit.quantum_info import SparsePauliOp

def create_cost_hamiltonian(G):
    nodes = list(G.nodes())
    index_map = {node: idx for idx, node in enumerate(nodes)}
    n = len(nodes)
    terms = []
    for u, v in G.edges():
        pauli_list = ["I"] * n
        pauli_list[index_map[u]] = "Z"
        pauli_list[index_map[v]] = "Z"
        pauli_str = "".join(pauli_list[::-1])
        terms.append((pauli_str, 1.0))
    return SparsePauliOp.from_list(terms)