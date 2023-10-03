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


measuring_list = ['Server_OUT','e_mobility_OUT',  ]

measuring_list_sankey =['Server_OUT','e_mobility_OUT', "Rest_[W]"]

Label = ['server','e_mobility', "rest"]
Consumption = [None, None,  "e_consumers_IN - Server_OUT - e_mobility_OUT" ]
Type =  ['Sink','Sink', 'Sink']
EnergyTypeInput = ['electricity','electricity','electricity',]
EnergyTypeOutput = ['-','-','-',]



if __name__ != "__main__":
    from pages.modules._module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data, get_module_figs

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

    from _module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data, get_module_figs

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


   

        
        


