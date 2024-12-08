import pandas as pd
from utils.read_CSV import getData
from utils.combineDataFrames import combineDataFrames
from utils.extraploation_class import Extrapolation

def calculateConsumption(consumption_development_rate): 
    directory_yearly_consumption = getData("Verbrauch")

    for year in range(2024,2031):
        prev_year_df =directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        extrapolated_data = Extrapolation(prev_year_df, year, None, None, None, consumption_development_rate)        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year]= extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    #consumption_extrapolation = combineDataFrames(directory_yearly_consumption,2023,2031)
    
    return directory_yearly_consumption



def getConsumptionYear(year, data_df):
    return data_df.get(year)



def calculateConsumption_lastprofile(consumption_development_rate): 
    path = 'CSV/Lastprofil/lastprofil_1.csv'
    lastprofil_weekday = pd.read_csv(path,delimiter= ';', thousands='.', decimal=',', dayfirst ="True") #, parse_dates=[[0,1]]

    #Herauslöschen der Spalte Datum bis, da diese keine zusätzlichen Informationen bietet
    lastprofil_weekday.drop(columns=["Datum bis"], inplace=True)



    directory_yearly_consumption = getData("Verbrauch")

    for year in range(2024,2031):
        prev_year_df =directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        extrapolated_data = Extrapolation(prev_year_df, year, None, None, None, consumption_development_rate)        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year]= extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    #consumption_extrapolation = combineDataFrames(directory_yearly_consumption,2023,2031)
    
    return directory_yearly_consumption
