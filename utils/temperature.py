import pandas as pd
from utils.read_CSV import getData
import os

"""
def temperature(case_Temperature):
    # Einlesen der CSV mit den monatlichen Durchschnittstemperaturen
    df_temperature = getData("Temperature")

    # Erstellen eines Dictionaries, bei dem der Key das Jahr ist und der Value ein DataFrame mit Monatswerten
    directoryTemperature = {
        year: df_temperature[df_temperature['Jahr'] == year].drop(columns='Jahr').reset_index(drop=True)
        for year in df_temperature['Jahr'].unique()
    }


    # DataFrame als Zwischenspeicher für die gerundeten Temperaturen
    df_rounded = pd.DataFrame()

    # DataFrame für verwendete Temperaturen
    df_usingTemperature = pd.DataFrame()

    # Auswahl und Bearbeitung der Temperaturdaten je nach Fall
    if case_Temperature == "BestCase":
        df_rounded = directoryTemperature[2022]
    elif case_Temperature == "WorstCase":
        df_rounded = directoryTemperature[2020]
    elif case_Temperature == "AverageCase":
        df_rounded = directoryTemperature[2021]
    else:
        print("Error: No valid case for temperature")
        return None

    # Runden der Temperaturen und Umwandeln in Integer
    df_rounded = df_rounded.round(0)
    df_usingTemperature = df_rounded.astype(int)
    
    print(df_usingTemperature)
    

    return df_usingTemperature

"""
    
def temperatureRegion(case_Temperature):
    #Dictionary für die Temperaturverläufe der Unterschiedlichen Regionen
    directoryRegionTemperature = {}

    #Einlesen der CSV der unterschiedlichen Regionen für die Temperatur nach case
    path_nord=case_Temperature +"_Temperature_North.csv"
    df_north_temperature = getData("Temperature", path_nord)
    df_north_temperature = df_north_temperature.round(0).astype(int) #Runden der Temperaturwerte und Umwandeln in Integer
    directoryRegionTemperature["North"] = df_north_temperature #Dataframe wird in das Dictionary für Region Nord eingefügt

    path_west = case_Temperature + "_Temperature_West.csv"
    df_west_temperature = getData("Temperature", path_west)
    df_west_temperature = df_west_temperature.round(0).astype(int) #Runden der Temperaturwerte und Umwandeln in Integer
    directoryRegionTemperature["West"] = df_west_temperature #Dataframe wird in das Dictionary für Region West eingefügt

    path_south = case_Temperature + "_Temperature_South.csv"
    df_south_temperature = getData("Temperature", path_south)
    df_south_temperature = df_south_temperature.round(0).astype(int) #Runden der Temperaturwerte und Umwandeln in Integer
    directoryRegionTemperature["South"] = df_south_temperature #Dataframe wird in das Dictionary für Region Süd eingefügt

    path_east = case_Temperature + "_Temperature_East.csv"
    df_east_temperature = getData("Temperature", path_east)
    df_east_temperature = df_east_temperature.round(0).astype(int) #Runden der Temperaturwerte und Umwandeln in Integer
    directoryRegionTemperature["East"] = df_east_temperature #Dataframe wird in das Dictionary für Region Ost eingefügt
    
    


    return directoryRegionTemperature
    
    
    





    
    
    


