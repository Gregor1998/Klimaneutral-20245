import matplotlib.pyplot as plt
import pandas as pd
from utils import config

def plot_coverage_histogram(consumption_df, comparison_df, column_name, title, filename):
    # Prozentsätze definieren
    percentages = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

    # Dictionary, um die Anzahl der Viertelstunden für jeden Prozentsatz zu speichern
    coverage_counts = {percentage: 0 for percentage in percentages}

    # Berechne die Deckung für jede Viertelstunde
    for percentage in percentages:
        mask = comparison_df[column_name] >= percentage * consumption_df['Gesamtverbrauch']
        coverage_counts[percentage] += mask.sum()

    # Füge die Gesamtanzahl der Viertelstunden hinzu
    total_quarters = len(comparison_df)
    coverage_counts['Gesamtanzahl'] = total_quarters

    # Erstelle ein Summenhistogramm
    plt.figure(figsize=(12, 6))
    coverage_counts_str_keys = {str(key): value for key, value in coverage_counts.items()}
    bars = plt.bar(coverage_counts_str_keys.keys(), coverage_counts_str_keys.values(), width=0.10, align='center')

    # Annotate bars with percentage of total quarters
    for bar in bars:
        height = bar.get_height()
        percentage = (height / total_quarters) * 100
        plt.annotate(f'{percentage:.2f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom')

    plt.xlabel('Prozentsatz des Gesamtverbrauchs')
    plt.ylabel('Anzahl der Viertelstunden')
    plt.title(title)
    plt.xticks([str(key) for key in coverage_counts.keys()], rotation=45)
    plt.grid(True)
    plt.savefig(filename)
    plt.show()