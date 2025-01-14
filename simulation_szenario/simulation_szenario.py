import xlwings as xw
import papermill as pm
import pandas as pd
import os
from pathlib import Path
import sys


def clear_existing_images(sheet, image_filenames):
    """Remove existing images from the Excel sheet based on the provided filenames."""
    for picture in sheet.pictures:
        if any(filename in picture.name for filename in image_filenames):
            picture.delete()

    
def read_sheet_parameters(sheet):
    """
    Read simulation parameters and consumption development per year from the active Excel sheet.
    """
    # Read the table into a DataFrame
    df = sheet.range('A1').options(pd.DataFrame, header=1, expand='table').value

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
        'IST_installierte_waermepumpen', 'SOLL_installierte_waermepumpen', 'gridlost',
        'growth_rate_PV', 'growth_rate_Onshore', 'growth_rate_Offshore',
        'max_power_storage', 'max_storage_capicity', 'max_power_flexipowerplant',
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

# Disable the debugger warning
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

def main(sheet_name=None):
    wb = xw.Book.caller()
    if not sheet_name:
        sheet = wb.sheets.active  # Default to the active sheet if no sheet name is provided
    else:
        sheet = wb.sheets[sheet_name]  # Get the active sheet (the one where the button was clicked)

    sheet["F1"].value = "Simulation in progress..."  # Write a message to the Excel sheet

    images = [
        ('assets/plots/heatmap.png', 'B16'),
        ('assets/plots/residual_diagramm.png', 'B36'),
        ('assets/plots/summenhistogramm.png', 'B56'),
        ('assets/plots/vergleich_verbrauch_lastprofile.png', 'B75'),
        ('assets/plots/wochendiagramm_KW.png', 'B95'),
        ('CSV/Installed/installed_capacities_projections.png', 'B115')
    ]

    # Clear existing images before adding new ones
    clear_existing_images(sheet, [Path(img[0]).name for img in images])

    # Set the working directory to the project root
    base_dir = Path(__file__).resolve().parent.parent
    os.chdir(base_dir)

    # Set the Python path to the project root
    if str(base_dir) not in sys.path:
        sys.path.append(str(base_dir))

    # Read parameters from the active sheet
    params = read_sheet_parameters(sheet) #-> Simulations Parameter
    print(params)

    # Path to your Jupyter Notebook
    base_dir = Path(__file__).resolve().parent.parent
    notebook_path = os.path.join(base_dir, "prototyp_2.ipynb")
   # output_path = os.path.join(base_dir, "assets", "notebooks", "simulation_notebook_output.ipynb")

    # Run the notebook with the parameters
    pm.execute_notebook(
        input_path=notebook_path,
        output_path=notebook_path,
        parameters=params
    )


    
    # Add images to the Excel sheet
    for img_path, cell in images:
        image_path = os.path.join(base_dir, img_path)
        if os.path.exists(image_path):
            sheet.pictures.add(image_path, top=sheet[cell].top, left=sheet[cell].left, width=500, height=273)



    # Write Dataframes from Simulation back to Excel
    df1 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_consumption.csv"))
    sheet["O1"].value = "Verbrauch final pro 15min"
    sheet.range("O2").value = df1

    
    # Write DataFrames to the active sheet
    df2 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_production.csv"))
    sheet["K1"].value = "Erzeugung final pro 15min"
    sheet.range("K2").value = df2

     # Write Costs back to the active sheet
    df3 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "total_costs.csv"))
    sheet["T1"].value = "CAPEX-Berechnung"
    sheet.range("T2").value = df3




    # Example: Write a confirmation message back to Excel
    sheet["F1"].value = "Simulation completed!"
    print("Notebook executed successfully!")

if __name__ == "__main__":
    xw.Book("simulation_szenario.xlsm").set_mock_caller()
    main()
