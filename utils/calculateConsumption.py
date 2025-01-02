import pandas as pd
from utils.read_CSV import getData
from utils.combineDataFrames import combineDataFrames
from utils.extraploation_class import Extrapolation, Extrapolation_Consumption
from utils.addTimeInformation import addTimeInformation

def calculateConsumption(consumption_development_per_year): 
    directory_yearly_consumption = getData("Consumption")

    for year in range(2024,2031):
        prev_year_df =directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        extrapolated_data = Extrapolation(prev_year_df, year, None, None, None, consumption_development_per_year.get(year-1))        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year]= extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    
    return directory_yearly_consumption




def getConsumptionYear(year, data_df):
    return data_df.get(year)


def calculateConsumption_lastprofile(consumption_development_per_year, lastprofile_dict, directory_heatpump_consumption): 
    directory_yearly_consumption = getData("Consumption")
    addTimeInformation(directory_yearly_consumption[2023])
    base_heatpump_lp = directory_heatpump_consumption.get(2024)
    

    # lastprofil abziehen
    base_lastprofile_eauto = lastprofile_dict[2023].copy()
    saturday = ["6"]  # Samstag
    sunday = ["7"]  # Sonntag
    workday = ["1", "2", "3", "4", "5"]  # Montag bis Freitag

    for idx, row in directory_yearly_consumption[2023].iterrows():
        weekday = row['Weekday']
        lp = None
        
        if weekday in saturday:
            lp = base_lastprofile_eauto['saturday']
        elif weekday in sunday:
            lp = base_lastprofile_eauto['sunday']
        elif weekday in workday:
            lp = base_lastprofile_eauto['workday']
        else:
            continue


        # Berechnen Sie den Index im Lastprofil-DataFrame
        lastprofil_idx = idx % len(lp)

        print(lp)

        # Fügen Sie den Wert aus dem Lastprofil-DataFrame hinzu
        row['Gesamtverbrauch'] -= ((lp.loc[lastprofil_idx, 'Strombedarf (kWh)']/1000) + base_heatpump_lp.loc[idx, 'Verbrauch'])


    for year in range(2024,2031):
        prev_year_df = directory_yearly_consumption.get(year-1).copy()    #Kopie des Dataframe des letzten Jahres
        lastprofil_waermepumpe_year = directory_heatpump_consumption.get(year) #Lastprofil für Wärmepumpe
        lastprofil_eAuto_year = lastprofile_dict[year] #Lastprofil für eAuto

        extrapolated_data = Extrapolation_Consumption(prev_year_df, year, None, None, None, consumption_development_per_year.get(year-1), lastprofil_eAuto_year, lastprofil_waermepumpe_year)        #Erstellung eines neuen Objekts, mit einem DataFrame
        directory_yearly_consumption[extrapolated_data.year] = extrapolated_data.df   #DataFrame in das Erzeugungsverzeichnis gespeichert wird

    
    return directory_yearly_consumption
