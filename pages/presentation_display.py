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

def main():
    
    
    columns = st.columns(2)
    columns[0].title(page_title)
    if columns[1].button("Main"):
            switch_page("Main")


    data_mapping = st.session_state.data_mapping
    st.write(data_mapping)




if __name__ == "__main__":
    main()

    


