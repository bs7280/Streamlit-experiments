from turtle import onclick
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
import folium
import pandas as pd

from utils import move_coordinates, mock_folium_map

def _callback_helper_active_row():
        #edited_rows = st.session_state["data_editor"]
    #print(st.session_state['edited_rows'])
    edited_rows = st.session_state['data_editor']['edited_rows']

    # Bad variable name, breaking out one-liner that was too long
    itterable_tmp = [(i, _dict.get('Include', None)) for i,_dict in edited_rows.items()]
    itterable_tmp = [x for x in itterable_tmp if x[1] is not None]
    new_checkbox_state = dict(itterable_tmp)

    if len(itterable_tmp) > 0:
        # Find toggled value
        active_ids = []
        inactive_ids = []
        for i, val in st.session_state.checkbox_state.items():
            if new_checkbox_state.get(i, False) != val:
                active_ids.append(i)
            else:
                inactive_ids.append(i)

        # Validate current state
        #print(active_ids)
        assert len(active_ids) <= 1, \
            "Unexpected state - more than one recently changed checkbox"
        
        assert len(active_ids) + len(inactive_ids) == len(st.session_state['config_data']['road_data'])
        
        # Update DF to untoggle other values
        new_vals = [False] * len(st.session_state['config_data']['road_data'])

        # Set new state for active row ID
        if len(active_ids) > 0:
            active_id = active_ids[0]
            st.session_state['active_row_id'] = active_id

            # Ensure new output column values still preserve our active row
            new_vals[active_id] = True

            # Set active row data in session state
            # important to do it in this callback function so it updates exactly once
            #st.session_state['config_data']['road_data'][active_id]

            #active_row = st.session_state['df_test'].iloc[active_id]
            #row_summary = active_row.to_dict()
            if False:
                st.session_state['active_row_data'] = {
                    # These two will never change... coords of initial click on map
                    'latitude': row_summary['Latitude'],
                    'longitude': row_summary['Longitude'],
                    # Will be modified and plotted
                    'modified_latitude': row_summary['Latitude'],
                    'modified_longitude': row_summary['Longitude'],
                    'fontsize': row_summary['Fontsize'],
                    'angle': row_summary['Angle_degrees'],
                }
        else:
            st.session_state['active_row_id'] = None

        st.session_state['active_row_series'] = new_vals
        #st.session_state['df_test']['Include'] = pd.Series(new_vals)

# Main entrypoint on data change
def callback_data_change():
    _callback_helper_active_row()

    ## TODO update recently edited rows to session state
    edited_rows = st.session_state['data_editor']['edited_rows']
    # Horrific one liner
    # Returns dicitonary of id: {changes} removing all cases of Include special field
    itterable_tmp = [(i, dict([(k,v) for k,v in _dict.items() if k != 'Include'])) 
        for i,_dict in edited_rows.items()]

    assert len(itterable_tmp) <= 1, "Unexpected state"
    if len(itterable_tmp) == 1:
        row_number, changes = itterable_tmp[0]
        
        for k,v in changes.items():
            st.session_state['config_data']['road_data'][row_number][k] = v

        #st.session_state['config_data']['road_data']


def callback_move_coords(direction, distance):
    active_row_id = st.session_state['active_row_id']
    active_row_data = st.session_state['config_data']['road_data'][active_row_id]

    #print(type(active_row_data), id(active_row_data))
    #print(type(st.session_state['config_data']['road_data'][active_row_id]), id(st.session_state['config_data']['road_data'][active_row_id]))

    start_lat = active_row_data['modified_latitude']
    start_long = active_row_data['modified_longitude']

    new_lat, new_long = move_coordinates(start_lat, start_long, distance, direction)

    st.session_state['config_data']['road_data'][active_row_id]['modified_latitude'] = new_lat
    st.session_state['config_data']['road_data'][active_row_id]['modified_longitude'] = new_long

def callback_reset_coords():
    pass #TODO 

## Streamlit UI Helper Methods
def create_editable_df(df):

    return st.data_editor(
        df,
        column_config={
            "Include": st.column_config.CheckboxColumn(
                "Include",
                help="Check to modify location",
                default=False,
            )
        },
        disabled=["Latitude", "Longitude"],
        hide_index=True,
        key="data_editor",
        num_rows="dynamic",
        on_change=callback_data_change,
    )

def st_compas_editor_ui():
    st.header("Lat / Long mover:")

    distance = st.slider("Moved distance (feet)", 0, 25, 5)

    grid = st.columns(5)
    with grid[0]:
        st.button("North", on_click=callback_move_coords, args=(0, distance))
    with grid[1]:
        st.button("South", on_click=callback_move_coords, args=(180, distance))
    with grid[2]:
        st.button("East", on_click=callback_move_coords, args=(90, distance))
    with grid[3]:
        st.button("West", on_click=callback_move_coords, args=(270, distance))
    with grid[4]:
        st.button("Reset") # TODO - set modified vals to base vals on click

#def get_folium_map(latitude, longitude, locations=[]):
@st.cache_data(experimental_allow_widgets=True)
def folium_map_obj(latitude, longitude, locations=[]):
    m = folium.Map(location=[latitude, longitude], zoom_start=15)
    for loc in locations:
        folium.Marker([loc[0], loc[1]]).add_to(m)

    #d = Draw(export=True)
    #d.add_to(m)

    #c1, c2 = st.columns(2)

    return m

def process_folium_output(folium_output, existing_points):
    def to_str(coords):
        return f"{coords[0]}, {coords[1]}"

    coords_out = existing_points
    new_coords = []

    existing_pts_index = set([to_str(x) for x in existing_points])

    if folium_output.get('all_drawings'):
        for obj in folium_output['all_drawings']:
            coords = obj['geometry']['coordinates']
            long = coords[0]
            lat = coords[1]

            if to_str((lat, long)) not in existing_pts_index:
                coords_out.append((lat, long))
                new_coords.append((lat, long))

    return new_coords #coords_out

def make_base_df(base_data):
    print("Making new dataframe")
    df = pd.DataFrame(base_data)
    df = df.rename(columns={
        'modified_latitude': 'Latitude',
        'modified_longitude': 'Longitude',
    })
    df = df[['Latitude', 'Longitude', 'name', 'fontsize', 'angle']]

    
    if 'active_row_series' not in st.session_state:
        df['Include'] = False
        st.session_state['active_row_series'] = df['Include'].to_list()
    else:
        df['Include'] = st.session_state['active_row_series']

    return df

def append_road_point(lat, long):
    
    st.session_state['config_data']['road_data'].append(
        {
            # These two will never change... coords of initial click on map
            'latitude': lat,
            'longitude': long,
            # Will be modified and plotted
            'modified_latitude': lat,
            'modified_longitude': long,
            'name': "1st st",
            'fontsize': 12,
            'angle': 0,
        }
    )

    st.session_state['active_row_series'].append(False)
    new_row_i = len(st.session_state['config_data']['road_data']) - 1
    st.session_state['checkbox_state'][new_row_i] = False

## Main Component function



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



    #print(folium_output)
    #new_points = process_folium_output(folium_output, map_pin_locations)

    #st.write(new_points)

    #st.write(folium_output)
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
