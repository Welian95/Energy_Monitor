import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey



page_title="Presentation Display"
st.set_page_config(
    page_title=page_title,
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': f"# This is the {page_title} of the E-Monitoring Software"
    }
    )







data_interface = st.session_state.data_interface 




def main():
    
    
    columns = st.columns(2)
    columns[0].title(page_title)
    if columns[1].button("Main"):
            switch_page("Main")


    data_mapping = st.session_state.data_mapping

    st.session_state.sankey_mapping

    columns = list(st.session_state.sankey_mapping.keys())

    st.write(columns[0])

    st.write(data_mapping)




    #last_data = read_data_from_csv_with_time_range(,only_last_row=True)

    "last_data:"
    last_row = data_interface.get_data(column_names= None, num_rows=1, ascending=False)
    last_row


    freq = data_interface.get_time_frequency()
    "freq"
    freq

    

    



    




if __name__ == "__main__":
    main()

    


