import pandas as pd #type: ignore



def calculateGeneration(case_PV, case_WindOnshore, case_WindOffshore,df_performance, df_generation_start_year):
   #Erstellung eines leeren Directories für die Generation
   directoryGeneration = {}
   
   PV_generation = pd.DataFrame({"Photovoltaik":[0.0]*35040})
   Onshore_generation = pd.DataFrame({"Wind Onshore":[0.0]*35040})
   Offshore_generation = pd.DataFrame({"Wind Offshore":[0.0]*35040})


   #Anlegung eines leeren DataFrames für die Generation pro Viertelstunde
   generation_df = pd.DataFrame(columns=["Photovoltaik", "Wind Onshore", "Wind Offshore"])

   #Pfade zu den CSV-Dateien, je nach Case
   filepath_PV = f'CSV/Installed/{case_PV}_Photovoltaik_projections.csv'
   filepath_Onshore = f'CSV/Installed/{case_WindOnshore}_Wind Onshore_projections.csv'
   filepath_Offshore = f'CSV/Installed/{case_WindOffshore}_Wind Offshore_projections.csv'
   

   #Einlesen der CSV-Dateien
   df_PV = pd.read_csv(filepath_PV)
   df_Onshore = pd.read_csv(filepath_Onshore)
   df_Offshore = pd.read_csv(filepath_Offshore)


    #Alle Daten ab 2024 sind von Interesse, daher alle Zeilen der vorangegangenden Jahre entfernen
   df_filtered_PV = df_PV[df_PV['year']>=2024]
   df_filtered_PV.reset_index(drop=True, inplace=True)

   df_filtered_Onshore = df_Onshore[df_Onshore['year']>=2024]
   df_filtered_Onshore.reset_index(drop=True, inplace=True)

   df_filtered_Offshore = df_Offshore[df_Offshore['year']>=2024]
   df_filtered_Offshore.reset_index(drop=True, inplace=True)
   
   #Zusammenführen der Daten und Umbenennung der Spalten
   df_combined = pd.concat([df_filtered_PV,df_filtered_Onshore['predicted_capacity'],df_filtered_Offshore['predicted_capacity']],axis=1)

   #Umbenennung der Spalten
   df_combined.columns = ['Jahr','Photovoltaik','Wind Onshore','Wind Offshore'] 
 
   print(df_combined)
   directoryInstalled = {}

   for year in df_combined['Jahr']:
      #Ermittlung bei welchem Index sich das Jahr befindet
      index_year = df_combined.index[df_combined['Jahr']== year]
      
      #Anlegung eines leeren DataFrames für die installierte Leistung pro Jahr und Technologie
      installed_capacity = pd.DataFrame(columns=['Photovoltaik','Wind Onshore','Wind Offshore'])
      
      #Zuweisung der installierten Leistung pro Jahr und Technologie
      installed_capacity['Photovoltaik'] = df_combined['Photovoltaik'].iloc[index_year]
      installed_capacity['Wind Onshore'] = df_combined['Wind Onshore'].iloc[index_year]
      installed_capacity['Wind Offshore'] = df_combined['Wind Offshore'].iloc[index_year]
      
      #Abspeicherung der installierten Leistung pro Jahr und Technologie im Directory
      directoryInstalled[year] = installed_capacity
    
   print(directoryInstalled)
    

   for year in range(2024,2031):
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

      for day in range(365):
          start_index = day*96
          end_index = start_index + 96


          if directoryInstalled.get(year+1) is not None:
                PV_generation = (directoryInstalled[year]["Photovoltaik"].iloc[0] + dayly_expansion_rate_PV * day)* 0.25 * df_performance["Photovoltaik"][start_index:end_index]
                Onshore_generation = (directoryInstalled[year]["Wind Onshore"].iloc[0] + dayly_expansion_rate_Wind_Onshore * day) * 0.25 * df_performance["Wind Onshore"][start_index:end_index]
                Offshore_generation = (directoryInstalled[year]["Wind Offshore"].iloc[0] + dayly_expansion_rate_Wind_Offshore * day) * 0.25 * df_performance["Wind Offshore"][start_index:end_index]
                
                
          else:
                PV_generation = directoryInstalled[year]["Photovoltaik"].iloc[0] * 0.25 * df_performance["Photovoltaik"]
                Onshore_generation = directoryInstalled[year]["Wind Onshore"].iloc[0] * 0.25 * df_performance["Wind Onshore"]
                Offshore_generation = directoryInstalled[year]["Wind Offshore"].iloc[0] * 0.25 * df_performance["Wind Offshore"]
      
      combined_generation = pd.concat([PV_generation,Onshore_generation,Offshore_generation, df_generation_start_year['Wasserkraft'], df_generation_start_year['Biomasse'], df_generation_start_year['Sonstige Erneuerbare']],axis=1)
      directoryGeneration[year] = combined_generation

      
      

      #Netzverluste einebziehen
      combined_generation['Photovoltaik'] = combined_generation['Photovoltaik'] * 0.95279
      combined_generation['Wind Onshore'] = combined_generation['Wind Onshore'] * 0.95279
      combined_generation['Wind Offshore'] = combined_generation['Wind Offshore'] * 0.95279
      combined_generation['Wasserkraft'] = combined_generation['Wasserkraft'] * 0.95279
      combined_generation['Biomasse'] = combined_generation['Biomasse'] * 0.95279
      combined_generation['Sonstige Erneuerbare'] = combined_generation['Sonstige Erneuerbare'] * 0.95279
      
      directoryGeneration[year] = combined_generation
      
    #Abspeichern der Generation pro Jahr im Directory

   return directoryGeneration

    



