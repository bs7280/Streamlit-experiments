import streamlit as st
from streamlit_folium import st_folium
import folium

from geo_utils import move_coordinates, mock_folium_map
from streamlit_callbacks import callback_data_change, callback_move_coords
from streamlit_utils import \
        create_editable_df, st_compas_editor_ui, \
        folium_map_obj, make_base_df, append_road_point
    

def map_road_picker_component(starting_lat, starting_long):

    ## Pre run - set state
    if 'active_row_id' not in st.session_state:
        st.session_state['active_row_id'] = None


    ## TODO - load data from map
    map_pin_locations = [
        # TODO - Maybe I set this to base pin location? Otherwise duplicates are possible after moving a pin
        # or maybe I 
        (x['modified_latitude'], x['modified_longitude']) 
        for x in st.session_state['config_data']['road_data']
    ]
    # TODO wrap in hash(map_pin_locations), 
    # if hash != state.last_map_hash:
    #    -> remake state.map_obj
    
    map_obj= folium_map_obj(starting_lat, starting_long, locations=map_pin_locations)
    map = st_folium(map_obj, width=700, height=500)

    #print(map)
    if map.get('last_clicked') is not None:
        new_lat, new_long = map['last_clicked']['lat'], map['last_clicked']['lng']
        append_road_point(new_lat, new_long)

        folium.Marker([new_lat, new_long]).add_to(map_obj)

    # Dummy DF
    df = make_base_df(st.session_state['config_data']['road_data'])

    ## Set initial session state
    #st.session_state['df_test'] = df

    if 'checkbox_state' not in st.session_state:
        st.session_state['checkbox_state'] = dict([(int(k),v) for k,v in df['Include'].to_dict().items()])

    data_editor = create_editable_df(df)

    if st.session_state['active_row_id'] is not None:
        _active_row_id = st.session_state['active_row_id']
        _active_row_data = st.session_state['config_data']['road_data'][_active_row_id]


        start_cords = (_active_row_data['latitude'], _active_row_data['longitude'])
        new_cords = (_active_row_data['modified_latitude'], _active_row_data['modified_longitude'])

        row_summary = f"Initial Cords: {start_cords} ; New Cords: {new_cords}"

        st.write(f"Active row ({_active_row_id}): {row_summary}")

        st_compas_editor_ui()
