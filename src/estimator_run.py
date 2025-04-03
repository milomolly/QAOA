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


def qaoa_cost_function(params, n_qubits, p, cost_hamiltonian):
    beta = params[:p]
    gamma = params[p:]
    qc = qaoa_circuit(beta, gamma, n_qubits, cost_hamiltonian)
    # Wrap input properly as a tuple
    job = estimator.run([qc], [bqm_to_pauli_sumop(cost_hamiltonian)])
    results = job.result().values[0]

    return results
def estimator_run_qaoa(n_qubits, p, cost_hamiltonian):
    initial_beta = np.random.uniform(0, np.pi, p)
    initial_gamma = np.random.uniform(0, 2 * np.pi, p)
    initial_params = np.concatenate([initial_beta, initial_gamma])

    result = minimize(
        qaoa_cost_function,
        initial_params,
        args=(n_qubits, p, cost_hamiltonian),
        method='COBYLA',
        options={'maxiter': 200, 'disp': True}
    )

    optimal_beta = result.x[:p]
    optimal_gamma = result.x[p:]

    return optimal_beta, optimal_gamma, result.fun

def estimator_run_qaoa_grid(n_qubits, p, cost_hamiltonian, grid_resolution=16):
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
            cost = qaoa_cost_function(params, n_qubits, p, cost_hamiltonian)
            print(cost)
            if cost < best_cost:
                best_cost = cost
                best_beta = beta
                best_gamma = gamma
    sampler = dimod.ExactSolver()
    sampleset = sampler.sample(cost_hamiltonian)
    best_sample = sampleset.first.sample
    best_energy = sampleset.first.energy

    print("\nBest sample (bitstring with lowest energy):")
    print(best_sample)
    print("Best energy:")
    print(best_energy)
    return np.array(best_beta), np.array(best_gamma), best_cost
