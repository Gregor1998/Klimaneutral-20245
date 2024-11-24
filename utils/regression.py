import numpy as np # type: ignore
import pandas as pd # type: ignore
from sklearn.linear_model import LinearRegression

def regression(directory_yearly_installed: dict) -> pd.DataFrame:
    # Daten für die Jahre 2015-2023 extrahieren
    years = np.array([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]).reshape(-1, 1)
    installed_capacity_pv = np.array([directory_yearly_installed[year]["Photovoltaik"].iloc[0] for year in years.flatten()])
    installed_capacity_onshore = np.array([directory_yearly_installed[year]["Wind Onshore"].iloc[0] for year in years.flatten()])
    installed_capacity_offshore = np.array([directory_yearly_installed[year]["Wind Offshore"].iloc[0] for year in years.flatten()])

    # Lineare Regression Modelle erstellen
    model_pv = LinearRegression().fit(years, installed_capacity_pv)
    model_onshore = LinearRegression().fit(years, installed_capacity_onshore)
    model_offshore = LinearRegression().fit(years, installed_capacity_offshore)

    # Jahre bis 2030
    future_years = np.array(range(2024, 2031)).reshape(-1, 1)

    # Vorhersagen für die zukünftigen Jahre
    predicted_pv = model_pv.predict(future_years)
    predicted_onshore = model_onshore.predict(future_years)
    predicted_offshore = model_offshore.predict(future_years)

    # Ergebnisse anzeigen
    predicted_data = pd.DataFrame({
        "Jahr": future_years.flatten(),
        "Photovoltaik": predicted_pv,
        "Wind Onshore": predicted_onshore,
        "Wind Offshore": predicted_offshore
    })

    return predicted_data

# Daten für die Jahre 2015-2023 extrahieren
years = np.array([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]).reshape(-1, 1)
installed_capacity_pv = np.array([directory_yearly_installed[year]["Photovoltaik"].iloc[0] for year in years.flatten()])
installed_capacity_onshore = np.array([directory_yearly_installed[year]["Wind Onshore"].iloc[0] for year in years.flatten()])
installed_capacity_offshore = np.array([directory_yearly_installed[year]["Wind Offshore"].iloc[0] for year in years.flatten()])

# Lineare Regression Modelle erstellen
model_pv = LinearRegression().fit(years, installed_capacity_pv)
model_onshore = LinearRegression().fit(years, installed_capacity_onshore)
model_offshore = LinearRegression().fit(years, installed_capacity_offshore)

# Jahre bis 2030
future_years = np.array(range(2024, 2031)).reshape(-1, 1)

# Vorhersagen für die zukünftigen Jahre
predicted_pv = model_pv.predict(future_years)
predicted_onshore = model_onshore.predict(future_years)
predicted_offshore = model_offshore.predict(future_years)

# Ergebnisse anzeigen
predicted_data = pd.DataFrame({
    "Jahr": future_years.flatten(),
    "Photovoltaik": predicted_pv,
    "Wind Onshore": predicted_onshore,
    "Wind Offshore": predicted_offshore
})

print(predicted_data)