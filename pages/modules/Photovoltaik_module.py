'''
Parameters:

- units:    
    A list of strings that should correspond to units supported by the pint module (https://pint.readthedocs.io/en/stable/).
    These units are presented to the user for selection, facilitating the representation of measurement series 
    in the unit of their choice. The specified units must be compatible with the measured values within the module.

    Example:
    units = ["W", "kW", "Wh", "kWh", "J", "°C", "K"]

- measuring_list:
    This list contains the names of the measured values to be used in this system module. 
    These measured values will be the basis for the data flows in the Sankey diagram.

    Example:
    measuring_list = ['transported_energy_IN', 'room_OUT_2']

- measuring_list_sankey:
    A list that includes both the measured and calculated values to be used in the Sankey diagram. 
    It's crucial to append units to calculated values!

    Example:
    measuring_list_sankey = ['transported_energy_IN', 'room_OUT_2', "MATHTEST_[W]"]

- Label:
    A list of labels used to describe the measured or calculated values in the Sankey diagram. 
    If the length of the Label list is shorter than that of measuring_list, 
    those missing labels will not be displayed in the Sankey diagram.

    Example:
    Label = ['transported_energy_IN', 'room_OUT_2', "MATHTEST"]

- Consumption:    
    Initially set to None for all entries. It gets updated during the processing in the Main.py script. 
    This field can contain simple keys that map to data_mapping, numerical values, or complex mathematical expressions. 
    Mathematical expressions can include column names, numerical values, operators, and conditional statements (IF-ELSE).

    Example:
    - Consumption = [None, None, "Compressor_Power + ambient_heat_IN"]
    - Consumption = [None, None, "IF( battery >= 0, battery, 0 )" ,"IF( battery <= 0, battery * - 1  , 0 )" ]

- Type:    
    Each label must have an associated Type. There are three types: Source, Transformer, and Sink. 
    Sources appear on the left and serve as inputs; Transformers connect one form of energy to another; 
    Sinks appear on the right and serve as outputs.

    Example:
    Type = ['Transformer', 'Sink', 'Sink']

- EnergyTypeInput:    
    Specifies what form of energy is going into a particular Sankey flow. 
    A hyphen (-) is used if the flow is not represented in the system. 
    For example, a 'Source' will always have EnergyTypeInput set to -.

    Example:
    EnergyTypeInput = ['electricity', 'heat', 'heat']

- EnergyTypeOutput:    
    Specifies what form of energy is coming out of a particular Sankey flow. 
    A hyphen (-) is used if the flow is not represented in the system. 
    For example, a 'Sink' will always have EnergyTypeOutput set to -.

    Example:
    EnergyTypeOutput = ['heat', '-', '-']

Special Handling of Consumption:

1. Conditional Statements:    
    If the Consumption field contains an IF-THEN-ELSE statement in the form IF(condition, true_value, false_value), 
    it's converted into Python's ternary operator: true_value if condition else false_value.

2. Tokenization:    
    The expression in Consumption is broken down into individual tokens separated by spaces. 
    A token can be a column name, a numerical value, or an operator.

3. Data Retrieval and Caching:    
    For each token that is neither a mathematical operator nor a numerical value, data is fetched from the DataFrame 
    and stored in a cache.

4. Token Replacement:    
    Tokens in the Consumption expression are replaced by their actual values from the cache.

5. Expression Evaluation:    
    The updated expression is then evaluated using Python's eval function.

6. Unit Conversion and Sankey Diagram Update:    
    The result is converted into the desired unit and updated in the Sankey diagram.

By following these steps, the Sankey diagram can represent both simple and complex energy flows, 
providing a comprehensive view of the energy system.
'''


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

def create_gauge_chart(value: float, title : str= None , reference_value: float = None) -> go.Figure:
    """
    Creates a customized Plotly Gauge Chart based on the given value and reference value.
    
    Parameters:
    - value (float): The current value to be displayed on the gauge.
    - title (str): The title of the gauge chart.
    - reference_value (float): The reference value for calculating the delta. Optional.
    
    Returns:
    - go.Figure: A Plotly Figure object representing the gauge chart.
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
    This is a function to create plant module specific images. This function must be created specifically for each plant module. 

    Parameters:
    -None

    Returns:
    - A list of charts which can be called with "st.plotly_chart()".
    
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
        Calls get_required_data_S and returns its output.
        """
        return get_required_data_S(measuring_list, units)


    def get_sankey_mapping(measuring_list=measuring_list_sankey, Consumption=Consumption, Label=Label, Type=Type, EnergyTypeInput=EnergyTypeInput, EnergyTypeOutput=EnergyTypeOutput):
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

    #Here you can test the module as a stand-alone script

    st.title("Test module:")


   

        
        


