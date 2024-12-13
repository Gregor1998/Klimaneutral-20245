import pandas as pd
from utils.read_CSV import getData
from utils.combineDataFrames import combineDataFrames
from utils.extraploation_class import Extrapolation, Extrapolation_Consumption

def calculateConsumption(consumption_development_per_year): 
    directory_yearly_consumption = getData("Consumption")

    for year in range(2024,2031):
        prev_year_df =directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        extrapolated_data = Extrapolation(prev_year_df, year, None, None, None, consumption_development_per_year.get(year-1))        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year]= extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    
    return directory_yearly_consumption




def getConsumptionYear(year, data_df):
    return data_df.get(year)


def calculateConsumption_lastprofile(consumption_development_per_year, lastprofile_dict): 
   
    directory_yearly_consumption = getData("Consumption")

    for year in range(2024,2031):
        prev_year_df =directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        extrapolated_data = Extrapolation_Consumption(prev_year_df, year, None, None, None, consumption_development_per_year.get(year-1), lastprofile_dict)        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year]= extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    
    return directory_yearly_consumption
