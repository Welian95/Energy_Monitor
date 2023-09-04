
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
# Importieren des statistics Moduls
from statistics import mean
from io import BytesIO
import base64
from matplotlib.patheffects import withStroke

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

def auto_scale_sankey_params(flows):
    """
    Automatically scale trunklength and pathlengths based on the flows in the diagram.

    Parameters:
        flows (list of int): The flows in the diagram.

    Returns:
        tuple: Recommended trunklength and pathlength.
    """
    # Calculate the mean flow size
    mean_flow_size = mean([abs(flow) for flow in flows])
    
    # Base trunklength and pathlength for a reference mean flow size (e.g., 100)
    base_trunklength = 100
    base_pathlength = 50
    
    # Scale trunklength and pathlength based on mean flow size
    scaling_factor = mean_flow_size / 100.0
    scaled_trunklength = base_trunklength * scaling_factor
    scaled_pathlength = base_pathlength * scaling_factor
    
    return scaled_trunklength, [scaled_pathlength] * len(flows)





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

# Berechnung des Mittelwerts der absoluten Werte in einer Zeile mit Lambda-Funktion und statistics.mean
calculate_mean_of_absolute_values = lambda numbers: mean([abs(x) for x in numbers])



#Konventionen:
    #PV Bezug und Einspeisung zeigt immer nach oben : orientations= 1
    #Netzbezug/Energielieferung kommt immer von links : orientations= 0
    #Wärmebezug kommt immer von Unten : orientations= -1
    #Energienutzng immer nach rechts : orientations= 0

    ## Jeder Energieträger hat eine feste Farbe 
    ## Umwandelnde Prozesse (wie Heizungen etc. bekommen eine eigene Farbe)


st.title("Sankey-Test")

# Erstellen Sie die Matplotlib-Figur und das Sankey-Diagramm
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                 title="Vereinfachtes Kraftwerksmodell")

# Deaktiviere die Rahmenlinien der Achsen
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Define RGBA colors with transparency
electricity_color = (0, 0, 1, 0.5)  # Light transparent blue
heat_connector_color = (1, 0.5, 0, 0.5)  # Light transparent orange
e_consumption_color = (0, 1, 1, 0.5)  # Light transparent blue
heat_flows_color = (1, 0, 0, 0.5)  # Light transparent red
air_condition_color = (0, 1, 0, 0.5)  # Light transparent green

# Define edge settings
edge_color = "black" # or: #565656"
edge_width = 1.0  # You can adjust this value


#fig, ax = plt.subplots()
sankey = Sankey(ax=ax, unit=None, ) 


############AIR_KONDITON######### Prior: 5
Air_IN = 20
HEAT_IN = 50
HEATED_AIR_OUT = (Air_IN + HEAT_IN) *-1
#############################



#############AIRCONNECTOR#########Prior:4
HLS_OUT = Air_IN *-1  #-20
HLS_IN = HLS_OUT *-1            #20
###############################


################Verbraucher#################PRIOR:3

Rest = -15
IT = -15
Server = -20
Verbraucher_in = abs(Rest+IT+Server)
###############################

############HEATFLOWS######## Prior:2
Room_Heat_IN = 100
Room_Heat_Out = Room_Heat_IN *-1 
##############################


############HEATCONNECTOR#########Prior:1
Umweltwärme = 60
Wärmepumpe_IN = 90
RLT_Wärme_IN = -50
Heizflächen = -100
#####################


##########Elektro-Gebäude###############PRIOR:0
PV_Ertrag = 60
Netzbezug = 120
Verbraucher_out =  Verbraucher_in * -1
Lüftungsanlage = HLS_OUT
Heat_pump_power = Wärmepumpe_IN *-1
Einspeisung_Netz = -20
########################











electricity_flows = [PV_Ertrag, Netzbezug, Verbraucher_out,Lüftungsanlage,Heat_pump_power,Einspeisung_Netz]
electricity_labels=['Erzeugung_PV','Strom_Standort', '', "", '',"Einspeisung", ]
scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(electricity_flows)


scaled_pathlengths[3] = 50
scaled_pathlengths[4] = 50



# first diagram, indexed by prior=0
sankey.add(flows=electricity_flows,
    labels=electricity_labels,
    label='Elektro-Gebäude',
    trunklength=scaled_trunklength,
    orientations=[1, 0, 0, 0, 0, 1],
    pathlengths=scaled_pathlengths,
    facecolor=electricity_color,
    edgecolor=edge_color,
    linewidth=edge_width,
    )

L_Connector = 100



heat_connector= [Umweltwärme, Wärmepumpe_IN, RLT_Wärme_IN, Heizflächen]
heat_connector_Labels= ['Wärme/Kältebezug', 'Strom_WP', 'Wärme/Kälte_RLT','Wärme/Kälte_WP']
scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(heat_connector)

scaled_pathlengths[0] = 50
scaled_pathlengths[1] = 150
scaled_pathlengths[2] = 50

# second diagram indexed by prior=1
sankey.add(flows=heat_connector,
        labels=heat_connector_Labels,
        label='Wärmepumpe',
        trunklength=scaled_trunklength,
        pathlengths=scaled_pathlengths,
        orientations=[-1, 0, 0, 0],
        facecolor=heat_connector_color,
        edgecolor=edge_color,
        linewidth=edge_width,

        prior=0,
        connect=(4, 1,))   #(Connect Index of Prio Flow with Index of Self-Flow)



heat_flows = [Room_Heat_IN, Room_Heat_Out]
heat_flows_labels = ["", "Raumbeheizung"]
scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(heat_flows)

# third diagram indexed by prior=2
sankey.add(flows=heat_flows,
        labels=heat_flows_labels,
        label="Beheizung",
        trunklength=scaled_trunklength,
        pathlengths=scaled_pathlengths,
        facecolor=heat_flows_color,
        edgecolor=edge_color,
        linewidth=edge_width,

        prior=1,
        connect=(3, 0))   #(Index of input Flow, Index of Outputflow)




e_consumtion= [Verbraucher_in, Rest, IT, Server ]
e_consumtion_labels=['', 'Rest','E-Mobilität','Strom_Server']
scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(e_consumtion)

scaled_pathlengths[0] = 50
scaled_pathlengths[1] = 100
scaled_pathlengths[2] = 150
scaled_pathlengths[3] = 200


# fourth diagram indexed by prior=3
sankey.add(flows=e_consumtion,
        labels=e_consumtion_labels,
        label='Strombezug_Anlagen',
        trunklength=scaled_trunklength,
        pathlengths=scaled_pathlengths,
        facecolor=e_consumption_color,
        edgecolor=edge_color,
        linewidth=edge_width,

        prior=0,
        connect=(2, 0))   #(Index of input Flow, Index of Outputflow)







air_connector= [ HLS_IN, HLS_OUT, ]
air_connector= [20,-20]
air_connector_Labels= ['Strom_HLS', '', ]
scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(air_connector)

scaled_pathlengths[0] = 100
scaled_pathlengths[1] = 240

# second diagram indexed by prior=4
sankey.add(flows=air_connector,
        labels=air_connector_Labels,
        label='HLS',
        trunklength=scaled_trunklength,
        pathlengths=scaled_pathlengths,
        orientations=[0, 0],
        facecolor="grey",
        linewidth=edge_width,

        prior=0,
        connect=(3, 0,))   #(Connect Index of Prio Flow with Index of Self-Flow)









Air_condition = [Air_IN, HEAT_IN, HEATED_AIR_OUT]
scaled_trunklength, scaled_pathlengths = auto_scale_sankey_params(Air_condition)

scaled_pathlengths[1] =200

# fives diagram indexed by prior=5
sankey.add(flows=Air_condition,
        labels=['', '','Kaumkonditionierung'],
        label='Kaumkonditionierung',
        trunklength=scaled_trunklength,
        pathlengths=scaled_pathlengths,
        facecolor=air_condition_color,
        edgecolor=edge_color,
        linewidth=edge_width,

        prior=4,
        connect=(1, 0))



#sankey.add(flows=Air_condition,
        #labels=['', '','Raumkonditionierung'],
        #label='Kaumkonditionierung',
        #trunklength=calculate_mean_of_absolute_values(e_consumtion),
        #pathlengths=[50,50,-50,],
        #prior=5,
        #connect=(1, 1)),
        #prior=[0,1],
        #connect=[(5, 0),(3,1)])
        #prior=1,
        #connect=(3, 1))   #(Index of input Flow, Index of Outputflow)







diagrams = sankey.finish()

# Durchlaufen aller Diagramme und Anpassen der Textstile
for diagram in diagrams:
    for text in diagram.texts:
        custom_style_text(text)

plt.title('Example Energy System')
#plt.legend(loc='upper right')

# Anpassen des Titel-Stils
custom_style_text(plt.title('Example Energy System'))

# Anpassen des Legenden-Stils
legend = plt.legend(loc='best')
for text in legend.get_texts():
    custom_style_text(text)


for i in range (len(diagrams)): 

    diagrams[i].patch.set_hatch('/')









# Konvertieren der Matplotlib-Figur in ein Byte-Array
img_stream = fig_to_image(fig)



# Anzeige des Byte-Arrays als Bild in Streamlit
st.image(img_stream, caption="Sankey Diagram", use_column_width=True, )























fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                 title="Vereinfachtes Kraftwerksmodell")
sankey = Sankey(ax=ax, unit=None)


sankey.add(flows=[1.0, -0.3, -0.1, -0.1, -0.5],
       pathlengths = [0.5, 0.06, 0.5, 0.5, 0.375],
       labels=['P$el$', 'Q$ab,vd$', 'P$vl,vd$', 'P$vl,mot$', ''],
       label='Laden',
       orientations=[0, -1, 1, 1, 0])



sankey.add(flows=[0.5, 0.1, 0.1, -0.1, -0.1, -0.1, -0.1, -0.3], fc='#37c959',
       label='Entladen',
       labels=['P$mech$', 'Q$zu,ex$', 'Q$zu,rekup$', 'P$vl,tb$', 'P$vl,gen$',                'Q$ab,tb$', 'Q$ab,rekup$', 'P$nutz$'],
       orientations=[0, -1, -1, 1, 1, -1, -1, 0], prior=0, connect=(4, 0))



sankey.add(flows=[-0.1, 0.1],
       label='Rekuperator',
       #labels=['bla'],
       orientations=[1,1], prior=1, connect=(2, 0))


diagrams = sankey.finish()
diagrams[-1].patch.set_hatch('/')
plt.legend(loc='upper right')


# Konvertieren der Matplotlib-Figur in ein Byte-Array
img_stream = fig_to_image(fig)

# Anzeige des Byte-Arrays als Bild in Streamlit
st.image(img_stream, caption="Sankey Diagram", use_column_width=True, )










