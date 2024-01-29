import streamlit as st

from utils import mock_folium_map
from streamlit_components import map_road_picker_component

## Main Component function

def main():
    #################### Start of App #######################
    st.title("Streamlit Complex Data Editor Tool")

    if 'config_data' not in st.session_state:
        st.session_state['config_data'] = {
            'road_data': mock_folium_map()
        }

    starting_lat, starting_lon = 41.8781, -87.6298
    map_road_picker_component(starting_lat, starting_lon)

    st.write("-----------------")
    st.write("Data from state outside component:")

    st.table(st.session_state['config_data']['road_data'])

if __name__ == "__main__":
    main()
