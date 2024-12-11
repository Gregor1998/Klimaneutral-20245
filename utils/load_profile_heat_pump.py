#Lastprofil für Wärmepumpe

import pandas as pd #type: ignore
import os

from utils.read_CSV import getData
from utils.addTimePerformance import addTimePerformance


def load_profile_heatpump(installed_heatpumps, expected_heatpumps, first_year, end_year):

    diffrence_year = end_year - first_year  # Abstand für die für die for-Schleife
    diffrence_heatpumps = expected_heatpumps - installed_heatpumps  # Differenz der installierten und erwarteten Wärmepumpen
    current_installed = installed_heatpumps # aktuell installierte Wärmepumpen

    directory_heatpump_comsumption = {} # Dictionary für die df für jedes Jahr

    df = getData("Heatpump") # Einlesen des Lastprofils für die Wärmepumpe
    

    daily_expansion_rate_heatpump = diffrence_heatpumps / (diffrence_year*365) # tägliche Zubaurate für die Wärmepumpe

    for year in range(first_year, end_year+1): 
        heatpump_df = pd.DataFrame({"Verbrauch": [0.0]*35040}) # Anlegung eines leeren DataFrames für das Lastprpfil pro Viertelstunde
        heatpump_df = addTimePerformance(heatpump_df, year) # Hinzufügen der Zeitspalte
                                
        for day in range(365):  #Lastprofil errechnen mit einer täglichen Zubaurate
            start_index = day*96
            end_index = start_index + 96

            current_installed += daily_expansion_rate_heatpump

            heatpump_df.loc[start_index:end_index, "Verbrauch"] = df["Lastprofil"][start_index:end_index] * current_installed/1000  # in MWh

        directory_heatpump_comsumption[year] = heatpump_df
        directory_heatpump_comsumption[year].to_csv(f"Heatpump_{year}.csv", index=False)

    return directory_heatpump_comsumption

    