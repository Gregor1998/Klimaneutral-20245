import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore

# Heatmap über Monate und Tage
def plotCalendarHeatmap(df_list, title_list, colName, linewidths=0.01):
    # Determine the global min and max values for the color scale
    vmin = float('inf')
    vmax = float('-inf')
    for df in df_list:
        heatmap_data = df.pivot_table(index='Year Month', columns='Day', values=colName, aggfunc=np.sum)
        vmin = min(vmin, heatmap_data.min().min())
        vmax = max(vmax, heatmap_data.max().max())

    # Plot each heatmap with the same color scale
    for df, title in zip(df_list, title_list):
        heatmap_data = df.pivot_table(index='Year Month', columns='Day', values=colName, aggfunc=np.sum)

        plt.figure(figsize=(20, 8))
        

        cmap = sns.diverging_palette(200, 30, as_cmap=True)

        sns.heatmap(heatmap_data, cmap=cmap, annot=False, linewidths=linewidths, cbar=True, xticklabels=1, cbar_kws={'label': 'MWh'}, vmin=vmin, vmax=vmax)

        plt.title(title)
        plt.xlabel('Tag')
        plt.ylabel('Monat')
        plt.savefig(f'assets/plots/heatmap_{title_list.index(title) + 1}_{title}.png')
        plt.show()

