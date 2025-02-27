import pandas as pd
import os
from functools import lru_cache

def read_SMARD_data(path, mode):
    # Spalten und Datentypen je nach Modus definieren
    if mode == "Generation":
        usecols = ["Datum von","Biomasse [MWh] Originalauflösungen","Wasserkraft [MWh] Originalauflösungen", "Wind Offshore [MWh] Originalauflösungen", "Wind Onshore [MWh] Originalauflösungen", "Photovoltaik [MWh] Originalauflösungen","Sonstige Erneuerbare [MWh] Originalauflösungen"]
        dtype = {"Biomasse [MWh] Originalauflösungen": "float32","Wasserkraft [MWh] Originalauflösungen": "float32","Wind Offshore [MWh] Originalauflösungen": "float32", "Wind Onshore [MWh] Originalauflösungen": "float32", "Photovoltaik [MWh] Originalauflösungen": "float32","Sonstige Erneuerbare [MWh] Originalauflösungen": "float32"}
    elif mode == "Consumption":
        usecols = ["Datum von", "Gesamt (Netzlast) [MWh] Originalauflösungen"]
        dtype = {"Gesamt (Netzlast) [MWh] Originalauflösungen": "float32"}
    elif mode == "Installed":
        usecols = ["Wind Offshore [MW] Originalauflösungen", "Wind Onshore [MW] Originalauflösungen", "Photovoltaik [MW] Originalauflösungen"]
        dtype = {col: "float32" for col in usecols}
    elif mode == "Heatpump":
        usecols = ["Datum", "Lastprofil"]
        dtype = {"Lastprofil": "float32"}
    elif mode == "Temperature":
        usecols = ["TT_TU"]
        dtype = {"TT_TU": "float32"}
    elif mode == "Population":
        usecols = None  # Alle Spalten laden, falls keine spezifischen bekannt sind
        dtype = None
    else:
        raise ValueError("Unbekannter Modus")

    # CSV-Datei laden mit optimierten Parametern
    df = pd.read_csv(
        path,
        delimiter=";",
        thousands=".",
        decimal=",",
        usecols=usecols,
        dtype=dtype
    )

    # Manuell Datum konvertieren (entfernt str dtype für Datum)
    if "Datum von" in df.columns:
        df["Datum von"] = pd.to_datetime(df["Datum von"], format="%d.%m.%Y %H:%M", errors='coerce')
    elif "Datum" in df.columns and mode != "Installed":
        df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y %H:%M", errors='coerce')

    # Spalten direkt umbenennen
    if mode == "Generation":
        df.rename(columns={
            "Datum von": "Datum",
            "Wind Offshore [MWh] Originalauflösungen": "Wind Offshore",
            "Wind Onshore [MWh] Originalauflösungen": "Wind Onshore",
            "Photovoltaik [MWh] Originalauflösungen": "Photovoltaik",
            "Biomasse [MWh] Originalauflösungen":"Biomasse",
            "Wasserkraft [MWh] Originalauflösungen":"Wasserkraft",
            "Sonstige Erneuerbare [MWh] Originalauflösungen":"Sonstige Erneuerbare"
        }, inplace=True)
    elif mode == "Consumption":
        df.rename(columns={
            "Datum von": "Datum",
            "Gesamt (Netzlast) [MWh] Originalauflösungen": "Gesamtverbrauch"
        }, inplace=True)
    elif mode == "Installed":
        df.rename(columns={
            "Wind Offshore [MW] Originalauflösungen": "Wind Offshore",
            "Wind Onshore [MW] Originalauflösungen": "Wind Onshore",
            "Photovoltaik [MW] Originalauflösungen": "Photovoltaik"
        }, inplace=True)
    elif mode == "Temperature":
        df.rename(columns={"TT_TU": "Temperatur"}, inplace=True)

    # Spezifische Anpassungen
    if mode in ["Generation", "Consumption", "Heatpump"] and "Datum" in df.columns:
        # Prüfe ob Datum eine Datetime-Spalte ist
        if pd.api.types.is_datetime64_dtype(df["Datum"]):
            # Entfernen des 29. Februars und Sortierung
            df = df[~((df["Datum"].dt.month == 2) & (df["Datum"].dt.day == 29))].sort_values(by="Datum")
            df.reset_index(drop=True, inplace=True)
        else:
            print(f"Warnung: Datum-Spalte konnte nicht als Datetime konvertiert werden in {path}")
            
    #if mode == "Heatpump" and "Datum" in df.columns:
        #df.drop(columns=["Datum"], inplace=True)

    return df

@lru_cache(maxsize=32)
def getData(type, year=None, start_year=None, end_year=None):
    """
    Read CSV data with caching for better performance.
    
    Args:
        type (str): Type of data to read ('Generation', 'Installed', etc.)
        year (int, optional): Specific year to load
        start_year (int, optional): Start year for range
        end_year (int, optional): End year for range
    
    Returns:
        dict: Dictionary of dataframes by year
    """
    directory_yearly = {}
    
    # Special case for Heatpump with no year specified
    if type == "Heatpump" and year is None and start_year is None and end_year is None:
        try:
            path_var = "CSV/Lastprofile/waermepumpe/"
            file_path = os.path.join(path_var, "Wärmepumpe.csv")
            if not os.path.exists(file_path):
                print(f"Datei nicht gefunden: {file_path}")
                return {}
                
            df = read_SMARD_data(file_path, "Heatpump")
            print(f"Heatpump base profile loaded successfully.")
            print(df)
            return {"Lastprofil": df}
        except Exception as e:
            print(f"Error loading heatpump base profile: {e}")
            return {}
    
    # If single year is requested
    if year is not None:
        return _read_single_year(type, year)
        
    # If range of years is requested
    if start_year is not None and end_year is not None:
        for year in range(start_year, end_year + 1):
            df_year = _read_single_year(type, year)
            if df_year:
                directory_yearly[year] = df_year.get(year)
    
    return directory_yearly

def _read_single_year(type, year):
    """Helper function to read data for a single year with optimized reading"""
    try:
        # Bestimme den Dateipfad
        if type == "Generation":
            file_path = f"CSV/{type}/Realisierte_Erzeugung_{year}01010000_{year+1}01010000_Viertelstunde.csv"
        elif type == "Consumption":
            file_path = f"CSV/{type}/Realisierter_Stromverbrauch_{year}01010000_{year+1}01010000_Viertelstunde.csv"
        elif type == "Installed":
            file_path = f"CSV/{type}/Installierte_Erzeugungsleistung_{year}01010000_{year+1}01010000_Jahr.csv"
        elif type == "Heatpump":
            # Heat pump data doesn't have year-specific files
            file_path = "CSV/Lastprofile/waermepumpen/Wärmepumpe.csv"
        else:
            raise ValueError(f"Unbekannter Datentyp: {type}")
        
        # Prüfe, ob die Datei existiert
        if not os.path.exists(file_path):
            print(f"Datei nicht gefunden: {file_path}")
            return None
            
        # Verwende read_SMARD_data für einheitliche Datenverarbeitung
        df = read_SMARD_data(file_path, type)
        
        if type == "Heatpump":
            # For heat pump data, add the year to the dates if needed
            if "Datum" in df.columns:
                df["Datum"] = df["Datum"].apply(lambda x: x.replace(year=year))
        
        print(f"Data für {year} loaded successfully.")
        return {year: df}
    except Exception as e:
        print(f"Error loading data for {year}: {e}")
        return None

