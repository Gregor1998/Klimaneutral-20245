def cast_parameters(params):
    int_keys = [
        'onshore_development_rate', 'offshore_development_rate', 'pv_development_rate',
        'share_coal', 'share_gas', 'IST_installierte_waermepumpen', 'SOLL_installierte_waermepumpen',
        'consumption_year', 'start_year_ee', 'end_year_ee', 'end_year_extrapolation_installed_power',
        'start_year_simulation', 'end_year_simulation', 'base_year_generation', 'max_power_storage',
        'max_storage_capicity', 'max_power_flexipowerplant'
    ]
    float_keys = [
        'CO2_factor_Kohle', 'CO2_factor_Gas', 'growth_rate_pv',
        'growth_rate_onshore', 'growth_rate_offshore', 'gridlost'
    ]

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

    # Handle `consumption_development_per_year`
    if 'consumption_development_per_year' in params:
        params['consumption_development_per_year'] = {
            int(year): value for year, value in params['consumption_development_per_year'].items()
        }

    return params


class Params:
    def __init__(self, params_dict):
        for key, value in params_dict.items():
            setattr(self, key, value)


# Build a clean params dictionary from locals()
def filter_injected_params(local_vars):
    return {key: value for key, value in local_vars.items() if key.isidentifier() and not key.startswith("__")}