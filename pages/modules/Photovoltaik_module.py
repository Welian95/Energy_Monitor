


units = ["W", "kW", "Wh", "kWh", "J", "°C", "K", ] #Units List (has to be pint Units)

measuring_list = ['PV_yield_IN','PV_supply_OUT','grid_supply_IN']

measuring_list_sankey = ['PV_yield_IN','PV_supply_OUT','grid_supply_IN']

Label = ['PV_yield','PV_feed-in','grid_supply']
Consumption = [None, None, None]
Type =  ['Source','Sink','Source']
EnergyTypeInput = ['-','electricity','-']
EnergyTypeOutput = ['electricity','-','electricity']



#Spezial for Photovoltaik_module
#Spezial:
import plotly.graph_objects as go

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
            'axis': {'range': [0, 100], 
                     'tickwidth': 1, 
                     'tickcolor': "lightblue",
                     'tickvals': [0, 100/3, 100/3*2, 100],  # Set tick positions at 0, 1/3, 2/3 and 100
                     'ticktext': ['0', '1/3', '2/3', '100']},  # Set tick texts
            'bar': {'color': "lightblue"},
            'bgcolor': "white",  # Set to white as transparent is not directly supported
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 100/3], 'color': '#666666'},  # Dark Gray for 'Bad'
                {'range': [100/3, 100/3*2], 'color': '#999999'},  # Gray for 'Average'
                {'range': [100/3*2, 100], 'color': '#CCCCCC'}],  # Light Gray for 'Good'
                
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': value}
        }))
    
    # Update chart layout for a transparent background
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", 
                      plot_bgcolor='rgba(0,0,0,0)', 
                      font={'color': "gray", 'family': "Arial"})
    
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
    This function specifically handles HP-specific consumption and degree of autarky calculations.
    It uses the `data_interface` for data retrieval.
    """

    #HP_spezific
    last_row_from_api = data_interface.get_data(["grid_supply_IN_[W]","room_heating_OUT_[W]", "e_consumers_IN_[W]", "transported_energy_OUT_[W]", "room_conditioning_OUT_[W]" ] ,num_rows=1, ascending=False)

    grid_supply = last_row_from_api["grid_supply_IN_[W]"]

    room_heating = last_row_from_api ["room_heating_OUT_[W]"]
    e_consumer = last_row_from_api ["e_consumers_IN_[W]"]
    transported_energy = last_row_from_api ["transported_energy_OUT_[W]"]
    room_conditioning = last_row_from_api ["room_conditioning_OUT_[W]"]

    
    Consumption = abs(room_heating) + e_consumer + abs(transported_energy) + abs(room_conditioning)


    if Consumption[0] == 0:
        degree_of_autarky = 100 
    else:
        degree_of_autarky = 100 - grid_supply/Consumption * 100

 

    title = "Degree of autarky [%]"


   
    fig = create_gauge_chart(int(degree_of_autarky), title, reference_value=None)
 


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

    #Here you can test the module as a stand-alone script

    st.title("Test module:")


   

        
        


