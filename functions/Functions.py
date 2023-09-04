import importlib
import streamlit as st
import pandas as pd
import pint
import numpy as np

ureg = pint.UnitRegistry()

if __name__ != "__main__":
    from functions import Data_API
    from functions import Imputation

def load_data_by_mapping (data_mapping,data):
    """
    Load the required data based on the given data mapping.

    This function dynamically imports the necessary modules based on the provided data mapping.
    It then checks if the imported module contains the function "load_required_data".
    The function "load_required_data" from each module is used to process the data and update
    the data mapping with the processed data.

    Args:
    - data_mapping (dict): A dictionary containing the names of the modules as keys and another dictionary
                           as values. The inner dictionary contains the required data names as keys and
                           their corresponding column names as values.
    - data (pd.DataFrame): A pandas DataFrame containing the raw data from the API.

    Returns:
    - dict: An updated data mapping where the column names have been replaced by the processed data
            from the respective modules.

    Note:
    If a module does not have the function "load_required_data", a warning is displayed and the module is skipped.
    """
    module = None

    for module_name, module_data in data_mapping.items():
       
        module = importlib.import_module(f"pages.modules.{module_name}_module")

        # Check if the module has the function "get_required_data"
        if not hasattr(module, "load_required_data"):
            st.warning(f"The selected system module '{module_name}' does not contain the function 'load_required_data'. Please update this system module or choose another module.")
            continue

        loaded_module_data = module.load_required_data(data, data_mapping, module_name)

        # Replace the values in data_mapping with the corresponding loaded_module_data
        for key in module_data.keys():
            
            data_mapping[module_name][key] = loaded_module_data[key]

    mapped_data = data_mapping
     
    ### Test the output for this function:
    #st.write("Data Mapping for each module:", mapped_data[module_name])
    #st.write("Data Mapping all keys vor each module:", mapped_data[module_name].keys())
    #st.write("Data Mapping get the first value for each module:", list(mapped_data[module_name].values())[0])

    return mapped_data

def load_data_for_module(data_mapping, module_names, filename, freq_input=None, start_time=None, end_time=None):
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
                raw_data_from_api = Data_API.read_data_from_csv_with_time_range(filename, [column_name], start_time, end_time,)

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



def convert_dataframe(df, input_unit, output_unit, column_name=None):
    """
    Converts the values of a specific column in a DataFrame from one unit to another.

    Args:
    - df (pandas.DataFrame): The DataFrame whose values need to be converted.
    - input_unit (str): The original unit of the values in the DataFrame. Must be a valid pint unit, e.g., 'meter', 'kilogram', 'second'.
    - output_unit (str): The desired unit for the values in the DataFrame. Must be a valid pint unit and compatible with the input_unit, e.g., 'kilometer', 'gram'.
    - column_name (str): The name of the column to convert.

    Returns:
    - pandas.DataFrame: A DataFrame with the converted values in the specified column.
    """
     # If no column name is specified, use the first column
    if column_name is None:
        column_name = df.columns[0]

     # Extract the values of the specified column and convert them to a pint Quantity
    values_with_unit = df[column_name].values.astype(float) * ureg(input_unit)

    # Convert the Quantity to the desired output unit
    converted_values = values_with_unit.to(output_unit).magnitude
    
    # Replace the values in the specified column with the converted values
    converted_df = df.copy()
    converted_df[column_name] = converted_values
    
    return converted_df








def find_compatible_units(base_unit):
    """
    Finds all units in the Pint unit registry that have the same dimensionality as the specified base unit.

    Parameters:
        base_unit (str): The name of the base unit against which compatibility is to be checked.
                         This should be the name of a unit defined in the Pint unit registry, such as 'joule'.

    Returns:
        list: A list of strings containing the names of all units that have the same dimensionality as the base unit.
              For example, for the base unit 'joule', the results might include 'calorie', 'kilowatt_hour', etc.

    Example:
        compatible_energy_units = find_compatible_units('joule')
        print(compatible_energy_units)  # Outputs all units compatible with joule
    """
    base_dimensionality = ureg[base_unit].dimensionality
    compatible_units = []

    # Durchsuchen Sie alle in der Einheitenregistrierung definierten Einheiten
    for unit_name in ureg:
        try:
            # Versuchen Sie, die Einheit in eine Quantity umzuwandeln
            unit = ureg.Quantity(1, unit_name)
            
            # Überprüfen Sie, ob die Dimensionalität der Einheit mit der der Basiseinheit übereinstimmt
            if unit.dimensionality == base_dimensionality:
                compatible_units.append(unit_name)
        except:
            # Wenn ein Fehler auftritt, ignorieren Sie diese Einheit
            pass

    return compatible_units










# Test Funktion if only this skript is running


if __name__ == "__main__":
    import Data_API
    import Imputation

    st.title("Test Functions.py")


    st.subheader("Unit conversion")

    

    #Choose Unit


    
    input_unit = st.text_input("Choose input unit:")

    compatible_energy_units = find_compatible_units(input_unit)

    output_unit = st.selectbox("Choose your output unit:",compatible_energy_units ) 

    col1, col2 = st.columns(2)

    # Erstellen eines Beispiel-DataFrames zur Überprüfung der Funktion
    example_data = {
        f'Data [{input_unit}]': [12, 7, 10, 9, 11, 5],}
    
    example_timestamps = pd.to_datetime(['2023-08-11 10:00:00', '2023-08-11 10:10:00', '2023-08-11 10:20:00', '2023-08-11 10:30:00', '2023-08-11 10:40:00', '2023-08-11 10:50:00',])
    example_df = pd.DataFrame(data=example_data, index=example_timestamps)

    col1.write("Input Dataframe:")
    col1.write(example_df)


    #Umrechnung 
    converted_df = convert_dataframe(example_df, input_unit, output_unit, )

    converted_df.columns = converted_df.columns.str.replace(r'\[.*\]', f'[{output_unit}]')

    col2.write(f"Dataframe converted from {input_unit} to {output_unit}:")
    col2.write(converted_df)
