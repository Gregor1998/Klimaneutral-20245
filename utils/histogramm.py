"""
Histogram Utility for Energy Consumption Analysis
------------------------------------------------
This module provides functionality to visualize energy consumption coverage data using histograms.
It helps analyze how frequently renewable energy sources cover certain percentages of the total energy consumption.

The main function plot_coverage_histogram() creates a histogram showing how many quarter-hour intervals
achieve different coverage percentages of renewable energy compared to total consumption.
"""

import matplotlib.pyplot as plt
import pandas as pd
from utils import config

def plot_coverage_histogram(consumption_df, comparison_df, column_name, title, filename):
    """
    Creates a histogram showing how many quarter-hour intervals achieve different coverage percentages.
    
    Parameters:
    -----------
    consumption_df : DataFrame
        DataFrame containing the total consumption data
    comparison_df : DataFrame
        DataFrame containing the energy production/generation data to compare against consumption
    column_name : str
        Name of the column in comparison_df to compare against consumption
    title : str
        Title for the histogram
    filename : str
        Path where the histogram image will be saved
    """
    # Define coverage percentages to analyze (10% to 100%)
    percentages = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

    # Initialize dictionary to store the count of quarter-hour intervals for each coverage percentage
    coverage_counts = {percentage: 0 for percentage in percentages}

    # Calculate coverage for each quarter-hour interval at each percentage threshold
    for percentage in percentages:
        # Count intervals where the specified column exceeds the given percentage of total consumption
        mask = comparison_df[column_name] >= percentage * consumption_df['Gesamtverbrauch']
        coverage_counts[percentage] += mask.sum()

    # Store the total number of quarter-hour intervals for later calculations
    total_quarters = len(comparison_df)
    coverage_counts['Gesamtanzahl'] = total_quarters

    # Create and configure the histogram plot
    plt.figure(figsize=(12, 6))
    coverage_counts_str_keys = {str(key): value for key, value in coverage_counts.items()}
    bars = plt.bar(coverage_counts_str_keys.keys(), coverage_counts_str_keys.values(), width=0.10, align='center')

    # Add percentage labels above each bar for better readability
    for bar in bars:
        height = bar.get_height()
        percentage = (height / total_quarters) * 100
        plt.annotate(f'{percentage:.2f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom')

    # Set up axis labels, title and other visual elements
    plt.xlabel('Prozentsatz des Gesamtverbrauchs')
    plt.ylabel('Anzahl der Viertelstunden')
    plt.title(title)
    plt.xticks([str(key) for key in coverage_counts.keys()], rotation=45)
    plt.grid(True)
    
    # Save the figure and display it
    plt.savefig(filename)
    plt.show()