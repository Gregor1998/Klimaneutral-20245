import pandas as pd #type: ignore

def performance_factors(directoryGeneration,directoryInstalled):
    directory_performance_factors = {}

    for year in range(2015,2024):
        #Faktoren für die Performance errechnen
        PV_factor = directoryInstalled[year]["Photovoltaik"].iloc[0]*0.25
        OnShore_factor = directoryInstalled[year]["Wind Onshore"].iloc[0] * 0.25
        OffShore_factor = directoryInstalled[year]["Wind Offshore"].iloc[0] * 0.25

        #Anlegung eines leeren DataFrames für die Performance Faktoren pro Viertelstunde
        
        performance_factors = pd.DataFrame(columns=["Datum","Photovoltaik", "Wind Onshore", "Wind Offshore"])

        #Befüllen des DataFrames mit den errechneten Performance
        performance_factors["Datum"] = directoryGeneration[year]["Datum"]  
        performance_factors["Photovoltaik"] = directoryGeneration[year]["Photovoltaik"] / PV_factor
        performance_factors["Wind Onshore"] = directoryGeneration[year]["Wind Onshore"] / OnShore_factor
        performance_factors["Wind Offshore"] = directoryGeneration[year]["Wind Offshore"] / OffShore_factor

        #Hinzufügen des DataFrames für das entsprechende Jahr zum Directory
        directory_performance_factors[year] = performance_factors


        
        directory_performance_factors[year].to_csv(f"Performance_Factors_{year}.csv", index = False)

    return directory_performance_factors

