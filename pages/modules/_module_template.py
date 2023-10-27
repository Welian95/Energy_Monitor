"""
Template for Module for Handling Energy System Parameters
----------------------------------------------------------

This module-template outlines various parameters and options for the energy system model.

Parameters
~~~~~~~~~~

- **units**:
    A list of strings corresponding to units supported by the pint module (`Pint Documentation <https://pint.readthedocs.io/en/stable/>`_).
    These units are used for presenting options to the user and must be compatible with the measures in the module.

    - Example: ``units = ["W", "kW", "Wh", "kWh", "J", "°C", "K"]``

- **measuring_list**:
    Contains the names of the measures used in this system module, forming the basis for the Sankey diagram.

    - Example: ``measuring_list = ['transported_energy_IN', 'room_OUT_2']``

- **measuring_list_sankey**:
    A list that includes both measured and calculated values for the Sankey diagram. Units must be appended to calculated values.

    - Example: ``measuring_list_sankey = ['transported_energy_IN', 'room_OUT_2', "MATHTEST_[W]"]``

- **Label**:
    Describes the measured or calculated values in the Sankey diagram. If shorter than ``measuring_list``, missing labels won't be displayed.

    - Example: ``Label = ['transported_energy_IN', 'room_OUT_2', "MATHTEST"]``

- **Consumption**:
    Initially set to ``None``. Updated during processing to contain keys, numerical values, or complex expressions.

    - Example:
        - ``Consumption = [None, None, "Compressor_Power + ambient_heat_IN"]``
        - ``Consumption = [None, None, "IF( battery >= 0, battery, 0 )", "IF( battery <= 0, battery * -1, 0 )"]``

- **Type**:
    Each label must have a corresponding type: Source, Transformer, or Sink.

    - Example: ``Type = ['Transformer', 'Sink', 'Sink']``

- **EnergyTypeInput**:
    Indicates the form of incoming energy. '-' is used for flows not represented.

    - Example: ``EnergyTypeInput = ['electricity', 'heat', 'heat']``

- **EnergyTypeOutput**:
    Indicates the form of outgoing energy. '-' is used for flows not represented.

    - Example: ``EnergyTypeOutput = ['heat', '-', '-']``

Special Handling of Consumption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Conditional Statements**:  
    Converts IF-THEN-ELSE to Python's ternary operator.

2. **Tokenization**:  
    Breaks down expressions into tokens.

3. **Data Retrieval and Caching**:  
    Fetches and caches data for non-operator, non-numeric tokens.

4. **Token Replacement**:  
    Replaces tokens with cached values.

5. **Expression Evaluation**:  
    Evaluates updated expressions.

6. **Unit Conversion and Update**:  
    Converts results to desired units and updates the Sankey diagram.

.. note:: 
    Following these steps enables the Sankey diagram to represent both simple and complex energy flows comprehensively.
"""


units = ["W", "kW", "Wh", "kWh", "J", "°C", "K", ] #Units List (has to be pint Units)

measuring_list = []

measuring_list_sankey =[]

Label = []
Consumption = [None]
Type =  []
EnergyTypeInput = []
EnergyTypeOutput = []





if __name__ != "__main__":
    from pages.modules._module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data, get_module_figs

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

    from _module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data, get_module_figs

    def get_required_data(measuring_list=measuring_list, units= units):
        """
        Wrapper function for get_required_data_S.
        Calls get_required_data_S and returns its output.
        """
        return get_required_data_S(measuring_list, units)
    
    #Intilazie interface:
    data_interface = initialize_data_interface()


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


   

        
        


