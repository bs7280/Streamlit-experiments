from streamlit_callbacks import callback_data_change, callback_move_coords
import streamlit as st
import pandas as pd
import folium

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

# TODO unused I think?
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
