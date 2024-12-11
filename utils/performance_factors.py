import pandas as pd #type: ignore

def performance_factors(directoryGeneration,directoryInstalled):
    directory_performance_factors = {}
            #df.loc[row_indexer, "col"] = values`
    for year in range(2015,2024):
        
        if directoryInstalled.get(year+1) is not None: #überprüfung ob es den installierete Nennleistung des Folgejahres gibt
            #Tägliche Zubaurate errechnen
            dayly_expansion_rate_PV = (directoryInstalled[year+1]["Photovoltaik"].iloc[0] - directoryInstalled[year]["Photovoltaik"].iloc[0]) / 365
            dayly_expansion_rate_Wind_Onshore = (directoryInstalled[year+1]["Wind Onshore"].iloc[0] - directoryInstalled[year]["Wind Onshore"].iloc[0]) / 365
            dayly_expansion_rate_Wind_Offshore = (directoryInstalled[year+1]["Wind Offshore"].iloc[0] - directoryInstalled[year]["Wind Offshore"].iloc[0]) / 365
        else:
            #Faktoren für die Performance errechnen
            PV_factor = directoryInstalled[year]["Photovoltaik"].iloc[0]*0.25
            OnShore_factor = directoryInstalled[year]["Wind Onshore"].iloc[0] * 0.25
            OffShore_factor = directoryInstalled[year]["Wind Offshore"].iloc[0] * 0.25

        #Anlegung eines leeren DataFrames für die Performance Faktoren pro Viertelstunde
        
        performance_factors = pd.DataFrame(columns=["Datum","Photovoltaik", "Wind Onshore", "Wind Offshore"])
        performance_factors["Datum"] = directoryGeneration[year]["Datum"]  

        #Performance Faktoren errechnen, mit einer täglichen Zubaurate
        for day in range(365):
            start_index = day*96
            end_index = start_index + 96

            if directoryInstalled.get(year+1) is not None:
                PV_factor = (directoryInstalled[year]["Photovoltaik"].iloc[0] + dayly_expansion_rate_PV * day) * 0.25
                OnShore_factor = (directoryInstalled[year]["Wind Onshore"].iloc[0] + dayly_expansion_rate_Wind_Onshore * day) * 0.25
                OffShore_factor = (directoryInstalled[year]["Wind Offshore"].iloc[0] + dayly_expansion_rate_Wind_Offshore * day) * 0.25

                performance_factors.loc[start_index:end_index, "Photovoltaik"] = directoryGeneration[year]["Photovoltaik"][start_index:end_index] / PV_factor
                performance_factors.loc[start_index:end_index, "Wind Onshore"] = directoryGeneration[year]["Wind Onshore"][start_index:end_index] / OnShore_factor
                performance_factors.loc[start_index:end_index, "Wind Offshore"] = directoryGeneration[year]["Wind Offshore"][start_index:end_index] / OffShore_factor
        
            #Befüllen des DataFrames mit den errechneten Performance-faktoren, falls es kein Folgejahr gibt
            else:
                performance_factors["Photovoltaik"] = directoryGeneration[year]["Photovoltaik"] / PV_factor
                performance_factors["Wind Onshore"] = directoryGeneration[year]["Wind Onshore"] / OnShore_factor
                performance_factors["Wind Offshore"] = directoryGeneration[year]["Wind Offshore"] / OffShore_factor

            

        #Hinzufügen des DataFrames für das entsprechende Jahr zum Directory
        directory_performance_factors[year] = performance_factors

    return directory_performance_factors

