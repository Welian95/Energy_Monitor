import streamlit as st
import importlib
import os
import json
from streamlit_extras.switch_page_button import switch_page
import inspect

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
        initial_sidebar_state="auto",
        menu_items={
            'About': f"# This is the {page_title} of the E-Monitoring Software"
        }
    )


def import_api_module():
    """Import the API module and return it.

    Returns
    -------
    Module
        The imported API module.
    """
    api_module = importlib.import_module('functions.api')

    return api_module

def list_available_interfaces(api_module):
    """List all available data interfaces that are subclasses of `DataInterface` from the given module.

    This function dynamically inspects the given module to find all subclasses of `DataInterface`.
    It does not include `DataInterface` itself in the list.

    Parameters
    ----------
    api_module : Module
        The module to inspect for subclasses of `DataInterface`.

    Returns
    -------
    list
        A list containing the names of all available data interface subclasses.
    """
    subclasses = []
    for name, obj in inspect.getmembers(api_module):
        if inspect.isclass(obj):
            if issubclass(obj, api_module.DataInterface) and obj is not api_module.DataInterface:
                subclasses.append(obj.__name__)
    return subclasses


def create_data_interface(api_module, selected_interface, **kwargs):
    """Dynamically creates an instance of the selected data interface from the given module.

    This function dynamically instantiates a class by its name from the given module.

    Parameters
    ----------
    api_module : Module
        The module to inspect for the selected data interface.
    selected_interface : str
        The name of the data interface class to instantiate.
    **kwargs : dict
        Arbitrary keyword arguments that will be passed to the constructor of the selected interface.

    Returns
    -------
    object
        An instance of the selected data interface, initialized with the provided keyword arguments.
    """
    for name, obj in inspect.getmembers(api_module):
        if name == selected_interface:
            return obj(**kwargs)
        


def choose_interface(api_module, default=None):
    """Display a Streamlit select box for the user to choose a data interface.

    Parameters
    ----------
    api_module : Module
        The module to inspect for available data interfaces.
    default : str, optional
        The name of the data interface to be selected by default. Defaults to None.

    Returns
    -------
    str
        The name of the selected data interface.
    """
    st.subheader("Available Interfaces:")
    available_interfaces = list_available_interfaces(api_module)
    selected_interface = st.selectbox(
        "Choose your interface:", available_interfaces, 
        index=available_interfaces.index(default) if default in available_interfaces else 0
    )  
    return selected_interface


def load_saved_mapping(config_file):
    """Load the saved data mapping, system modules, and selected interface from a configuration file.

    Parameters
    ----------
    config_file : str
        Path to the configuration file.

    Returns
    -------
    tuple
        The saved data mapping, the selected system modules, and the selected interface.
    """
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            saved_data = json.load(file)
        return (
            saved_data.get("data_mapping", {}), 
            saved_data.get("system_modules", []), 
            saved_data.get("selected_interface", None)
        )
    else:
        return {}, [], None

def save_current_mapping(data_mapping, system_modules, selected_interface, config_file):
    """Save the current data mapping, selected system modules, and selected interface to a configuration file.

    Parameters
    ----------
    data_mapping : dict
        The current data mapping to be saved.
    system_modules : list
        The selected system modules to be saved.
    selected_interface : str
        The selected data interface to be saved.
    config_file : str
        Path to the configuration file.
    """
    saved_data = {
        "data_mapping": data_mapping,
        "system_modules": system_modules,
        "selected_interface": selected_interface
    }
    with open(config_file, "w") as file:
        json.dump(saved_data, file)

def get_available_system_modules(module_path):
    """Retrieve the list of available system modules.

    Parameters
    ----------
    module_path : str
        The file path where system modules are located.

    Returns
    -------
    list
        A list of module names that are available for selection.
    """
    available_system_modules = []
    for filename in os.listdir(module_path):
        if filename.endswith("_module.py"):
            module_name = filename.split("_module.py")[0].capitalize()
            available_system_modules.append(module_name)
    return available_system_modules

def get_default_values(column_list, saved_data_mapping, module_name, data_name, units):
    """Get default values for column and unit selection from saved data mapping.
    
    Parameters
    ----------
    column_list : list
        List of available columns.
    saved_data_mapping : dict
        Dictionary containing previously saved data mappings.
    module_name : str
        The name of the system module.
    data_name : str
        The name of the data to be mapped.
    units : list
        List of available units.
    
    Returns
    -------
    int, int
        The default indices for column and unit selection.
    """
    saved_unit = None
    for saved_key in saved_data_mapping.get(module_name, {}):
        if saved_key.startswith(data_name):
            saved_unit = saved_key.split("[")[1].split("]")[0]
            break

    if saved_unit:
        value_from_saved_mapping = saved_data_mapping.get(module_name, {}).get(f"{data_name}_[{saved_unit}]", None)
        default_value = column_list.index(value_from_saved_mapping) if value_from_saved_mapping in column_list else 0
        default_unit = units.index(saved_unit)
    else:
        default_value = 0
        default_unit = 0

    return default_value, default_unit

def display_data_mapping(column_names, active_system_modules, saved_data_mapping):
    """Display the data mapping interface for the user to map columns to system modules and select units.
    
    Parameters
    ----------
    column_names : list
        List of available columns.
    active_system_modules : list
        List of active system modules.
    saved_data_mapping : dict, optional
        A dictionary containing previously saved data mappings.
    
    Returns
    -------
    dict
        A dictionary representing the user's data mapping selections.
    """
    st.title("Data Mapping")
    data_mapping = {}
    counter = 1000  # Create a Counter to change the selectbox-key in every iteration

    for module_name in active_system_modules:
        module = importlib.import_module(f"pages.modules.{module_name}_module")

        if not hasattr(module, "get_required_data"):
            st.warning(f"The selected system module '{module_name}' does not contain the function 'get_required_data'. Please update this system module or choose another.")
            continue

        required_data = module.get_required_data()
        st.markdown('****')
        st.header(f"Data for {module_name}")

        col1, col2 = st.columns([3, 1])
        module_data_mapping = {}

        for data_name, units in required_data.items():
            column_list = list(column_names)  # Convert to list to use the index() method
            default_value, default_unit = get_default_values(column_list, saved_data_mapping, module_name, data_name, units)

            selected_column = col1.selectbox(f"Select input data for {data_name}:", column_list, index=default_value, key=counter)
            counter += 1
            selected_unit = col2.selectbox(f"Select input unit for {data_name}:", units, index=default_unit, key=counter)
            counter += 1

            module_data_mapping[f"{data_name}_[{selected_unit}]"] = selected_column

        data_mapping[module_name] = module_data_mapping

    return data_mapping




def set_sankey_mapping(active_system_modules, module_path="pages.modules"):
    """Create a sankey mapping dictionary based on active system modules.

    This function dynamically imports modules based on their names, invokes
    a `get_sankey_mapping` function in each module (if it exists), and merges
    the returned mappings.

    Parameters
    ----------
    active_system_modules : list
        List of strings, names of the active system modules.
    module_path : str, optional
        The file path where system modules are located. Defaults to "pages.modules".

    Returns
    -------
    dict
        The sankey mapping created by merging all active system modules.
    """
    sankey_mapping = {}
    
    for module_name in active_system_modules:
        # Import the module dynamically
        module = importlib.import_module(f"{module_path}.{module_name}_module")
        
        # Check if the module has the function "get_sankey_mapping"
        if not hasattr(module, "get_sankey_mapping"):
            st.warning(f"The selected system module '{module_name}' does not contain the function 'get_sankey_mapping'. Please update this system module or choose another.")
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




def flatten_data_mapping(data_mapping: dict) -> dict:
    """Flatten a nested dictionary into a single-level dictionary.
    
    Parameters
    ----------
    data_mapping : dict
        A nested dictionary to be flattened.
        
    Returns
    -------
    dict
        A single-level dictionary.
    """
    flat_data_mapping = {}
    for main_key, sub_dict in data_mapping.items():
        flat_data_mapping.update(sub_dict)
    return flat_data_mapping

def map_consumption_values(data_mapping: dict, sankey_mapping: dict) -> dict:
    """Maps the 'Consumption' values in sankey_mapping using the values from data_mapping.
    Also includes units in the keys of the sankey_mapping.
    
    Parameters
    ----------
    data_mapping : dict
        A dictionary containing the mapping between data fields and their labels.
    sankey_mapping : dict
        A dictionary defining Sankey diagram attributes like 'Label', 'Consumption', etc.
        
    Returns
    -------
    dict
        The updated sankey_mapping with 'Consumption' values and units in keys.
    """
    flat_data_mapping = flatten_data_mapping(data_mapping)
    new_sankey_mapping = {}
    
    for sankey_key, attributes in sankey_mapping.items():
        new_attributes = attributes.copy()
        
        if attributes['Consumption'] is None:
            for sub_key, sub_value in flat_data_mapping.items():
                clean_sub_key = sub_key.split('_[')[0]
                if clean_sub_key == sankey_key:
                    new_attributes['Consumption'] = sub_value
                    unit = sub_key.split('_[')[1][:-1] if '_[' in sub_key else ''
                    new_key = f"{sankey_key}_[{unit}]" if unit else sankey_key
                    new_sankey_mapping[new_key] = new_attributes
                    break
            else:
                new_sankey_mapping[sankey_key] = new_attributes
                
        else:
            expression = attributes['Consumption']
            for sub_key, sub_value in flat_data_mapping.items():
                clean_sub_key = sub_key.split('_[')[0]
                expression = expression.replace(clean_sub_key, sub_value)
            new_attributes['Consumption'] = expression
            new_sankey_mapping[sankey_key] = new_attributes
    
    return new_sankey_mapping




def load_configuration(config_file_path):
    """Load saved configurations from a JSON file.

    Parameters
    ----------
    config_file_path : str
        Absolute or relative path to the configuration JSON file.

    Returns
    -------
    tuple
        A tuple containing saved_data_mapping, saved_system_modules, and saved_interface.
    """
    return load_saved_mapping(config_file_path)





# Main function of the Main script 
def main():
    """Main function to run the Streamlit application for data mapping.

    This function serves as the entry point for the Streamlit application.
    It handles interface selection, data mapping, and saving configurations.
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
    module_path = os.path.join(os.path.dirname(__file__), "pages/modules")
    available_system_modules = get_available_system_modules(module_path)

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

    

    # Path to current file-dir (Main.py) 
    current_file_directory = os.path.dirname(__file__)

    #Set working directory for Main.py
    os.chdir(current_file_directory)


    # Set interface
    selected_interface = choose_interface(api_module, default=saved_interface)

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
        data_interface = create_data_interface(api_module, selected_interface, filename=csv_file_path,timestamp_col=timestamp_col, sep=sep, decimal=decimal, encoding=encoding)
    
    else:
        data_interface = create_data_interface(api_module, selected_interface)
    
    
    st.session_state.data_interface = data_interface

    #column_names = get_column_names(csv_file_path)
    column_names = data_interface.get_column_names()


    # Display the data mapping user interface
    data_mapping = display_data_mapping(column_names, active_system_modules, saved_data_mapping)



    # Save sankey mapping in session state
    sankey_mapping = set_sankey_mapping(active_system_modules,)


    updated_sankey_mapping = map_consumption_values(data_mapping, sankey_mapping)


    st.session_state.sankey_mapping = updated_sankey_mapping


    # Save the current settings
    save_current_mapping(data_mapping, active_system_modules, selected_interface, config_file)
    

    # Store the updated data mapping in the session state
    st.session_state.data_mapping = data_mapping

    # Rerun Code to save all changes
    st.markdown('****')

    if st.button('Save Mapping'):
        st.rerun()

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
    api_module = import_api_module()
    configure_streamlit_page("Main-Skript")
    main()
