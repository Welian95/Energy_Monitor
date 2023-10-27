import streamlit as st
import pandas as pd
import pint
import numpy as np

ureg = pint.UnitRegistry()

if __name__ != "__main__":
    
    from functions import imputation
    

def convert_unit_of_value(value, input_unit, output_unit):
    """
    Converts a single value from one unit to another using pint.
    
    Parameters
    ----------
    value : float
        The value to be converted.
    input_unit : str
        The original unit of the value. Must be a valid pint unit, e.g., 'W' for Watt.
    output_unit : str
        The desired unit for the value. Must be a valid pint unit and compatible with the input_unit, e.g., 'kW' for kiloWatt.
    
    Returns
    -------
    float
        The converted value.
    """
    # Create a pint Quantity for the value and input unit
    value_with_unit = ureg.Quantity(value, input_unit)
    
    # Convert the value to the output unit
    converted_value = value_with_unit.to(output_unit).magnitude
    
    return converted_value


def convert_unit_of_dataframe(df, input_unit, output_unit, column_name=None):
    """
    Converts the values of a specific column in a DataFrame from one unit to another.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the values to be converted.
    input_unit : str
        The original unit of the values in the DataFrame.
    output_unit : str
        The desired unit for the values in the DataFrame.
    column_name : str, optional
        The name of the column to convert. Defaults to the first column if not provided.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the converted values in the specified column.
    """
     # If no column name is specified, use the first column
    if column_name is None:
        column_name = df.columns[0]

    input_quantity = ureg.parse_expression(input_unit)
    output_quantity = ureg.parse_expression(output_unit)

     # Extract the values of the specified column and convert them to a pint Quantity
    values_with_unit = df[column_name].values.astype(float) * input_quantity

    # Convert the Quantity to the desired output unit
    converted_values = values_with_unit.to(output_quantity).magnitude
    
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
    '''
    Streamlit UI to test the function in development
    '''

    import imputation

    st.title("Conversion.py")


    st.subheader("Unit conversion")

    

    #Choose Unit
    input_unit = st.text_input("Choose input unit:")

    compatible_energy_units = find_compatible_units(input_unit)

    output_unit = st.selectbox("Choose your output unit:",compatible_energy_units ) 

    col1, col2 = st.columns(2)


    example_data = {
        f'Data [{input_unit}]': [12, 7, 10, 9, 11, 5],}
    
    example_timestamps = pd.to_datetime(['2023-08-11 10:00:00', '2023-08-11 10:10:00', '2023-08-11 10:20:00', '2023-08-11 10:30:00', '2023-08-11 10:40:00', '2023-08-11 10:50:00',])
    example_df = pd.DataFrame(data=example_data, index=example_timestamps)

    col1.write("Input Dataframe:")
    col1.write(example_df)

 
    converted_df = convert_unit_of_dataframe(example_df, input_unit, output_unit, )

    converted_df.columns = converted_df.columns.str.replace(r'\[.*\]', f'[{output_unit}]')

    col2.write(f"Dataframe converted from {input_unit} to {output_unit}:")
    col2.write(converted_df)
