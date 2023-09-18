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


#Funktion zum Lesen von csv Dateien
def read_last_row_and_headers(csv_file_path):
    """
    Read the headers and the last row from a CSV file.

    Parameters:
    - csv_file_path (str): The path to the CSV file.

    Returns:
    - tuple: A tuple containing the headers as a list and the last row as a list.
    """
    headers = None
    last_row = None
    
    # Open the CSV file
    with open(csv_file_path, 'r', encoding=None) as file:
        reader = csv.reader(file, delimiter=';')
        
        # Read headers (first row)
        headers = next(reader)
        
        # Read rows and only keep the last one
        for row in reader:
            last_row = row

    return headers, last_row



from random import randint

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
    
    Parameters:
        table (DataFrame): The DataFrame containing input data for Sankey diagram.
        
    Returns:
        tuple: A tuple containing labels, source, target, value, and color lists for the Sankey diagram.
    """
    labels = []
    source = []
    target = []
    value = []
    color = []
    
    label_index_dict = {}
    energy_type_color_dict = {}
    
    # Predefined colors for certain types of energy
    predefined_colors = {
        "electricity": "rgba(173, 216, 230, 0.8)",
        "heat": "rgba(255, 213, 128, 0.8)"
    }

    # First pass: collect all unique labels and their corresponding index in the labels list
    for index, row in table.iterrows():
        label = row['Label'].strip()  # Remove any extra spaces
        if label not in label_index_dict:
            label_index_dict[label] = len(labels)
            labels.append(label)
        
    # Second pass: populate source, target, value, and color lists based on the table rows
    for index, row in table.iterrows():
        label = row['Label'].strip()  # Remove any extra spaces
        src = label_index_dict[label]
        tgt = None
        
        if row['Consumption'] == 0:  # Skip rows with zero consumption
            continue
        
        if row['Type'] == 'Source':
            if row['EnergyTypeOutput'].strip() not in label_index_dict:
                label_index_dict[row['EnergyTypeOutput'].strip()] = len(labels)
                labels.append(row['EnergyTypeOutput'].strip())
            
            tgt = label_index_dict[row['EnergyTypeOutput'].strip()]
            color.append(predefined_colors.get(row['EnergyTypeOutput'].strip(), "rgba(128, 128, 128, 0.8)"))
        elif row['Type'] == 'Transformer':
            if row['EnergyTypeInput'].strip() not in label_index_dict:
                label_index_dict[row['EnergyTypeInput'].strip()] = len(labels)
                labels.append(row['EnergyTypeInput'].strip())
            if row['EnergyTypeOutput'].strip() not in label_index_dict:
                label_index_dict[row['EnergyTypeOutput'].strip()] = len(labels)
                labels.append(row['EnergyTypeOutput'].strip())
            
            src = label_index_dict[row['EnergyTypeInput'].strip()]
            tgt = label_index_dict[row['EnergyTypeOutput'].strip()]
            color.append(mix_colors(predefined_colors.get(row['EnergyTypeInput'].strip(), "rgba(128, 128, 128, 0.8)"),
                                    predefined_colors.get(row['EnergyTypeOutput'].strip(), "rgba(128, 128, 128, 0.8)")))
        elif row['Type'] == 'Sink':
            if row['EnergyTypeInput'].strip() not in label_index_dict:
                label_index_dict[row['EnergyTypeInput'].strip()] = len(labels)
                labels.append(row['EnergyTypeInput'].strip())
            
            src = label_index_dict[row['EnergyTypeInput'].strip()]
            tgt = label_index_dict[label]
            color.append(predefined_colors.get(row['EnergyTypeInput'].strip(), "rgba(128, 128, 128, 0.8)"))
        
        if src is not None and tgt is not None:
            source.append(src)
            target.append(tgt)
            value.append(row['Consumption'])
    
    return labels, source, target, value, color



def create_dynamic_plotly_sankey(table):
    """
    Create a dynamic Plotly Sankey diagram based on given table.
    
    Parameters:
        table (DataFrame): The DataFrame containing input data for Sankey diagram.
        
    Returns:
        fig: Plotly figure object containing the Sankey diagram.
    """
    
    #print(table)
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
            source=source,
            target=target,
            value=value,
            color=color  # Add color parameter here
        )
    ))
    
    return fig







##########################################################################################################################################################


if __name__ == "__main__":


    ##################################CODE, welcher in den Anlagen Modulen geamcht werden muss ######################################
    csv_file_path = r"C:\Users\Jwesterhorstmann\Desktop\Masterarbeit\Energy_monitor\example\example_data1.csv" # Replace with the path to your CSV file
    Columns, data = read_last_row_and_headers(csv_file_path)

    #data[1:] = list(map(float, data[1:]))
    data[1:] = [float(x.replace(',', '.')) for x in data[1:]]




    ############################################################################# DATA for Snakey - wich has to be Created in Anlagen-Komponenten! #############################################################################


    transported_energy_IN = data [13] 
    room_conditioning_IN = data [14]  #Waermebezug_RLT + Kaeltebezug_RLT
    room_heating_IN = data [8] # Waermebezug_HZ + Kaeltebezug_HZ
    e_mobility_OUT = data [11]  
    Server_OUT = data [10]  
    e_consumers_IN = data [9]  
    ambient_heat_IN = data [6]  #Waermebezug_Sonden + Kaeltebezug_Sonden
    heat_pump_power_IN = data [7]  
    battery_charge = data [16]  
    PV_yield_IN = data [3] 
    grid_supply_IN = data [5] 
    PV_supply_OUT = data [4] 

    if battery_charge <= 0:
        battery_discharge_OUT = battery_charge
        battery_charge_IN = 0

    else:
        battery_charge_IN = battery_charge
        battery_discharge_OUT = 0



    if battery_charge <= 0:
        battery_charge_OUT = battery_charge
        battery_discharge_IN = 0

    else:
        battery_discharge_IN = battery_charge
        battery_charge_OUT = 0




    ############Raumkonditionierung_Belüftung######### Prior: 5
    room_OUT_2 = (transported_energy_IN + room_conditioning_IN) *-1
    #############################

    #############Energieverteilungssysteme#########Prior:4
    transported_energy_OUT = transported_energy_IN *-1  
    auxiliary_energy_IN = transported_energy_IN                       #M: HLS_Strom   
    ###############################

    ################Elektro-Nutzer#################PRIOR:3
    rest_OUT = ( e_consumers_IN + Server_OUT + e_mobility_OUT ) *-1
    ############################################

    ############Raumkonditionierung_Wärmeübertragungsflächen################# Prior:2
    room_OUT_1 = room_heating_IN *-1 
    ########################################

    ############Wärme#########Prior:1
    room_conditioning_OUT = room_conditioning_IN *-1
    room_heating_OUT = room_heating_IN * -1
    #########################################

    ##########Elektro-Gebäude###############PRIOR:0
    e_consumers_OUT =  e_consumers_IN * -1
    auxiliary_energy_OUT = auxiliary_energy_IN * -1
    heat_pump_power_OUT = heat_pump_power_IN *-1
    #################################################
    ##########################################################################################################################################################




    #############################################################################DATA for PLOTLY #############################################################################




    sample_data = {
        'Label': ['PV_yield_IN','PV_supply_OUT','grid_supply_IN','battery_charge_OUT','battery_discharge_IN','heat_pump_power_OUT','ambient_heat_IN','room_OUT_1','Server_OUT','e_mobility_OUT','rest_OUT','transported_energy_IN','room_OUT_2']
    ,
        'Consumption': [ abs(PV_yield_IN), abs(PV_supply_OUT) , abs(grid_supply_IN) ,abs(battery_charge_OUT) ,abs(battery_discharge_IN) ,abs(heat_pump_power_OUT) ,abs(ambient_heat_IN) ,abs(room_OUT_1), abs(Server_OUT) , abs(e_mobility_OUT) , abs(rest_OUT) , abs(transported_energy_IN) , abs(room_OUT_2)]
    ,
        'Type': ['Source','Sink','Source','Sink','Source','Transformer','Source','Sink','Sink','Sink','Sink','Transformer','Sink']
    ,
        'EnergyTypeInput': ['-','electricity','-','electricity','-','electricity','-','heat','electricity','electricity','electricity','electricity','heat']
    ,
        'EnergyTypeOutput': ['electricity','-','electricity','-','electricity','heat','heat','-','-','-','-','heat','-']
    }




































    st.title("Sankey-Test")



    toggle1 , toggle2 = st.columns(2)
    test = toggle1.toggle("Create Sankey", value=False,)
    auto_rerun = toggle2.toggle("Auto_rerun", value=False,)

    
    if test == True:

        with st.expander("Show data"):
            col1, col2 = st.columns(2)
            col1.write(Columns)
            col2.write(data)


        st.subheader("Plotly - Sankey")

        sample_table = pd.DataFrame(sample_data)

        # Create and show the Sankey diagram
        sample_sankey_fig = create_dynamic_plotly_sankey(sample_table)

        st.plotly_chart(sample_sankey_fig,use_container_width=True)






        if auto_rerun == True:
            # Sleep for 1 second
            time.sleep(1)
            
            # Rerun the app
            st.experimental_rerun()



