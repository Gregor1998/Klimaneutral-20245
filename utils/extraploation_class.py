from utils.addTimeInformation import addTimeInformation


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

"""
Extrapolation Module
-------------------
This module provides classes for extrapolating energy production and consumption data.
It allows scaling of different energy sources (wind onshore/offshore, photovoltaic) 
and consumption values by specific factors, and adjusting the year of the dataset.
"""

class Extrapolation:
    """
    Base class for extrapolating energy data by applying scaling factors to various columns
    and updating the year information in the dataset.
    """
    def __init__(self, df, year, factor_OnShore=None, factor_OffShore=None, factor_Photo=None, factor_Consumption=None):
        """
        Initialize the extrapolation with a dataframe and scaling factors.
        
        Parameters:
        -----------
        df : pandas.DataFrame
            The dataframe containing energy data
        year : int
            Target year for extrapolation
        factor_OnShore : float, optional
            Scaling factor for onshore wind energy
        factor_OffShore : float, optional
            Scaling factor for offshore wind energy
        factor_Photo : float, optional
            Scaling factor for photovoltaic energy
        factor_Consumption : float, optional
            Scaling factor for overall consumption
        """
        self.df = df
        self.year = year
        self.factor_OnShore = factor_OnShore
        self.factor_OffShore = factor_OffShore
        self.factor_Photo = factor_Photo
        self.factor_Consumption = factor_Consumption

        self.multiply()  # Apply scaling factors
        self.update_year()  # Update year information
        addTimeInformation(self.df)  # Add additional time-related columns

    def multiply(self):
        """
        Apply scaling factors to respective columns in the dataframe.
        Each factor is only applied if it's not None.
        """
        if self.factor_OnShore is not None:
            self.df["Wind Onshore"] = self.df["Wind Onshore"] * self.factor_OnShore
        if self.factor_OffShore is not None:
            self.df["Wind Offshore"] = self.df["Wind Offshore"] * self.factor_OffShore
        if self.factor_Photo is not None:
            self.df["Photovoltaik"] = self.df["Photovoltaik"] * self.factor_Photo
        if self.factor_Consumption is not None:
            self.df["Gesamtverbrauch"] = self.df["Gesamtverbrauch"] * self.factor_Consumption

    def update_year(self):
        """
        Update the year component in the 'Datum' column and add a 'Year' column.
        """
        # Change the year component in all date entries
        self.df["Datum"] = self.df["Datum"].apply(lambda x: x.replace(year=self.year))
        # Add a separate Year column for easier filtering
        self.df["Year"] = self.year


class Extrapolation_Consumption(Extrapolation):
    """
    Specialized subclass for extrapolating consumption data.
    Focuses on consumption scaling while setting production factors to None.
    """
    def __init__(self, df, year, factor_OnShore=None, factor_OffShore=None, factor_Photo=None, factor_Consumption=None):
        """
        Initialize consumption extrapolation, focusing on the consumption factor.
        
        Parameters are the same as the parent class, but production factors are set to None
        when passed to the parent constructor.
        """
        # Call parent constructor but only pass consumption factor (set others to None)
        super().__init__(df, year, None, None, None, factor_Consumption=factor_Consumption)
        
        # Note: The following lines are commented out but would be used for load profile handling
        #self.lastprofil = lastprofil_dict
        #self.waermepumpe = lastprofil_waermepumpe_year
        #self.apply_lastprofile()
        
        addTimeInformation(self.df)  # Update time information columns

"""
    def apply_lastprofile(self):
        saturday = ["6"]  # Samstag
        sunday = ["7"]  # Sonntag
        workday = ["1", "2", "3", "4", "5"]  # Montag bis Freitag

        for idx, row in self.df.iterrows():
            weekday = row['Weekday']
            lp_wohnen, lp_buro, lp_public = None, None, None
           
            if weekday in saturday:
                lp_wohnen = self.lastprofil['Wohnen']['saturday']
                lp_buro = self.lastprofil['Büro']['saturday']
                lp_public = self.lastprofil['Öffentliche_Ladepunkte']['saturday']
            elif weekday in sunday:
                lp_wohnen = self.lastprofil['Wohnen']['sunday']
                lp_buro = self.lastprofil['Büro']['sunday']
                lp_public = self.lastprofil['Öffentliche_Ladepunkte']['sunday']
            elif weekday in workday:
                lp_wohnen = self.lastprofil['Wohnen']['workday']
                lp_buro = self.lastprofil['Büro']['workday']
                lp_public = self.lastprofil['Öffentliche_Ladepunkte']['workday']
            else:
                continue

        
            # Berechnen Sie den Index im Lastprofil-DataFrame
            lastprofil_idx = idx % len(lp_wohnen)

            lp_eautos_sum = lp_wohnen.loc[lastprofil_idx, 'Strombedarf (kWh)'] + lp_buro.loc[lastprofil_idx, 'Strombedarf (kWh)'] + lp_public.loc[lastprofil_idx, 'Strombedarf (kWh)']

            # Fügen Sie den Wert aus dem Lastprofil-DataFrame hinzu
            self.df.loc[idx, 'Gesamtverbrauch'] += ((lp_eautos_sum/1000) + self.waermepumpe.loc[idx, 'Verbrauch in MWh'])


        #self.df.drop(columns=['Weekday'], inplace=True)
    """