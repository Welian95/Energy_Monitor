import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import datetime as dt
import pandas as pd
import importlib




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



def create_figure(selected_data, start_date, end_date ):
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
                figures.append(fig)
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
        figures.append(fig)

    for fig in figures:
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

    return figures




#Functions to get the range of time in given data
def get_latest_timestamp_overall(selected_data):
    """Durchsucht ein verschachteltes Dictionary und findet den neuesten Zeitstempel aller DataFrames.

    Args:
    selected_data (dict): Das übergeordnete Dictionary, das die Daten enthält.

    Returns:
    str: Der neueste Zeitstempel als String. Wenn kein DataFrame gefunden wird, wird None zurückgegeben.
    """
    latest_timestamp = None

    # Durchlaufen aller Einträge im übergeordneten Dictionary
    for key1 in selected_data:
        sub_dict = selected_data[key1]
        
        # Durchlaufen aller Einträge in jedem Unter-Dictionary
        for key2 in sub_dict:
            df = sub_dict[key2]

            # Wenn der neueste Zeitstempel dieses DataFrame später ist als der bisher neueste Zeitstempel,
            # diesen Zeitstempel als den neuesten speichern
            if latest_timestamp is None or df.index[-1] > latest_timestamp:
                latest_timestamp = df.index[-1]

    return str(latest_timestamp) if latest_timestamp is not None else None

def get_newest_timestamp_overall(selected_data):
    """Durchsucht ein verschachteltes Dictionary und findet den neuesten Zeitstempel aller DataFrames.

    Args:
    selected_data (dict): Das übergeordnete Dictionary, das die Daten enthält.

    Returns:
    str: Der neueste Zeitstempel als String. Wenn kein DataFrame gefunden wird, wird None zurückgegeben.
    """
    newest_timestamp = None

    # Durchlaufen aller Einträge im übergeordneten Dictionary
    for key1 in selected_data:
        sub_dict = selected_data[key1]
        
        # Durchlaufen aller Einträge in jedem Unter-Dictionary
        for key2 in sub_dict:
            df = sub_dict[key2]

            # Wenn der neueste Zeitstempel dieses DataFrame später ist als der bisher neueste Zeitstempel,
            # diesen Zeitstempel als den neuesten speichern
            if newest_timestamp is None or df.index[0] > newest_timestamp:
                newest_timestamp = df.index[0]

    return str(newest_timestamp) if newest_timestamp is not None else None

#Function to select timerange 
def date_range_selector(start_date: dt.date, end_date: dt.date):
    ## Range selector
    cols1, cols2 = st.columns((1, 2))  # To make it narrower
    
    format = 'YYYY-MM-DD'  # format output

    selected_start_date = start_date
    selected_end_date = end_date
    
    
    slider = st.slider('Select date', min_value=start_date, value=(selected_start_date, selected_end_date), max_value=end_date, format=format)
    
    selected_start_date = slider[0]
    selected_end_date = slider[1]
    
    date_range = cols1.date_input('Select date range', [selected_start_date, selected_end_date],start_date,end_date)

    selected_start_date = date_range[0]
    selected_end_date = date_range[1]

    ## Sanity check
    cols2.table(pd.DataFrame([[selected_start_date, selected_end_date]],
                          columns=['start',
                                   'end'],
                          index=['date']))
    
    return selected_start_date, selected_end_date



def main():
    columns = st.columns(2)
    columns[0].title(page_title)
    st.warning("Attention, currently it is only possible to display whole days, so if new data is added that does not yet represent a whole day, it cannot be displayed yet.", icon="⚠️")

    # Specify the filename or path of the file to read from the API
    filename = st.session_state.filename

    # Sidebar
    st.sidebar.title("Module Data Selection")

    data_mapping = st.session_state.data_mapping

    # Create a Counter to change the checkbox-key in every iteration
    counter = 0

    selected_data= {}
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
                module = importlib.import_module(f'pages.modules.{module_name}_module') #The module import from sub-pages must always direct to the main-script!

                # Load the data from the API

                with st.expander (f"Change time frequenz of {data_name} "):
                    freq = st.number_input("Input a frequnz in Minutes:",value =0 , help = "If value is 0 the original frequenz of the data is used", key = counter)

                    if freq <= 0:
                        freq = None
                    else:
                        freq = f'{freq}T'

                loaded_data = module.load_module_data(data_mapping, [module_name], filename, freq)

                # Store the loaded data in the selected_data_mapping
                selected_data[module_name][data_name] = loaded_data[module_name][data_name]

    st.session_state.selected_data = selected_data




    # Check if any data has been selected
    if any(selected_data.values()):


        #select time series 

        newest_time = datetime.strptime(get_newest_timestamp_overall(st.session_state.selected_data), "%Y-%m-%d %H:%M:%S")
        latest_time = datetime.strptime(get_latest_timestamp_overall(st.session_state.selected_data), "%Y-%m-%d %H:%M:%S")

        selected_times = date_range_selector(newest_time.date(), latest_time.date())
        start_time = selected_times[0]
        end_time =  selected_times[1]

        # Create and display the combined chart
        figures = create_figure(st.session_state.selected_data,start_time, end_time)
        for fig in figures:
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("Please select data to display.")

    

if __name__ == "__main__":
    main()

