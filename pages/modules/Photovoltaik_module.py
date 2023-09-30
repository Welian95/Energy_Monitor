
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


units = ["W", "kW", "Wh", "kWh", "J", "°C", "K", ] #Units List (has to be pint Units)


measuring_list = ['PV_yield_IN','PV_supply_OUT','grid_supply_IN']



Label = ['PV_yield_IN','PV_supply_OUT','grid_supply_IN']
Consumption = None
Type =  ['Source','Sink','Source']
EnergyTypeInput = ['-','electricity','-']
EnergyTypeOutput = ['electricity','-','electricity']


if __name__ != "__main__":
    from pages.modules._module_functions import initialize_data_interface, get_required_data_S, get_sankey_mapping_S, load_module_data, get_module_figs

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


   

        
        


