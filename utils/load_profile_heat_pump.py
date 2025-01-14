#Lastprofil für Wärmepumpe

import pandas as pd #type: ignore
import os
import numpy as np

from utils.read_CSV import getData
from utils.addTimePerformance import addTimePerformance
from utils.temperature import temperatureRegion

"""
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
        directory_heatpump_comsumption[year].to_csv(f"CSV/Lastprofile/waermepumpe/Hochrechnung/Heatpump_{year}.csv", index=False)

    return directory_heatpump_comsumption
"""

""""
def lastprofil_heatpump(installed_heatpumps, expected_heatpumps, first_year, end_year, case_Temperature):
    # Anzahl der Monate insgesamt
    total_months = (end_year - first_year + 1) * 12

    # Berechnung der monatlichen Zubaurate
    monthly_expansion_rate = (expected_heatpumps - installed_heatpumps) / total_months

    # Einlesen der Temperaturdaten
    df_temperature = temperature(case_Temperature)  # DataFrame mit Temperaturwerten pro Monat

    # Einlesen des Lastprofils
    df_lastprofile = getData("Heatpump")  # DataFrame mit Lastprofilen (-12 bis 18 °C, 96 Zeilen pro Tag)
    if len(df_lastprofile) != 96:
        raise ValueError("Lastprofil muss 96 Zeilen pro Tag enthalten.")
    
    #df_lastprofile.columns auf selben dtype casten
    df_lastprofile.columns = df_lastprofile.columns.map(int)
    columns_list = list(map(int, df_lastprofile.columns))

    # Dictionary zur Speicherung der Ergebnisse
    dictionary_heatpump_consumption = {}

    # Jahresschleife
    for year in range(first_year, end_year + 1):
        # DataFrame für das gesamte Jahr (35040 Zeilen)
        yearly_profile = pd.DataFrame()

        # Monatsschleife
        for month in range(1, 13):

            monthly_consumption = pd.DataFrame()

            # Monatstemperatur abrufen
            month_temperature = int(df_temperature.iloc[0, month - 1])


            # Sicherstellen, dass die Temperatur im Lastprofil existiert
            if month_temperature not in columns_list:
                raise ValueError(f"Temperatur {month_temperature}°C nicht im Lastprofil enthalten.")

            # Lastprofil für den Monat abrufen
            monthly_load_profile = df_lastprofile[month_temperature].copy()

            # Wiederholen für die Anzahl der Tage im Monat
            days_in_month = 30 if month in [4, 6, 9, 11] else 31
            if month == 2:  # Februar
                days_in_month = 28  # Immer 28 Tage im Februar

            monthly_consumption = pd.concat([monthly_load_profile] * days_in_month, ignore_index=True)

            # Verbrauch für installierte Wärmepumpen berechnen
            monthly_consumption = (monthly_consumption * installed_heatpumps / 1000).reset_index(drop=True)

            # Auf das Jahresprofil anhängen
            yearly_profile = pd.concat([yearly_profile, monthly_consumption], ignore_index=True)

            # Monatlicher Zubau von Wärmepumpen
            installed_heatpumps += monthly_expansion_rate

            monthly_consumption = None
        
        if len(yearly_profile) != 35040:
            raise ValueError(f"Jahresprofil für {year} hat nicht die erwartete Länge von 35040 Zeilen.")

        #Datumsspalte hinzufügen
        yearly_profile = addTimePerformance(yearly_profile, year)  
            

        # Jahresprofil speichern
        dictionary_heatpump_consumption[year] = yearly_profile

        yearly_profile = None
"""
   


from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def calculate_load_for_region(region, hour, index, current_installed, distribution, directory_temperature, directory_load_profile_by_hour):
    temperature = directory_temperature[region]["Temperatur"][index]
    # Begrenzung der Temperatur auf den Bereich [-12, 18]
    if temperature < -12:
        temperature = -12
    elif temperature > 18:
        temperature = 18

    # Das Lastprofil für die aktuelle Stunde auswählen (4 Werte für Viertelstunden)
    load_profile = directory_load_profile_by_hour[hour][temperature].copy()
    # Skaliere das Lastprofil nach Anzahl der Wärmepumpen und Verteilung
    load_profile_scaled = (load_profile * (current_installed * distribution)) / 1000  # Verbrauch in MWh
    return load_profile_scaled  # Gibt ein DataFrame oder eine Serie mit 4 Werten zurück

def heatpump_Region(installed_heatpumps, expected_heatpumps, first_year, end_year, case_Temperature):
    df_population = getData("Population")  # Einlesen der Bevölkerungszahlen
    combined_population = float(df_population.sum(axis=1))  # Summe der Bevölkerungszahlen für Deutschland

    population_North = float(
        df_population["Hamburg"][0]
        + df_population["Bremen"][0]
        + df_population["Schleswig-Holstein"][0]
        + df_population["Niedersachsen"][0]
        + df_population["Mecklenburg-Vorpommern"][0]
    )
    population_East = float(
        df_population["Berlin"][0]
        + df_population["Brandenburg"][0]
        + df_population["Sachsen"][0]
        + df_population["Sachsen-Anhalt"][0]
        + df_population["Thüringen"][0]
    )
    population_South = float(df_population["Bayern"][0] + df_population["Baden-Württemberg"][0])
    population_West = float(
        df_population["Nordrhein-Westfalen"][0]
        + df_population["Rheinland-Pfalz"][0]
        + df_population["Saarland"][0]
        + df_population["Hessen"][0]
    )

    distribution_north = population_North / combined_population
    distribution_east = population_East / combined_population
    distribution_south = population_South / combined_population
    distribution_west = population_West / combined_population

    directory_heatpump_comsumption = {}
    directory_temperature = temperatureRegion(case_Temperature)

    diffrence_year = end_year - first_year
    diffrence_heatpumps = expected_heatpumps - installed_heatpumps
    current_installed = installed_heatpumps
    dayly_expansion_rate_heatpump = diffrence_heatpumps / ((diffrence_year + 1) * 365)

    directory_load_profile_by_hour = getData("Heatpump")

    for year in range(first_year, end_year + 1):
        heatpump_df = pd.DataFrame()
        north_df = pd.DataFrame()
        east_df = pd.DataFrame()
        south_df = pd.DataFrame()
        west_df = pd.DataFrame()

        for day in range(365):
            current_installed += dayly_expansion_rate_heatpump

            tasks = []
            results = {region: [] for region in ["North", "East", "South", "West"]}

            with ThreadPoolExecutor() as executor:
                for hour in range(24):
                    index = day * 24 + hour

                    for region, distribution in zip(
                        ["North", "East", "South", "West"],
                        [distribution_north, distribution_east, distribution_south, distribution_west],
                    ):
                        # Füge parallele Aufgaben hinzu
                        tasks.append(
                            executor.submit(
                                calculate_load_for_region,
                                region,
                                hour,
                                index,
                                current_installed,
                                distribution,
                                directory_temperature,
                                directory_load_profile_by_hour,
                            )
                        )

                # Ergebnisse sammeln
                for task, region in zip(tasks, ["North", "East", "South", "West"] * 24):
                    results[region].append(task.result())

            # Ergebnisse korrekt auf die DataFrames aufteilen (auf Viertelstundenbasis)
            for region, data in results.items():
                region_df = pd.concat(data, ignore_index=True)  # Kombiniert alle Viertelstunden-Daten
                if region == "North":
                    north_df = pd.concat([north_df, region_df], ignore_index=True)
                elif region == "East":
                    east_df = pd.concat([east_df, region_df], ignore_index=True)
                elif region == "South":
                    south_df = pd.concat([south_df, region_df], ignore_index=True)
                elif region == "West":
                    west_df = pd.concat([west_df, region_df], ignore_index=True)

        # Überprüfen, ob die DataFrames die erwartete Länge haben
        if (
            len(north_df) != 35040
            or len(east_df) != 35040
            or len(south_df) != 35040
            or len(west_df) != 35040
        ):
            raise ValueError(
                f"Mindestens eines der Jahresprofile für {year} hat nicht die erwartete Länge von 35040 Zeilen."
            )
        else:
            heatpump_df = north_df + east_df + south_df + west_df
            heatpump_df.rename(columns={0: "Verbrauch in MWh"}, inplace=True)
            heatpump_df = addTimePerformance(heatpump_df, year)
            directory_heatpump_comsumption[year] = heatpump_df

    return directory_heatpump_comsumption