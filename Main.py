import streamlit as st
import importlib
import os
import json
from streamlit_extras.switch_page_button import switch_page
import inspect



api_module = importlib.import_module('functions.api')

#Configer streamlit page
page_title="Main-Skript"
st.set_page_config(
    page_title=page_title,
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'About': f"# This is the {page_title} of the E-Monitoring Software"
    }
    )


def list_available_interfaces():
    subclasses = []
    for name, obj in inspect.getmembers(api_module):  # Verwenden Sie das importierte Modul als Argument
        if inspect.isclass(obj):
            if issubclass(obj, api_module.DataInterface) and obj is not api_module.DataInterface:
                subclasses.append(obj.__name__)
    return subclasses

def create_data_interface(selected_interface, **kwargs):
    for name, obj in inspect.getmembers(api_module):
        if name == selected_interface:
            return obj(**kwargs)
        


def choose_interface(default=None):
    st.subheader("Available Interfaces:")
    available_interfaces = list_available_interfaces()
    selected_interface = st.selectbox("Choose your interface:", available_interfaces, index=available_interfaces.index(default) if default in available_interfaces else 0)  
    return selected_interface




def load_saved_mapping(config_file):
    """
    Load the saved data mapping, system modules, and selected interface from a configuration file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        tuple: The saved data mapping, the selected system modules, and the selected interface.
    """
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            saved_data = json.load(file)
        return saved_data.get("data_mapping", {}), saved_data.get("system_modules", []), saved_data.get("selected_interface", None)
    else:
        return {}, [], None

def save_current_mapping(data_mapping, system_modules, selected_interface, config_file):
    """
    Save the current data mapping, selected system modules, and selected interface to a configuration file.

    Args:
        data_mapping (dict): The current data mapping to be saved.
        system_modules (list): The selected system modules to be saved.
        selected_interface (str): The selected data interface to be saved.
        config_file (str): Path to the configuration file.
    """
    saved_data = {
        "data_mapping": data_mapping,
        "system_modules": system_modules,
        "selected_interface": selected_interface
    }
    with open(config_file, "w") as file:
        json.dump(saved_data, file)

# Function to retrieve available system modules
def get_available_system_modules():
    """
    Retrieve the list of available system modules.
    
    Returns:
        list: A list of module names that are available for selection.
    """
    available_system_modules = []
    module_path = os.path.join(os.path.dirname(__file__), "pages/modules")
    for filename in os.listdir(module_path):
        if filename.endswith("_module.py"):
            module_name = filename.split("_module.py")[0].capitalize()
            available_system_modules.append(module_name)
    return available_system_modules


# Function to display the data mapping user interface
def display_data_mapping(column_names, active_system_modules, saved_data_mapping):
    """
    Display the data mapping interface for the user to map columns to system modules and select units.
    
    Args:
        column_names (list): List of available columns.
        active_system_modules (list): List of active system modules.
        saved_data_mapping (dict, optional): A dictionary containing previously saved data mappings. Defaults to None.
    
    Returns:
        dict: A dictionary representing the user's data mapping selections.
    """
    st.title("Data Mapping")
    data_mapping = {}

    # Create a Counter to change the selectbox-key in every iteration
    counter = 1000

    for module_name in active_system_modules:
        module = importlib.import_module(f"pages.modules.{module_name}_module")

        # Check if the module has the function "get_required_data"
        if not hasattr(module, "get_required_data"):
            st.warning(f"The selected system module '{module_name}' does not contain the function 'get_required_data'. Please update this system module or choose another module.")
            continue

        required_data = module.get_required_data()
        st.markdown('****')
        st.header(f"Data for {module_name}")

        col1, col2 = st.columns([3, 1])

        # Create a dictionary to store the selected data for this module
        module_data_mapping = {}

        for data_name, units in required_data.items():
            
            # Convert column_names to a list so we can use the index() method
            column_list = list(column_names)

            # Try to find the saved unit for this data_name
            saved_unit = None
            for saved_key in saved_data_mapping.get(module_name, {}):
                if saved_key.startswith(data_name):
                    saved_unit = saved_key.split("[")[1].split("]")[0]
                    break

            # If we found the saved unit, set the default value for the column and the unit
            if saved_unit:
                value_from_saved_mapping = saved_data_mapping.get(module_name, {}).get(f"{data_name}_[{saved_unit}]", None)
                default_value = column_list.index(value_from_saved_mapping) if value_from_saved_mapping in column_list else 0
                default_unit = units.index(saved_unit)
            else:
                default_value = 0
                default_unit = 0

            
            selected_column = col1.selectbox(f"Select input data from source for {data_name}:", column_list, index=default_value, key=counter, help="The data series required for the selected plant component are to be entered here. The dropdown selection lists all data series from the interface to the database. " )
            counter += 1

            selected_unit = col2.selectbox(f"Select input unit from source  for {data_name}:", units, index=default_unit, key=counter, help="Here you must select the unit which the data from the data source was acquired. ")
            counter += 1

            # Concatenate the selected column and the unit
            module_data_mapping[f"{data_name}_[{selected_unit}]"] = selected_column

        # Store the data mapping for this module in the main data_mapping
        data_mapping[module_name] = module_data_mapping


    return data_mapping



def set_sankey_mapping_old():
    sankey_mapping = {}

    # Create a Counter to change the selectbox-key in every iteration
    counter = 1000

    for module_name in active_system_modules:
        module = importlib.import_module(f"pages.modules.{module_name}_module")

        # Check if the module has the function "get_required_data"
        if not hasattr(module, "get_sankey_mapping"):
            st.warning(f"The selected system module '{module_name}' does not contain the function 'get_sankey_mapping'. Please update this system module or choose another module.")
            continue

        sankey_mapping = module.get_sankey_mapping()
        

    return sankey_mapping

def set_sankey_mapping(active_system_modules):
    """
    Create a sankey mapping dictionary based on active system modules.
    
    Parameters:
    - active_system_modules: list of strings, names of the active system modules
    
    Returns:
    - sankey_mapping: dictionary, the mapping created by merging all active system modules
    """
    sankey_mapping = {}
    
    for module_name in active_system_modules:
        # Import the module dynamically
        module = importlib.import_module(f"pages.modules.{module_name}_module")
        
        # Check if the module has the function "get_sankey_mapping"
        if not hasattr(module, "get_sankey_mapping"):
            # Assuming `st.warning` is a Streamlit function to show a warning message
            st.warning(f"The selected system module '{module_name}' does not contain the function 'get_sankey_mapping'. Please update this system module or choose another module.")
            continue
        
        # Get the mapping for the current module
        module_mapping = module.get_sankey_mapping()
        
        # Merge the mapping into the existing sankey_mapping
        for key, value in module_mapping.items():
            if key in sankey_mapping:
                sankey_mapping[key].extend(value)
            else:
                sankey_mapping[key] = value
                
    return sankey_mapping


def map_consumption_values(data_mapping: dict, sankey_mapping: dict) -> dict:
    """
    Maps the 'Consumption' values in sankey_mapping using the values from data_mapping.
    Also includes units in the keys of the sankey_mapping.
    
    Parameters:
    - data_mapping (dict): A dictionary containing the mapping between data fields and their labels.
    - sankey_mapping (dict): A dictionary defining Sankey diagram attributes like 'Label', 'Consumption', etc.
    
    Returns:
    - dict: The updated sankey_mapping with 'Consumption' values and units in keys.
    """
    
    # Create an empty dictionary to hold the new sankey_mapping with units
    new_sankey_mapping = {}
    
    # Loop through each key-value pair in data_mapping
    for main_key, sub_dict in data_mapping.items():
        # Loop through each sub-key-value pair in the sub-dictionary
        for sub_key, sub_value in sub_dict.items():
            # Retrieve the unit from the key (e.g., get '_[W]' from 'Compressor_Power_[W]')
            unit = sub_key.split('_[')[1][:-1] if '_[' in sub_key else ''
            
            # Check if the clean key exists in sankey_mapping
            clean_sub_key = sub_key.split('_[')[0]
            if clean_sub_key in sankey_mapping:
                # Create a new key by appending the unit to the clean key
                new_key = f"{clean_sub_key}_[{unit}]" if unit else clean_sub_key
                
                # Copy the existing attributes to the new key
                new_sankey_mapping[new_key] = sankey_mapping[clean_sub_key].copy()
                
                # Update the 'Consumption' value for that key in the new sankey_mapping
                new_sankey_mapping[new_key]['Consumption'] = sub_value
                
    return new_sankey_mapping


# Main function of the main script
def main():
    """
    Main function to run the Streamlit application for data mapping.
    """
    

    # Initialisiere die data_mapping-Variable
    data_mapping = {}

    #Create a Multipage-App
    st.subheader("Jump to:")

    columns = st.columns(2)

    if columns[0].button("Presentation Display"):
        switch_page("presentation_display")

    if columns[1].button("Analysis Layer"):
        switch_page("analysis_layer")





    st.sidebar.title("Select System Modules")
    # List all available system modules (retrieve dynamically)
    available_system_modules = get_available_system_modules()

    # Load the saved configuration
    config_file = os.path.join(os.path.dirname(__file__), "Configuration.json")

    saved_data_mapping, saved_system_modules, saved_interface = load_saved_mapping(config_file)

    
    global active_system_modules # This is required to run the other functions!
    # List of selected system modules (select from Streamlit sidebar)
    default_selection = saved_system_modules if saved_system_modules else available_system_modules
    active_system_modules = st.sidebar.multiselect(
        "Selection of components:", available_system_modules, default=default_selection,
        help="All system modules that are present in the modules folder are listed here. If components are not available in your measuring system, you can deselect them here."
    )

    

    # Pfad zum Verzeichnis der aktuellen Datei (Main.py) ermitteln
    current_file_directory = os.path.dirname(__file__)

    # Arbeitsverzeichnis auf das Verzeichnis der Main.py setzen
    os.chdir(current_file_directory)


    # Set interface
    selected_interface = choose_interface(default=saved_interface)

    # Check if the selected interface is CSVDataInterface to prompt for file path
    if selected_interface == "CSVDataInterface":
        #### Use csv as API ####
        default_path = r"example/example_data1.csv" # rel path 
        csv_file_path = st.text_input("Enter the CSV file path:", default_path)
        c1,c2,c3,c4 = st.columns (4)
        timestamp_col=c1.number_input("Index of timestamp column:",value=0) 
        sep=c2.text_input("CSV seperator:", value=';') 
        decimal=c3.text_input("Decimal divider:",value=',') 
        encoding=c4.text_input("CSV encoding",value=None)
        if encoding == "None":
            encoding = None
        data_interface = create_data_interface(selected_interface, filename=csv_file_path,timestamp_col=timestamp_col, sep=sep, decimal=decimal, encoding=encoding)
    
    else:
        data_interface = create_data_interface(selected_interface)
    
    
    st.session_state.data_interface = data_interface

    #column_names = get_column_names(csv_file_path)
    column_names = data_interface.get_column_names()


    # Display the data mapping user interface
    data_mapping = display_data_mapping(column_names, active_system_modules, saved_data_mapping)


    # Save sankey mapping in session state
    sankey_mapping = set_sankey_mapping(active_system_modules)
    updated_sankey_mapping = map_consumption_values(data_mapping, sankey_mapping)
    st.session_state.sankey_mapping = updated_sankey_mapping


    # Save the current settings
    save_current_mapping(data_mapping, active_system_modules, selected_interface, config_file)
    

    # Store the updated data mapping in the session state
    st.session_state.data_mapping = data_mapping

    # Rerun Code to save all changes
    st.markdown('****')

    if st.button('Save Mapping'):
        st.experimental_rerun()

    # show mapping 

    with st.expander("Show Mapping:"):
        "selected_interface:"
        st.write(selected_interface)
        "sankey_mapping:"
        st.write(sankey_mapping)
       
        
        "saved_system_modules:"
        st.write(saved_system_modules)
        "saved_data_mapping:"
        st.write(saved_data_mapping)
        




if __name__ == "__main__":
    main()
