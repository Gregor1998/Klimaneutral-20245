"""
Calendar Heatmap Plotting Utility

This module provides functionality to create calendar heatmaps for time series data.
The heatmaps visualize data across days and months, making it easy to spot
temporal patterns, trends, and anomalies in the data.

The main function plotCalendarHeatmap takes lists of dataframes and corresponding titles,
and creates heatmaps with consistent color scales across all plots for meaningful comparison.
"""

import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore

def plotCalendarHeatmap(df_list, title_list, colName, linewidths=0.01):
    """
    Creates calendar heatmaps for multiple dataframes with a consistent color scale.
    
    Parameters:
    -----------
    df_list : list of DataFrames
        List of pandas DataFrames containing the data to plot
    title_list : list of str
        List of titles for each heatmap (one per DataFrame)
    colName : str
        Name of the column containing values to be visualized
    linewidths : float, optional
        Width of the lines separating cells in the heatmap
    """
    # Define consistent color scale limits for all heatmaps to enable direct comparison
    vmin = -1e6
    vmax = 2.5e6 
    
    # Iterate through each dataframe and create a separate heatmap
    for df, title in zip(df_list, title_list):
        # Reshape data into a format suitable for heatmap (months as rows, days as columns)
        heatmap_data = df.pivot_table(index='Year Month', columns='Day', values=colName, aggfunc=np.sum)

        # Create a new figure with appropriate size
        plt.figure(figsize=(20, 8))
        
        # Define color palette - using a diverging palette for positive/negative values
        cmap = sns.diverging_palette(200, 30, as_cmap=True)

        # Generate the heatmap with the specified parameters
        sns.heatmap(heatmap_data, 
                   cmap=cmap, 
                   annot=False,  # Don't show values in cells
                   linewidths=linewidths, 
                   cbar=True,  # Show color bar
                   xticklabels=1,  # Show x-axis labels
                   cbar_kws={'label': 'MWh'},  # Label for the color bar
                   vmin=vmin,  # Consistent minimum value for color scale
                   vmax=vmax)  # Consistent maximum value for color scale

        # Set titles and labels for the plot
        plt.title(title)
        plt.xlabel('Tag')
        plt.ylabel('Monat')
        
        # Save the figure to a file
        plt.savefig(f'assets/plots/heatmap_{title_list.index(title) + 1}_{title}.png')
        
        # Display the plot
        plt.show()