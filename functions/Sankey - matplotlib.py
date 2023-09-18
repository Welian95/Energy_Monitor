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


def auto_scale_sankey_params(flows):
    """
    Auto-scale the parameters of a Sankey diagram based on the provided flows.
    
    Parameters:
        flows (list): List of flow values for the Sankey diagram.
        
    Returns:
        tuple: Scaled trunklength and list of scaled pathlengths.
    """
    
    # Calculate the maximum flow to set the trunk length
    max_flow = max(abs(flow) for flow in flows)
    scaled_trunklength = max_flow  # Example scaling factor, adjust as needed
    
    # Scale pathlengths based on individual flows
    scaled_pathlengths = [abs(flow)  for flow in flows]  # Example scaling factor, adjust as needed
    
    return scaled_trunklength, scaled_pathlengths


def create_matplot_sankey(PV_yield_IN, grid_supply_IN, e_consumers_OUT, auxiliary_energy_OUT, 
                          heat_pump_power_OUT, PV_supply_OUT, battery_charge_OUT, battery_discharge_IN,
                          ambient_heat_IN, heat_pump_power_IN, room_conditioning_OUT, room_heating_OUT,
                          room_heating_IN, room_OUT_1, e_consumers_IN, Server_OUT, rest_OUT, e_mobility_OUT,
                          auxiliary_energy_IN, transported_energy_OUT, transported_energy_IN, room_conditioning_IN, room_OUT_2,
                          auto_scale_sankey_params, custom_style_text):
    """
    Create a Matplotlib Sankey diagram based on the given parameters.
    
    Parameters:
        All the parameters represent the flows in the Sankey diagram.
        auto_scale_sankey_params (function): Function to auto-scale Sankey diagram parameters.
        custom_style_text (function): Function to style text in the Sankey diagram.
        
    Returns:
        fig: Matplotlib figure object containing the Sankey diagram.
    """
    
    # Initialize the Matplotlib figure and the Sankey diagram
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                         title="Matplotlib - Sankey")

    # Disable the axis frame lines
    for position in ['top', 'right', 'bottom', 'left']:
        ax.spines[position].set_visible(False)
    
    # Define RGBA colors with transparency
    electricity_color = (0, 0, 1, 0.5)  # Light transparent blue
    heat_connector_color = (1, 0.5, 0, 0.5)  # Light transparent orange
    e_consumption_color = (0, 1, 1, 0.5)  # Light transparent blue
    heat_flows_color = (1, 0, 0, 0.5)  # Light transparent red
    heat_flows_color = (0, 1, 0, 0.5)  # Light transparent red
    air_condition_color = (0, 1, 0, 0.5)  # Light transparent green

    # Define edge settings
    edge_color = "black" # or: #565656"
    edge_width = 1.0  # You can adjust this value


    #fig, ax = plt.subplots()
    sankey = Sankey(ax=ax, unit=None, ) 

    electricity_flows = [PV_yield_IN, grid_supply_IN, e_consumers_OUT, auxiliary_energy_OUT, heat_pump_power_OUT, PV_supply_OUT, battery_charge_OUT, battery_discharge_IN]
    electricity_labels=['PV-Ertrag','Stromnetzbezug', '', "Hilfsenergien", '',"PV-Netzeinspeisung","Stromspeicher laden","Stromspeicher entladen" ]
    scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(electricity_flows)


    # first diagram, indexed by prior=0
    sankey.add(flows=electricity_flows,
        labels=electricity_labels,
        label='Elektro-Gebäude',
        trunklength=scaled_trunklength,
        orientations=[1, 0, 0, 0, 0, 1,-1,-1],
        pathlengths=scaled_pathlengths,
        facecolor=electricity_color,
        edgecolor=edge_color,
        linewidth=edge_width,
        )



    heat_connector = [ambient_heat_IN, heat_pump_power_IN, room_conditioning_OUT, room_heating_OUT]
    heat_connector_Labels= ['Energieaustausch Erdsonden', 'Stromaufnahme WP', '','']
    scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(heat_connector)



    fixed_pathlengths1 = scaled_pathlengths[1] 
    fixed_pathlengths2 = scaled_pathlengths[2] 

    scaled_pathlengths[1] = fixed_pathlengths1 *3
    scaled_pathlengths[2] = fixed_pathlengths2        

    # second diagram indexed by prior=1
    sankey.add(flows=heat_connector,
            labels=heat_connector_Labels,
            label='Wärme',
            trunklength=scaled_trunklength,
            pathlengths=scaled_pathlengths,
            orientations=[-1, 0, 0, 0],
            facecolor=heat_connector_color,
            edgecolor=edge_color,
            linewidth=edge_width,

            prior=0,
            connect=(4, 1,))   #(Connect Index of Prio Flow with Index of Self-Flow)



    heat_flows = [room_heating_IN, room_OUT_1]
    heat_flows_labels = ["", "Wärmeübertragungsflächen"]
    scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(heat_flows)

    # third diagram indexed by prior=2
    sankey.add(flows=heat_flows,
            labels=heat_flows_labels,
            trunklength=scaled_trunklength,
            pathlengths=scaled_pathlengths,
            facecolor=heat_flows_color,
            edgecolor=edge_color,
            linewidth=edge_width,

            prior=1,
            connect=(3, 0))   #(Index of input Flow, Index of Outputflow)




    e_consumtion = [e_consumers_IN, Server_OUT, rest_OUT, e_mobility_OUT,  ]
    e_consumtion_labels=['','Strombezug Server','Strombezug Rest','Strombezug E-Autos', ]
    scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(e_consumtion)


    scaled_pathlengths[0] = scaled_pathlengths[0] * 5
    scaled_pathlengths[1] = scaled_pathlengths[1] * 10
    scaled_pathlengths[2] = scaled_pathlengths[2] * 10
    scaled_pathlengths[3] = scaled_pathlengths[3] * 10


    # fourth diagram indexed by prior=3
    sankey.add(flows=e_consumtion,
            labels=e_consumtion_labels,
            label='Elektro-Nutzer',
            trunklength=scaled_trunklength,
            pathlengths=scaled_pathlengths,
            facecolor=e_consumption_color,
            edgecolor=edge_color,
            linewidth=edge_width,
            orientations=[0,1,1,1],

            prior=0,
            connect=(2, 0))   #(Index of input Flow, Index of Outputflow)



    auxiliary_connector = [auxiliary_energy_IN, transported_energy_OUT]
    auxiliary_connector_Labels= ['', '', ]
    scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(auxiliary_connector)



    
    scaled_pathlengths[0] = fixed_pathlengths1  *8    ##### No Changes without scaling heat_conncetor pathlengths!!!!!!
    scaled_pathlengths[1] = fixed_pathlengths2         ##### No Changes without scaling heat_conncetor pathlengths!!!!!!

    # second diagram indexed by prior=4
    sankey.add(flows=auxiliary_connector,
            labels=auxiliary_connector_Labels,
            label='Energieverteilungssysteme',
            trunklength=scaled_trunklength,
            pathlengths=scaled_pathlengths,
            orientations=[0, 0],
            facecolor="grey",
            linewidth=edge_width,

            prior=0,
            connect=(3, 0,))   #(Connect Index of Prio Flow with Index of Self-Flow)




    Air_condition = [transported_energy_IN, room_conditioning_IN, room_OUT_2]
    scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(Air_condition)


    # fives diagram indexed by prior=5
    sankey.add(flows=Air_condition,
            labels=['', '','Belüftungssystem'],
            label='Raumkonditionierung',
            trunklength=scaled_trunklength,
            pathlengths=scaled_pathlengths,
            facecolor=air_condition_color,
            edgecolor=edge_color,
            linewidth=edge_width,

            prior=4,
            connect=(1, 0))






    diagrams = sankey.finish()

    # Durchlaufen aller Diagramme und Anpassen der Textstile
    for diagram in diagrams:
        for text in diagram.texts:
            custom_style_text(text)

    #plt.title('Example Energy System')
    #plt.legend(loc='upper right')

    # Anpassen des Titel-Stils
    custom_style_text(plt.title(''))

    # Anpassen des Legenden-Stils
    legend = plt.legend(loc='best')
    legend.get_frame().set_alpha(0.0)
    for text in legend.get_texts():
        custom_style_text(text)


    for i in range (len(diagrams)): 

        diagrams[i].patch.set_hatch('/')


    # Return the Matplotlib figure
    return fig





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

def generate_sankey_data_from_table_old(table):
    """
    Generate Sankey diagram data (labels, source, target, value, color) from a given table.
    
    Parameters:
        table (DataFrame): The DataFrame containing input data for Sankey diagram.
        
    Returns:
        tuple: A tuple containing labels, source, target, value, and color lists for the Sankey diagram.
    """
    st.write (table)
    labels = []
    source = []
    target = []
    value = []
    color = []
    
    label_index_dict = {}
    energy_type_color_dict = {}  # Dictionary to store unique colors for each energy type
    
    # Predefined colors for certain types of energy
    predefined_colors = {
        "electricity": "rgba(173, 216, 230, 0.8)",  # Blue
        "heat": "rgba(255, 213, 128, 0.8)"  # Orange
    }

    for index, row in table.iterrows():
        label = row['Label']
        if label not in label_index_dict:
            label_index_dict[label] = len(labels)
            labels.append(label)
            
        for etype in ['EnergyTypeInput', 'EnergyTypeOutput']:
            energy_type = row[etype]
            if energy_type and energy_type != '-':
                if energy_type not in label_index_dict:
                    label_index_dict[energy_type] = len(labels)
                    labels.append(energy_type)
                
                if energy_type not in energy_type_color_dict:
                    # Use the predefined color if available, else generate a random color
                    energy_type_color_dict[energy_type] = predefined_colors.get(
                        energy_type, 
                        f'rgba({randint(0, 255)}, {randint(0, 255)}, {randint(0, 255)}, 0.5)'
                )
                    
    for index, row in table.iterrows():
        src = label_index_dict[row['Label']]
        tgt = None
        
        if row['Type'] == 'Source':
            tgt = label_index_dict[row['EnergyTypeOutput']]
            color.append(energy_type_color_dict[row['EnergyTypeOutput']])
        elif row['Type'] == 'Transformer':
            src = label_index_dict[row['EnergyTypeInput']]
            tgt = label_index_dict[row['EnergyTypeOutput']]
            color.append(mix_colors(energy_type_color_dict[row['EnergyTypeInput']], energy_type_color_dict[row['EnergyTypeOutput']]))
        elif row['Type'] == 'Sink':
            src = label_index_dict[row['EnergyTypeInput']]
            tgt = label_index_dict[row['Label']]
            color.append(energy_type_color_dict[row['EnergyTypeInput']])
            
        if tgt is not None:
            source.append(src)
            target.append(tgt)
            value.append(row['Consumption'])
    
    return labels, source, target, value, color

def generate_sankey_data_from_table_wrong(table):
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
    energy_type_color_dict = {}  # Dictionary to store unique colors for each energy type
    
    # Predefined colors for certain types of energy
    predefined_colors = {
        "electricity": "rgba(173, 216, 230, 0.8)",  # Blue
        "heat": "rgba(255, 213, 128, 0.8)"  # Orange
    }

    # Create labels and a label index dictionary
    for index, row in table.iterrows():
        label = row['Label']
        if label not in label_index_dict:
            label_index_dict[label] = len(labels)
            labels.append(label)
            
        for etype in ['EnergyTypeInput', 'EnergyTypeOutput']:
            energy_type = row[etype]
            if energy_type and energy_type != '-':
                if energy_type not in label_index_dict:
                    label_index_dict[energy_type] = len(labels)
                    labels.append(energy_type)
                
                # Assign colors to the energy types
                if energy_type not in energy_type_color_dict:
                    energy_type_color_dict[energy_type] = predefined_colors.get(
                        energy_type, 
                        f'rgba({randint(0, 255)}, {randint(0, 255)}, {randint(0, 255)}, 0.5)'
                    )

    # Create source, target, value, and color lists
    for index, row in table.iterrows():
        src = label_index_dict[row['Label']]
        tgt = None
        edge_color = "rgba(128, 128, 128, 0.5)"  # Default color
        
        if row['Type'] == 'Source':
            tgt = label_index_dict.get(row['EnergyTypeOutput'], None)
            edge_color = energy_type_color_dict.get(row['EnergyTypeOutput'], edge_color)
        elif row['Type'] == 'Transformer':
            src = label_index_dict.get(row['EnergyTypeInput'], src)
            tgt = label_index_dict.get(row['EnergyTypeOutput'], None)
            edge_color = energy_type_color_dict.get(row['EnergyTypeInput'], edge_color)
        elif row['Type'] == 'Sink':
            src = label_index_dict.get(row['EnergyTypeInput'], src)
            tgt = label_index_dict[row['Label']]
            edge_color = energy_type_color_dict.get(row['EnergyTypeInput'], edge_color)

        # If tgt is None, set it to a placeholder value (e.g., -1)
        tgt = tgt if tgt is not None else -1

        source.append(src)
        target.append(tgt)
        value.append(row['Consumption'])
        color.append(edge_color)

    return labels, source, target, value, color






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
        label = row['Label']
        if label not in label_index_dict:
            label_index_dict[label] = len(labels)
            labels.append(label)
        
    # Second pass: populate source, target, value, and color lists based on the table rows
    for index, row in table.iterrows():
        src = label_index_dict[row['Label']]
        tgt = None
        
        if row['Type'] == 'Source':
            if row['EnergyTypeOutput'] not in label_index_dict:
                label_index_dict[row['EnergyTypeOutput']] = len(labels)
                labels.append(row['EnergyTypeOutput'])
            
            tgt = label_index_dict[row['EnergyTypeOutput']]
            color.append(predefined_colors.get(row['EnergyTypeOutput'], "rgba(128, 128, 128, 0.8)"))
        elif row['Type'] == 'Transformer':
            if row['EnergyTypeInput'] not in label_index_dict:
                label_index_dict[row['EnergyTypeInput']] = len(labels)
                labels.append(row['EnergyTypeInput'])
            if row['EnergyTypeOutput'] not in label_index_dict:
                label_index_dict[row['EnergyTypeOutput']] = len(labels)
                labels.append(row['EnergyTypeOutput'])
            
            src = label_index_dict[row['EnergyTypeInput']]
            tgt = label_index_dict[row['EnergyTypeOutput']]
            color.append(mix_colors(predefined_colors.get(row['EnergyTypeInput'], "rgba(128, 128, 128, 0.8)"),
                                    predefined_colors.get(row['EnergyTypeOutput'], "rgba(128, 128, 128, 0.8)")))
        elif row['Type'] == 'Sink':
            if row['EnergyTypeInput'] not in label_index_dict:
                label_index_dict[row['EnergyTypeInput']] = len(labels)
                labels.append(row['EnergyTypeInput'])
            
            src = label_index_dict[row['EnergyTypeInput']]
            tgt = label_index_dict[row['Label']]
            color.append(predefined_colors.get(row['EnergyTypeInput'], "rgba(128, 128, 128, 0.8)"))
        
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
    st.write (len(labels))
    st.write (len(source))
    st.write (len(target))
    st.write (len(value))
    st.write (len(color))
    "Labels:"
    st.write (labels)
    "Values"
    st.write (value)

    print("labels", labels)
    print("source", source)
    print("target", target)
    print("value", value)
    print("color",color)
    
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














sample_data = {
    'Label': [' PV_yield_IN','PV_supply_OUT','grid_supply_IN','battery_charge_OUT','battery_discharge_IN','heat_pump_power_OUT','ambient_heat_IN','room_OUT_1','Server_OUT','e_mobility_OUT','rest_OUT','transported_energy_IN','room_OUT_2']


,
    'Consumption': [ 15, 0 , 0 ,3 ,0 ,5 ,5 ,12.5 ,10, 0.5 , 3 , 1.5 , 2 , 9.5]

,
    'Type': [' Source','Sink','Source','Sink','Source','Transformer','Source','Sink','Sink','Sink','Sink','Transformer','Sink']

,
    'EnergyTypeInput': [' -','electricity','-','electricity','-','electricity','-','heat','electricity','electricity','electricity','electricity','heat']


,
    'EnergyTypeOutput': [' electricity','-','electricity','-','electricity','heat','heat','-','-','-','-','heat','-']


,
    'Verbrauch Label': [' PV_yield_IN','PV_supply_OUT','grid_supply_IN','battery_charge_OUT','battery_discharge_IN','heat_pump_power_OUT','ambient_heat_IN','room_OUT_1','Server_OUT','e_mobility_OUT','rest_OUT','transported_energy_IN','room_OUT_2']


}

#sample_table = pd.DataFrame(sample_data)

# Create and show the Sankey diagram
#sample_sankey_fig = create_dynamic_plotly_sankey(sample_table)


#st.plotly_chart(sample_sankey_fig)


















# Berechnung des Mittelwerts der absoluten Werte in einer Zeile mit Lambda-Funktion und statistics.mean
calculate_mean_of_absolute_values = lambda numbers: mean([abs(x) for x in numbers])



#Konventionen:
    #PV Bezug und Einspeisung zeigt immer nach oben : orientations= 1
    #Netzbezug/Energielieferung kommt immer von links : orientations= 0
    #Wärmebezug kommt immer von Unten : orientations= -1
    #Energienutzng immer nach rechts : orientations= 0

    ## Jeder Energieträger hat eine feste Farbe 
    ## Umwandelnde Prozesse (wie Heizungen etc. bekommen eine eigene Farbe)








# Example usage


csv_file_path = r"C:\Users\Jwesterhorstmann\Desktop\Masterarbeit\Energy_monitor\example\example_data1.csv" # Replace with the path to your CSV file
Columns, data = read_last_row_and_headers(csv_file_path)

#data[1:] = list(map(float, data[1:]))
data[1:] = [float(x.replace(',', '.')) for x in data[1:]]




############################################################################# DATA for MATPLOTLIP #############################################################################


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
    'Label': [' PV_yield_IN','PV_supply_OUT','grid_supply_IN','battery_charge_OUT','battery_discharge_IN','heat_pump_power_OUT','ambient_heat_IN','room_OUT_1','Server_OUT','e_mobility_OUT','rest_OUT','transported_energy_IN','room_OUT_2']


,
    'Consumption': [ abs(PV_yield_IN), abs(PV_supply_OUT) , abs(grid_supply_IN) ,abs(battery_charge_OUT) ,abs(battery_discharge_IN) ,abs(heat_pump_power_OUT) ,abs(ambient_heat_IN) ,abs(room_OUT_1), abs(Server_OUT) , abs(e_mobility_OUT) , abs(rest_OUT) , abs(transported_energy_IN) , abs(room_OUT_2)]

,
    'Type': [' Source','Sink','Source','Sink','Source','Transformer','Source','Sink','Sink','Sink','Sink','Transformer','Sink']

,
    'EnergyTypeInput': ['-','electricity','-','electricity','-','electricity','-','heat','electricity','electricity','electricity','electricity','heat']


,
    'EnergyTypeOutput': ['electricity','-','electricity','-','electricity','heat','heat','-','-','-','-','heat','-']


,
    'Verbrauch Label': ['PV_yield_IN','PV_supply_OUT','grid_supply_IN','battery_charge_OUT','battery_discharge_IN','heat_pump_power_OUT','ambient_heat_IN','room_OUT_1','Server_OUT','e_mobility_OUT','rest_OUT','transported_energy_IN','room_OUT_2']


}

##########################################################################################################################################################


if __name__ == "__main__":


    st.title("Sankey-Test")

    with st.expander("Balancing test"):

        #Konventioen Raumkonditionierung_Belüftung
        sum_1 = transported_energy_IN + room_conditioning_IN
        sum_2 = room_OUT_2 *-1
        sum_Test_12 = sum_1 == sum_2
        st.write ("sum_Test_12:Bilanz für Raumkonditionierung_Belüftung ausgeglichen? ",sum_Test_12)

        #Konventioen Energieverteilungssysteme
        sum_3 = auxiliary_energy_IN 
        sum_4 = transported_energy_OUT *-1
        sum_Test_34 = sum_3 == sum_4
        st.write ("sum_Test_34:Bilanz für Energieverteilungssysteme ausgeglichen? ",sum_Test_34)

        #Konventioen Elektro-Nutzer
        sum_5 = e_consumers_IN 
        sum_6 = (e_mobility_OUT + Server_OUT + rest_OUT) * -1
        sum_Test56 = sum_5 == sum_6
        st.write ("sum_Test56:Bilanz für Elektro-Nutzer ausgeglichen? ",sum_Test56 )

        #Konventioen Raumkonditionierung_Wärmeübertragungsflächen
        sum_7 = room_heating_IN
        sum_8 =  room_OUT_1 *-1
        sum_Test78 = sum_7== sum_8
        st.write ("sum_Test78:Bilanz für Raumkonditionierung_Wärmeübertragungsflächen ausgeglichen? ",sum_Test78)

        #Konventioen Wärme
        sum_9 = ambient_heat_IN + heat_pump_power_IN
        sum_10 = ( room_conditioning_OUT + room_heating_OUT ) *-1
        sum_Test_910 = sum_9 == sum_10 
        st.write ("sum_Test_910:Bilanz für Wärme ausgeglichen? ",sum_Test_910)


        #Konventioen Elektro-Gebäude:
        sum_11 = battery_charge_IN + PV_yield_IN + grid_supply_IN
        sum_12 = ( battery_discharge_OUT + e_consumers_OUT +auxiliary_energy_OUT + heat_pump_power_OUT + PV_supply_OUT ) * -1
        sum_Test1112 = sum_11 == sum_12
        st.write ("sum_Test1112:Bilanz für Elektro-Gebäude ausgeglichen? ",sum_Test1112)


        #Konventioen Gesamtsystem Strom:
        sum_13 = e_consumers_OUT + auxiliary_energy_OUT + heat_pump_power_OUT 
        sum_14 = (e_consumers_IN + auxiliary_energy_IN + heat_pump_power_IN ) *-1

        sum_Test1314 = sum_13 == sum_14
        st.write ("sum_Test1314:Bilanz der Summe der Stromflüsse ins Gebäude ausgeglichen? ", sum_Test1314)

        #Konventioen Gesamtsystem Wärme:
        sum_15 = transported_energy_OUT + room_conditioning_OUT + room_heating_OUT
        sum_16 = (room_heating_IN +  transported_energy_IN + room_conditioning_IN ) * -1 

        sum_Test_1516 = sum_15 == sum_16
        st.write("sum_Test_1516:Bilanz der Summe der Wärmeflüsse ins Gebäude ausgeglichen? ", sum_Test_1516)



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




        st.subheader("Matplotlib - Sankey")

        fig = create_matplot_sankey(PV_yield_IN, 
                                    grid_supply_IN, 
                                    e_consumers_OUT, 
                                    auxiliary_energy_OUT, 
                                    heat_pump_power_OUT, 
                                    PV_supply_OUT, 
                                    battery_charge_OUT, 
                                    battery_discharge_IN,
                                    ambient_heat_IN, 
                                    heat_pump_power_IN, 
                                    room_conditioning_OUT, 
                                    room_heating_OUT,
                                    room_heating_IN, 
                                    room_OUT_1, 
                                    e_consumers_IN, 
                                    Server_OUT, rest_OUT, 
                                    e_mobility_OUT,
                                    auxiliary_energy_IN, 
                                    transported_energy_OUT, 
                                    transported_energy_IN, 
                                    room_conditioning_IN, 
                                    room_OUT_2, 
                                    auto_scale_sankey_params, 
                                    custom_style_text)
        

        img_stream = fig_to_image(fig)
        st.image(img_stream, caption="Sankey Matplotlib", use_column_width=True)


        




        if auto_rerun == True:
            # Sleep for 1 second
            time.sleep(1)
            
            # Rerun the app
            st.experimental_rerun()



