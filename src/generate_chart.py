import matplotlib.pyplot as plt
import os


def generate_heatmap(expectation_values, folder="output/graph", filename="heatmap.png"):
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)
    # Full path to save the file
    filepath = os.path.join(folder, filename)
    # Generate the heatmap and save it
    plt.figure(figsize=(16, 8))
    plt.xlabel(r"$\gamma / \pi$")
    plt.ylabel(r"$\beta / \pi$")
    plt.imshow(expectation_values, aspect='auto', origin='lower',
               extent=[0, 2, 0, 1], cmap='RdYlBu')
    plt.colorbar(label=r"$\langle \beta, \gamma | C | \beta, \gamma \rangle$")
    plt.title("QAOA Cost Hamiltonian Expectation Values")
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

def generate_distribution(counts, folder="output/graph", filename="distribution.png"):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    plt.figure(figsize=(12, 6))
    plt.bar(counts.keys(), counts.values())
    plt.xlabel("Bitstring")
    plt.ylabel("Frequency")
    plt.title("Measurement Outcomes for the Optimal QAOA Circuit")
    plt.xticks(rotation=90)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
