import pandas as pd
import xlwings as xw
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

# Alle Tabellen aus der Excel-Datei laden
#excel_file = pd.ExcelFile('szenarioDefinition/szenario_parameter.xlsx')
#szenarien = {}

def process_opened_excel():
    # Aktive Excel-Arbeitsmappe abrufen
    wb = xw.Book.caller()
    excel_file = wb.fullname  # Pfad zur geöffneten Datei
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
    print(szenarien)

    plot_example()
    insert_dynamic_content_with_xlwings()
# Szenarien ausgeben zur Kontrolle


def plot_example():
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 15, 25, 30]
    plt.plot(x, y)
    plt.title("Beispieldiagramm")
    plt.savefig("diagramm.png")
    plt.close()

def insert_dynamic_content_with_xlwings():
    wb = xw.Book("szenarioDefinition/szenario_parameter.xlsx")
    sheet = wb.sheets["Szenario 1 - Best_Best"]
    
    # Text hinzufügen
    sheet.range("A13").value = "Klimaziel-Analyse"
    sheet.range("A14").value = "Simulationsergebnisse:"
    
    # Diagramm dynamisch einfügen
    plot_example()
    sheet.pictures.add("diagramm.png", top=sheet.range("A17").top, left=sheet.range("A17").left)
    
    wb.save("szenarioDefinition/szenario_parameter.xlsx")
    wb.close()

process_opened_excel()








# Excel-Datei lesen
"""df = pd.read_excel('szenarioDefinition/szenario_parameter.xlsx')

# Variablen zuweisen
consumption_development_per_year = df.set_index('Jahr')['Verbrauchsentwicklung'].dropna().to_dict()
onshore_development_rate = df.loc[df['Variable'] == 'onshore_development_rate', 'Wert'].values[0]
offshore_development_rate = df.loc[df['Variable'] == 'offshore_development_rate', 'Wert'].values[0]
pv_development_rate = df.loc[df['Variable'] == 'pv_development_rate', 'Wert'].values[0]
CO2_factor_Kohle = df.loc[df['Variable'] == 'CO2_factor_Kohle', 'Wert'].values[0]
CO2_factor_Gas = df.loc[df['Variable'] == 'CO2_factor_Gas', 'Wert'].values[0]
share_coal = df.loc[df['Variable'] == 'share_coal', 'Wert'].values[0]
share_gas = df.loc[df['Variable'] == 'share_gas', 'Wert'].values[0]
IST_installierte_waermepumpen = df.loc[df['Variable'] == 'IST_installierte_waermepumpen', 'Wert'].values[0]
SOLL_installierte_waermepumpen = df.loc[df['Variable'] == 'SOLL_installierte_waermepumpen', 'Wert'].values[0]
netzverluste = df.loc[df['Variable'] == 'netzverluste', 'Wert'].values[0]

# Ausgabe zur Überprüfung
print(consumption_development_per_year)
print(onshore_development_rate)
print(offshore_development_rate)
print(pv_development_rate)
print(CO2_factor_Kohle)
print(CO2_factor_Gas)
print(share_coal)
print(share_gas)
print(IST_installierte_waermepumpen)
print(SOLL_installierte_waermepumpen)
print(netzverluste)"""