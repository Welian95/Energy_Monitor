import streamlit as st
import sys
import os
import json
import inspect
import pandas as pd
import re 



def initialize_data_interface():
    """
    Initialize the data interface based on the saved interface in Configuration.json.
    
    Returns
    -------
    obj or None
        Returns an instance of the saved data interface, or None if the saved interface could not be loaded.

    Notes
    -----
    The function dynamically imports the 'api' module and creates an instance of the saved data interface.
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




def get_required_data_S(measuring_list, units):
    """
    Retrieve the required data names and their possible units for this system component.
    This function provides a dictionary where keys represent the names of data 
    variables relevant for this system component. Each key is mapped to a list 
    of possible units in which that data variable might be recorded.
    
    Parameters
    ----------
    measuring_list : list
        List of names for the data variables relevant for this system component.
    units : list
        List of possible units for the data variables.
        
    Returns
    -------
    dict
        A dictionary where keys are the names of data variables and values are 
        lists of possible units.
        
        - keys : strings
          Representing the names of data variables required by this component.
        - values : lists of strings
          Representing the possible units for the respective data variable.
    """
    # Return the list of required data for this module
    
    required_data = {}

    for i in measuring_list:
        required_data[i] = units

    return required_data




def get_sankey_mapping_S (measuring_list,Consumption, labels, types, energy_type_inputs, energy_type_outputs):
    """
    Create a data mapping dictionary from lists of labels, types, energy_type_inputs, and energy_type_outputs.
    
    Parameters
    ----------
    measuring_list : list
        List of data series in the DataFrame.
    Consumption : list
        List of consumption values corresponding to each data series in the DataFrame.
    labels : list
        List of labels corresponding to each data series in the DataFrame.
    types : list
        List of types corresponding to each data series in the DataFrame.
    energy_type_inputs : list
        List of energy type inputs corresponding to each data series in the DataFrame.
    energy_type_outputs : list
        List of energy type outputs corresponding to each data series in the DataFrame.
        
    Returns
    -------
    dict
        The data mapping dictionary.
    """
    
    # Initialize an empty dictionary to hold the mapping
    sankey_mapping = {}
    
    # Loop through each column in the DataFrame to populate the mapping
    for col, label, Consumption, typ, energy_type_input, energy_type_output in zip(measuring_list, labels, Consumption,  types, energy_type_inputs, energy_type_outputs):
        
        # Populate the mapping dictionary for the current data series
        sankey_mapping[col] = {
            "Label": label,
            "Consumption": Consumption,
            "Type": typ,
            "EnergyTypeInput": energy_type_input,
            "EnergyTypeOutput": energy_type_output
        }
    
    return sankey_mapping
    




def load_module_data(data_mapping, module_names, start_time=None, end_time=None):
    """
    Load data for specified modules from the API and interpolate missing values.

    Parameters
    ----------
    data_mapping : dict
        The data mapping dictionary.
    module_names : list
        List of module names for which data should be loaded.
    start_time : str or datetime, optional
        The start time for data retrieval.
    end_time : str or datetime, optional
        The end time for data retrieval.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the actual data from the API.
    """
    
    raw_df = pd.DataFrame()
    data_cache = {}
    operators = set(["+", "-", "*", "/", "(", ")", "if", "else", ">=", "<=", ">", "<", "=="])
    
    for module, data in data_mapping.items():
        if module in module_names:
            for data_name, column_name in data.items():
                
                # Check if the column_name is a simple column name or a mathematical expression
                if set(column_name.split(" ")).isdisjoint(operators):
                    # It's a simple column name
                    raw_df[column_name] = data_interface.get_data([column_name], start_time, end_time)
                else:
                    # It's a mathematical expression
                    expression = column_name
                    
                    # Replace IF(condition, true_value, false_value) with Python's ternary operator
                    while "IF(" in expression:
                        match = re.search(r'IF\(([^,]+),([^,]+),([^)]+)\)', expression)
                        if match:
                            condition, true_value, false_value = match.groups()
                            ternary_expression = f"{true_value.strip()} if {condition.strip()} else {false_value.strip()}"
                            expression = expression.replace(match.group(), ternary_expression)
                    
                    # Split the expression by spaces
                    tokens = [token for token in expression.split(" ") if token.strip()]
                    
                    for token in tokens:
                        if token not in operators and not token.replace(".", "", 1).isdigit():
                            if token not in data_cache:
                                data_output = data_interface.get_data([token], start_time, end_time)
                                
                                # Store the data in the cache
                                data_cache[token] = data_output

                            # Replace the token with the actual data value
                            expression = expression.replace(token, f"data_cache['{token}']")
                    
                    # Evaluate the expression and store it in raw_df
                    raw_df[column_name] = eval(expression)
                    
    return raw_df





def get_module_figs():
    """
    Create plant module-specific images.

    Returns
    -------
    list
        A list of charts that can be displayed using st.plotly_chart().
    """

    figures = []

    return figures


data_interface = initialize_data_interface()


if __name__ != "__main__":
    #Intilazie interface:
    data_interface = initialize_data_interface()

    



