import streamlit as st
import pandas as pd
import pint

#Help Funktions of this skript 

# Use pint 
ureg = pint.UnitRegistry()

def freq_to_pint(freq):
    """
    Convert a pandas frequency string to a pint quantity.
    
    Parameters:
    - freq (str): A string representing the desired frequency in pandas format. 
                  Possible values include:
                  '1S' : 1 second
                  '30S' : 30 seconds
                  '1T' or '1Min' : 1 minute
                  '5T' or '5Min' : 5 minutes
                  '15T' or '15Min' : 15 minutes
                  '30T' or '30Min' : 30 minutes
                  '1H' : 1 hour
    
    Returns:
    - pint.Quantity: The equivalent frequency as a pint quantity.
    
    Example:
    >>> freq_to_pint('1S')
    <Quantity(1, 'second')>
    
    Note:
    This function currently supports a subset of pandas frequency strings. 
    For a comprehensive list of pandas frequency strings, consult the pandas documentation.
    """
    
    mapping = {
        'S': ureg.second,
        'T': ureg.minute,
        'Min': ureg.minute,
        'H': ureg.hour,
    }
    
    # Find the first non-digit character to separate magnitude and unit
    for i, char in enumerate(freq):
        if not char.isdigit():
            magnitude = int(freq[:i]) if i > 0 else 1
            unit_str = freq[i:]
            break
    else:
        raise ValueError(f"Unsupported frequency format: {freq}")
    
    unit = mapping[unit_str]
    return magnitude * unit


def classify_unit(unit_str):
    """
    Classifies the given unit as "power", "energy", or "unknown" based on its dimensionality.

    Parameters:
    - unit_str (str): The unit to be classified, e.g., "W", "J", "mW", etc.

    Returns:
    - str: "power" if the unit is a power unit, "energy" if it's an energy unit, 
           or "unknown" if the unit is neither power nor energy.
    """
    # Convert the unit string to a pint Quantity
    unit = ureg(unit_str)
    
    # Extract the dimensionality of the unit
    dim = unit.dimensionality
    
    # Check the dimensionality to classify the unit
    if dim == ureg.watt.dimensionality:
        return "power"
    elif dim == ureg.joule.dimensionality:
        return "energy"
    else:
        return "unknown"
    



# Main funktion of this skript 


def power_energy(df, input_unit, output_unit, frequency):
    """
    Convert power values in a DataFrame to energy values or vice versa.

    Given a DataFrame with power values and a specified time interval, this function
    can convert the power values to energy values, or vice versa based on the 
    provided input and output units.

    Parameters:
    ----------
    df : pd.DataFrame
        A DataFrame containing power or energy data with a consistent timestamp 
        as its index. The timestamp index must have a fixed time interval frequency.
    input_unit : str
        The unit of the values in the input DataFrame. 
        Supported power units include: W, mW, kW, MW, GW, J/s, cal/s, BTU/h, etc.
        Supported energy units include: J, mJ, kJ, MJ, GJ, cal, kcal, Wh, kWh, MWh, BTU, etc.
    output_unit : str
        The desired unit for the output values. This must be dimensionally 
        consistent with the input_unit.

    Returns:
    -------
    pd.DataFrame
        A DataFrame with values converted to the specified output unit and 
        retaining the original timestamp index.
    """
    time_Unit = freq_to_pint(frequency)

    # Convert power values in the DataFrame to pint quantities
    values_with_unit = df.values * ureg(input_unit)

    if classify_unit(input_unit) == "power" and classify_unit(output_unit) == "energy":
        energy_values = (values_with_unit * time_Unit).to(output_unit)
        column_name = f"Energy [{energy_values.units}]"
        output_df = pd.DataFrame(energy_values.magnitude, index=df.index, columns=[column_name])
    elif classify_unit(input_unit) == "energy" and classify_unit(output_unit) == "power":
        power_values = (values_with_unit / time_Unit).to(output_unit)
        column_name = f"Power [{power_values.units}]"
        output_df = pd.DataFrame(power_values.magnitude, index=df.index, columns=[column_name])
    elif classify_unit(input_unit) == "power" and classify_unit(output_unit) == "power":
        power_values = values_with_unit.to(output_unit)
        column_name = f"Power [{power_values.units}]"
        output_df = pd.DataFrame(power_values.magnitude, index=df.index, columns=[column_name])
    elif classify_unit(input_unit) == "energy" and classify_unit(output_unit) == "energy":
        energy_values = values_with_unit.to(output_unit)
        column_name = f"Energy [{energy_values.units}]"
        output_df = pd.DataFrame(energy_values.magnitude, index=df.index, columns=[column_name])
    else:
        output_df = f"Wrong input-{input_unit} or output-{output_unit} variable"
    
    return output_df












# Test Funktion if only this skript is running


if __name__ == "__main__":

    import imputation

    st.title("Test of compute_energy.py")

    c1, c2, c3, c4 = st.columns(4)

    ### 1. Example Data

     # Erstellen eines Beispiel-DataFrames zur Überprüfung der Funktion
    example_data = {
        'Power [watt]': [12, 7, 10, 9, 11, 5],}
    
    example_timestamps = pd.to_datetime(['2023-08-11 10:00:00', '2023-08-11 10:10:00', '2023-08-11 10:20:00', '2023-08-11 10:30:00', '2023-08-11 10:40:00', '2023-08-11 10:50:00',])
    example_df = pd.DataFrame(data=example_data, index=example_timestamps)

     # Erstellen eines Beispiel-DataFrames zur Überprüfung der Funktion
    example_data2 = {
        'Power [watt]': [12, 7, 10, 9],}
    
    example_timestamps = pd.to_datetime(['2023-08-11 10:00:00', '2023-08-11 10:15:00', '2023-08-11 10:30:00', '2023-08-11 10:45:00',])
    example_df2 = pd.DataFrame(data=example_data2, index=example_timestamps)

    frequency = pd.infer_freq(example_df.index)

    mean = example_df.mean()

    c1.subheader("Example DATA")

    c1.write(example_df)

    c1.write("Frequency:")
    c1.write(frequency)

    ### 2. Konsistenter Datensatz mit vorgegebener Frequnz erstellen 

    freq = "10T" # 1 minute time Intervall


    c2.subheader(f"Interploated DATA (time interval = {freq})")

    

    interpolated_data = imputation.interpolate_impute(example_df, freq=freq)

    frequency = pd.infer_freq(interpolated_data.index)

    mean = interpolated_data.mean()

    c2.write(interpolated_data)

    c2.write("Mean:")
    c2.write(str( mean))

    c2.write("Frequency:")
    c2.write(freq_to_pint(frequency))



    ### 3. Convert power to energy

    input_unit, output_unit = "W" , "Wh"

    c3.subheader(f"Convert Power to Energy [{input_unit} -> {output_unit}] ")


    convertedP2E_df = power_energy (interpolated_data, input_unit, output_unit )
    
    c3.write(convertedP2E_df)

    c3.write("Sum:" )
    c3.write(str (convertedP2E_df.sum()))




    ### 4. Convert energy to power

    input_unit, output_unit = "Wh" , "J/s"

    c4.subheader(f"Convert Power to Energy [{input_unit} -> {output_unit}] ")


    convertedE2P_df = power_energy (convertedP2E_df, input_unit, output_unit )
    
    c4.write(convertedE2P_df)

    c4.write("Mean:" )
    c4.write(str (convertedE2P_df.mean()))













    ### Summarry:
    with st.expander("Explanation of the relationship between power and energy"):
        summary = """
                    Summary:

                    The relationship between Power (P), Energy (E), and Time (t) is described by the following formula:
                    E = P × t

                    - Power (P): The rate at which energy is transferred or converted over time. It is measured in Watts (W).
                    - Energy (E): The total amount of energy consumed over a specific period. It is measured in Watt-hours (Wh).
                    - Time (t): The duration over which the energy is consumed.

                    If you calculate the average power over a specific time span and multiply this average power by the duration of that span, you get the total energy consumed during that span.

                    Example 1:

                    Measured power per unit of time (over an hour):
                    - Average Power: 9 W
                    - Time Span: 1 hour
                    - Calculated Total Energy: E = 9 W × 1 hour = 9 Wh

                    Example 2:

                    Measured power per unit of time (over 50 minutes):
                    - Average Power: 9.045455 W
                    - Time Span: 50/60 hour (or 5/6 hour)
                    - Sum of calculated energy for each 5-minute interval: 8.291667 Wh

                    In this case, the time series does not cover a full hour but only 50 minutes. Therefore, the sum of the energy will not exactly match the average power over a full hour.

                    Conclusion:

                    The sum of energy over a specific time span corresponds to the average power multiplied by that span. However, if the time span is not exactly one hour, the sum of the energy will not necessarily match the average power over a full hour.
                """

        st.write(summary)