# =============================================================================
# determinePerformanceSzenarios.py
# =============================================================================
# This module analyzes historical performance data for renewable energy sources
# (Photovoltaic, Wind Onshore, Wind Offshore) and determines different performance
# scenarios (Best Case, Worst Case, and Average Case) based on this data.
# The function processes yearly performance data from 2015 to 2023 to help
# model future energy production scenarios for climate neutrality planning.
# =============================================================================

import pandas as pd #type: ignore

def determinePerformanceSzenarios(directory_performance):   #Funktion zur Ermittlung der verschiedenen Szenarien
    """
    Analyzes historical performance data and generates different performance scenarios.
    
    Parameters:
        directory_performance: Dictionary with yearly performance data (key=year, value=DataFrame)
        
    Returns:
        Dictionary containing DataFrames for BestCase, WorstCase, and AverageCase scenarios
    """
    directory_szenarios = {}    #Dictionary für die verschiedenen Szenarien (Dort sind die DataFrames für die Szenarien hinterlegt)
    meanPerformanceFactors=pd.DataFrame(columns=["Jahr","Photovoltaik","Wind Onshore","Wind Offshore"]) #Leeres DataFrame für die mittleren Performance Faktoren
    
    #Schleife für die Jahre 2015-2023, die die mittleren Performance Faktoren für die Szenarien berechnet
    for year in range(2015,2024):
        # Calculate average performance factors for each technology for the current year
        meanPV=directory_performance[year]["Photovoltaik"].mean()
        meanOnshore=directory_performance[year]["Wind Onshore"].mean()
        meanOffshore=directory_performance[year]["Wind Offshore"].mean()
        meanPerformanceFactors = pd.concat([meanPerformanceFactors, pd.DataFrame([{"Jahr": year, "Photovoltaik": meanPV, "Wind Onshore": meanOnshore, "Wind Offshore": meanOffshore}])], ignore_index=True)

    #Ermittlung des besten, schlechtesten Jahr pro Technologie
    # Identify years with highest and lowest performance for each technology
    bestPV = meanPerformanceFactors.loc[meanPerformanceFactors["Photovoltaik"].idxmax()]
    worstPV = meanPerformanceFactors.loc[meanPerformanceFactors["Photovoltaik"].idxmin()]

    bestOnshore = meanPerformanceFactors.loc[meanPerformanceFactors["Wind Onshore"].idxmax()]
    worstOnshore = meanPerformanceFactors.loc[meanPerformanceFactors["Wind Onshore"].idxmin()]

    bestOffshore = meanPerformanceFactors.loc[meanPerformanceFactors["Wind Offshore"].idxmax()]
    worstOffshore = meanPerformanceFactors.loc[meanPerformanceFactors["Wind Offshore"].idxmin()]

    # Create best case and worst case scenarios by combining the best/worst years for each technology
    bestCase = pd.concat([directory_performance[bestPV["Jahr"]]["Photovoltaik"], directory_performance[bestOnshore["Jahr"]]["Wind Onshore"], directory_performance[bestOffshore["Jahr"]]["Wind Offshore"]], axis=1)
    worstCase = pd.concat([directory_performance[worstPV["Jahr"]]["Photovoltaik"], directory_performance[worstOnshore["Jahr"]]["Wind Onshore"], directory_performance[worstOffshore["Jahr"]]["Wind Offshore"]], axis=1)

    #Ermittlung eines durchschnittlichen Jahres über die letzten 8 Jahre
    meanOveralldf = pd.DataFrame(columns=["Photovoltaik","Wind Onshore","Wind Offshore"])    #Leeres DataFrame für den durchschnittlichen Jahresverlauf
    averagePV = pd.DataFrame()    #Leeres DataFrame für den durchschnittlichen Jahresverlauf
    averageOnshore = pd.DataFrame()  #Leeres DataFrame für den durchschnittlichen Jahresverlauf
    averageOffshore = pd.DataFrame()    #Leeres DataFrame für den durchschnittlichen Jahresverlauf
    num_years = len(directory_performance)  #Anzahl der Jahre, die in dem Dictonary "directory_performance" hinterlegt sind

    #Iteration über jedes Jahr im Directory
    for year, df in directory_performance.items():
        # Aggregate each technology's performance data across all years
        averagePV = averagePV.add(df[["Photovoltaik"]],fill_value=0)
        averageOnshore = averageOnshore.add(df[["Wind Onshore"]],fill_value=0)
        averageOffshore = averageOffshore.add(df[["Wind Offshore"]],fill_value=0)

    # Calculate average performance by dividing by the number of years   
    averagePV /= num_years
    averageOnshore /= num_years
    averageOffshore /= num_years

    #zusammenführung der durchschnittlichen Performance Faktoren
    meanOveralldf = pd.concat([averagePV, averageOnshore, averageOffshore], axis=1)

    # Store all scenarios in the result dictionary
    directory_szenarios["BestCase"] = bestCase
    directory_szenarios["WorstCase"] = worstCase
    directory_szenarios["AverageCase"] = meanOveralldf
    
    return directory_szenarios