import pandas as pd
import matplotlib.pyplot as plt

def plotResidualDiagram(startYear, endYear, directory_yearly_generation, directory_yearly_consumption):
    # Erstelle einen leeren DataFrame, um die Ergebnisse zu speichern
    all_years_difference_df = pd.DataFrame()

    # Iteriere durch jedes Jahr in den Dictionaries
    for year in range(startYear, endYear):  # Beispiel: von 2023 bis 2031
        if year in directory_yearly_generation and year in directory_yearly_consumption:
            production_df = directory_yearly_generation[year]
            consumption_df = directory_yearly_consumption[year]
            
            # Berechne die Gesamterzeugung_EE
            required_columns = ['Wind Offshore', 'Wind Onshore', 'Photovoltaik']
            if all(column in production_df.columns for column in required_columns):
                production_df['Gesamterzeugung_EE'] = production_df[required_columns].sum(axis=1)
            else:
                print(f"Eine oder mehrere der erforderlichen Spalten fehlen im DataFrame für das Jahr {year}.")
                continue
            
            # Überprüfe, ob beide DataFrames die gleiche Zeitachse haben
            if consumption_df['Datum'].equals(production_df['Datum']):
                # Berechne die Differenz zwischen Verbrauch und Produktion
                difference_df = pd.DataFrame()
                difference_df['Datum'] = consumption_df['Datum']
                difference_df['Differenz'] =  production_df['Gesamterzeugung_EE'] - consumption_df['Gesamtverbrauch']
                difference_df['Jahr'] = year
                
                # Füge die Ergebnisse dem Gesamt-DataFrame hinzu
                all_years_difference_df = pd.concat([all_years_difference_df, difference_df], ignore_index=True)
            else:
                print(f"Die Zeitachsen der DataFrames stimmen für das Jahr {year} nicht überein.")
        else:
            print(f"DataFrames für das Jahr {year} fehlen in einem der Verzeichnisse.")

    yearly_sums = all_years_difference_df.groupby('Jahr')['Differenz'].sum()

    # Erstelle das Liniendiagramm
    plt.figure(figsize=(10, 6))
    plt.plot(yearly_sums.index, yearly_sums.values, marker='o', linestyle='-', color='b')

    # Achsenbeschriftungen und Titel hinzufügen
    plt.xlabel('Jahr')
    plt.ylabel('Summe der Differenz')
    plt.title('Jährliche Summe der Differenz zwischen Verbrauch und Produktion')
    plt.grid(True)

    # Diagramm anzeigen
    plt.show()