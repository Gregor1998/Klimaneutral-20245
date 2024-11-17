import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore

# Heatmap über Monate und Tage
def plotCalendarHeatmap(df, title, colName, linewidths=0.01):
    heatmap_data = df.pivot_table(index='Year Month', columns='Day', values=colName, aggfunc=np.sum)    # aggfunc=np.sum ->Werte summiert über den Tag!

    plt.figure(figsize=(20, 8))

    cmap = sns.diverging_palette(200, 30, as_cmap=True)

    sns.heatmap(heatmap_data, cmap=cmap, annot=False, linewidths=linewidths, cbar=True, xticklabels=1, cbar_kws={'label': 'MWh'})

    plt.title(title)
    plt.xlabel('Tag')
    plt.ylabel('Monat')

    plt.show()