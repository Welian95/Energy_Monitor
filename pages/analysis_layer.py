# Standard Libraries
import datetime as dt, datetime
from datetime import timedelta
from datetime import date as dt_date
import streamlit as st
import importlib
import re
from collections import defaultdict
from typing import Dict, Optional 

# Third-party Libraries
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


# Custom Modules
from functions import imputation
from functions import compute_energy
from functions import conversion 




#Configer streamlit page
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

def extract_unit(column_name: str) -> Optional[str]:
    """
    Extract the unit from a column name enclosed in square brackets.

    Parameters
    ----------
    column_name : str
        The name of the column, e.g., "Temperature [C]".

    Returns
    -------
    Optional[str]
        The unit extracted from the column name, e.g., "C". 
        Returns None if no unit is found.

    Examples
    --------
    >>> extract_unit("Temperature [C]")
    'C'
    >>> extract_unit("Pressure")
    None
    """
    match = re.search(r'\[(.*?)\]', column_name)
    return match.group(1) if match else None

def load_module_data(module_name: str, data_mapping: Dict, start_time: datetime, end_time: datetime):
    """
    Dynamically imports a module and loads its data based on the provided time range.

    Parameters
    ----------
    module_name : str
        The name of the module to be imported.
    data_mapping : Dict
        A dictionary that maps module names to data names and column names.
    start_time : datetime
        The start time for data filtering.
    end_time : datetime
        The end time for data filtering.

    Returns
    -------
    Dict
        Loaded data as a dictionary.

    Raises
    ------
    Exception
        If the data could not be loaded.
    """
    module = importlib.import_module(f'pages.modules.{module_name}_module')
    try:
        return module.load_module_data(data_mapping, [module_name], start_time, end_time)
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def get_selected_data(data_mapping: Dict, start_time: datetime, end_time: datetime) -> Dict:
    """
    Process selected data based on user input from the Streamlit sidebar.

    Parameters
    ----------
    data_mapping : Dict
        A dictionary that maps module names to data names and column names.
    start_time : datetime
        The start time for data filtering.
    end_time : datetime
        The end time for data filtering.

    Returns
    -------
    Dict
        A dictionary containing the selected data.

    Examples
    --------
    >>> get_selected_data({'Module1': {'Data1': 'Column1'}}, start_time, end_time)
    {'Module1': {'Data1': loaded_data}}
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
                try:
                    # Load the data from the API
                    loaded_data = load_module_data(module_name, data_mapping, start_time, end_time)

                    # Organize data in dict
                    selected_data[module_name][data_name] = loaded_data[column_name]
                except Exception as e:
                    st.write(f"Ein Fehler ist aufgetreten: {e}")

    return selected_data

def unit_conversion_settings(display_option: str, col: object) -> Optional[str]:
    """
    Handle unit conversion settings based on the selected display option.

    Parameters
    ----------
    display_option : str
        The selected display option: "Individual", "Display as energy", "Display as power".
    col : object
        Streamlit column object for placing widgets.

    Returns
    -------
    Optional[str]
        The selected unit for energy or power conversion. None if "Individual" is selected.
    """
    selected_unit = None
    if display_option == "Display as energy":
        unit_options = ["kWh", "Wh", "J", "MJ", "GJ"]
        selected_unit = col.selectbox("Select energy unit:", unit_options, index=0)
    elif display_option == "Display as power":
        unit_options = ["kW", "W", "J/s", "MW", "GW"]
        selected_unit = col.selectbox("Select power unit:", unit_options, index=0)
    return selected_unit

def handle_interpolation_settings(col1: object, col2: object) -> str:
    """
    Handle interpolation settings and return the selected frequency.

    Parameters
    ----------
    col1 : object
        Streamlit column object for placing widgets.
    col2 : object
        Streamlit column object for placing widgets.

    Returns
    -------
    str
        The selected frequency for interpolation.
    """
    freq_dict = {
        "None" : 0,
        "15 minutes" : 15,
        "30 minutes" : 30,
        "hour" : 60,
        "day" : 1440,
        "week (fixed frequency)": 10080,
        "month (fixed frequency)": 43800,
    }
    selected_key = col1.selectbox("Choose a time frequency:", list(freq_dict.keys()))
    freq_range = freq_dict[selected_key]
    freq = col2.number_input("Input a frequency in Minutes:", value=freq_range)
    if freq <= 0:
        freq = None
    elif freq == 60:
        freq = "1H"
    elif freq == 1440:
        freq = "1D"
    else:
        freq = f"{freq}T"
    return freq

def convert_processed_data(selected_data: Dict) -> Dict:
    """
    Processes and converts the selected data entered by the user via the Streamlit user interface.

    Parameters
    ----------
    selected_data : dict
        A dictionary containing the selected data from different modules.

    Returns
    -------
    dict
        A dictionary containing the processed and possibly converted data.
    """
    processed_data = {}
    general_expander = st.expander("General Settings for Selected Data")
    col1, col2 = general_expander.columns([1, 3])
    col_imputation_1, col_imputation_2 = general_expander.columns([1, 3])

    display_option = col1.radio(
        "Display Option:",
        ("Individual", "Display as energy", "Display as power")
    )

    selected_unit = unit_conversion_settings(display_option, col2)
    freq = handle_interpolation_settings(col_imputation_1, col_imputation_2)

    for module_name, module_data in selected_data.items():
        processed_data[module_name] = {}
        
        for data_name, data_series in module_data.items():
            # Extract the original unit from data_name
            original_unit = extract_unit(data_name)
            
            # Handle individual unit conversion
            if display_option == "Individual":
                compatible_units = conversion.find_compatible_units(original_unit)
                compatible_units.append("None")
                default_index = compatible_units.index(original_unit) if original_unit in compatible_units else compatible_units.index("None")
                selected_individual_unit = col2.selectbox(f"Select unit for {module_name} - {data_name}:", compatible_units, index=default_index)
                
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
                    general_expander.warning("The time series data contains fewer than 3 timestamps, so the frequency of the data cannot be determined. Defaulting to 1 minute.")
            
            # Interpolate data
            interpolated_data = imputation.interpolate_impute(data_series.to_frame(), freq=freq)

            # Perform unit conversion if necessary and if selected_unit is not None
            if selected_unit is not None:
                converted_data = compute_energy.power_energy(interpolated_data, original_unit, selected_unit, freq)
                new_data_name = data_name.replace(f"[{original_unit}]", f"[{selected_unit}]")
            else:
                converted_data = interpolated_data
                new_data_name = data_name
            
            # Check if conversion was successful
            if isinstance(converted_data, str):
                st.write(f"Conversion failed for {data_name} in module {module_name}. Keeping original data.")
                processed_data[module_name][data_name] = data_series
            else:
                processed_data[module_name][new_data_name] = converted_data.squeeze()

    return processed_data

def convert_to_dataframe(nested_dict: Dict) -> pd.DataFrame:
    """
    Converts a nested dictionary to a single-level Pandas DataFrame.

    Parameters
    ----------
    nested_dict : dict
        The nested dictionary containing the data.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the flattened data.
    """
    # Initialize an empty DataFrame to hold the final data
    final_df = pd.DataFrame()
    
    # Loop through each module and its series
    for module, series_dict in nested_dict.items():
        for series_name, series_data in series_dict.items():
            # Create a new column name based on the module and series name
            new_col_name = f"{module}_{series_name}"
            
            # Add the series to the final DataFrame
            final_df[new_col_name] = series_data
            
    return final_df

def manage_units_and_subplots(figures, unit, fig=None, unit_list=None):
    """
    Manages the list of units and creates new subplots as needed.
    
    Parameters
    ----------
    figures : list
        List of existing figures and their associated unit lists.
    unit : str
        The unit to be added.
    fig : plotly.graph_objs.Figure, optional
        Current working figure.
    unit_list : list, optional
        List of units already added to the current figure.
        
    Returns
    -------
    figures : list
        List of figures, potentially with a new figure added.
    fig : plotly.graph_objs.Figure
        The updated or new figure.
    unit_list : list
        The updated list of units.
    """
    if fig is None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    if unit_list is None:
        unit_list = []
        
    if unit not in unit_list:
        unit_list.append(unit)
        
    if len(unit_list) > 2:
        figures.append((fig, unit_list[:-1]))
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        unit_list = [unit]
        
    return figures, fig, unit_list

def update_figure_layout(fig, unit_list, start_date, end_date):
    """
    Updates the layout and axis titles for a given figure.
    
    Parameters
    ----------
    fig : plotly.graph_objs.Figure
        The figure to update.
    unit_list : list
        List of units associated with this figure.
    start_date : str or datetime object
        Start date for the x-axis range.
    end_date : str or datetime object
        End date for the x-axis range.
    """
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
    fig.update_xaxes(range=[start_date, end_date], autorange=False)

def create_line_figure(selected_data, start_date, end_date):
    """
    Creates a list of combined Plotly figures based on the selected data.

    Parameters
    ----------
    selected_data : dict
        A dictionary containing the selected data.
    start_date : str or datetime object
        A string or datetime object indicating the start date.
    end_date : str or datetime object
        A string or datetime object indicating the end date.

    Returns
    -------
    list
        A list of Plotly figures.
    """
    figures = []
    fig = None  # Initialize to None
    unit_list = None  # Initialize to None
    
    for module, data in selected_data.items():
        for column_name, column_data in data.items():
            unit = extract_unit(column_name)
            
            # Update figures, fig, and unit_list based on the new unit
            figures, fig, unit_list = manage_units_and_subplots(figures, unit, fig, unit_list)
            
            secondary_y = unit_list.index(unit) == 1
            
            # Add the data to the figure
            fig.add_trace(go.Scatter(
                x=column_data.index, 
                y=column_data, 
                name=column_name,
                mode='lines',
                hovertemplate=
                '<br>Date: %{x}<br>' +
                'Value: %{y} [' + unit + ']<br>',
                hoverlabel=dict(namelength=-1)
            ), secondary_y=secondary_y)
            
    if len(fig.data) > 0:
        figures.append((fig, unit_list[:]))  # If there's a figure with more than 2 units, add it to the list
    
    # Update the layout for all figures
    for fig, unit_list in figures:
        update_figure_layout(fig, unit_list, start_date, end_date)
            
    return [fig for fig, _ in figures]

def create_bar_figure(selected_data, start_date, end_date):
    """
    Creates a list of combined Plotly bar charts based on the selected data.

    Parameters
    ----------
    selected_data : dict
        A dictionary containing the selected data.
    start_date : str or datetime object
        A string or datetime object indicating the start date.
    end_date : str or datetime object
        A string or datetime object indicating the end date.

    Returns
    -------
    list
        A list of Plotly figures.
    """
    figures = []
    fig = None  # Initialize to None
    unit_list = None  # Initialize to None
    
    for module, data in selected_data.items():
        for column_name, column_data in data.items():
            unit = extract_unit(column_name)
            
            # Update figures, fig, and unit_list based on the new unit
            figures, fig, unit_list = manage_units_and_subplots(figures, unit, fig, unit_list)
            
            secondary_y = unit_list.index(unit) == 1
            
            # Add the data as a bar chart
            fig.add_trace(go.Bar(
                x=column_data.index,
                y=column_data,
                name=column_name,
                hovertemplate=
                '<br>Date: %{x}<br>' +
                'Year: %{x|%Y}<br>' +
                'Value: %{y} [' + unit + ']<br>',
                hoverlabel=dict(namelength=-1)
            ), secondary_y=secondary_y)
            
    if len(fig.data) > 0:
        figures.append((fig, unit_list[:]))  # If there's a figure with more than 2 units, add it to the list
    
    # Update the layout for all figures
    for fig, unit_list in figures:
        update_figure_layout(fig, unit_list, start_date, end_date)
            
    return [fig for fig, _ in figures]

def create_duration_curve_figure(selected_data, start_date, end_date):
    """
    Creates a list of combined Plotly duration curve charts with the x-axis in hours based on the selected data.
    The function automatically infers the time frequency from the data index using pd.infer_freq and converts it to minutes.

    Parameters
    ----------
    selected_data : dict
        A dictionary containing the selected data.
    start_date : str or datetime object
        A string or datetime object indicating the start date.
    end_date : str or datetime object
        A string or datetime object indicating the end date.

    Returns
    -------
    list
        A list of Plotly figures.
    """

    figures = []
    fig = make_subplots(specs=[[{"secondary_y": True}]])  # Create a subplot with secondary y-axis
    unit_list = []
    
    # Iterate over each module and its data
    for module, data in selected_data.items():
        for column_name, column_data in data.items():
            unit = extract_unit(column_name)  # Extract the unit from the column name
            
            # Add the unit to the list if it's not already there
            if unit not in unit_list:
                unit_list.append(unit)
            
            # If we've added 2 units to the current figure, add it to the list and start a new one
            if len(unit_list) > 2:
                figures.append((fig, unit_list[:]))
                fig = make_subplots(specs=[[{"secondary_y": True}]])  # Create a new subplot
                unit_list = [unit]
            
            secondary_y = unit_list.index(unit) == 1  # Check if this is a secondary y-axis
            
            # Sort the data in descending order and create a duration curve
            sorted_data = column_data.sort_values(ascending=False).reset_index(drop=True)
            
            # Infer the frequency
            freq_str = pd.infer_freq(column_data.index)
            if freq_str:
                freq_offset = pd.tseries.frequencies.to_offset(freq_str)
                # Check if the offset object has a 'delta' attribute
                if hasattr(freq_offset, 'delta'):
                    freq_seconds = freq_offset.delta.total_seconds()
                else:
                    # Manually convert the frequency to seconds for special offsets like 'W' for week
                    if freq_str == 'W':
                        freq_seconds = 7 * 24 * 60 * 60
                    elif freq_str == 'M':
                        freq_seconds = 30 * 24 * 60 * 60  # Approximation
                    else:
                        freq_seconds = None  # Unknown frequency
                
                if freq_seconds is not None:
                    freq_minutes = freq_seconds / 60
                    intervals_per_hour = 60 / freq_minutes
            
                    # Calculate the duration in hours
                    duration_in_hours = sorted_data.index / intervals_per_hour
                else:
                    duration_in_hours = sorted_data.index  # Unknown frequency, use index as is
            else:
                # If frequency cannot be inferred, use the index as is
                duration_in_hours = sorted_data.index
            
            # Add the data as a scatter plot
            fig.add_trace(go.Scatter(
                x=duration_in_hours,
                y=sorted_data,
                name=column_name,
                mode='lines',
                hovertemplate=
                '<br>Duration: %{x} hours<br>' +
                'Value: %{y} [' + unit + ']<br>',
                hoverlabel=dict(namelength=-1)
            ), secondary_y=secondary_y)
    
    # Check if there is any data in the figure
    if len(fig.data) > 0:
        figures.append((fig, unit_list[:]))
        
    # Update the layout and axis titles
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

        # Update the x-axis range and title
        fig.update_xaxes(title_text="Duration [hours]", autorange=True)

    return [fig for fig, _ in figures]

def create_heatmap_figure(selected_data, start_date, end_date):
    """
    Creates a list of Plotly heatmap figures based on the selected data. Each data series will have its own figure.
    The x-axis represents the date, the y-axis represents the hours of the day, and the color represents the value.

    Parameters
    ----------
    selected_data : dict
        A dictionary containing the selected data.
    start_date : str or datetime object
        A string or datetime object indicating the start date.
    end_date : str or datetime object
        A string or datetime object indicating the end date.

    Returns
    -------
    list
        A list of Plotly figures.
    """

    figures = []
    
    # Iterate over each module and its data
    for module, data in selected_data.items():
        for column_name, column_data in data.items():
            unit = extract_unit(column_name)  # Extract the unit from the column name
            
            # Resample the data to hourly frequency and calculate the mean
            column_data = column_data.resample('H').mean()
            
            # Create a DataFrame to hold the heatmap data
            heatmap_data = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date, freq='H'))
            
            # Fill the DataFrame with the data from the selected series
            heatmap_data = heatmap_data.join(column_data).rename(columns={column_data.name: 'value'})
            
            # Drop the date component to keep only the time (hour) as index
            heatmap_data.index = heatmap_data.index.time
            
            # Create a pivot table for the heatmap
            heatmap_data['date'] = [d.date() for d in column_data.index]
            heatmap_data.reset_index(inplace=True)
            heatmap_data = heatmap_data.pivot(index='index', columns='date', values='value')
            
            # Create the heatmap figure
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                colorbar=dict(title=f"[{unit}]"),
            ))
            
            fig.update_layout(
                title=column_name,
                xaxis_title="Date",
                yaxis_title="Hour of Day",
            )
            
            figures.append(fig)
    
    return figures

def create_themeriver_figure(selected_data, start_date, end_date):
    """
    Creates a list of Plotly ThemeRiver figures based on the selected data.
    Each figure represents a group of data series with the same unit.
    The y-values of the series are summed up to create the 'river' shape.
    The hover mode is customized to only show the sum of the river.
    The fill between lines is also implemented to represent the stacked nature of the series.

    Parameters
    ----------
    selected_data : dict
        A dictionary containing the selected data.
    start_date : str or datetime object
        A string or datetime object indicating the start date.
    end_date : str or datetime object
        A string or datetime object indicating the end date.

    Returns
    -------
    list
        A list of Plotly figures.
    """

    figures = []
    
    # Group data by unit
    data_by_unit = defaultdict(dict)
    for module, data in selected_data.items():
        for column_name, column_data in data.items():
            unit = extract_unit(column_name)  # Extract the unit from the column name
            data_by_unit[unit][column_name] = column_data

    # Create a figure for each unit
    for unit, data in data_by_unit.items():
        fig = go.Figure()
        
        # Sort columns by their mean values (ascending), so that negative values are plotted first
        sorted_columns = sorted(data.keys(), key=lambda x: data[x].mean())
        
        # Sum up the y-values to create the 'river' shape
        y_values_sum = np.zeros(len(data[list(data.keys())[0]]))
        prev_y_values_sum = np.zeros(len(data[list(data.keys())[0]]))
        
        for column_name in sorted_columns:
            column_data = data[column_name]
            prev_y_values_sum = y_values_sum.copy()
            y_values_sum += column_data.values
            
            fill_target = 'tonexty' if column_name != sorted_columns[0] else 'tozeroy'
            
            fig.add_trace(go.Scatter(
                x=column_data.index,
                y=y_values_sum,
                fill=fill_target,
                mode='lines',
                name=column_name,
                hovertemplate=
                '<br>Date: %{x}<br>' +
                'Total Value: %{y} [' + unit + ']<br>',
                hoverlabel=dict(namelength=-1)
            ))
        
        # Update the layout and axis titles
        fig.update_layout(
            title=f"ThemeRiver [{unit}]",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        fig.update_yaxes(title_text=f"[{unit}]")
        fig.update_xaxes(title_text="Date", autorange=True)

        figures.append(fig)
    
    return figures

def initialize_session_state(start_date: dt_date, end_date: dt_date):
    """Initialize Streamlit session state variables for start and end dates.
    
    Parameters
    ----------
    start_date : datetime.date
        The earliest selectable date.
    end_date : datetime.date
        The latest selectable date.
    """
    if 'start_date' not in st.session_state:
        st.session_state.start_date = start_date
    if 'end_date' not in st.session_state:
        st.session_state.end_date = end_date

def ensure_date_order(start_date: dt_date, end_date: dt_date) -> dt_date:
    """Ensure that the end date is at least one day after the start date.
    
    Parameters
    ----------
    start_date : datetime.date
        The start date.
    end_date : datetime.date
        The end date.
        
    Returns
    -------
    datetime.date
        Adjusted end date.
    """
    if start_date == end_date:
        return start_date + timedelta(days=1)
    return end_date

def date_range_selector(start_date: dt_date, end_date: dt_date) -> tuple:
    """Display a date range selector UI using Streamlit and return the selected date range.
    
    Parameters
    ----------
    start_date : datetime.date
        The earliest selectable date.
    end_date : datetime.date
        The latest selectable date.
        
    Returns
    -------
    tuple
        A tuple containing the selected start and end dates (datetime.date, datetime.date).
    """
    initialize_session_state(start_date, end_date)
    end_date = ensure_date_order(start_date, end_date)
    
    # Create columns for layout
    cols1, cols2 = st.columns((2, 1))

    # Ensure the range of the slider never goes below the initial input range
    min_date = min(st.session_state.start_date, start_date)
    max_date = max(st.session_state.end_date, end_date)

    # Check if the time span is greater than one year
    if (max_date - min_date).days > 365:
        initial_value = (max_date - timedelta(days=365), max_date)
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

def get_timestamps(data_interface):
    """Get the first and last timestamps from the data interface.
    
    Parameters
    ----------
    data_interface : object
        The data interface object.
        
    Returns
    -------
    tuple
        A tuple containing the first and last timestamps.
    """
    try:
        return data_interface.get_first_timestamp(), data_interface.get_last_timestamp()
    except Exception as e:
        st.write(f"An error occurred: {e}")
        return None, None

def select_time_range(first_timestamp, last_timestamp):
    """Select the time range using a date range selector.
    
    Parameters
    ----------
    first_timestamp : datetime
        The first available timestamp.
    last_timestamp : datetime
        The last available timestamp.
        
    Returns
    -------
    tuple
        A tuple containing the selected start and end times.
    """
    selected_times = date_range_selector(first_timestamp.date(), last_timestamp.date())
    return selected_times[0], selected_times[1]

def select_and_process_data(data_mapping, start_time, end_time):
    """Select and process the data based on the time range and data mapping.
    
    Parameters
    ----------
    data_mapping : dict
        The mapping of available data.
    start_time : datetime
        The start time.
    end_time : datetime
        The end time.
        
    Returns
    -------
    dict
        The processed data.
    """
    selected_data = get_selected_data(data_mapping, start_time, end_time)
    return convert_processed_data(selected_data)

def display_figures(figure_type, processed_data, start_time, end_time):
    """Display the selected type of figure based on the processed data.
    
    Parameters
    ----------
    figure_type : str
        The type of figure to display.
    processed_data : dict
        The processed data.
    start_time : datetime
        The start time.
    end_time : datetime
        The end time.
    """
    figures = []
    if figure_type == 'Line Chart':
        figures = create_line_figure(processed_data, start_time, end_time)
    elif figure_type == 'Bar Chart':
        figures = create_bar_figure(processed_data, start_time, end_time)
    elif figure_type == 'Duration Curve':
        figures = create_duration_curve_figure(processed_data, start_time, end_time)
    elif figure_type == 'Heatmap':
        figures = create_heatmap_figure(processed_data, start_time, end_time)
    elif figure_type == 'ThemeRiver':
        figures = create_themeriver_figure(processed_data, start_time, end_time)
    for fig in figures:
        st.plotly_chart(fig, use_container_width=True)

def main():
    """
    Main function to run the Streamlit app for Analysis Layer.
    """
    
    # Setup
    columns = st.columns(2)
    columns[0].title(page_title)
    data_interface = st.session_state.data_interface
    st.sidebar.title("Module Data Selection")
    data_mapping = st.session_state.data_mapping
    
    # Fetch and select time range
    first_timestamp, last_timestamp = get_timestamps(data_interface)
    start_time, end_time = select_time_range(first_timestamp, last_timestamp)
    
    # Process Data
    processed_data = select_and_process_data(data_mapping, start_time, end_time)
    st.session_state.processed_data = processed_data
    
    # Display Figures
    if any(processed_data.values()):
        figure_type = st.selectbox("Choose your figure type:", options=['Line Chart', 'Bar Chart', 'Duration Curve', 'Heatmap', 'ThemeRiver'])
        display_figures(figure_type, processed_data, start_time, end_time)
        


        export_df = convert_to_dataframe(st.session_state.processed_data)

        for col in export_df.select_dtypes(include=['number']).columns:
            export_df[col] = export_df[col].astype(float)

        csv_data = export_df.to_csv(index=True, sep=';', decimal=',',)

        st.markdown("Download selected data:")

        st.download_button(
            label="CSV-Export",
            data=csv_data,
            file_name="export.csv",
            mime="text/csv",
        )

    else:
        st.write("Please select data to display.")

if __name__ == "__main__":
    page_title="Analysis Layer"
    configure_streamlit_page(page_title)
    main()

