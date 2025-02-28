# =============================================================================
# castParameters.py
# =============================================================================
# This module provides utilities for parameter management in the climate model simulation.
# It handles type conversion for various parameters, provides a class for parameter 
# access, and includes helper functions for parameter processing.
# 
# The module ensures proper data types for all parameter values before they are used
# in calculations and simulations.
# =============================================================================

def cast_parameters(params):
    """
    Convert parameter values to their appropriate data types based on predefined mappings.
    This ensures all parameters have the correct data type before being used in calculations.
    
    Args:
        params (dict): Dictionary containing parameter key-value pairs
        
    Returns:
        dict: The same dictionary with values converted to appropriate types
    """
    # Define parameter keys that should be integers
    int_keys = [
        'onshore_development_rate', 'offshore_development_rate', 'pv_development_rate',
        'share_coal', 'share_gas', 'IST_installierte_waermepumpen', 'SOLL_installierte_waermepumpen',
        'consumption_year', 'start_year_ee', 'end_year_ee', 'end_year_extrapolation_installed_power',
        'start_year_simulation', 'end_year_simulation', 'base_year_generation', 'max_power_storage',
        'max_storage_capicity', 'max_power_flexipowerplant'
    ]
    # Define parameter keys that should be floats
    float_keys = [
        'CO2_factor_Kohle', 'CO2_factor_Gas', 'growth_rate_pv',
        'growth_rate_onshore', 'growth_rate_offshore', 'gridlost'
    ]
    # Define parameter keys that should be strings
    string_keys = [
        'selected_week_plot', 'selected_year_plot'
    ]

    # Cast to integers
    for key in int_keys:
        if key in params:
            params[key] = int(params[key])

    # Cast to floats
    for key in float_keys:
        if key in params:
            params[key] = float(params[key])

    # Cast to strings
    for key in string_keys:
        if key in params:
            params[key] = str(params[key])

    # Special handling for consumption_development_per_year dictionary
    # Converts year keys to integers while preserving values
    if 'consumption_development_per_year' in params:
        params['consumption_development_per_year'] = {
            int(year): value for year, value in params['consumption_development_per_year'].items()
        }

    return params


class Params:
    """
    A class that converts a parameter dictionary into an object with attributes.
    This allows for more convenient attribute-style access to parameters.
    
    Example:
        p = Params({'a': 1, 'b': 2})
        p.a  # Returns 1
    """
    def __init__(self, params_dict):
        # Set each key-value pair as an attribute of this object
        for key, value in params_dict.items():
            setattr(self, key, value)


def filter_injected_params(local_vars):
    """
    Filter a locals() dictionary to extract only valid parameter variables.
    
    Args:
        local_vars (dict): Typically the result of locals() call
        
    Returns:
        dict: A filtered dictionary containing only valid parameter variables
    """
    # Return only valid identifiers that don't start with double underscores
    return {key: value for key, value in local_vars.items() if key.isidentifier() and not key.startswith("__")}