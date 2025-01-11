import xlwings as xw
import pandas as pd
import os
from pathlib import Path

def process_opened_excel(wb):
    # Aktive Excel-Arbeitsmappe abrufen
    
    szenarien = {}

    # Lade alle Tabellen der geöffneten Arbeitsmappe
    for sheet in wb.sheets:
        df = sheet.range('A1').options(pd.DataFrame, header=1, index=False, expand='table').value
        if "Jahr" in df.columns:  # Überprüfung, ob die Tabelle relevante Daten enthält
            szenarien[sheet.name] = {
        'consumption_development_per_year': df.set_index('Jahr')['Verbrauchsentwicklung'].dropna().to_dict(),
        'onshore_development_rate': df.loc[df['Variable'] == 'onshore_development_rate', 'Wert'].values[0],
        'offshore_development_rate': df.loc[df['Variable'] == 'offshore_development_rate', 'Wert'].values[0],
        'pv_development_rate': df.loc[df['Variable'] == 'pv_development_rate', 'Wert'].values[0],
        'CO2_factor_Kohle': df.loc[df['Variable'] == 'CO2_factor_Kohle', 'Wert'].values[0],
        'CO2_factor_Gas': df.loc[df['Variable'] == 'CO2_factor_Gas', 'Wert'].values[0],
        'share_coal': df.loc[df['Variable'] == 'share_coal', 'Wert'].values[0],
        'share_gas': df.loc[df['Variable'] == 'share_gas', 'Wert'].values[0],
        'IST_installierte_waermepumpen': df.loc[df['Variable'] == 'IST_installierte_waermepumpen', 'Wert'].values[0],
        'SOLL_installierte_waermepumpen': df.loc[df['Variable'] == 'SOLL_installierte_waermepumpen', 'Wert'].values[0],
        'netzverluste': df.loc[df['Variable'] == 'netzverluste', 'Wert'].values[0],
        # Weitere Parameter hier extrahieren...
    }
   
    output_df = pd.DataFrame(szenarien)

    sheet_name = "Scenario Results"
    if sheet_name in [sheet.name for sheet in wb.sheets]:
        new_sheet = wb.sheets[sheet_name]
        new_sheet.clear()  # Clear existing content
    else:
        new_sheet = wb.sheets.add(name=sheet_name, after=wb.sheets[-1])

    new_sheet["F1"].value = output_df


    # Resolve the correct image path relative to main.py
    base_dir = Path(__file__).resolve().parent.parent  # Get the directory of the current script
    image_path = os.path.join(base_dir, 'assets', 'plots', 'heatmap.png')  # Build the full path
    
    new_sheet.pictures.add(image_path, top=wb.sheets[0]["F5"].top, left=wb.sheets[0]["F5"].left,width=300,height=200)



    
# Szenarien ausgeben zur Kontrolle

def main():
    wb = xw.Book.caller()
    sheet = wb.sheets[0]
    
    process_opened_excel(wb)

if __name__ == "__main__":
    xw.Book("IPJ.xlsm").set_mock_caller()
    main()
