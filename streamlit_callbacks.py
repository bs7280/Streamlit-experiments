import streamlit as st
from utils import move_coordinates

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
