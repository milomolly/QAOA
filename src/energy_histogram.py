import os
import matplotlib.pyplot as plt
import numpy as np
from qiskit_aer import AerSimulator
from qaoa_circuit import qaoa_circuit

def calculate_mwis_value_dual(bitstring, G):
    """
    Calculate the MWIS value for a given bitstring under both interpretations:
      - Interpreting bit '0' as the vertex being selected.
      - Interpreting bit '1' as the vertex being selected.
    Return the larger valid total weight or None if both are invalid.
    """
    def calc_value(bitstr, selected_bit):
        total_weight = 0
        valid = True
        for node in G.nodes():
            if bitstr[node] == selected_bit:
                total_weight += G.nodes[node].get("weight", 1.0)
        # Check the independent set constraint.
        for i, j in G.edges():
            if bitstr[i] == selected_bit and bitstr[j] == selected_bit:
                valid = False
                break
        return total_weight if valid else None

    value0 = calc_value(bitstring, '0')
    value1 = calc_value(bitstring, '1')

    if value0 is None and value1 is None:
        return None
    elif value0 is None:
        return value1
    elif value1 is None:
        return value0
    else:
        return max(value0, value1)


def generate_mwis_histogram(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian, G):
    """
    1) Generate a histogram comparing MWIS values (QAOA vs random sampling).
    2) Additionally generate a stacked bar chart showing the fractional contribution
       of each bitstring to each MWIS value bin.
    """
    # -- 1. Run QAOA circuit and gather measured bitstrings --
    simulator = AerSimulator()
    optimal_circuit = qaoa_circuit(optimal_beta, optimal_gamma, n_qubits, cost_hamiltonian)
    optimal_circuit.measure_all()
    result = simulator.run(optimal_circuit, shots=1024).result()
    counts = result.get_counts()

    # Collect MWIS values for QAOA
    qaoa_values = []
    for bitstring, freq in counts.items():
        value = calculate_mwis_value_dual(bitstring, G)
        if value is not None:
            # Extend the list by freq times
            qaoa_values.extend([value] * freq)

    # Generate random samples for comparison
    num_random_samples = 1024
    random_values = []
    for _ in range(num_random_samples):
        random_bitstring = "".join(str(x) for x in np.random.choice([0, 1], size=n_qubits))
        value = calculate_mwis_value_dual(random_bitstring, G)
        if value is not None:
            random_values.append(value)

    # -- 2. Plot histogram (QAOA vs. Random Sampling) --
    plt.figure(figsize=(12, 6))
    plt.hist(qaoa_values, bins=20, alpha=0.7, label="QAOA Optimal Parameters",
             edgecolor='k', color='blue')
    plt.hist(random_values, bins=20, alpha=0.7, label="Random Sampling",
             edgecolor='k', color='red')
    plt.xlabel("MWIS Value (Total Weight)")
    plt.ylabel("Frequency")
    plt.title("Comparison of MWIS Value Distribution: QAOA vs. Random Sampling")
    plt.legend()
    plt.grid(True)

    folder = "output/graph"
    filename = "mwis_histogram.png"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    # -- 3. Build data for stacked bar chart of bitstring contributions --
    # Dictionary of {mwis_value: {bitstring: freq}}
    mwis_dict = {}
    for bitstring, freq in counts.items():
        mw_value = calculate_mwis_value_dual(bitstring, G)
        if mw_value is not None:
            mwis_dict.setdefault(mw_value, {})
            mwis_dict[mw_value][bitstring] = mwis_dict[mw_value].get(bitstring, 0) + freq

    # Sort MWIS values for x-axis
    unique_mw_values = sorted(mwis_dict.keys())

    # Gather all unique bitstrings across all MWIS values
    all_bitstrings = set()
    for mwv in mwis_dict:
        for bs in mwis_dict[mwv]:
            all_bitstrings.add(bs)
    all_bitstrings = sorted(all_bitstrings)  # for consistent ordering

    # Prepare for stacked bar
    x_positions = np.arange(len(unique_mw_values))
    width = 0.8
    bottoms = np.zeros(len(unique_mw_values))

    # -- 4. Create a stacked bar chart with fraction of each bitstring in that MWIS bin --
    plt.figure(figsize=(12, 6))
    # For each bitstring, build an array of fractions across all MWIS bins
    for bitstring in all_bitstrings:
        fraction_array = []
        for mwv in unique_mw_values:
            freq_for_bs = mwis_dict[mwv].get(bitstring, 0)
            total_freq = sum(mwis_dict[mwv].values())
            fraction = freq_for_bs / total_freq if total_freq > 0 else 0
            fraction_array.append(fraction)

        plt.bar(x_positions, fraction_array, width, bottom=bottoms, label=bitstring)
        bottoms += fraction_array

    plt.xticks(x_positions, unique_mw_values)
    plt.xlabel("MWIS Value (Total Weight)")
    plt.ylabel("Fraction of Measurements in Bin")
    plt.title("Fraction of Each Bitstring per MWIS Value Bin")

    # If you have many distinct bitstrings, the legend can be huge; consider limiting the top K bitstrings or
    # removing the legend. For now, we include it.
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')
    plt.tight_layout()

    filename_stacked = "mwis_bitstring_fractions.png"
    filepath_stacked = os.path.join(folder, filename_stacked)
    plt.savefig(filepath_stacked, dpi=300, bbox_inches='tight')
    plt.close()
