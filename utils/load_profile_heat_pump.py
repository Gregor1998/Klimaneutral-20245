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
   


def heatpump_Region(installed_heatpumps, expected_heatpumps, first_year, end_year, case_Temperature):
    
    df_population = getData("Population") # Einlesen der Bevölkerungszahlen
    combined_population = float(df_population.sum(axis=1)) # Summe der Bevölkerungszahlen für Deutschland
    
    
    population_North = (
        float(df_population["Hamburg"][0] 
        + df_population["Bremen"][0]
        + df_population["Schleswig-Holstein"][0] 
        + df_population["Niedersachsen"][0] 
        + df_population["Mecklenburg-Vorpommern"][0])
     ) #Summe der Bevölkerungszahlen für den Norden
    
    population_East = (
        float(df_population["Berlin"][0] + 
        df_population["Brandenburg"][0] 
        + df_population["Sachsen"][0] 
        + df_population["Sachsen-Anhalt"][0] 
        + df_population["Thüringen"][0])
     ) #Summe der Bevölkerungszahlen für den Osten
    
    population_South = (
        float(df_population["Bayern"][0] 
        + df_population["Baden-Württemberg"][0])
     ) #Summe der Bevölkerungszahlen für den Süden
    
    population_West = (
        float(df_population["Nordrhein-Westfalen"][0]
        + df_population["Rheinland-Pfalz"][0] 
        + df_population["Saarland"][0] 
        + df_population["Hessen"][0])
     ) #Summe der Bevölkerungszahlen für den Westen

    distribution_north = (population_North / combined_population) #Verteilung der Bevölkerungszahlen für den Norden
    distribution_east = (population_East / combined_population) #Verteilung der Bevölkerungszahlen für den Osten
    distribution_south = (population_South / combined_population) #Verteilung der Bevölkerungszahlen für den Süden
    distribution_west = (population_West / combined_population) #Verteilung der Bevölkerungszahlen für den Westen

   
    
    directory_heatpump_comsumption = {} # Dictionary für die df für jedes Jahr

    directory_temperature = temperatureRegion(case_Temperature) # Dictionary für die Temperaturverläufe der Unterschiedlichen Regionen

    diffrence_year = end_year - first_year  # Abstand für die für die for-Schleife
    diffrence_heatpumps = expected_heatpumps - installed_heatpumps  # Differenz der installierten und erwarteten Wärmepumpen
    current_installed = installed_heatpumps # aktuell installierte Wärmepumpen
    dayly_expansion_rate_heatpump = diffrence_heatpumps / ((diffrence_year+1)*365) # tägliche Zubaurate für die Wärmepumpe
    

    directory_load_profile_by_hour = getData("Heatpump") # Einlesen des Lastprofils für die Wärmepumpe
    
    


    for year in range(first_year, end_year+1):
        heatpump_df = pd.DataFrame() # Anlegung eines leeren DataFrames für das Lastprpfil pro Viertelstunde für ein Jahr Deutschlandweit

        north_df = pd.DataFrame() #Anlegung für Verbrauch für die Region Nord
        east_df = pd.DataFrame() #Anlegung für Verbrauch für die Region Ost
        south_df = pd.DataFrame() #Anlegung für Verbrauch für die Region Süd
        west_df = pd.DataFrame() #Anlegung für Verbrauch für die Region West

        for day in range(365):
            current_installed += dayly_expansion_rate_heatpump #aktuelle installierte Wärmepumpen Deutschlandweit

            
            for hour in range(24):
                index = day*24 + hour #Index für die passende Stunde für die Temperatur

                #Lastprofil für die Region Nord berechnen
                temperatureNorth = directory_temperature["North"]["Temperatur"][index]  #Temperatur für jeweilige Stunde Region Nord
                if temperatureNorth < -12:  #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureNorth = -12
                elif temperatureNorth > 18: #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureNorth = 18

                loadProfileNorth = directory_load_profile_by_hour[hour][temperatureNorth].copy() #Lastprofil für die Stunde und Temperatur
                loadProfileHourNorth = (loadProfileNorth*(current_installed*distribution_north))/1000    #Last für die Region North in einer bestimmten Stunde in MWh
                north_df = pd.concat([north_df, loadProfileHourNorth], ignore_index=True) #Anhängen an den Jahresverbrauch für die Region North
                

                #Lastprofil für die Region Ost berechnen
                temperatureEast = directory_temperature["East"]["Temperatur"][index] #Temperatur für jeweilige Stunde Region Ost
                if temperatureEast < -12: #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureEast = -12
                elif temperatureEast > 18: #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureEast = 18

                loadProfileEast = directory_load_profile_by_hour[hour][temperatureEast].copy() #Lastprofil für die Stunde und Temperatur
                loadProfileHourEast = (loadProfileEast*(current_installed*distribution_east))/1000   #Last für die Region East in einer bestimmten Stunde in MWh
                east_df = pd.concat([east_df, loadProfileHourEast], ignore_index=True) #Anhängen an den Jahresverbrauch für die Region East


                #Lastprofil für die Region Süd berechnen
                temperatureSouth = directory_temperature["South"]["Temperatur"][index] #Temperatur für jeweilige Stunde Region Süd
                if temperatureSouth < -12: #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureSouth = -12
                elif temperatureSouth > 18: #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureSouth = 18
                
                loadProfileSouth = directory_load_profile_by_hour[hour][temperatureSouth].copy() #Lastprofil für die Stunde und Temperatur
                loadProfileHourSouth = (loadProfileSouth*(current_installed*distribution_south))/1000  #Last für die Region South in einer bestimmten Stunde in MWh
                south_df = pd.concat([south_df, loadProfileHourSouth], ignore_index=True) #Anhängen an den Jahresverbrauch für die Region South


                #Lastprofil für die Region West berechnen
                temperatureWest = directory_temperature["West"]["Temperatur"][index] #Temperatur für jeweilige Stunde Region West
                if temperatureWest < -12: #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureWest = -12
                elif temperatureWest > 18: #Sicherstellen, dass die Temperatur im Lastprofil existiert
                    temperatureWest = 18
                
                loadProfileWest = directory_load_profile_by_hour[hour][temperatureWest].copy() #Lastprofil für die Stunde und Temperatur
                loadProfileHourWest = (loadProfileWest*(current_installed*distribution_west))/1000 #Last für die Region West in einer bestimmten Stunde in MWh
                west_df = pd.concat([west_df, loadProfileHourWest], ignore_index=True) #Anhängen an den Jahresverbrauch für die Region West

                

        if len(north_df) != 35040 or len(east_df) != 35040 or len(south_df) != 35040 or len(west_df) != 35040: #Überprüfung, ob alle Jahresprofile die richtige Länge haben
            raise ValueError(f"Mindestens eines der Jahresprofile für {year} hat nicht die erwartete Länge von 35040 Zeilen.")
        else:
            heatpump_df = north_df + east_df + south_df + west_df #Gesamtverbrauch = Summe der Verbräuche für die Regionen
            heatpump_df.rename(columns={0: "Verbrauch in MWh"}, inplace=True) #Umbenennung der Spalte
            heatpump_df = addTimePerformance(heatpump_df, year) #Hinzufügen der Zeit
            directory_heatpump_comsumption[year] = heatpump_df #Speichern des Jahresverbrauchs in das Dictionary
            

    return directory_heatpump_comsumption #Rückgabe des Dictionarys mit den Jahresverbräuchen für Deutschland



        






        
        



        


            

   


