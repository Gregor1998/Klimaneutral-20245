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
        
        

        #Überprüfung, ob eine Dunkelflaute vorliegt
        threshold = 0.1
        min_consecutive_quarter_hours = 288
        count = 0
        start_date = None

        for i in range(len(df)):
            if df.loc[i, 'combinedPerformanceFactor'] < threshold:
                if count == 0:
                    start_date = df.loc[i, 'Datum']
                count += 1
                if count >= min_consecutive_quarter_hours:
                    end_date = df.loc[i, 'Datum']
                    print(f"Es lag eine Dunkelflaute vom {start_date} bis zum {end_date} vor Anzahl Viertelstunden: {count}")
                    break
            else:
                count = 0
                start_date = None



    
       
    
    



        

    