import pandas as pd # type: ignore
import os
from utils.addTimeInformation import addTimeInformation

# SMARD-Daten genau einlesen und in ein DataFrame umwandeln
def read_SMARD_data(path, mode):
    df = pd.read_csv(path,delimiter= ';', thousands='.', decimal=',', dayfirst ="True") #, parse_dates=[[0,1]]

    #Herauslöschen der Spalte Datum bis, da diese keine zusätzlichen Informationen bietet
    df.drop(columns=["Datum bis"], inplace=True)

    if mode == "Erzeugung":
        #Umbenennung der Spalten
        df.rename(columns={
            "Datum von":"Datum",
            "Biomasse [MWh] Originalauflösungen":"Biomasse",
            "Wasserkraft [MWh] Originalauflösungen":"Wasserkraft",
            "Wind Offshore [MWh] Originalauflösungen":"Wind Offshore",
            "Wind Onshore [MWh] Originalauflösungen":"Wind Onshore",
            "Photovoltaik [MWh] Originalauflösungen":"Photovoltaik",
            "Sonstige Erneuerbare [MWh] Originalauflösungen":"Sonstige Erneuerbare",
            "Kernenergie [MWh] Originalauflösungen":"Kernenergie",
            "Braunkohle [MWh] Originalauflösungen":"Braunkohle",
            "Steinkohle [MWh] Originalauflösungen":"Steinkohle",
            "Erdgas [MWh] Originalauflösungen":"Erdgas",
            "Pumpspeicher [MWh] Originalauflösungen":"Pumpspeicher",
            "Sonstige Konventionelle [MWh] Originalauflösungen":"Sonstige Konventionelle"    
        }, inplace = True)

        df.drop(columns = ["Biomasse"], inplace = True)
        df.drop(columns = ["Wasserkraft"], inplace = True)
        df.drop(columns = ["Sonstige Erneuerbare"], inplace = True)
        df.drop(columns = ["Kernenergie"], inplace = True)
        df.drop(columns = ["Braunkohle"], inplace = True)
        df.drop(columns = ["Steinkohle"], inplace = True)
        df.drop(columns = ["Erdgas"], inplace = True)
        df.drop(columns = ["Pumpspeicher"], inplace = True)
        df.drop(columns = ["Sonstige Konventionelle"], inplace = True)

        #Formatierung der Datumstpalte
        df['Datum'] = pd.to_datetime(df['Datum'], format= '%d.%m.%Y %H:%M')

    elif mode == "Verbrauch":
        #Umbenennung der Spalten
        df.rename(columns= {
        "Datum von":"Datum",
        "Gesamt (Netzlast) [MWh] Originalauflösungen":"Gesamtverbrauch",
        "Residuallast [MWh] Originalauflösungen":"Residuallast",
        "Pumpspeicher [MWh] Originalauflösungen":"Pumpspeicher",  
        }, inplace = True)

        df.drop(columns = ["Pumpspeicher"], inplace = True)
        df.drop(columns = ["Residuallast"], inplace = True)

        #Formatierung der Datumstpalte
        df['Datum'] = pd.to_datetime(df['Datum'], format= '%d.%m.%Y %H:%M')

    else :
        print("Mode not found")

    addTimeInformation(df)

    return df



def getData(mode):
    dataFrames = {}

    if mode == "Verbrauch":
         # Dictionary für die df für jedes Jahr
        path_var = "CSV/Verbrauch/" #Pfad auf den Ordner, um später durch die Datein zu navigieren

        #Schleife für die Jahre 2015-2023 und Einlesen der Datei
        for year in range(2023,2024): # hier könnte man später sich die Jahre auch vom User geben lassen, welche Jahre er gerne eingelesen haben möchte
            #Dateipfad für das entsprechende Jahr
            file_path = os.path.join(path_var, f"Realisierter_Stromverbrauch_{year}01010000_{year+1}01010000_Viertelstunde.csv")
            if os.path.exists(file_path):   #Falls dieser zusammengesetze Pfad existiert,...
                dataFrames[year] = read_SMARD_data(file_path, "Verbrauch")   #... soll dieser eingelesen werden
                print(f"Data für {year} loaded succsessfully.")
            else:
                print(f"File for {year} not found at path: {file_path}") #... anstonsten nicht

    elif mode == "Erzeugung":
        path_var = "CSV/" #Pfad auf den Ordner, um später durch die Datein zu navigieren

        #Schleife für die Jahre 2015-2023 und Einlesen der Datei
        for year in range(2015,2024): # hier könnte man später sich die Jahre auch vom User geben lassen, welche Jahre er gerne eingelesen haben möchte
            #Dateipfad für das entsprechende Jahr
            file_path = os.path.join(path_var, f"Realisierte_Erzeugung_{year}01010000_{year+1}01010000_Viertelstunde.csv")
            if os.path.exists(file_path):   #Falls dieser zusammengesetze Pfad existiert,...
                dataFrames[year] = read_SMARD_data(file_path, "Erzeugung")   #... soll dieser eingelesen werden
                print(f"Data für {year} loaded succsessfully.")
            else:
                print(f"File for {year} not found at path: {file_path}") #... anstonsten nicht

    else:
        print("Mode not found")


    return dataFrames   #Rückgabe der eingelesenen Date als DataFrame