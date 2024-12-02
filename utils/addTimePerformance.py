import pandas as pd

def addTimePerformance(df,year):
    #Startdatumund Enddatum definieren:
    start_date  = f'{year}-01-01 00:00:00'
    end_date    = f'{year}-12-31 23:45:00'

    #Zeitreiehe in 15 min Takt erstellen
    time_range = pd.date_range(start=start_date, end=end_date, freq='15T')

    #Überprüfen, ob die Lännge der Zeitreihe mit der Länge des übergebenen DataFrames übereinstimmt
    if len(df) != len(time_range):
        raise ValueError('Length of DataFrame and Time Range do not match')
    else:
        #Zeitreihe als erste Spalte in den DataFrame einfügen
        df.insert(0,'Datum',time_range)

        #Zeitspalte korrekt formatieren
        df['Datum'] = pd.to_datetime(df['Datum'], format= '%d.%m.%Y %H:%M')

    return df

