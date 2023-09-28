import streamlit as st
import sys
import os
import json
import importlib
import inspect
import pandas as pd
    


    





units = ["W", "kW", "Wh", "kWh", "J", "°C", "K", ] #Units List (has to be pint Units)


measuring_list = ["Compressor_Power", "ambient_heat_IN", "Heat_OUT" ]

Label = ["Wärmepumpenantrieb" , "Umgebungswärme", "Wärmeabgabe"]
Consumption = None
Type =  ['Transformer','Source','Sink']
EnergyTypeInput = ['electricity','-','heat']
EnergyTypeOutput = ['heat','heat','-']



def initialize_data_interface():
    """
    Initialize the data interface based on the saved interface in Configuration.json.
    """
    # Add the directory containing api.py to the Python path
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../functions'))

    # Function to load saved interface from Configuration.json
    def load_saved_interface(config_file):
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                saved_data = json.load(file)
            return saved_data.get("selected_interface", None)
        else:
            return None

    # Load the saved interface
    config_file = os.path.join(os.path.dirname(__file__), '../../Configuration.json')
    saved_interface = load_saved_interface(config_file)

    # Import the API module dynamically
    import api

    # Function to create a data interface dynamically
    def create_data_interface(selected_interface, **kwargs):
        for name, obj in inspect.getmembers(api):
            if name == saved_interface:
                return obj(**kwargs)

    # Create the data interface
    if saved_interface:
        return create_data_interface(saved_interface)
    else:
        return None




def get_required_data(measuring_list=measuring_list, units= units ):
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
    
    required_data = {}

    for i in measuring_list:
        required_data[i] = units

    
    #required_data = ["Compressor_Power_[W]", "Heating_Capacity_[W]", "Power_grid_purchase_[kW]"] #It is required that the units are in the brekets "[]"
    return required_data




def get_sankey_mapping (measuring_list=measuring_list,Consumption=Consumption, labels=Label, types=Type, energy_type_inputs=EnergyTypeInput, energy_type_outputs=EnergyTypeOutput):
    """
    Create a data mapping dictionary from lists of labels, types, energy_type_inputs and energy_type_outputs.
    
    Parameters:
    - dataframe (pd.DataFrame): The DataFrame containing the data series.
    - labels (list): List of labels corresponding to each data series in the DataFrame.
    - types (list): List of types corresponding to each data series in the DataFrame.
    - energy_type_inputs (list): List of energy type inputs corresponding to each data series in the DataFrame.
    - energy_type_outputs (list): List of energy type outputs corresponding to each data series in the DataFrame.
    
    Returns:
    - dict: The data mapping dictionary.
    """
    
    # Initialize an empty dictionary to hold the mapping
    sankey_mapping = {}
    
    # Loop through each column in the DataFrame to populate the mapping
    for col, label, typ, energy_type_input, energy_type_output in zip(measuring_list, labels, types, energy_type_inputs, energy_type_outputs):
        # Get the last value of the data series for 'Consumption'
        #consumption = measuring_list[col].iloc[-1] if not measuring_list[col].empty else None
        
        # Populate the mapping dictionary for the current data series
        sankey_mapping[col] = {
            "Label": label,
            "Consumption": Consumption,
            "Type": typ,
            "EnergyTypeInput": energy_type_input,
            "EnergyTypeOutput": energy_type_output
        }
    
    return sankey_mapping
    





def load_module_data(data_mapping, module_names, freq_input=None, start_time=None, end_time=None,):
    """
    Load data for specified modules from the API and interpolate missing values.

    Args:
        data_mapping: The data mapping dictionary.
        module_names: List of module names for which data should be loaded.
        filename: The filename or path to the file to read from the API.
        freq_input: Desired frequency for data (default is '1T' for 1 minute).

    Returns:
        A dictionary with the same structure as data_mapping, but with actual data 
        from the API instead of column names.
    """

    loaded_data = {}
    for module, data in data_mapping.items():
        if module in module_names:
            loaded_data[module] = {}
            for data_name, column_name in data.items():
                raw_data_from_api = data_interface.get_data([column_name], start_time, end_time,)

                if freq_input is not None:
                    freq = freq_input
                else:
                    try:
                        freq = pd.infer_freq(raw_data_from_api.index)
                        if freq is None:
                            raise ValueError
                    except ValueError:
                        freq = "1T"
                        st.warning("The time series data contains fewer than 3 timestamps, so the frequency of the data cannot be determined. Defaulting to 1 minute. Please make sure you have at least 3 records with timestamps in your dataset.")

                interpolated_data = Imputation.interpolate_impute(raw_data_from_api, freq=freq)
                
                loaded_data[module][data_name] = interpolated_data[column_name]

    return loaded_data


#Intilazie interface:
data_interface = initialize_data_interface()

if __name__ != "__main__":
    from functions import Imputation

    

# Your other functions like get_required_data, get_sankey_mapping, load_module_data remain the same

if __name__ == "__main__":
    # Change the working directory
    current_file_directory = os.path.dirname(__file__)
    os.chdir(os.path.join(current_file_directory, '../../'))
    import Imputation

    # Display data if the data_interface is initialized
    if data_interface:
        column_names = data_interface.get_column_names()
        st.write(column_names)

    # Your other Streamlit UI elements
    st.write(get_required_data())
    st.write(get_sankey_mapping(measuring_list, Consumption, Label, Type, EnergyTypeInput, EnergyTypeOutput))
    st.write(list(get_required_data().keys()))



    #Test the load_data function:
    if st.toggle("api test", help="Only used if example_data is connected"):
        data_mapping = {'Heat_pump': {'Compressor_Power_[W]': 'heat_pump_power_IN_[W]', 'ambient_heat_IN_[W]': 'ambient_heat_IN_[W]', 'Heat_OUT_[W]': 'room_heating_IN_[W]'}, 'Photovoltaik': {'P_yield_[W]': 'PV_yield_IN_[W]', 'Battery_charge_[Wh]': 'battery_[W]'}}
        module_names = ['Heat_pump']

        st.write(load_module_data(data_mapping, module_names, freq_input=None, start_time=None, end_time=None,))
