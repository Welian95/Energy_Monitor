


import streamlit as st
import os

#spezieal:
import plotly.graph_objects as go
    



units = ["W", "kW", "Wh", "kWh", "J", "°C", "K", ] #Units List (has to be pint Units)



measuring_list = ["Compressor_Power", "ambient_heat_IN","room_heating_OUT", "thermal_hp_OUT"]

measuring_list_sankey = ["Compressor_Power", "ambient_heat_IN","room_heating_OUT"]

Label = ["Compressor_Power" , "ambient_heat", "room_heating"]
Consumption = [None, None, None ]
Type =  ['Transformer','Source', 'Sink']
EnergyTypeInput = ['electricity','-','heat']
EnergyTypeOutput = ['heat','heat','-']



#Spezial for heat_pump_module

def create_gauge_chart(value: float, title: str = None, reference_value: float = None) -> go.Figure:
    """
    Create a Plotly Gauge Chart based on provided values.
    
    Parameters
    ----------
    value : float
        The current value to be displayed on the gauge.
    title : str, optional
        The title for the gauge chart.
    reference_value : float, optional
        The reference value for calculating the delta.
        
    Returns
    -------
    go.Figure
        A Plotly Figure object representing the gauge chart.

    Notes
    -----
    The function supports optional delta and threshold settings based on the reference value.
    """
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta" if reference_value is not None else "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 14}},
        delta = {'reference': reference_value, 'increasing': {'color': "RebeccaPurple"}} if reference_value is not None else None,
        
        # Gauge settings
        gauge = {
            'axis': {'range': [1, 5], 'tickwidth': 1, 'tickcolor': "lightblue"},
            'bar': {'color': "lightgoldenrodyellow"},
            'bgcolor': "white",  # Set to white as transparent is not directly supported
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [1, 2], 'color': '#666666'},  # Dark Gray for 'Bad'
                {'range': [2, 4], 'color': '#999999'},  # Gray for 'Average'
                {'range': [4, 5], 'color': '#CCCCCC'}], # Light Gray for 'Good'
                
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': value}
            }))
    
    # Update chart layout for a transparent background
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", 
                  plot_bgcolor = 'rgba(0,0,0,0)', 
                  font = {'color': "gray", 'family': "Arial"})
    
    return fig



def get_module_figs():
    """
    Create plant module-specific figures.

    This function must be customized for each plant module and retrieves data from an external API.

    Returns
    -------
    list
        A list of Plotly figures which can be displayed using `st.plotly_chart()`.

    Notes
    -----
    This function specifically handles HP-specific power rating calculations.
    It uses the `data_interface` for data retrieval.
    """

    #HP_spezific
    last_row_from_api = data_interface.get_data(["heat_pump_power_IN_[W]","thermal_hp_OUT_[W]"] ,num_rows=1, ascending=False)

    thermal_hp_OUT = last_row_from_api["thermal_hp_OUT_[W]"]
    heat_pump_power = last_row_from_api["heat_pump_power_IN_[W]"]

    HP_power_rating = abs(thermal_hp_OUT) /heat_pump_power

    title = "Heat pump power rating"

    fig = create_gauge_chart(float(HP_power_rating),title, reference_value=None)


    figures = [fig]

    return figures




if __name__ != "__main__":
    from pages.modules._module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data

    def get_required_data(measuring_list=measuring_list, units= units):
        """
        Wrapper function for get_required_data_S.
        
        Parameters
        ----------
        measuring_list : list
            List of names for the data variables relevant for this system component.
        units : list
            List of possible units for the data variables.
        
        Returns
        -------
        dict
            A dictionary where keys are the names of data variables and values are lists of possible units.
        """
        return get_required_data_S(measuring_list, units)


    def get_sankey_mapping(measuring_list=measuring_list_sankey, Consumption=Consumption, Label=Label, Type=Type, EnergyTypeInput=EnergyTypeInput, EnergyTypeOutput=EnergyTypeOutput):
        """
        Wrapper function for get_sankey_mapping_S.
        
        Parameters
        ----------
        measuring_list : list
            List of data series in the DataFrame.
        Consumption : list
            List of consumption values corresponding to each data series in the DataFrame.
        labels : list
            List of labels corresponding to each data series in the DataFrame.
        types : list
            List of types corresponding to each data series in the DataFrame.
        energy_type_inputs : list
            List of energy type inputs corresponding to each data series in the DataFrame.
        energy_type_outputs : list
            List of energy type outputs corresponding to each data series in the DataFrame.
        
        Returns
        -------
        dict
            The data mapping dictionary.
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
        last_row_from_api = data_interface.get_data(["heat_pump_power_IN_[W]","thermal_hp_OUT_[W]"] ,num_rows=1, ascending=False)
        last_row_from_api


        "thermal_hp_OUT"
        thermal_hp_OUT = last_row_from_api["thermal_hp_OUT_[W]"]
        thermal_hp_OUT

        "heat_pump_power"
        heat_pump_power = last_row_from_api["heat_pump_power_IN_[W]"]
        heat_pump_power


        
        "HP_power_rating"
        HP_power_rating = thermal_hp_OUT/heat_pump_power
        HP_power_rating


        
        
        fig = create_gauge_chart(float(HP_power_rating), reference_value=None)

        st.plotly_chart(fig)

