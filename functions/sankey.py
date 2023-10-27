import streamlit as st
from matplotlib.patheffects import withStroke
import pandas as pd
import plotly.graph_objects as go



def extract_rgba_components(color):
    """
    Extract RGBA components from a given color string.

    Parameters:
    ----------
    color : str
        The color string in the format 'rgba(r, g, b, a)'.

    Returns:
    -------
    tuple
        A tuple containing the RGBA components as integers and float.
    """
    r, g, b, a = map(float, color[5:-1].split(", "))
    return r, g, b, a

def mix_colors(color1, color2):
    """
    Mix two RGBA colors.

    Parameters:
    ----------
    color1 : str
        The first input color in the format 'rgba(r, g, b, a)'.
    color2 : str
        The second input color in the format 'rgba(r, g, b, a)'.

    Returns:
    -------
    str
        The mixed color in the same format.
    """
    r1, g1, b1, a1 = extract_rgba_components(color1)
    r2, g2, b2, a2 = extract_rgba_components(color2)
    
    r = int((r1 + r2) // 2)
    g = int((g1 + g2) // 2)
    b = int((b1 + b2) // 2)
    a = (a1 + a2) / 2.0  # Use float for the alpha component
    
    return f"rgba({r}, {g}, {b}, {a})"

def initialize_label_dicts(table):
    """
    Initialize dictionaries for label indices and energy type colors.

    Parameters:
    ----------
    table : pd.DataFrame
        The input table containing relevant columns for 'Label', 'Type', 'EnergyTypeInput', 
        and 'EnergyTypeOutput'.

    Returns:
    -------
    tuple
        Two dictionaries - one for label indices and another for energy type colors.
    """
    label_index_dict = {}
    # Initialize the index dictionary for each unique label and energy type
    for index, row in table.iterrows():
        for col in ['Label', 'EnergyTypeInput', 'EnergyTypeOutput']:
            label = row[col].strip()
            if label and label != '-' and label not in label_index_dict:
                label_index_dict[label] = len(label_index_dict)
    
    return label_index_dict

def generate_sankey_data_from_table(table): 
    """
    Generate data required to plot a Sankey diagram from a given Pandas DataFrame table.

    The table is expected to have the following columns:
    - 'Label': Identifier for the node (e.g., "Plant A")
    - 'Type': Type of the node ("Source", "Transformer", "Sink")
    - 'EnergyTypeInput': Type of input energy (e.g., "electricity")
    - 'EnergyTypeOutput': Type of output energy (e.g., "heat")
    - 'Consumption': Energy consumption or transformation value
    
    The function generates five lists:
    - labels_with_values: A list of node labels appended with their total energy value.
    - source: A list of source node indices corresponding to 'labels_with_values'.
    - target: A list of target node indices corresponding to 'labels_with_values'.
    - value: A list of energy values (consumption or transformation) for each source-target pair.
    - color: A list of colors for each flow link between source and target nodes.

    Parameters:
    ----------
    table : pd.DataFrame
        The input table containing columns for 'Label', 'Type', 'EnergyTypeInput', 
        'EnergyTypeOutput', and 'Consumption'.

    Returns:
    -------
    tuple
        A tuple containing five lists - (labels_with_values, source, target, value, color).
    """
    
    labels = []
    source = []
    target = []
    value = []
    color = []
    
    # New list to keep track of the values of nodes
    node_values = []
    
    label_index_dict = initialize_label_dicts(table)

    # Predefined colors for certain types of energy
    predefined_colors = {
        "electricity": "rgba(173, 216, 230, 0.8)",
        "heat": "rgba(255, 213, 128, 0.8)"
    }
    
    for index, row in table.iterrows():
        for col in ['Label', 'EnergyTypeInput', 'EnergyTypeOutput']:
            label = row[col].strip()
            if label and label != '-' and label not in labels:
                labels.append(label)
                node_values.append(0)  # Initialize with zero

    # Populate source, target, value, and color lists based on the table rows
    for index, row in table.iterrows():
        label = row['Label'].strip()
        src = label_index_dict.get(label, None)
        tgt = None
        
        # Update node_values based on the Consumption
        if src is not None:
            node_values[src] += row['Consumption']
        
        if row['Consumption'] == 0:  # Skip rows with zero consumption
            continue
        
        if row['Type'] == 'Source':
            tgt = label_index_dict.get(row['EnergyTypeOutput'].strip(), None)
            color.append(predefined_colors.get(row['EnergyTypeOutput'].strip(), "rgba(128, 128, 128, 0.8)"))
        elif row['Type'] == 'Transformer':
            src = label_index_dict.get(row['EnergyTypeInput'].strip(), None)
            tgt = label_index_dict.get(row['EnergyTypeOutput'].strip(), None)
            color.append(mix_colors(predefined_colors.get(row['EnergyTypeInput'].strip(), "rgba(128, 128, 128, 0.8)"),
                                    predefined_colors.get(row['EnergyTypeOutput'].strip(), "rgba(128, 128, 128, 0.8)")))
        elif row['Type'] == 'Sink':
            src = label_index_dict.get(row['EnergyTypeInput'].strip(), None)
            tgt = label_index_dict.get(label, None)
            color.append(predefined_colors.get(row['EnergyTypeInput'].strip(), "rgba(128, 128, 128, 0.8)"))
        
        if src is not None and tgt is not None:
            source.append(src)
            target.append(tgt)
            value.append(row['Consumption'])

    # Combine labels and node_values to display next to nodes
    labels_with_values = [f"{label} ({value:.2f})" for label, value in zip(labels, node_values)]

    return labels_with_values, source, target, value, color


def create_dynamic_plotly_sankey(table):
    """
    Create a dynamic Plotly Sankey diagram based on the given table.

    Parameters
    ----------
    table : pd.DataFrame
        The DataFrame containing input data for the Sankey diagram. It should have a 'Consumption' column
        and other columns that `generate_sankey_data_from_table` expects.

    Returns
    -------
    fig : plotly.graph_objects.Figure
        Plotly figure object containing the Sankey diagram.

    Notes
    -----
    The function modifies the 'Consumption' column in the input DataFrame to its absolute value.
    """

    table['Consumption'] = abs(table['Consumption'])

    labels, source, target, value, color = generate_sankey_data_from_table(table)


    
    node_color = ["rgba(128, 128, 128, 0.8)" for _ in labels]  # Gray color for all nodes
    
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_color  # Set color for nodes here
        ),
        link=dict(
            arrowlen=15,
            source=source,
            target=target,
            value=value,
            #label=labels,
            #label=["Link 1", "Link 2", "Link 3"],  # Label the links
            color=color  # Add color parameter here
        )
    ))
    
    return fig



if __name__ == "__main__":
    '''
    Streamlit UI to test the function in development
    '''

   


    sample_data1 = {
        'Label': ['Wärmepumpenantrieb', 'Umgebungswärme', 'Wärmeabgabe'], 
        'Consumption': [0.6998817114217672, 1.7497042785544181, 1.3997634228435345], 
        'Type': ['Transformer', 'Source', 'Sink'], 
        'EnergyTypeInput': ['electricity', '-', 'heat'], 
        'EnergyTypeOutput': ['heat', 'heat', '-']}
    
    sample_data2 = {
        'Label': ['PV_yield_IN', 'PV_supply_OUT', 'grid_supply_IN', 'battery_charge_OUT', 'battery_discharge_IN', 'heat_pump_power_OUT', 'ambient_heat_IN', 'room_OUT_1', 'Server_OUT', 'e_mobility_OUT', 'rest_OUT', 'transported_energy_IN', 'room_OUT_2'], 
        'Consumption': [3000.0, 0.0, 0.0, 0, 7078.296644473448, 4199.2902685306035, 10498.225671326509, 8398.580537061207, 419.92902685306035, 2519.574161118362, 1259.787080559181, 1679.7161074122414, 7978.651510208147], 
        'Type': ['Source', 'Sink', 'Source', 'Sink', 'Source', 'Transformer', 'Source', 'Sink', 'Sink', 'Sink', 'Sink', 'Transformer', 'Sink'], 
        'EnergyTypeInput': ['-', 'electricity', '-', 'electricity', '-', 'electricity', '-', 'heat', 'electricity', 'electricity', 'electricity', 'electricity', 'heat'], 
        'EnergyTypeOutput': ['electricity', '-', 'electricity', '-', 'electricity', 'heat', 'heat', '-', '-', '-', '-', 'heat', '-']}




    st.title("Sankey-Test")



    toggle1 , toggle2 = st.columns(2)
    test = toggle1.toggle("Create Sankey", value=False,)
    choose_data = toggle2.toggle("Sankey2", value=False,)

    if choose_data == True:
        sample_data = sample_data2

    else:
        sample_data = sample_data1
    

    
    if test == True:

        with st.expander("Show data"):


            
            st.write(pd.DataFrame(sample_data))
            


        st.subheader("Plotly - Sankey")

        sample_table = pd.DataFrame(sample_data)

        # Create and show the Sankey diagram
        sample_sankey_fig = create_dynamic_plotly_sankey(sample_table)

        st.plotly_chart(sample_sankey_fig,use_container_width=True)





