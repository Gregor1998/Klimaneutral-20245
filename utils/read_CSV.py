"""
-------------------------------------------------------------------------------
read_CSV.py - SMARD Energy Data Reader Utility
-------------------------------------------------------------------------------
This module provides functions to read and process energy data from SMARD CSV files.
It handles various data types including renewable energy generation, consumption,
installed capacity, and heat pump load profiles.

The module optimizes data loading through caching and specialized parsing for
different data types. All data is returned as clean pandas DataFrames with
standardized column names and appropriate data types.

Main functions:
- read_SMARD_data: Processes CSV files with different modes (Generation, Consumption, etc.)
- getData: Cached function to retrieve data by year or year ranges

Created for the Klimaneutral-2024 project.
-------------------------------------------------------------------------------
"""
import pandas as pd
import os
from functools import lru_cache

def read_SMARD_data(path, mode):
    """
    Read and process SMARD data CSV files according to specified mode.
    
    Args:
        path (str): Path to the CSV file
        mode (str): Type of data - 'Generation', 'Consumption', 'Installed', 'Heatpump'
    
    Returns:
        pandas.DataFrame: Processed data with standardized column names
    """
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
    else:
        raise ValueError("Unbekannter Modus")

    # CSV-Datei laden mit optimierten Parametern
    # German-formatted CSV: semicolon separator, comma as decimal, period as thousands separator
    df = pd.read_csv(
        path,
        delimiter=";",
        thousands=".",
        decimal=",",
        usecols=usecols,
        dtype=dtype
    )

    # Manuell Datum konvertieren (entfernt str dtype für Datum)
    # Handle date formatting based on column names
    if "Datum von" in df.columns:
        df["Datum von"] = pd.to_datetime(df["Datum von"], format="%d.%m.%Y %H:%M", errors='coerce')
    elif "Datum" in df.columns and mode != "Installed":
        df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y %H:%M", errors='coerce')

    # Spalten direkt umbenennen für einheitliche Namensgebung in der gesamten Anwendung
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

    # Spezifische Anpassungen: Entferne Schalttage (29. Februar) für konsistente Jahresvergleiche
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
    The function uses lru_cache to avoid re-reading files that have been
    accessed recently, improving application performance.
    
    Args:
        type (str): Type of data to read ('Generation', 'Consumption', 'Installed', 'Heatpump')
        year (int, optional): Specific year to load
        start_year (int, optional): Start year for range
        end_year (int, optional): End year for range
    
    Returns:
        dict: Dictionary of dataframes by year or single dataframe for heatpump
    """
    directory_yearly = {}
    
    # Special case for Heatpump with no year specified
    # Heat pump profiles are template-based and not year-specific by default
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
        
    # If range of years is requested - build dictionary with year as key
    if start_year is not None and end_year is not None:
        for year in range(start_year, end_year + 1):
            df_year = _read_single_year(type, year)
            if df_year:
                directory_yearly[year] = df_year.get(year)
    
    return directory_yearly

def _read_single_year(type, year):
    """
    Helper function to read data for a single year with optimized reading
    
    Args:
        type (str): Type of data to read
        year (int): Year to load
        
    Returns:
        dict: Dictionary with year as key and dataframe as value, or None if error
    """
    try:
        # Bestimme den Dateipfad basierend auf dem Datentyp und Jahr
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
            # This allows using the template profile for specific years
            if "Datum" in df.columns:
                df["Datum"] = df["Datum"].apply(lambda x: x.replace(year=year))
        
        print(f"Data für {year} loaded successfully.")
        return {year: df}
    except Exception as e:
        print(f"Error loading data for {year}: {e}")
        return None
