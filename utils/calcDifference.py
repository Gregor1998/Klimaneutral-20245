import pandas as pd # type: ignore

# Verbrauch - Produktion
def differenceBetweenDataframes(df1, df2):
    
    if df1['Datum'].equals(df2['Datum']):
        # Berechne die Differenz zwischen Verbrauch und Produktion
        difference_df = pd.DataFrame()
        difference_df['Datum'] = df1['Datum']
        difference_df['Differenz'] =  df1['Gesamtverbrauch']- df2['Gesamterzeugung_EE']
        
        #print(difference_df)
        return difference_df
    else:
        #print("Die Zeitachsen der DataFrames stimmen nicht überein.")
        return None