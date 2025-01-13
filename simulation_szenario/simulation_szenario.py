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
    """Read simulation parameters and consumption development per year from the active Excel sheet."""
    # Read the table into a DataFrame
    df = sheet.range('A1').options(pd.DataFrame, header=1, expand='table').value

    # Strip whitespace from column names to avoid issues
    df.columns = df.columns.str.strip()

    # Convert the 'Wert' column to a dictionary for simulation parameters
    params = df['Wert'].to_dict()

    # Drop rows with missing or non-finite values in 'Jahr'
    df = df.dropna(subset=['Jahr'])

    # Convert 'Jahr' to integers
    df['Jahr'] = df['Jahr'].astype(int)

    # Extract 'Verbrauchsentwicklung' per year with integer keys
    consumption_development = {
        int(year): value for year, value in df.set_index('Jahr')['Verbrauchsentwicklung'].dropna().to_dict().items()
    }

    # Add the consumption development to the params dictionary
    params['consumption_development_per_year'] = consumption_development

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




    # Example: Write a confirmation message back to Excel
    sheet["F1"].value = "Simulation completed!"
    print("Notebook executed successfully!")

if __name__ == "__main__":
    xw.Book("simulation_szenario.xlsm").set_mock_caller()
    main()
