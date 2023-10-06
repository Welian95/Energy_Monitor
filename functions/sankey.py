import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
# Importieren des statistics Moduls
from statistics import mean
from io import BytesIO
import base64
from matplotlib.patheffects import withStroke
import csv
import time
import pandas as pd
import plotly.graph_objects as go

def custom_style_text(text, fontsize=6):
    """
    Customizes the style of a Matplotlib text element, including font size.

    Parameters:
        text (matplotlib.text.Text): The text element to be styled.
        fontsize (int, optional): The size of the font. Default is 12.

    Returns:
        None
    """
    text.set_color('white')
    text.set_path_effects([
        withStroke(linewidth=3, foreground='black')
    ])
    text.set_weight('bold')
    text.set_fontsize(fontsize)



# Funktion zum Konvertieren einer Matplotlib-Figur in ein Byte-Array
def fig_to_image(fig):
    """
    Converts a Matplotlib figure to a byte array that can be displayed as an image in Streamlit.

    Parameters:
        fig (matplotlib.figure.Figure): The Matplotlib figure to convert.

    Returns:
        BytesIO: A byte array representation of the image.
    """
    img_stream = BytesIO()
    fig.savefig(img_stream, format='png', transparent=True) # Set transparent=True to make the background transparent
    img_stream.seek(0)
    return img_stream




def mix_colors(color1, color2):
    """
    Mix two RGBA colors.
    
    Parameters:
        color1, color2 (str): The input colors in the format 'rgba(r, g, b, a)'.
        
    Returns:
        str: The mixed color in the same format.
    """
    r1, g1, b1, a1 = color1[5:-1].split(", ")
    r2, g2, b2, a2 = color2[5:-1].split(", ")
    
    r = (int(r1) + int(r2)) // 2
    g = (int(g1) + int(g2)) // 2
    b = (int(b1) + int(b2)) // 2
    a = (float(a1) + float(a2)) / 2.0  # Use float for the alpha component
    
    return f"rgba({r}, {g}, {b}, {a})"



def generate_sankey_data_from_table(table): 
    """
    Generate Sankey diagram data (labels, source, target, value, color) from a given table.
    """
    labels = []
    source = []
    target = []
    value = []
    color = []
    
    # New list to keep track of the values of nodes
    node_values = []
    
    label_index_dict = {}
    energy_type_color_dict = {}
    
    # Predefined colors for certain types of energy
    predefined_colors = {
        "electricity": "rgba(173, 216, 230, 0.8)",
        "heat": "rgba(255, 213, 128, 0.8)"
    }

    # Initialize node_values with zeros for each label and EnergyTypeInput/Output
    for index, row in table.iterrows():
        for col in ['Label', 'EnergyTypeInput', 'EnergyTypeOutput']:
            label = row[col].strip()
            if label and label != '-' and label not in label_index_dict:
                label_index_dict[label] = len(labels)
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

    # Alternitive: Combine labels and node_values to display next to nodes, rounding to whole numbers
    #labels_with_values = [f"{label} ({int(round(value))})" for label, value in zip(labels, node_values)]
    
    return labels_with_values, source, target, value, color



def create_dynamic_plotly_sankey(table):
    """
    Create a dynamic Plotly Sankey diagram based on given table.
    
    Parameters:
        table (DataFrame): The DataFrame containing input data for Sankey diagram.
        
    Returns:
        fig: Plotly figure object containing the Sankey diagram.
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





