from utils.addTimeInformation import addTimeInformation
from typing import override
import pdb

"""
class Extrapolation: #Erstellt ein Objekt, welches ein DataFrame mitbekommt, und bestimmte werte aus diesen DataFrame Multipliziert
    def __init__ (self, df, factor_OnShore, factor_OffShore, factor_Photo, year):
        self.df = df
        self.factor_OnShore = factor_OnShore
        self.factor_OffShore = factor_OffShore
        self.factor_Photo = factor_Photo
        self.year = year

        self.multiply()
        self.update_year()
        addTimeInformation(self.df)

    def multiply(self):
        self.df["Photovoltaik"] = self.df["Photovoltaik"]*self.factor_Photo
        self.df["Wind Offshore"]= self.df["Wind Offshore"] * self.factor_OffShore
        self.df["Wind Onshore"] = self.df["Wind Onshore"] * self.factor_OnShore

    def update_year(self):
        # Ändern der Jahreskomponente in der "Datum"-Spalte
        self.df["Datum"] = self.df["Datum"].apply(lambda x: x.replace(year=self.year))


class Extrapolation: #Erstellt ein Objekt, welches ein DataFrame mitbekommt, und bestimmte werte aus diesen DataFrame Multipliziert
    def __init__ (self, df, factor, year):
        self.df = df
        self.factor = factor
        self.year = year

        self.multiply()
        self.update_year()
        #addTimeInformation(self.df)

    def multiply(self):
        self.df["Gesamtverbrauch"] = self.df["Gesamtverbrauch"] * self.factor

    def update_year(self):
        # Ändern der Jahreskomponente in der "Datum"-Spalte
        self.df["Datum"] = self.df["Datum"].apply(lambda x: x.replace(year=self.year))
        self.df["Year"] = self.year
"""

class Extrapolation:
    def __init__(self, df, year, factor_OnShore=None, factor_OffShore=None, factor_Photo=None, factor_Consumption=None):
        self.df = df
        self.year = year
        self.factor_OnShore = factor_OnShore
        self.factor_OffShore = factor_OffShore
        self.factor_Photo = factor_Photo
        self.factor_Consumption = factor_Consumption

        self.multiply()
        self.update_year()
        addTimeInformation(self.df)  # Falls benötigt, kannst du diese Zeile wieder aktivieren

    def multiply(self):
        if self.factor_OnShore is not None:
            self.df["Wind Onshore"] = self.df["Wind Onshore"] * self.factor_OnShore
        if self.factor_OffShore is not None:
            self.df["Wind Offshore"] = self.df["Wind Offshore"] * self.factor_OffShore
        if self.factor_Photo is not None:
            self.df["Photovoltaik"] = self.df["Photovoltaik"] * self.factor_Photo
        if self.factor_Consumption is not None:
            self.df["Gesamtverbrauch"] = self.df["Gesamtverbrauch"] * self.factor_Consumption

    def update_year(self):
        # Ändern der Jahreskomponente in der "Datum"-Spalte
        self.df["Datum"] = self.df["Datum"].apply(lambda x: x.replace(year=self.year))
        self.df["Year"] = self.year


class Extrapolation_Consumption(Extrapolation):
    
    def __init__(self, df, year,  factor_OnShore=None, factor_OffShore=None, factor_Photo=None, factor_Consumption=None, lastprofil_dict=None, lastprofil_waermepumpe_year = None):
        super().__init__(df, year, None, None, None, factor_Consumption=factor_Consumption)

        self.lastprofil = lastprofil_dict
        self.waermepumpe = lastprofil_waermepumpe_year
        
        self.apply_lastprofile()
        addTimeInformation(self.df)  # Falls benötigt, kannst du diese Zeile wieder aktivieren


    def apply_lastprofile(self):
        saturday = ["6"]  # Samstag
        sunday = ["7"]  # Sonntag
        workday = ["1", "2", "3", "4", "5"]  # Montag bis Freitag

        for idx, row in self.df.iterrows():
            weekday = row['Weekday']
            lp = None
           
            if weekday in saturday:
                lp = self.lastprofil['saturday']
            elif weekday in sunday:
                lp = self.lastprofil['sunday']
            elif weekday in workday:
                lp = self.lastprofil['workday']
            else:
                continue

        
            # Berechnen Sie den Index im Lastprofil-DataFrame
            lastprofil_idx = idx % len(lp)

            # Fügen Sie den Wert aus dem Lastprofil-DataFrame hinzu
            self.df.loc[idx, 'Gesamtverbrauch'] += ((lp.loc[lastprofil_idx, 'Strombedarf (kWh)']/1000) + self.waermepumpe.loc[idx, 'Verbrauch'])


        #self.df.drop(columns=['Weekday'], inplace=True)
            