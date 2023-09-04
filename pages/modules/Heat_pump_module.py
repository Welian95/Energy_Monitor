import streamlit as st
from functions import Functions
from functions import Data_API

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
    required_data = {"Compressor_Power" : ["W", "kW", ],
                      "Heating_Capacity" : ["W", "kW", ],
                      "Power_grid_purchase" : ["W", "kW",]}

    
    #required_data = ["Compressor_Power_[W]", "Heating_Capacity_[W]", "Power_grid_purchase_[kW]"] #It is required that the units are in the brekets "[]"
    return required_data



def load_module_data(data_mapping, module_names, filename,  freq, start_time=None, end_time=None,): 
    '''
    This function is only to set the freq vor each module individualy 
    '''


    loaded_data = Functions.load_data_for_module(data_mapping, module_names, filename, freq, start_time, end_time,)

    return loaded_data






if __name__ == "__main__":
    st.write(list(get_required_data().keys()))

    #test = Imputation.interpolate_impute(selected_data, '30T')
