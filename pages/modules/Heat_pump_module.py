'''
This is a system module script. 
This is used to select the required parameters to display parts of the entire system. 

Params:
- units:    
            A list of strings that must be included in the pint module (https://pint.readthedocs.io/en/stable/). 
            These units are presented to the user in a selection to choose the unit of the measurement series. 
            The units must match the requested measurement values for the module. 

- measuring_list:
            A list of the measured values to be used in this system module.

- Label:
            a list of labels which is used to describe the measured values in the Saney diagram. 
            If the "label" list is shorter than the "measuring_list", 
            the measurement series without labels are not displayed in the Sankey.
- Consumption:
            This value is always set to "None" and is only added after mapping in the "Main.py" script. 

- Type: 
            A "Type" must be defined for each label. There are three types: 'Source', 'Transformer','Sink' . 
            Sources are placed on the left of the sankey and are inputs, 
            transformers are connectors that convert one form of energy into another and 
            sinks are placed on the right of the sankey and are outputs.

- EnergyTypeInput:
            These are indications wich form of energy goes into the considered Sankey flow. 
            A "-" is selected if the flow is not represented in the system.  
            For example: A "source" never has an EnergyTypeInput and is always set to "-".

- EnergyTypeOutput:
            These are indications wich form of energy goes out of the considered Sankey flow. 
            A "-" is selected if the flow is not represented in the system.  
            For example: A "sink" never has an EnergyTypeOutput and is always set to "-".

'''


import streamlit as st
import os


#spezieal:
import plotly.graph_objects as go
    



units = ["W", "kW", "Wh", "kWh", "J", "°C", "K", ] #Units List (has to be pint Units)



measuring_list = ["Compressor_Power", "ambient_heat_IN", "Heat_OUT","thermal_hp_OUT"]

Label = ["Wärmepumpenantrieb" , "Umgebungswärme", "Wärmeabgabe"]
Consumption = None
Type =  ['Transformer','Source','Sink']
EnergyTypeInput = ['electricity','-','heat']
EnergyTypeOutput = ['heat','heat','-']



#Spezial for heat_pump_module

def create_gauge_chart(value: float, reference_value: float = None) -> go.Figure:
    """
    Creates a customized Plotly Gauge Chart based on the given value and reference value.
    
    Parameters:
    - value (float): The current value to be displayed on the gauge.
    - reference_value (float): The reference value for calculating the delta. Optional.
    
    Returns:
    - go.Figure: A Plotly Figure object representing the gauge chart.
    """
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta" if reference_value is not None else "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Heat pump power rating", 'font': {'size': None}},
        delta = {'reference': reference_value, 'increasing': {'color': "RebeccaPurple"}} if reference_value is not None else None,
        
        # Gauge settings
        gauge = {
            'axis': {'range': [1, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",  # Set to white as transparent is not directly supported
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [1, 2], 'color': '#666666'},  # Dark Gray for 'Bad'
                {'range': [2, 4], 'color': '#999999'},  # Gray for 'Average'
                {'range': [4, 5], 'color': '#CCCCCC'}], # Light Gray for 'Good'
            }))
    
    # Update chart layout for a transparent background
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", 
                  plot_bgcolor = 'rgba(0,0,0,0)', 
                  font = {'color': "white", 'family': "Arial"})
    
    return fig



def get_module_figs():
    """
    This is a function to create plant module specific images. This function must be created specifically for each plant module. 

    Parameters:
    -None

    Returns:
    - A list of charts which can be called with "st.plotly_chart()".
    
    """

    #HP_spezific
    last_row_from_api = data_interface.get_data(["heat_pump_power_IN_[W]","thermal_hp_OUT"] ,num_rows=1, ascending=False)

    thermal_hp_OUT = last_row_from_api["thermal_hp_OUT"]
    heat_pump_power = last_row_from_api["heat_pump_power_IN_[W]"]
    HP_power_rating = thermal_hp_OUT/heat_pump_power
    fig = create_gauge_chart(float(HP_power_rating), reference_value=None)


    figures = [fig]

    return figures




if __name__ != "__main__":
    from pages.modules._module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data

    def get_required_data(measuring_list=measuring_list, units= units):
        """
        Wrapper function for get_required_data_S.
        Calls get_required_data_S and returns its output.
        """
        return get_required_data_S(measuring_list, units)


    def get_sankey_mapping(measuring_list=measuring_list, Consumption=Consumption, Label=Label, Type=Type, EnergyTypeInput=EnergyTypeInput, EnergyTypeOutput=EnergyTypeOutput):
        """
        Wrapper function for get_sankey_mapping_S.
        Calls get_sankey_mapping_S and returns its output.
        """
        return get_sankey_mapping_S(measuring_list, Consumption, Label, Type, EnergyTypeInput, EnergyTypeOutput)
    
    #Intilazie interface:
    data_interface = initialize_data_interface()
    


if __name__ == "__main__":
    import streamlit as st

    from _module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data

    def get_required_data(measuring_list=measuring_list, units= units):
        """
        Wrapper function for get_required_data_S.
        Calls get_required_data_S and returns its output.
        """
        return get_required_data_S(measuring_list, units)


    def get_sankey_mapping(measuring_list=measuring_list, Consumption=Consumption, Label=Label, Type=Type, EnergyTypeInput=EnergyTypeInput, EnergyTypeOutput=EnergyTypeOutput):
        """
        Wrapper function for get_sankey_mapping_S.
        Calls get_sankey_mapping_S and returns its output.
        """
        return get_sankey_mapping_S(measuring_list, Consumption, Label, Type, EnergyTypeInput, EnergyTypeOutput)


    #Intilazie interface:
    data_interface = initialize_data_interface()

    st.title("Test functions:")

    # Change the working directory
    current_file_directory = os.path.dirname(__file__)
    os.chdir(os.path.join(current_file_directory, '../../'))

    #Intilazie interface:
    "initialize_data_interface()"
    data_interface = initialize_data_interface()
    data_interface
    
    

    "data_interface.get_column_names()"
    column_names = data_interface.get_column_names()
    column_names

    "get_required_data()"
    required_data =get_required_data()
    required_data

    "get_sankey_mapping(measuring_list, Consumption, Label, Type, EnergyTypeInput, EnergyTypeOutput)"
    sankey_mapping = get_sankey_mapping()
    sankey_mapping




    #Test the load_data function:
    if st.toggle("api test", help="Only used if example_data is connected"):
        data_mapping = {
            'Heat_pump': 
                        {'Compressor_Power_[W]': 'heat_pump_power_IN_[W]', 'ambient_heat_IN_[W]': 'ambient_heat_IN_[W]', 'Heat_OUT_[W]': 'room_heating_IN_[W]'}, 
            'Photovoltaik': 
                        {'P_yield_[W]': 'PV_yield_IN_[W]', 'Battery_charge_[Wh]': 'battery_[W]'}
                        }
        
        module_names = ['Heat_pump']

        
        "load_module_data(data_mapping, module_names, start_time=None, end_time=None,)"
        module_data = load_module_data(data_mapping, module_names, start_time=None, end_time=None,)
        module_data

        first_columns = list(list(data_mapping.values())[0].values())

        #test_columns = ['heat_pump_power_IN_[W]',  'ambient_heat_IN_[W]', 'room_heating_IN_[W]']
        "last_row_from_api"
        last_row_from_api = data_interface.get_data(["heat_pump_power_IN_[W]","thermal_hp_OUT"] ,num_rows=1, ascending=False)
        last_row_from_api


        "thermal_hp_OUT"
        thermal_hp_OUT = last_row_from_api["thermal_hp_OUT"]
        thermal_hp_OUT

        "heat_pump_power"
        heat_pump_power = last_row_from_api["heat_pump_power_IN_[W]"]
        heat_pump_power


        
        "HP_power_rating"
        HP_power_rating = thermal_hp_OUT/heat_pump_power
        HP_power_rating


        
        
        fig = create_gauge_chart(float(HP_power_rating), reference_value=None)

        st.plotly_chart(fig)

