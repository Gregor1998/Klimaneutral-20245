# Heatmap über Monate und Tage
def plotCalendarHeatmap(df, title, colName, linewidths=0.01):
    heatmap_data = df.pivot_table(index='Year Month', columns='Day', values=colName, aggfunc=np.sum)    # aggfunc=np.sum ->Werte summiert über den Tag!

    plt.figure(figsize=(20, 8))
    sns.heatmap(heatmap_data, cmap='coolwarm', annot=False, linewidths=linewidths, cbar=True, xticklabels=1)

    plt.title(title)
    plt.xlabel('Tag')
    plt.ylabel('Monat')

    plt.show()