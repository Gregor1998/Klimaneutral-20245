import pandas as pd
import os
from utils import config
eAutoskWh = config.params.eAutoskWh
eAutosNow = config.params.eAutosNow # 1.4 Mio eAutos in Deutschland Stand 2023
eAutosIncrease = config.params.eAutosIncrease # wieiviele eAutos kommen pro Jahr dazu
wochentage = ['Wochentag', 'Samstag', 'Sonntag']
lastprofilTypes = ['Wohnen', 'Büro', 'Öffentliche_Ladepunkte']
chargin_distribution = {
    'Wohnen': config.params.chargin_distribution_home,
    'Büro': config.params.chargin_distribution_office,
    'Öffentliche_Ladepunkte': config.params.chargin_distribution_public
}
# lastprofilType = Büro/Wohnen/Öffentliche_Ladepunkte
def calcLastprofil(year, eAutosAmount, lastprofilType):
    # read csv to dataframe
    # calculate values to dataframe
    # write dataframe to csv
    # lastprofil -> lp
    

    for tag in wochentage:

        filepath_lp = f'CSV/Lastprofile/eMobilitaet/base/{lastprofilType}/{tag}.csv'
        output_dir = f'CSV/Lastprofile/eMobilitaet/{year}/{lastprofilType}'
        output_filepath = f'{output_dir}/{tag}.csv'

        # Einlesen der CSV-Dateien
        lp = pd.read_csv(filepath_lp, delimiter=';')

       # Ersetze Komma durch Punkt und konvertiere die Spalte in numerische Werte
        lp['Relativer Bedarf'] = lp['Relativer Bedarf'].str.replace(',', '.').astype(float)


        #calculate other columns
        sum_relative_bedarf = lp['Relativer Bedarf'].sum()

        # Normalisierter Bedarf
        lp['Normierter Bedarf'] = lp['Relativer Bedarf'] / sum_relative_bedarf

        # Anzahl Autos
        lp['Anzahl Autos'] = lp['Normierter Bedarf'] * eAutosAmount

        # Strombedarf 
        lp['Strombedarf (kWh)'] = lp['Anzahl Autos'] * eAutoskWh

        # Erstelle das Verzeichnis, falls es nicht existiert
        os.makedirs(output_dir, exist_ok=True)

        # Schreibe den DataFrame in eine CSV-Datei
        lp.to_csv(output_filepath, index=False, sep=';')



for year in range(config.params.start_year_simulation-1, config.params.end_year_simulation+1):

    # für jeden Bereich die lastprofile für alle jahre berechnen (wohnen, büro, öffentliche ladepunkte)
    for lastprofilType in lastprofilTypes:
        
        # Berechne die Anzahl der eAutos pro Ladebereich
        eAutos_per_chargin_area = eAutosNow * chargin_distribution[lastprofilType]
        # Berechne das Lastprofil
        calcLastprofil(year, eAutos_per_chargin_area, lastprofilType)

    eAutosNow += eAutosIncrease