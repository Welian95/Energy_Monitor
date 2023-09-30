# Optimized and well-commented code example

# Standard Libraries
from typing import Dict
import copy 
import importlib

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
    Converts the unit of the consumption value to a specified unit (default is "kWh"), irrespective of the input unit.
    
    Parameters:
    - sankey_mapping (dict): A dictionary defining Sankey diagram attributes.
    - frequency (str): The frequency of the time index in the DataFrame, e.g., 'H' for hourly, 'D' for daily, etc.
                        This is used for unit conversion.
    - unit (str, optional): The desired output unit for the consumption values. Default is "kWh".
    
    Returns:
    - dict: Updated sankey_mapping with 'Consumption' values filled and converted to the specified unit.
    """
    for key, attributes in sankey_mapping.items():
        column_name = attributes['Consumption']
        if column_name is not None:
            # Fetch the consumption value
            consumption_value = float(st.session_state.data_interface.get_data(column_names=column_name, num_rows=1, ascending=False))
            
            # Extract the unit from the key
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
data_interface = st.session_state.data_interface 




def main():
    
    
     # Streamlit Layout
    columns = st.columns(2)
    columns[0].title("Presentation Display")
    
    # Navigation
    if columns[1].button("Main"):
        switch_page("Main")

    #Define the output unit for sankey values
    unit = "kWh"
    frequency = data_interface.get_time_frequency()

    last_timestamp = data_interface.get_last_timestamp()
    st.markdown(f"Timestamp: **:blue[{last_timestamp}]**, Unit: **:blue[[{unit}]]**, Measuring frequency: **:blue[{frequency}]**")


    
    # Data preparation for Sankey Diagram
    sankey_mapping = copy.deepcopy(st.session_state.sankey_mapping)
    
    #Load consumption data from api into sankey_mapping
    sankey_mapping_w_data = update_sankey_consumption(sankey_mapping,frequency, unit)    
    transformed_data = transform_data_for_sankey(sankey_mapping_w_data)
    #print(transformed_data)
    sankey_table = pd.DataFrame(transformed_data)
    
    # Sankey Diagram creation and display
    sankey_fig = create_dynamic_plotly_sankey(sankey_table)  # Assuming this function exists and works as expected
    



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
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.plotly_chart(sankey_fig, use_container_width=True)
        
    with col2:
        for fig in figures:
            st.plotly_chart(fig, use_container_width=True)




    

    




if __name__ == "__main__":
    main()

    


