import pandas as pd # type: ignore

def dunkelflautePerformanceFactor(directoryPerformance):
    directoryDunkelflaute = {}
    
    for year in range(2015,2024):
        #Erstellen eines Dataframes zur Analyse von Dunkelflauten
        df = pd.DataFrame(columns=['Datum', 'combinedPerformanceFactor'])
        #Hinzufügen der Datumsspalte
        df['Datum'] = directoryPerformance[year]['Datum'] 

        #Zusammenrechnung der Performancefaktoren, um Durchschnitts-Performancefaktor zu erhalten
        df['combinedPerformanceFactor'] = (directoryPerformance[year]['Wind Offshore'] + directoryPerformance[year]['Wind Onshore'] + directoryPerformance[year]['Photovoltaik'])/3
        
        #Hinzufügen des Dataframes zum Dictionary
        directoryDunkelflaute[year] = df

    
       
    
    



        

    