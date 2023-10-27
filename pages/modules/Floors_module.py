

units = ["W", "kW", "Wh", "kWh", "J", "°C", "K", ] #Units List (has to be pint Units)

measuring_list = ["e_consumers_IN" ,"electricity_UG",	"electricity_EG",	"electricity_1OG",	"electricity_2OG",	"electricity_3OG" ]


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


   

        
        


