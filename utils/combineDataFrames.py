import pandas as pd
from utils.addTimeInformation import addTimeInformation

def combineDataFrames(directory, startYear, endYear): #Funktion, die alle DataFrames aus dem jährlichen Verzeichnis zusammenführt
    filterdDirectory = {year: df for year, df in directory.items() if startYear <= year <= endYear} #Zusammenführung der dataFrames aus dem Dictionary zwischen den angegebenen Jahren und Speicherung in ein vorläufiges df
    combined_df = pd.concat(filterdDirectory.values()) #zusammenführung der Daten der gewünschten Jahre
    combined_df['Datum'] = pd.to_datetime(combined_df['Datum'], format='%d.%m.%Y %H:%M') #Formatierung der Datum Spalte in DateTime
    addTimeInformation(combined_df)
    return combined_df