import os
import matplotlib.pyplot as plt
import numpy as np
from qiskit_aer import AerSimulator
from qaoa_circuit import qaoa_circuit


def compute_energy(bitstring, G, A=0):

    energy = 0.0
    if G.edges():
        A = max(G.nodes[u].get("weight", 1.0) + G.nodes[v].get("weight", 1.0) for u, v in G.edges())
    else:
        A = 0

    # First term: Vertex contributions
    for i in G.nodes():
        weight = G.nodes[i].get("weight", 1.0)
        z_val = 1 if bitstring[i] == '0' else -1
        energy += - (weight / 2.0) * (z_val + 1)
    # Second term: Edge penalty contributions
    for (i, j) in G.edges():
        z_i = 1 if bitstring[i] == '0' else -1
        z_j = 1 if bitstring[j] == '0' else -1
        energy += A * (1 + z_i) * (1 + z_j)

    return energy


def generate_mwis_histogram(optimal_params_list, n_qubits, cost_hamiltonian, G, A=10):
    simulator = AerSimulator()

    # -- 1. Run QAOA circuits and gather measured bitstrings --
    qaoa_results = []
    labels = []
    for i, (optimal_beta, optimal_gamma) in enumerate(optimal_params_list):
        print(f"QAOA {i + 1}: beta={optimal_beta}, gamma={optimal_gamma}")
        optimal_circuit = qaoa_circuit(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian)
        optimal_circuit.measure_all()
        result = simulator.run(optimal_circuit, shots=1024).result()
        counts = result.get_counts()

        # Collect energies for this QAOA run
        energies = []
        for bitstring, freq in counts.items():
            energy = compute_energy(bitstring, G, A)
            if energy <= 50:
                energies.extend([energy] * freq)

        qaoa_results.append((counts, energies))
        labels.append(f"QAOA p = {i + 1}")

    # Generate random samples for comparison
    num_random_samples = 1024
    random_energies = []
    for _ in range(num_random_samples):
        random_bitstring = "".join(str(x) for x in np.random.choice([0, 1], size=n_qubits))
        energy = compute_energy(random_bitstring, G, A)
        if energy <= 50:
            random_energies.append(energy)

    # -- 2. Plot histogram (Multiple QAOA vs. Random Sampling) --
    plt.figure(figsize=(12, 6))
    colors = ['blue', 'green']  # Extend this list if you have more parameter sets

    # Plot histograms for QAOA runs
    for i, (_, energies) in enumerate(qaoa_results):
        plt.hist(energies, bins=200, alpha=0.7, label=labels[i],
                 edgecolor='k', color=colors[i % len(colors)])
    # Plot histogram for random sampling
    plt.hist(random_energies, bins=200, alpha=0.7, label="Random Sampling",
             edgecolor='k', color='red')

    # -- 3. Add dashed lines for the mean energies --
    # Mean energy for random sampling
    random_mean = np.mean(random_energies)
    plt.axvline(random_mean, color='red', linestyle='--', linewidth=2,
                label=f'Random Mean: {random_mean:.2f}')
    # Mean energies for each QAOA run
    for i, (_, energies) in enumerate(qaoa_results):
        qaoa_mean = np.mean(energies)
        plt.axvline(qaoa_mean, color=colors[i % len(colors)], linestyle='--', linewidth=2,
                    label=f'QAOA p = {i+1} Mean: {qaoa_mean:.2f}')

    plt.xlabel("Energy")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)

    folder = "output/graph"
    os.makedirs(folder, exist_ok=True)
    filename = "energy_distribution_cobyla.png"
    filepath = os.path.join(folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    # -- 4. Build stacked bar charts for each QAOA run --
    for idx, (counts, _) in enumerate(qaoa_results):
        # Dictionary: {energy: {bitstring: frequency}}
        energy_dict = {}
        for bitstring, freq in counts.items():
            energy = compute_energy(bitstring, G, A)
            if energy is not None and energy <= 50:
                energy_dict.setdefault(energy, {})
                energy_dict[energy][bitstring] = energy_dict[energy].get(bitstring, 0) + freq

        # Sort energies for x-axis and collect unique bitstrings
        sorted_energies = sorted(energy_dict.keys())
        all_bitstrings = sorted(set(bs for energy in energy_dict for bs in energy_dict[energy]))

        x_positions = np.arange(len(sorted_energies))
        width = 0.8
        bottoms = np.zeros(len(sorted_energies))

        # -- 5. Create a stacked bar chart --
        plt.figure(figsize=(12, 6))
        for bitstring in all_bitstrings:
            fractions = []
            for energy in sorted_energies:
                freq_for_bs = energy_dict[energy].get(bitstring, 0)
                total_freq = sum(energy_dict[energy].values())
                fraction = freq_for_bs / total_freq if total_freq > 0 else 0
                fractions.append(fraction)
            plt.bar(x_positions, fractions, width, bottom=bottoms, label=bitstring)
            bottoms += np.array(fractions)

        plt.xticks(x_positions, sorted_energies)
        plt.xlabel("Energy")
        plt.ylabel("Fraction of Measurements")
        plt.title(f"Stacked Energy Distribution (QAOA p = {idx + 1})")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')
        plt.tight_layout()

        filename_stacked = f"energy_distribution_stacked_qaoa_{idx + 1}.png"
        filepath_stacked = os.path.join(folder, filename_stacked)
        plt.savefig(filepath_stacked, dpi=300, bbox_inches='tight')
        plt.close()

