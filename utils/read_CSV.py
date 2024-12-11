import pandas as pd # type: ignore
import os
from utils.addTimeInformation import addTimeInformation

# SMARD-Daten genau einlesen und in ein DataFrame umwandeln
def read_SMARD_data(path, mode):
    df = pd.read_csv(path,delimiter= ';', thousands='.', decimal=',', dayfirst ="True") #, parse_dates=[[0,1]]

    retrunvalue = None
    #Herauslöschen der Spalte Datum bis, da diese keine zusätzlichen Informationen bietet
    if mode != "Heatpump":
        df.drop(columns=["Datum bis"], inplace=True)

    if mode == "Generation":
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

        #df.drop(columns = ["Biomasse"], inplace = True)
        #df.drop(columns = ["Wasserkraft"], inplace = True)
        #df.drop(columns = ["Sonstige Erneuerbare"], inplace = True)
        df.drop(columns = ["Kernenergie"], inplace = True)
        df.drop(columns = ["Braunkohle"], inplace = True)
        df.drop(columns = ["Steinkohle"], inplace = True)
        df.drop(columns = ["Erdgas"], inplace = True)
        df.drop(columns = ["Pumpspeicher"], inplace = True)
        df.drop(columns = ["Sonstige Konventionelle"], inplace = True)

        #Formatierung der Datumstpalte
        df['Datum'] = pd.to_datetime(df['Datum'], format= '%d.%m.%Y %H:%M')

        #Werte des 29.Februar entfernen, falls vorhanden
        df = df[~((df['Datum'].dt.month == 2) & (df['Datum'].dt.day == 29))].sort_values(by="Datum")
        df.reset_index(drop=True, inplace=True)


    elif mode == "Comsumption":
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
    
    elif mode == "Installed":
        
    
    
        #Umbenennung der Spalten
        df.rename(columns={
            "Datum von":"Datum",
            "Biomasse [MW] Originalauflösungen":"Biomasse",
            "Wasserkraft [MW] Originalauflösungen":"Wasserkraft",
            "Wind Offshore [MW] Originalauflösungen":"Wind Offshore",
            "Wind Onshore [MW] Originalauflösungen":"Wind Onshore",
            "Photovoltaik [MW] Originalauflösungen":"Photovoltaik",
            "Sonstige Erneuerbare [MW] Originalauflösungen":"Sonstige Erneuerbare",
            "Kernenergie [MW] Originalauflösungen":"Kernenergie",
            "Braunkohle [MW] Originalauflösungen":"Braunkohle",
            "Steinkohle [MW] Originalauflösungen":"Steinkohle",
            "Erdgas [MW] Originalauflösungen":"Erdgas",
            "Pumpspeicher [MW] Originalauflösungen":"Pumpspeicher",
            "Sonstige Konventionelle [MW] Originalauflösungen":"Sonstige Konventionelle"    
        }, inplace = True)

        #Herauslöschen der Spalten, die nicht benötigt werden
        df.drop(columns = ["Datum"], inplace = True) #Datum wird nicht benötigt, da später das Datum von der Generation übernommen wird
        #df.drop(columns=["Datum bis"], inplace=True)
        df.drop(columns = ["Biomasse"], inplace = True)
        df.drop(columns = ["Wasserkraft"], inplace = True)
        df.drop(columns = ["Sonstige Erneuerbare"], inplace = True)
        df.drop(columns = ["Kernenergie"], inplace = True)
        df.drop(columns = ["Braunkohle"], inplace = True)
        df.drop(columns = ["Steinkohle"], inplace = True)
        df.drop(columns = ["Erdgas"], inplace = True)
        df.drop(columns = ["Pumpspeicher"], inplace = True)
        df.drop(columns = ["Sonstige Konventionelle"], inplace = True)

    elif(mode == "Heatpump"):
         #Formatierung der Datumstpalte
            df['Datum'] = pd.to_datetime(df['Datum'], format= '%d.%m.%Y %H:%M')

            #Herauslöschen der Zeilen des 29. Feburars
            #Werte des 29.Februar entfernen, falls vorhanden
            df = df[~((df['Datum'].dt.month == 2) & (df['Datum'].dt.day == 29))].sort_values(by="Datum")
            df.reset_index(drop=True, inplace=True)

            df.drop(columns = ["Datum"], inplace = True)


    else :
        print("Mode not found")

    #addTimeInformation(df)
    #Formatierung der Datumstpalte
        df['Datum'] = pd.to_datetime(df['Datum'], format= '%d.%m.%Y %H:%M')
        
    return df



def getData(mode):
    dataFrames = {}

    if mode == "Comsumption":
         # Dictionary für die df für jedes Jahr
        path_var = "CSV/Comsumption/" #Pfad auf den Ordner, um später durch die Datein zu navigieren

        #Schleife für die Jahre 2015-2023 und Einlesen der Datei
        for year in range(2023,2024): # hier könnte man später sich die Jahre auch vom User geben lassen, welche Jahre er gerne eingelesen haben möchte
            #Dateipfad für das entsprechende Jahr
            file_path = os.path.join(path_var, f"Realisierter_Stromverbrauch_{year}01010000_{year+1}01010000_Viertelstunde.csv")
            if os.path.exists(file_path):   #Falls dieser zusammengesetze Pfad existiert,...
                dataFrames[year] = read_SMARD_data(file_path, "Comsumption")   #... soll dieser eingelesen werden
                print(f"Data für {year} loaded succsessfully.")
            else:
                print(f"File for {year} not found at path: {file_path}") #... anstonsten nicht


    elif mode == "Generation":
        path_var = "CSV/Generation/" #Pfad auf den Ordner, um später durch die Datein zu navigieren

        #Schleife für die Jahre 2015-2023 und Einlesen der Datei
        for year in range(2015,2024): # hier könnte man später sich die Jahre auch vom User geben lassen, welche Jahre er gerne eingelesen haben möchte
            #Dateipfad für das entsprechende Jahr
            file_path = os.path.join(path_var, f"Realisierte_Erzeugung_{year}01010000_{year+1}01010000_Viertelstunde.csv")
            if os.path.exists(file_path):   #Falls dieser zusammengesetze Pfad existiert,...
                dataFrames[year] = read_SMARD_data(file_path, "Generation")   #... soll dieser eingelesen werden
                print(f"Data für {year} loaded succsessfully.")
            else:
                print(f"File for {year} not found at path: {file_path}") #... anstonsten nicht


    elif mode == "Installed":
        path_var = "CSV/Installed/"
        for year in range(2015,2024):
            file_path = os.path.join(path_var, f"Installierte_Erzeugungsleistung_{year}01010000_{year+1}01010000_Jahr.csv")
            if os.path.exists(file_path):
                dataFrames[year] = read_SMARD_data(file_path, "Installed")
                print(f"Data für {year} loaded succsessfully.")
            else:
                print(f"File for {year} not found at path: {file_path}")
    
    elif mode == "Heatpump":
        path_var = "load-profile/"
        file_path = os.path.join(path_var, "Wärmepumpe.csv")
        if os.path.exists(file_path):
            df_heatpump = read_SMARD_data(file_path, "Heatpump")

    else:
        print("Mode not found")

    
    if mode == "Heatpump":
        returnvalue = df_heatpump
    else:
        returnvalue = dataFrames
    
    return returnvalue  #Rückgabewert je nach Modus