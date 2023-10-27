# Standard Libraries
from typing import Dict, Union, Any, List
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


def configure_streamlit_page(page_title):
    """Configure the main settings of the Streamlit page.

    Parameters
    ----------
    page_title : str
        The title of the Streamlit page.
    """
    st.set_page_config(
        page_title=page_title,
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'About': f"# This is the {page_title} of the E-Monitoring Software"
        }
        )




def evaluate_expression(expression: str, data_cache: Dict[str, Union[int, float]]) -> float:
    """
    Evaluate a mathematical expression and return its value.

    Parameters
    ----------
    expression : str
        The mathematical expression to evaluate.
    data_cache : dict
        A dictionary containing previously fetched data for optimization.

    Returns
    -------
    float
        The evaluated value of the expression.
    """
    operators = set(["+", "-", "*", "/", "(", ")", "if", "else", ">=", "<=", ">", "<", "=="])

    # Replace IF(condition, true_value, false_value) with Python's ternary operator
    while "IF(" in expression:
        match = re.search(r'IF\(([^,]+),([^,]+),([^)]+)\)', expression)
        if match:
            condition, true_value, false_value = match.groups()
            ternary_expression = f"{true_value.strip()} if {condition.strip()} else {false_value.strip()}"
            expression = expression.replace(match.group(), ternary_expression)

    tokens = [token for token in expression.split(" ") if token.strip()]
    
    for token in tokens:
        if token not in operators and not token.replace(".", "", 1).isdigit():
            if token not in data_cache:
                data_value = fetch_data(token)
                data_cache[token] = data_value

            expression = expression.replace(token, str(data_cache[token]))

    return eval(expression)



def fetch_data(token: str) -> float:
    """
    Fetch the data for a given token from an external data source.

    Parameters
    ----------
    token : str
        The name of the data field to fetch.

    Returns
    -------
    float
        The fetched data value.
    """
    data_output = st.session_state.data_interface.get_data(column_names=token, num_rows=1, ascending=False)
    if isinstance(data_output, pd.DataFrame):
        if token in data_output.columns:
            return float(data_output[token].iloc[0])
    elif isinstance(data_output, pd.Series):
        return float(data_output.iloc[0])
    else:
        raise TypeError("Unexpected data type returned from get_data.")
    

def convert_units(df: pd.DataFrame, unit_str: str, target_unit: str, frequency: str) -> pd.DataFrame:
    """
    Convert the unit of a DataFrame column to a target unit.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the values to convert.
    unit_str : str
        The original unit of the values.
    target_unit : str
        The target unit for conversion.
    frequency : str
        The frequency of the time index in the DataFrame.

    Returns
    -------
    pd.DataFrame
        The DataFrame with values converted to the target unit.
    """
    return power_energy(df, unit_str, target_unit, frequency)

def update_sankey_consumption(sankey_mapping: Dict[str, Dict], frequency: str, unit: str = "kWh") -> Dict[str, Dict]:
    """
    Update the 'Consumption' fields in sankey_mapping using data from an external data interface.

    Parameters
    ----------
    sankey_mapping : dict
        A dictionary containing the mapping for Sankey diagram attributes.
    frequency : str
        The frequency of the time index in the DataFrame.
    unit : str, optional
        The desired unit for the consumption values. Default is "kWh".

    Returns
    -------
    dict
        The updated sankey_mapping with 'Consumption' values filled and converted to the specified unit.
    """
    data_cache = {}
    for key, attributes in sankey_mapping.items():
        expression = attributes['Consumption']

        # Evaluate the expression to get the consumption value
        consumption_value = evaluate_expression(expression, data_cache)

        # Convert the unit to the target unit
        df = pd.DataFrame({'Value': [consumption_value]}, index=[None])
        unit_str = key.split('_[')[1][:-1] if '_[' in key and ']' in key else None
        converted_df = convert_units(df, unit_str, unit, frequency)
        converted_value = converted_df.iloc[0, 0]

        # Update the 'Consumption' value in sankey_mapping
        sankey_mapping[key]['Consumption'] = converted_value

    return sankey_mapping


def transform_data_for_sankey(sankey_mapping: Dict[str, Dict[str, str]]) -> Dict[str, list]:
    """
    Transform the sankey_mapping dictionary to a specific dictionary format suitable for creating Sankey diagrams.
    
    Parameters
    ----------
    sankey_mapping : Dict[str, Dict[str, str]]
        A dictionary defining Sankey diagram attributes. 
        Each key is a unique identifier, and the value is another dictionary containing attributes like 'Label', 'Consumption', etc.

    Returns
    -------
    Dict[str, list]
        Transformed dictionary in the required format. 
        It contains keys like 'Label', 'Consumption', 'Type', etc., and each key maps to a list of values extracted from the input sankey_mapping.

    Example
    -------
    >>> transform_data_for_sankey({'node1': {'Label': 'Label1', 'Consumption': 10, 'Type': 'Type1'}})
    {'Label': ['Label1'], 'Consumption': [10], 'Type': ['Type1']}
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





def initialize_data_interface() -> Any:
    """
    Initialize the data interface for the application.

    Returns
    -------
    Any
        The initialized data interface.

    Raises
    ------
    RuntimeError
        If the data interface is not initialized.
    """
    if "data_interface" in st.session_state:
        return st.session_state.data_interface
    else:
        st.error("data_interface wurde nicht initialisiert.")
        st.stop()


def load_module_figs(data_mapping: Dict) -> List:
    """
    Load figures from each module based on the data mapping.

    Parameters
    ----------
    data_mapping : Dict
        The data mapping for the modules.

    Returns
    -------
    List
        A list of figures from the modules.
    """
    figures = []
    for module_name, module_data in data_mapping.items():
        module = importlib.import_module(f'pages.modules.{module_name}_module')
        figures += module.get_module_figs()
    return figures


def main():
    """
    Main function to run the Streamlit app for Presentation Display.
    """
    
    #Exception handling for st.rerun if the Code fails 
    try:
        # Initialize data interface
        data_interface = initialize_data_interface()

        # Streamlit Layout
        columns1, columns2, columns3 = st.columns([5, 1, 1])
        columns1.title("Presentation Display")

        # Navigation
        if columns2.button("Main"):
            switch_page("Main")

        # Define the output unit for Sankey values
        unit = "kWh"
        frequency = data_interface.get_time_frequency()
        last_timestamp = data_interface.get_last_timestamp()
        st.markdown(f"Timestamp: **:blue[{last_timestamp}]**, Unit: **:blue[[{unit}]]**, Measuring frequency: **:blue[{frequency}]**")

        # Data preparation for Sankey Diagram
        sankey_mapping = copy.deepcopy(st.session_state.sankey_mapping)
        sankey_mapping_w_data = update_sankey_consumption(sankey_mapping, frequency, unit)    
        transformed_data = transform_data_for_sankey(sankey_mapping_w_data)
        sankey_table = pd.DataFrame(transformed_data)
        sankey_fig = create_dynamic_plotly_sankey(sankey_table)  

        # Load module figures
        data_mapping = copy.deepcopy(st.session_state.data_mapping)
        figures = load_module_figs(data_mapping)

        # Update layout sizes
        sankey_height = 720
        sankey_fig.update_layout(height=sankey_height)
        individual_height = sankey_height / len(figures)
        for fig in figures:
            fig.update_layout(height=individual_height)

        # Streamlit display
        col1, col2, = st.columns([5, 1])
        with col1:
            st.plotly_chart(sankey_fig, use_container_width=True, theme="streamlit")
        with col2:
            for fig in figures:
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    except Exception as e:
        st.warning(f"An error occurs: {e}")

    # Auto rerun toggle
    auto_rerun = columns3.toggle("Auto rerun")
    if auto_rerun:
        time.sleep(1)
        st.rerun()

    



if __name__ == "__main__":
    configure_streamlit_page("Presentation Display")
    main()

    



