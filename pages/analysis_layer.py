import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import datetime as dt
import pandas as pd
import importlib
from functions import imputation
from functions import compute_energy
from functions import conversion 




#Configer streamlit page
page_title="Analysis Layer"
st.set_page_config(
    page_title=page_title,
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'About': f"# This is the {page_title} of the E-Monitoring Software"
    }
)

def extract_unit(column_name):
    return column_name[column_name.find("[")+1:column_name.find("]")]



def create_figure(selected_data, start_date, end_date):
    """
    Creates a list of combined plotly figures based on the selected data.
    
    Args:
        selected_data: A dictionary containing the selected data.
        start_date: A string or datetime object indicating the start date.
        end_date: A string or datetime object indicating the end date.
    
    Returns:
        A list of plotly figures.
    """
    figures = []
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    unit_list = []
    
    for module, data in selected_data.items():
        for column_name, column_data in data.items():
            unit = extract_unit(column_name)
            
            # Add the unit to the list if it's not already there
            if unit not in unit_list:
                unit_list.append(unit)
            
            # If we've added 2 units to the current figure, add it to the list and start a new one
            if len(unit_list) > 2:
                figures.append((fig, unit_list[:]))
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                unit_list = [unit]
            
            secondary_y = unit_list.index(unit) == 1
            
            # Add the data to the figure
            fig.add_trace(go.Scatter(
                x=column_data.index, 
                y=column_data, 
                name=column_name,
                fill='tozeroy',
                mode='lines',
                hovertemplate=
                '<br>Date: %{x}<br>' +
                'Year: %{x|%Y}<br>' +
                'Value: %{y} [' + unit + ']<br>',
                hoverlabel=dict(namelength=-1)
            ), secondary_y=secondary_y)
    
    # If there's a figure with less than 2 units, add it to the list
    if len(fig.data) > 0:
        figures.append((fig, unit_list[:]))

    for fig, unit_list in figures:
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        fig.update_yaxes(title_text=f"[{unit_list[0]}]", secondary_y=False)
        if len(unit_list) > 1:
            fig.update_yaxes(title_text=f"[{unit_list[1]}]", secondary_y=True)

        # Update the x-axis range
        fig.update_xaxes(range=[start_date, end_date], autorange=False)

    return [fig for fig, _ in figures]





def date_range_selector(start_date: dt.date, end_date: dt.date):
    """
    Display a date range selector UI using Streamlit and return the selected date range.
    
    Parameters:
    - start_date (dt.date): The earliest selectable date.
    - end_date (dt.date): The latest selectable date.
    
    Returns:
    - tuple: A tuple containing the selected start and end dates (dt.date, dt.date).
    """

    # Initialize session state if it doesn't exist yet
    if 'start_date' not in st.session_state:
        st.session_state.start_date = start_date
    if 'end_date' not in st.session_state:
        st.session_state.end_date = end_date

    # Ensure end_date is at least one day after start_date
    if start_date == end_date:
        end_date = start_date + dt.timedelta(days=1)
    
    # Create columns for layout
    cols1, cols2 = st.columns((2, 1))

    # Ensure the range of the slider never goes below the initial input range
    min_date = min(st.session_state.start_date, start_date)
    max_date = max(st.session_state.end_date, end_date)

    # Check if the time span is greater than one year
    if (max_date - min_date).days > 365:
        initial_value = (max_date - dt.timedelta(days=365), max_date)
    else:
        initial_value = (min_date, max_date)
    
    # Display the slider
    slider = cols1.slider('Select date', min_value=min_date, value=initial_value, max_value=max_date)
    st.session_state.start_date, st.session_state.end_date = slider
    
    # Date input for further refinement
    prev_start_date = st.session_state.start_date
    prev_end_date = st.session_state.end_date
    date_range = cols2.date_input('Select date range', [st.session_state.start_date, st.session_state.end_date])
    if date_range[0] != prev_start_date or date_range[1] != prev_end_date:
        st.session_state.start_date, st.session_state.end_date = date_range
        st.rerun()
    
    return st.session_state.start_date, st.session_state.end_date





# Updated version of the process_selected_data function
def get_selected_data(data_mapping, start_time, end_time):
    """
    Process selected data based on user input from the Streamlit sidebar.
    
    Parameters:
    - data_mapping (dict): A mapping of module names to data names and column names.
    - start_time (datetime): The start time for data filtering.
    - end_time (datetime): The end time for data filtering.
    
    Returns:
    - selected_data (dict): A dictionary containing the selected data.
    """
    
    # Initialize a counter to change the checkbox-key in every iteration
    counter = 0
    
    # Initialize an empty dictionary to store selected data
    selected_data = {}
    
    # Iterate through each module and its corresponding data
    for module_name, module_data in data_mapping.items():
        selected_data[module_name] = {}
        expander = st.sidebar.expander(f"Analyse Data for {module_name}")
        counter += 1
        
        for data_name, column_name in module_data.items():
            key = f"{module_name}_{data_name}_{counter}"
            selected = expander.checkbox(data_name, value=False, key=key)
            counter += 1
            
            if selected:
                
                # Dynamically import the module
                module = importlib.import_module(f'pages.modules.{module_name}_module')
                
                # Load the data from the API
                loaded_data = module.load_module_data(data_mapping, [module_name], start_time, end_time)
                
                # Organize data in dict
                selected_data[module_name][data_name] = loaded_data[column_name]

    return selected_data


def convert_processed_data(selected_data):
    """
    Process and convert selected data based on user input from the Streamlit UI.
    
    Parameters:
    - selected_data (dict): A dictionary containing the selected data from different modules.
    
    Returns:
    - processed_data (dict): A dictionary containing the processed and possibly converted data.
    """
    
    # Initialize an empty dictionary to store processed data
    processed_data = {}
    
    # Create a general expander for unit settings and interpolation
    general_expander = st.expander("General Settings for Selected Data")

    col1, col2 = general_expander.columns([1,3])

    # Unit conversion settings
    display_option = col1.radio(
        "Display Option:",
        ("Individual", "Display as energy", "Display as power"),
        help= "With Individual, the unit can be converted for each selected module. With dispaly as energy, all energy and power values are displayed in energy with display as power vice versa. "
    )

    # Initialize selected_unit as None
    selected_unit = None

    if display_option == "Display as energy":
        unit_options = ["kWh", "Wh", "J", "MJ", "GJ"]
        selected_unit = col2.selectbox("Select energy unit:", unit_options, index=0)
        
    elif display_option == "Display as power":
        unit_options = ["kW", "W", "J/s", "MW", "GW"]
        selected_unit = col2.selectbox("Select power unit:", unit_options, index=0)
    
    # Interpolation settings
    freq = general_expander.number_input("Input a frequency in Minutes:", value=0, help="If value is 0 the original frequency of the data is used")
    
    if freq <= 0:
        freq = None
    else:
        freq = f"{freq}T"
    
    # Iterate through each module and its corresponding data
    for module_name, module_data in selected_data.items():
        processed_data[module_name] = {}
        
        for data_name, data_series in module_data.items():

            # Extract the original unit from data_name
            original_unit = extract_unit(data_name)
            
            # Handle individual unit conversion
            if display_option == "Individual":
                # Use your conversion.find_compatible_units function here
                compatible_units = conversion.find_compatible_units(original_unit)
                
                # Add "None" as an option for no conversion
                compatible_units.append("None")

                # Determine the default index for the original unit, or set to the index for "None"
                default_index = compatible_units.index(original_unit) if original_unit in compatible_units else compatible_units.index("None")
                
                # Add a selectbox for each data series
                selected_individual_unit = col2.selectbox(f"Select unit for {module_name} - {data_name}:", compatible_units, index=default_index)
                
                # Use your conversion.convert_unit_of_dataframe function here if selected_individual_unit is not "None"
                if selected_individual_unit != "None" and selected_individual_unit != original_unit:
                    data_series = conversion.convert_unit_of_dataframe(data_series.to_frame(), original_unit, selected_individual_unit).squeeze()
                    data_name = data_name.replace(f"[{original_unit}]", f"[{selected_individual_unit}]")
            

            # Check or get frequency
            if freq is None:
                try:
                    freq = pd.infer_freq(data_series.index)
                    if freq is None:
                        raise ValueError
                except ValueError:
                    freq = "1T"
                    general_expander.warning("The time series data contains fewer than 3 timestamps, so the frequency of the data cannot be determined. Defaulting to 1 minute. Please make sure you have at least 3 records with timestamps in your dataset.")

            # Interpolate data
            interpolated_data = imputation.interpolate_impute(data_series.to_frame(), freq=freq)

            # Perform unit conversion if necessary and if selected_unit is not None
            if selected_unit is not None:
                converted_data = compute_energy.power_energy(interpolated_data, original_unit, selected_unit, freq)
                
                # Update data_name to reflect the new unit
                new_data_name = data_name.replace(f"[{original_unit}]", f"[{selected_unit}]")
            else:
                converted_data = interpolated_data
                new_data_name = data_name

            
            # Check if conversion was successful
            if isinstance(converted_data, str):
                st.write(f"Conversion failed for {data_name} in module {module_name}. Keeping original data.")
                processed_data[module_name][data_name] = data_series
            else:
                # Organize data in dict
                processed_data[module_name][new_data_name] = converted_data.squeeze()

    return processed_data




def main():
    
    columns = st.columns(2)
    columns[0].title(page_title)

    #Set datainterface
    data_interface = st.session_state.data_interface 


    # Sidebar
    st.sidebar.title("Module Data Selection")

    data_mapping = st.session_state.data_mapping


    #Get timestamps from api
    
    first_timstamp = data_interface.get_first_timestamp()
    last_timestamp = data_interface.get_last_timestamp()
    

    # set start- and end- time
    start_time = None
    end_time =  None
    
    #select time series 
    if start_time and end_time is not None:

        newest_time = st.session_state.selected_data
        latest_time = st.session_state.selected_data
    else:
        newest_time = first_timstamp
        latest_time = last_timestamp

    selected_times = date_range_selector(newest_time.date(), latest_time.date())
    start_time = selected_times[0]
    end_time =  selected_times[1]

    #Load and change Data:
    selected_data = get_selected_data(data_mapping, start_time, end_time)
    
    processed_data = convert_processed_data(selected_data)
    

    # Store the selected data in the Streamlit session state
    st.session_state.processed_data = processed_data


    # Check if any data has been selected
    if any(processed_data.values()):


        # Create and display the combined chart
        figures = create_figure(st.session_state.processed_data,start_time, end_time)
        for fig in figures:
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("Please select data to display.")

    

if __name__ == "__main__":
    main()

