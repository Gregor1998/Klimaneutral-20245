"""
Simulation Scenario Execution Framework

This script provides an interface between Excel and a simulation Jupyter notebook
for energy scenario modeling. It enables users to:
1. Define simulation parameters in Excel sheets
2. Run complex energy simulations using Papermill to execute a Jupyter notebook
3. Process and visualize results
4. Write results back to Excel sheets for analysis

The workflow is:
- Read parameters from an Excel sheet
- Execute a simulation notebook with those parameters
- Generate visualizations and statistics
- Write results back to an Excel result sheet

This file is meant to be called from Excel using xlwings.
"""

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
    
    Parameters:
        sheet: xlwings Sheet object - The Excel sheet containing parameter data
        
    Returns:
        dict: Dictionary of simulation parameters with formatted values
    """
    # Read the table into a DataFrame
    df = sheet.range('B1').options(pd.DataFrame, header=1, expand='table').value
    
    # Strip whitespace from column names for consistent handling
    df.columns = df.columns.str.strip()

    # Set 'Variable' as the index if not already set
    if df.index.name != 'Variable':
        df.set_index('Variable', inplace=True)

    # Convert the 'Wert' column to a dictionary for simulation parameters
    params = df['Wert'].dropna().to_dict()

    # Convert whole number values in `params` to integers for cleaner processing
    for key, value in params.items():
        if isinstance(value, float) and value.is_integer():
            params[key] = int(value)

    # Numeric keys that may need special handling (e.g., German formatting with commas)
    # These are all the parameters that should be converted to numeric values
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

    # Handle special formatting for numeric values (e.g., German decimal format)
    for key in numeric_keys:
        if key in params:
            # Handle German-style decimal formatting (replace ',' with '.')
            try:
                params[key] = float(str(params[key]).replace(',', '.'))
            except ValueError:
                print(f"Warning: Could not convert parameter {key} to numeric value.")

    # Extract 'Verbrauchsentwicklung' per year if available in the sheet
    if 'Jahr' in df.columns and 'Verbrauchsentwicklung' in df.columns:
        # Drop rows with missing years or Verbrauchsentwicklung values
        consumption_df = df.dropna(subset=['Jahr', 'Verbrauchsentwicklung'])

        # Convert 'Jahr' to integers and create a dictionary of consumption development by year
        params['consumption_development_per_year'] = {
            int(year): float(value)
            for year, value in consumption_df[['Jahr', 'Verbrauchsentwicklung']].values
        }

    return params


def write_results_to_excel(base_dir, sheet_name, images, params):
    """
    Write simulation results to a new Excel sheet, including visualizations and data tables.
    
    Parameters:
        base_dir: Path to the project root directory
        sheet_name: Name of the original Excel sheet with parameters
        images: List of tuples with (image_path, cell_position) for plot placement
        params: Dictionary of simulation parameters
    """
    wb = xw.Book.caller()
    active_sheet_name = sheet_name
    result_sheet_name = f"{active_sheet_name}_result"

    # Delete the result sheet if it exists to avoid duplicate content
    if result_sheet_name in [sheet.name for sheet in wb.sheets]:
        wb.sheets[result_sheet_name].delete()

    # Create a new result sheet
    result_sheet = wb.sheets.add(result_sheet_name)

    # Add visualization plots to the result sheet
    for img_path, cell in images:
        image_path = os.path.join(base_dir, img_path)
        if os.path.exists(image_path):
            result_sheet.pictures.add(image_path, top=result_sheet[cell].top, left=result_sheet[cell].left, width=500, height=273)

    # --- Add data tables to the result sheet ---
    
    # Final consumption data (15-minute intervals)
    df1 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_consumption.csv"))
    result_sheet["J1"].value = "Verbrauch final pro 15min (MWh)"
    result_sheet.range("J2").value = df1.columns.tolist()
    result_sheet.range("J3").value = df1.values.tolist()

    # Consumption without load profile
    df1 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_consumption_ohne_lp.csv"))
    result_sheet["L1"].value = "Verbrauch ohne LP"
    result_sheet.range("L2").value = df1.columns.tolist()
    result_sheet.range("L3").value = df1.values.tolist()

    # Energy production data (15-minute intervals)
    df2 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_production.csv"))
    result_sheet["N1"].value = "Erzeugung final pro 15min (MWh)"
    result_sheet.range("N2").value = df2.columns.tolist()
    result_sheet.range("N3").value = df2.values.tolist()

    # Residual load after flexible sources and storage
    df3 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "final_residual.csv"))
    result_sheet["AA1"].value = "Residuallast nach inklusion Flexiblen + Speicher (MWh)"
    result_sheet.range("AA2").value = df3.columns.tolist()
    result_sheet.range("AA3").value = df3.values.tolist()

    # Additional demand data
    df4 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "further_demand.csv"))
    result_sheet["X1"].value = "Residuallast nach inklusion Flexiblen + Speicher (MWh)"
    result_sheet.range("X2").value = df4.values.tolist()

    # Peak power requirements from residual generators
    df5 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "further_power.csv"))
    result_sheet.range("Y1").value = "Peak benötigte Leistung  von residual Erzeuger(MW)"
    result_sheet.range("Y2").value = df5.values.tolist()

    # Capital expenditure (CAPEX) calculations
    df6 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "total_costs.csv"))
    result_sheet["AF1"].value = "CAPEX-Berechnung €"
    result_sheet.range("AF2").value = df6.columns.tolist()
    result_sheet.range("AF3").value = df6.values.tolist()

    # Production, storage and flexible sources overview
    df7 = pd.read_csv(os.path.join(base_dir, 'CSV', 'Storage_co', f"{params['scenario_name']}_all_combined.csv"))
    result_sheet["AN1"].value = "Übersicht Erzeugung + Speicher + Flexible"
    result_sheet.range("AN2").value = df7.columns.tolist()
    result_sheet.range("AN3").value = df7.values.tolist()

    # Current storage levels
    df8 = pd.read_csv(os.path.join(base_dir, "CSV", "Storage_co", f"{params['scenario_name']}_storage.csv"))
    result_sheet["AS1"].value = "Aktueller Speicherstand"
    result_sheet.range("AS2").value = df8.columns.tolist()
    result_sheet.range("AS3").value = df8.values.tolist()

    # Heat pump load profile for the simulation end year
    df9 = pd.read_csv(os.path.join(base_dir, "CSV", "Lastprofile","waermepumpe", "Hochrechnung", f"Heatpump_{params['end_year_simulation']}.csv"))
    result_sheet["AZ1"].value = "Lastprofil Wärmepumpe"
    result_sheet.range("AZ2").value = df9.columns.tolist()
    result_sheet.range("AZ3").value = df9.values.tolist()
 
    # Data on longest period of energy shortage ("Dunkelflaute")
    df10 = pd.read_csv(os.path.join(base_dir, "CSV", "Storage_co", "longest_positive_period.csv"))
    result_sheet["BC1"].value = "Längste Dunkelflaute"
    result_sheet.range("BC2").value = df10.columns.tolist()
    result_sheet.range("BC3").value = df10.values.tolist()

    # Storage capacity values
    df11 = pd.read_csv(os.path.join(base_dir, "CSV", "Results", "storage_values.csv"))
    result_sheet["BJ1"].value = "Speicherwerte"
    result_sheet.range("BJ2").value = df11.columns.tolist()
    result_sheet.range("BJ3").value = df11.values.tolist()
    
    print(f"Results written to '{result_sheet_name}'")


def main(sheet_name=None):
    """
    Main function to execute the simulation process.
    
    Parameters:
        sheet_name: Name of the Excel sheet containing parameters (optional)
                    If not provided, uses the active sheet
    """
    # Connect to the Excel workbook
    wb = xw.Book.caller()
    if not sheet_name:
        sheet = wb.sheets.active  # Default to the active sheet if no sheet name is provided
        sheet_name = sheet.name
    else:
        sheet = wb.sheets[sheet_name]  # Get the specified sheet

    print(sheet)

    # Display a status message in Excel to inform the user
    sheet["G1"].value = "Simulation in progress..."

    # --- Set up environment ---
    
    # Set the working directory to the project root
    base_dir = Path(__file__).resolve().parent.parent
    os.chdir(base_dir)

    # Set the Python path to the project root
    if str(base_dir) not in sys.path:
        sys.path.append(str(base_dir))

    # Read parameters from the active sheet
    params = read_sheet_parameters(sheet)
    print(params)
    print(params['scenario_name'])

    # --- Execute the simulation notebook ---
    
    # Path to the Jupyter Notebook containing the simulation logic
    base_dir = Path(__file__).resolve().parent.parent
    notebook_path = os.path.join(base_dir, "prototyp_2.ipynb")
    
    # Execute the notebook with the parameters using Papermill
    # This runs the entire simulation with the specified parameters
    pm.execute_notebook(
        input_path=notebook_path,
        output_path=notebook_path,  # Overwrite the input notebook with results
        parameters=params,
        log_output=False  # Disable progress output
    )

    # --- Process results ---
    
    # Define the visualization images to include in the results
    images = [
        ('assets/plots/heatmap_1_Differenz von EE und Verbrauch in MWh.png', 'A6'),
        ('assets/plots/heatmap_1_Überschüssige bzw. Restbedarf Energie nach maximal möglicher Nutzung von Speicher.png', 'A26'),
        ('assets/plots/heatmap_2_Überschüssige bzw. Restbedarf Energie nach zusätzlich optimalen Ausbau von Flexiblen.png', 'A46'),
        (f'assets/plots/heatmap_3_Überschüssige bzw. Restbedarf Energie mit Speicher ({params["scenario_name"]}).png', 'A66'),
        (f'assets/plots/heatmap_4_Überschüssige bzw. Restbedarf Energie mit Speicher und Flexiblen ({params["scenario_name"]}).png', 'A86'),
        (f'assets/plots/wochendiagramm_KW_week{params["selected_week_plot"]}_{params["selected_year_plot"]}.png', 'A106'),
        ('assets/plots/summenhistogramm.png', 'A126'),
        ('assets/plots/summenhistogramm_all.png', 'A146'),
        ('assets/plots/summenhistogramm_ee_storage.png', 'A166'),
        ('assets/plots/vergleich_verbrauch_lastprofile.png', 'A196'),
        ('CSV/Installed/installed_capacities_projections.png', 'A216'),
    ]
    
    # Write all results back to Excel
    write_results_to_excel(base_dir, sheet_name, images, params)

    # Update the status message to indicate completion
    sheet["G1"].value = "Simulation completed!"
    print("Notebook executed successfully!")


if __name__ == "__main__":
    # When running this script directly, set up a mock Excel caller for testing
    xw.Book("simulation_szenario/simulation_szenario.xlsm").set_mock_caller()
    main()
