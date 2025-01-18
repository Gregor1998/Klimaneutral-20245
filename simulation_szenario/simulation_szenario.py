import xlwings as xw
import papermill as pm
import pandas as pd
import os
from pathlib import Path
import sys

# Disable the debugger warning
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"


def read_sheet_parameters(sheet):
    """
    Read simulation parameters and consumption development per year from the active Excel sheet.
    """
    # Read the table into a DataFrame
    df = sheet.range('B1').options(pd.DataFrame, header=1, expand='table').value

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Set 'Variable' as the index if not already set
    if df.index.name != 'Variable':
        df.set_index('Variable', inplace=True)

    # Convert the 'Wert' column to a dictionary for simulation parameters
    params = df['Wert'].dropna().to_dict()

    # Convert whole number values in `params` to integers
    for key, value in params.items():
        if isinstance(value, float) and value.is_integer():
            params[key] = int(value)

    # Numeric keys that may need special handling (e.g., German formatting with commas)
    numeric_keys = [
        'onshore_development_rate', 'offshore_development_rate', 'pv_development_rate',
        'CO2_factor_Kohle', 'CO2_factor_Gas', 'share_coal', 'share_gas',
        'IST_installierte_waermepumpen', 'SOLL_installierte_waermepumpen', 'eAutoskWh', 'eAutosNow', 'eAutosIncrease', 'chargin_distribution_public', 'chargin_distribution_office', 'chargin_distribution_home', 'gridlost',
        'growth_rate_PV', 'growth_rate_Onshore', 'growth_rate_Offshore',
        'max_power_storage', 'max_storage_capacity', 'max_power_flexipowerplant',
        'max_power_storage_start_year', 'capex_Onshore', 'capex_Offshore',
        'capex_PV_Dach_Kleinanlagen', 'capex_PV_Dach_Großanlagen', 'capex_PV_Freifläche', 'capex_Agri_PV',
        'capex_percentage_Dach_Kleinanlgage', 'capex_percentage_Dach_Großanlagen', 'capex_percentage_Freifläche', 'capex_percentage_Agri_PV',
        'capex_Bat_PV_klein', 'capex_Bat_PV_groß', 'capex_Bat_PV_frei',
        'capex_percentage_Bat_PV_klein', 'capex_percentage_Bat_PV_groß', 'capex_percentage_Bat_PV_frei',
        'capex_H2_Gasturbine', 'capex_H2_GuD', 'capex_percentage_H2_Gasturbine', 'capex_percentage_H2_GuD'
    ]

    for key in numeric_keys:
        if key in params:
            # Handle German-style decimal formatting (replace ',' with '.')
            try:
                params[key] = float(str(params[key]).replace(',', '.'))
            except ValueError:
                print(f"Warning: Could not convert parameter {key} to numeric value.")

    # Extract 'Verbrauchsentwicklung' per year
    if 'Jahr' in df.columns and 'Verbrauchsentwicklung' in df.columns:
        # Drop rows with missing years or Verbrauchsentwicklung values
        consumption_df = df.dropna(subset=['Jahr', 'Verbrauchsentwicklung'])

        # Convert 'Jahr' to integers and create a dictionary
        params['consumption_development_per_year'] = {
            int(year): float(value)
            for year, value in consumption_df[['Jahr', 'Verbrauchsentwicklung']].values
        }

    return params



def write_results_to_excel(base_dir, sheet_name, images, params):
    wb = xw.Book.caller()
    active_sheet_name = sheet_name
    result_sheet_name = f"{active_sheet_name}_result"

    # Delete the result sheet if it exists
    if result_sheet_name in [sheet.name for sheet in wb.sheets]:
        wb.sheets[result_sheet_name].delete()

    # Create a new result sheet
    result_sheet = wb.sheets.add(result_sheet_name)

    # Write images to the result sheet
    for img_path, cell in images:
        image_path = os.path.join(base_dir, img_path)
        if os.path.exists(image_path):
            result_sheet.pictures.add(image_path, top=result_sheet[cell].top, left=result_sheet[cell].left, width=500, height=273)

    # Write DataFrames to the result sheet
    df1 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_consumption.csv"))
    result_sheet["J1"].value = "Verbrauch final pro 15min (MWh)"
    result_sheet.range("J2").value = df1.columns.tolist()
    result_sheet.range("J3").value = df1.values.tolist()

     # Write DataFrames to the result sheet
    df1 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_consumption_ohne_lp.csv"))
    result_sheet["L1"].value = "Verbrauch ohne LP"
    result_sheet.range("L2").value = df1.columns.tolist()
    result_sheet.range("L3").value = df1.values.tolist()

    df2 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_production.csv"))
    result_sheet["N1"].value = "Erzeugung final pro 15min (MWh)"
    result_sheet.range("N2").value = df2.columns.tolist()
    result_sheet.range("N3").value = df2.values.tolist()

    df3 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_residual.csv"))
    result_sheet["AA1"].value = "Residuallast nach inklusion Flexiblen + Speicher (MWh)"
    result_sheet.range("AA2").value = df3.columns.tolist()
    result_sheet.range("AA3").value = df3.values.tolist()

    df4 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "further_demand.csv"))
    result_sheet["X1"].value = "Residuallast nach inklusion Flexiblen + Speicher (MWh)"
    result_sheet.range("X2").value = df4.values.tolist()

    df5 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "further_power.csv"))
    result_sheet.range("Y1").value = "Peak benötigte Leistung  von residual Erzeuger(MW)"
    result_sheet.range("Y2").value = df5.values.tolist()

    df6 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "total_costs.csv"))
    result_sheet["AF1"].value = "CAPEX-Berechnung €"
    result_sheet.range("AF2").value = df6.columns.tolist()
    result_sheet.range("AF3").value = df6.values.tolist()

    df7 = pd.read_csv(os.path.join(base_dir, 'CSV', 'Storage_co', f"{params['scenario_name']}_all_combined.csv"))
    result_sheet["AN1"].value = "Übersicht Erzeugung + Speicher + Flexible"
    result_sheet.range("AN2").value = df7.columns.tolist()
    result_sheet.range("AN3").value = df7.values.tolist()

    df8 = pd.read_csv(os.path.join(base_dir, "CSV", "Storage_co", f"{params['scenario_name']}_storage.csv"))
    result_sheet["AS1"].value = "Aktueller Speicherstand"
    result_sheet.range("AS2").value = df8.columns.tolist()
    result_sheet.range("AS3").value = df8.values.tolist()

    df9 = pd.read_csv(os.path.join(base_dir, "CSV", "Lastprofile","waermepumpe", "Hochrechnung", f"Heatpump_{params['end_year_simulation']}.csv"))
    result_sheet["AZ1"].value = "Lastprofil Wärmepumpe"
    result_sheet.range("AZ2").value = df9.columns.tolist()
    result_sheet.range("AZ3").value = df9.values.tolist()
 
    df10 = pd.read_csv(os.path.join(base_dir, "CSV", "Storage_co", "longest_positive_period.csv"))
    result_sheet["BC1"].value = "Längste Dunkelflaute"
    result_sheet.range("BC2").value = df10.columns.tolist()
    result_sheet.range("BC3").value = df10.values.tolist()

    df11 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "storage_values.csv"))
    result_sheet["BJ1"].value = "Speicherwerte"
    result_sheet.range("BJ2").value = df11.columns.tolist()
    result_sheet.range("BJ3").value = df11.values.tolist()
    print(f"Results written to '{result_sheet_name}'")

def main(sheet_name=None):
    wb = xw.Book.caller()
    if not sheet_name:
        sheet = wb.sheets.active  # Default to the active sheet if no sheet name is provided
        sheet_name = sheet.name
    else:
        sheet = wb.sheets[sheet_name]  # Get the active sheet (the one where the button was clicked)

    print(sheet)

    sheet["G1"].value = "Simulation in progress..."  # Write a message to the Excel sheet


    # Set the working directory to the project root
    base_dir = Path(__file__).resolve().parent.parent
    os.chdir(base_dir)

    # Set the Python path to the project root
    if str(base_dir) not in sys.path:
        sys.path.append(str(base_dir))

    # Read parameters from the active sheet
    params = read_sheet_parameters(sheet) #-> Simulations Parameter
    print(params)
    print(params['scenario_name'])

    # Path to your Jupyter Notebook
    base_dir = Path(__file__).resolve().parent.parent
    notebook_path = os.path.join(base_dir, "prototyp_2.ipynb")
   # output_path = os.path.join(base_dir, "assets", "notebooks", "simulation_notebook_output.ipynb")

    # Run the notebook with the parameters
    pm.execute_notebook(
        input_path=notebook_path,
        output_path=notebook_path,
        parameters=params,
        log_output=False  # Disable progress output
    )


    images = [
        ('assets/plots/heatmap_1_Differenz von EE und Verbrauch in MWh.png', 'A6'),
        ('assets/plots/heatmap_1_Überschüssige bzw. Restbedarf Energie nach maximal möglicher Nutzung von Speicher.png', 'A26'),
        ('assets/plots/heatmap_2_Überschüssige bzw. Restbedarf Energie nach zusätzlich optimalen Ausbau von Flexiblen.png', 'A46'),
        (f'assets/plots/heatmap_3_Überschüssige bzw. Restbedarf Energie mit Speicher ({params['scenario_name']}).png', 'A66'),
        (f'assets/plots/heatmap_4_Überschüssige bzw. Restbedarf Energie mit Speicher und Flexiblen ({params['scenario_name']}).png', 'A86'),
        ('assets/plots/wochendiagramm_KW.png', 'A106'),
        ('assets/plots/summenhistogramm.png', 'A126'),
        ('assets/plots/summenhistogramm_all.png', 'A146'),
        ('assets/plots/summenhistogramm_ee_storage.png', 'A166'),
        ('assets/plots/vergleich_verbrauch_lastprofile.png', 'A196'),
        ('CSV/Installed/installed_capacities_projections.png', 'A216'),
    ]
    
    write_results_to_excel(base_dir, sheet_name, images, params)




    # Example: Write a confirmation message back to Excel
    sheet["G1"].value = "Simulation completed!"
    print("Notebook executed successfully!")

if __name__ == "__main__":
    xw.Book("simulation_szenario/simulation_szenario.xlsm").set_mock_caller()
    main()

