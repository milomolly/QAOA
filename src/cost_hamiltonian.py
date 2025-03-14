from qiskit.quantum_info import SparsePauliOp


def create_cost_hamiltonian(G):
    nodes = list(G.nodes())
    n = len(nodes)
    # Map each node to a qubit index
    index_map = {node: idx for idx, node in enumerate(nodes)}
    terms = []

    # 1. Vertex terms: for each vertex, add -w_i/2*(Z_i + I)
    for node in nodes:
        weight = G.nodes[node].get("weight", 1.0)  # Default weight is 1.0 if not specified.
        # Term for Z_i with coefficient -w_i/2
        pauli_list = ["I"] * n
        pauli_list[index_map[node]] = "Z"
        pauli_str = "".join(pauli_list[::-1])
        terms.append((pauli_str, -weight / 2))

        # Identity term with coefficient -w_i/2
        id_str = "I" * n
        terms.append((id_str, -weight / 2))

    # Compute penalty A as the maximum sum of weights for any edge (u,v)
    if G.edges():
        A = max(G.nodes[u].get("weight", 1.0) + G.nodes[v].get("weight", 1.0) for u, v in G.edges())
    else:
        A = 0

    # 2. Edge terms: for each edge, add penalty terms using the computed A
    for u, v in G.edges():
        # Identity term: coefficient A/4
        id_str = "I" * n
        terms.append((id_str, A / 4))

        # Term for Z_u: coefficient A/4
        pauli_list = ["I"] * n
        pauli_list[index_map[u]] = "Z"
        pauli_str = "".join(pauli_list[::-1])
        terms.append((pauli_str, A / 4))

        # Term for Z_v: coefficient A/4
        pauli_list = ["I"] * n
        pauli_list[index_map[v]] = "Z"
        pauli_str = "".join(pauli_list[::-1])
        terms.append((pauli_str, A / 4))

        # Term for Z_u Z_v: coefficient A/4
        pauli_list = ["I"] * n
        pauli_list[index_map[u]] = "Z"
        pauli_list[index_map[v]] = "Z"
        pauli_str = "".join(pauli_list[::-1])
        terms.append((pauli_str, A / 4))

    return SparsePauliOp.from_list(terms)

