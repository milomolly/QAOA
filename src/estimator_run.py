from itertools import product

import dimod
import numpy as np
from scipy.optimize import minimize
from qiskit_aer import AerSimulator
from src.qaoa_circuit import qaoa_circuit
from qiskit.primitives import Estimator
from cost_hamiltonian import bqm_to_pauli_sumop
simulator = AerSimulator()

estimator = Estimator()


def qaoa_cost_function(params, n_qubits, p, cost_mwis):
    beta = params[:p]
    gamma = params[p:]
    qc = qaoa_circuit(beta, gamma, n_qubits, cost_mwis)
    # Wrap input properly as a tuple
    job = estimator.run([qc], [bqm_to_pauli_sumop(cost_mwis)])
    results = job.result().values[0]

    return results
def estimator_run_qaoa(n_qubits, p, cost_mwis):
    initial_beta = np.random.uniform(0, np.pi, p)
    initial_gamma = np.random.uniform(0, 2 * np.pi, p)
    initial_params = np.concatenate([initial_beta, initial_gamma])

    result = minimize(
        qaoa_cost_function,
        initial_params,
        args=(n_qubits, p, cost_mwis),
        method='COBYLA',
        tol=1e-4
    )

    optimal_beta = result.x[:p]
    optimal_gamma = result.x[p:]

    return optimal_beta, optimal_gamma, result.fun

def estimator_run_qaoa_grid(n_qubits, p, cost_mwis, grid_resolution=16):
    beta_range = np.linspace(0, np.pi, grid_resolution)
    gamma_range = np.linspace(0, 2 * np.pi, grid_resolution * 2 )

    best_cost = float('inf')
    best_beta = None
    best_gamma = None

    # Create a grid over all beta and gamma combinations
    beta_grid = list(product(beta_range, repeat=p))
    gamma_grid = list(product(gamma_range, repeat=p))

    for beta in beta_grid:
        for gamma in gamma_grid:
            params = np.concatenate([beta, gamma])
            cost = qaoa_cost_function(params, n_qubits, p, cost_mwis)
            if cost < best_cost:
                best_cost = cost
                best_beta = beta
                best_gamma = gamma

    return np.array(best_beta), np.array(best_gamma), best_cost
