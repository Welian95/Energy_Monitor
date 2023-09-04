from functions import Functions

def get_required_data():
    """
    Retrieve the required data names and their possible units for this system component.

    This function provides a dictionary where keys represent the names of data 
    variables relevant for this system component. Each key is mapped to a list 
    of possible units in which that data variable might be recorded.

    Returns:
        dict: A dictionary where:
            - keys are strings representing the names of data variables required by this component.
            - values are lists of strings representing the possible units for the respective data variable.

    Example:
        For a component that requires power yield (P_yield) and battery charge (Battery_charge), 
        the function might return:
        {
            "P_yield" : ["W", "kW",],
            "Battery_charge" : ["Wh", "kWh"]
        }

    Notes:
        The returned structure is used for data mapping in the main application, helping users 
        match their data columns to the requirements of this system component and specify the 
        units of their data.
    """

    # Return the list of required data for this module
    required_data = {"P_yield" : ["W", "kW", "J"],
                      "Battery_charge" : ["Wh", "kWh"]}

    return required_data

def load_module_data(data_mapping, module_names, filename, freq, start_time=None, end_time=None,): 
    '''
    This function is only to set the freq vor each module individualy 
    '''


    loaded_data = Functions.load_data_for_module(data_mapping, module_names, filename, freq, start_time, end_time,)

    return loaded_data


