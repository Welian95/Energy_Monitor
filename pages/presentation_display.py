# Standard Libraries
from typing import Dict
import copy 
import importlib
import time
import re

# Third-party Libraries
import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

# Custom Modules
from functions.sankey import create_dynamic_plotly_sankey 
from functions.conversion import convert_unit_of_value
from functions.compute_energy import power_energy


page_title="Presentation Display"
st.set_page_config(
    page_title=page_title,
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': f"# This is the {page_title} of the E-Monitoring Software"
    }
    )




def update_sankey_consumption(sankey_mapping: dict, frequency, unit="kWh") -> dict:
    """
    Updates the 'Consumption' fields in sankey_mapping using data from an external data interface.
    Allows for mathematical expressions and conditions within the 'Consumption' fields.
    Converts the unit of the consumption value to a specified unit (default is "kWh").
    
    Parameters:
    - sankey_mapping (dict): A dictionary defining Sankey diagram attributes.
    - frequency (str): The frequency of the time index in the DataFrame.
    - unit (str, optional): The desired output unit for the consumption values. Default is "kWh".
    
    Returns:
    - dict: Updated sankey_mapping with 'Consumption' values filled and converted to the specified unit.
    """
    data_cache = {}
    operators = set(["+", "-", "*", "/", "(", ")", "if", "else", ">=", "<=", ">", "<", "=="])

    for key, attributes in sankey_mapping.items():
        expression = attributes['Consumption']

        # Replace IF(condition, true_value, false_value) with Python's ternary operator
        while "IF(" in expression:
            match = re.search(r'IF\(([^,]+),([^,]+),([^)]+)\)', expression)
            if match:
                condition, true_value, false_value = match.groups()
                ternary_expression = f"{true_value.strip()} if {condition.strip()} else {false_value.strip()}"
                expression = expression.replace(match.group(), ternary_expression)

        # Remove any extra spaces around operators and inside brackets
        expression = re.sub(r'\s+', ' ', expression).replace('( ', '(').replace(' )', ')')
        
        # Now split the expression by spaces
        tokens = [token for token in expression.split(" ") if token.strip()]

        for token in tokens:
            if token not in operators and not token.replace(".", "", 1).isdigit():
                if token not in data_cache:
                    data_output = st.session_state.data_interface.get_data(column_names=token, num_rows=1, ascending=False)
                    
                    # Check if it's a DataFrame or a Series
                    if isinstance(data_output, pd.DataFrame):
                        if token in data_output.columns:
                            data_value = float(data_output[token].iloc[0])
                        else:
                            raise ValueError(f"Column '{token}' not found in DataFrame.")
                    elif isinstance(data_output, pd.Series):
                        data_value = float(data_output.iloc[0])
                    else:
                        raise TypeError("Unexpected data type returned from get_data.")

                    data_cache[token] = data_value

                # Replace the token with the actual data value
                expression = expression.replace(token, str(data_cache[token]))

        # Evaluate the expression to get the consumption value
        consumption_value = eval(expression)


        # Extract the unit from the key
        #key
        unit_str = key.split('_[')[1][:-1] if '_[' in key and ']' in key else None
        
        # Create a DataFrame with a single value and a None index
        df = pd.DataFrame({'Value': [consumption_value]}, index=None)

        
        # Convert the unit to "kWh" using the power_energy function

        output_df = power_energy(df, unit_str, unit,frequency)

        converted_value = output_df.iloc[0, 0]
        
        # Update the 'Consumption' value in sankey_mapping
        sankey_mapping[key]['Consumption'] = converted_value
            
    return sankey_mapping


def transform_data_for_sankey(sankey_mapping: Dict) -> Dict:
    """
    Transform the sankey_mapping dictionary to a specific dictionary format suitable for creating Sankey diagrams.
    
    Parameters:
    - sankey_mapping (Dict): A dictionary defining Sankey diagram attributes.
    
    Returns:
    - Dict: Transformed dictionary in the required format.
    """
    labels, consumptions, types, energy_type_inputs, energy_type_outputs = [], [], [], [], []
    for key, attributes in sankey_mapping.items():
        labels.append(attributes['Label'])
        consumptions.append(attributes['Consumption'])
        types.append(attributes['Type'])
        energy_type_inputs.append(attributes['EnergyTypeInput'])
        energy_type_outputs.append(attributes['EnergyTypeOutput'])
        
    return {
        'Label': labels,
        'Consumption': consumptions,
        'Type': types,
        'EnergyTypeInput': energy_type_inputs,
        'EnergyTypeOutput': energy_type_outputs
    }





#Set datainterface
if "data_interface" in st.session_state:
    data_interface = st.session_state.data_interface
else:
    st.error("data_interface wurde nicht initialisiert.")
    st.stop()




def main():
    
    
     # Streamlit Layout

    columns1, columns2, columns3 = st.columns([5, 1, 1])

    columns1.title("Presentation Display")
    
    # Navigation
    if columns2.button("Main"):
        switch_page("Main")

    #Define the output unit for sankey values
    unit = "kW"
    frequency = data_interface.get_time_frequency()

    last_timestamp = data_interface.get_last_timestamp()
    st.markdown(f"Timestamp: **:blue[{last_timestamp}]**, Unit: **:blue[[{unit}]]**, Measuring frequency: **:blue[{frequency}]**")


    
    # Data preparation for Sankey Diagram
    sankey_mapping = copy.deepcopy(st.session_state.sankey_mapping)


    #Load consumption data from api into sankey_mapping
    sankey_mapping_w_data = update_sankey_consumption(sankey_mapping,frequency, unit)    

    transformed_data = transform_data_for_sankey(sankey_mapping_w_data)
    
    sankey_table = pd.DataFrame(transformed_data)
    
    # Sankey Diagram creation and display
    sankey_fig = create_dynamic_plotly_sankey(sankey_table)  
    



    data_mapping= copy.deepcopy(st.session_state.data_mapping)

    figures = []

    # Iterate through each module and its corresponding data
    for module_name, module_data in data_mapping.items():
        
        for data_name, column_name in module_data.items():
            
            # Dynamically import the module
            module = importlib.import_module(f'pages.modules.{module_name}_module')
            
            # Load the data from the API

        figures += module.get_module_figs()







   
    sankey_height = 720
    # Setze die Höhe des Sankey-Diagramms auf die kumulierte Höhe der anderen Grafiken
    sankey_fig.update_layout(height=sankey_height)

     # Setze die Höhe jeder Figur manuell
    individual_height = sankey_height / len(figures)
    for fig in figures:
        fig.update_layout(height=individual_height)

    # Streamlit Code
    
    col1, col2, = st.columns([5, 1, ])
    
    with col1:
        st.plotly_chart(sankey_fig, use_container_width=True, theme="streamlit",)
        
    with col2:
        for fig in figures:
            st.plotly_chart(fig, use_container_width=True, theme="streamlit",)



    auto_rerun = columns3.toggle("Auto rerun")

    if auto_rerun == True:
        # Sleep for 1 second
        time.sleep(1)

        st.rerun()

    



if __name__ == "__main__":
    main()

    



