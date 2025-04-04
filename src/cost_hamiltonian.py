import dimod
import networkx as nx
from qiskit.quantum_info import Pauli, SparsePauliOp


def create_cost_hamiltonian_mwis(G):

    nodes = list(G.nodes())
    linear = {}
    quadratic = {}

    # Linear terms from vertex weights
    for node in nodes:
        weight = G.nodes[node].get("weight", 1.0)  # Default weight is 1.0 if not specified.
        linear[node] = -weight / 2.0  # -w_i/2 * Z_i

    # Compute penalty A as the maximum sum of weights for any edge
    if G.edges():
        A = max(G.nodes[u].get("weight", 1.0) + G.nodes[v].get("weight", 1.0) for u, v in G.edges())
    else:
        A = 0

    # Quadratic terms from edges
    for u, v in G.edges():
        quadratic[(u, v)] = A / 4  # (A/4) * Z_u * Z_v

        # Adjust linear biases due to additional terms
        linear[u] += A / 4
        linear[v] += A / 4

    # Create the BQM model
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, offset=0, vartype=dimod.SPIN)

    return bqm
def bqm_to_pauli_sumop(bqm):
    n = len(bqm.variables)
    var_index = {var: i for i, var in enumerate(bqm.variables)}

    terms = []
    # Linear terms: hi * Zi
    for var, bias in bqm.linear.items():
        pauli_str = ['I'] * n
        pauli_str[var_index[var]] = 'Z'
        pauli_label = ''.join(pauli_str)
        terms.append((bias, Pauli(pauli_label)))

    # Quadratic terms: Jij * Zi * Zj
    for (u, v), bias in bqm.quadratic.items():
        pauli_str = ['I'] * n
        pauli_str[var_index[u]] = 'Z'
        pauli_str[var_index[v]] = 'Z'
        pauli_label = ''.join(pauli_str)
        terms.append((bias, Pauli(pauli_label)))

    # Handle offset if nonzero by adding an identity term.
    if hasattr(bqm, 'offset') and bqm.offset != 0:
        identity_label = 'I' * n
        terms.append((bqm.offset, Pauli(identity_label)))

    # Convert to PauliSumOp. Note: Each tuple is (pauli_str, coefficient)
    return SparsePauliOp.from_list([(p.to_label(), c) for c, p in terms])