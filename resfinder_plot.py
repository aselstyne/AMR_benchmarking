import matplotlib.pyplot as plt
import pandas as pd
import os
from pathlib import Path
import src.amr_utility.name_utility as name_utility

# NICE PLOTS STUFF from ChatGPT
plt.rcParams.update({
    "font.size": 12,
})

species = ['Escherichia coli', 'Klebsiella pneumoniae', 'Acinetobacter baumannii',
           'Staphylococcus aureus', 'Pseudomonas aeruginosa']
species_drugs = []
all_resfinder_f1s = {}

# Open the resfinder results for each species
all_dataframes = []
for sp in species:
    file_path = name_utility.GETname_ResfinderResults(sp, "resfinder_b", "./") + ".csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, delimiter="\t", index_col=0)
        all_dataframes.append(df)
        # Get the list of drugs for this species
        drugs = df.index.tolist()
        for drug in drugs:
            species_drugs.append((sp, drug))
            all_resfinder_f1s[(sp, drug)] = (df.loc[drug, 'f1_macro'])
    else:
        print(f"Warning: {file_path} does not exist and will be skipped.")



chandar_df = pd.read_csv("chandar_best_results.csv")
chandar_data = {}
for index, row in chandar_df.iterrows():
    species_name = row['pathogen'].capitalize().replace('_', ' ')
    drug_name = row['antibiotic']
    f1_macro = row['mean_f1_macro']
    if (species_name, drug_name) not in all_resfinder_f1s:
        print(f"Warning: ({species_name}, {drug_name}) from Chandar data not found in ResFinder data.")
    else:
        chandar_data[(species_name, drug_name)] = f1_macro
        # Add a new column to the dataframe for ResFinder accuracy

easy = [('Acinetobacter baumannii', 'ciprofloxacin'), ('Klebsiella pneumoniae', 'tobramycin'), ('Staphylococcus aureus', 'erythromycin')]
med = [('Acinetobacter baumannii', 'ceftazidime'), ('Escherichia coli', 'cefotaxime'), ('Klebsiella pneumoniae', 'meropenem')]
hard = [('Escherichia coli', 'cefepime'), ('Pseudomonas aeruginosa', 'aztreonam'), ('Escherichia coli', 'imipenem')]

# Create bar charts for each of the easy, medium, and hard categories
# Include 2 bars per species-drug pair: one for Chandar et al. and one for ResFinder
categories = {'Easy': easy, 'Medium': med, 'Hard': hard}

for category, pairs in categories.items():
    plt.figure(figsize=(10, 6), dpi=300)  # high resolution (300 dpi)

    chandar_f1s = [chandar_data[pair] for pair in pairs]
    resfinder_f1s = [all_resfinder_f1s[pair] for pair in pairs]
    labels = [f"{pair[0].split()[0]}-{pair[1]}" for pair in pairs]
    x = range(len(pairs))

    # Bars
    plt.bar(x, chandar_f1s, width=0.4, label='Chandar',
            color='#ff6361', align='center')
    plt.bar([p + 0.42 for p in x], resfinder_f1s, width=0.4, label='ResFinder',
            color='#58508d', align='center')

    # Limits & labels
    plt.ylim(0, 1.05)
    plt.ylabel('F1 Macro', fontsize=14)
    plt.title(f'F1 Macro for {category} Cases', fontsize=16, fontweight='bold')

    # X ticks
    plt.xticks([p + 0.2 for p in x], labels, rotation=20, ha='right')

    # Value labels above bars
    for i, v in enumerate(chandar_f1s):
        plt.text(i, v + 0.025, f"{v:.2f}", ha='center', va='bottom', fontsize=10)
    for i, v in enumerate(resfinder_f1s):
        plt.text(i + 0.4, v + 0.025, f"{v:.2f}", ha='center', va='bottom', fontsize=10)

    # Legend
    plt.legend(frameon=True, fontsize=12)

    # Prettier grid (dashed, light gray)
    plt.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.7)

    # Tight layout to avoid cutoff
    plt.tight_layout()

    # Save high-quality PNG
    plt.savefig(f"{category.lower()}_cases_f1.png", dpi=300, bbox_inches="tight")
    print("Saved", f"{category.lower()}_cases_f1.png")