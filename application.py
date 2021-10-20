import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime
from dateutil.relativedelta import relativedelta

@st.cache(allow_output_mutation=True)
def getDatasets():
    url = "https://data.wprdc.org/datastore/dump/00eb9600-69b5-4f11-b20a-8c8ddd8cfe7a"
    otp_dataset = pd.read_csv(url)
    url = "https://data.wprdc.org/dataset/ece64ad3-05eb-46dd-ba38-c83b5373812f/resource/3f40b94b-4ac4-48f1-8c61-8439d2d2f420/download/wprdc_stop_data.csv"
    stops_dataset = pd.read_csv(url)

    return otp_dataset, stops_dataset

def filterDatasets(dataframe, column, values):
    if type(values) == type([]):
        filtered = dataframe[dataframe[column].isin(values)]
        return filtered
    if type(values) == type(datetime.now()):
        filtered = dataframe[pd.to_datetime(dataframe[column])>values]
        return filtered

with st.spinner('Bringing you awesome...'):
    otp_dataset, stops_dataset = getDatasets()

# introduction page
def introduction(otp_dataset, stops_dataset):
    st.title('Introduction')

# geographic distribution page
def geographic_distribution(otp_dataset, stops_dataset):
    st.title('Geographic distribution of OTP')

    st.header('Filter the data')

    # Filter the otp data
    otp_dataset = otp_dataset[otp_dataset['on_time_percent']>0]

    dayFilter = st.multiselect('1. Day of Week',['WEEKDAY', 'SAT.', 'SUN.'])
    if not dayFilter:
        dayFilter = ['WEEKDAY', 'SAT.', 'SUN.']
    otp_dataset_filtered = filterDatasets(otp_dataset, 'day_type', dayFilter)
    otp_dataset_filtered['day_weight'] = otp_dataset_filtered.apply(lambda row: 5 if row['day_type'] == 'WEEKDAY' else 1, axis = 1)
    otp_dataset_filtered['otp(weighted)'] = otp_dataset_filtered['day_weight'] * otp_dataset_filtered['on_time_percent']

    garages = ['Ross', 'Collier', 'East Liberty', 'East Liberty/West Mifflin']
    garageFilter = st.multiselect('2. Garage', garages)
    if not garageFilter:
        garageFilter = garages
    otp_dataset_filtered = filterDatasets(otp_dataset_filtered, 'current_garage', garageFilter)
    
    timeDuration = st.selectbox('3. How recent data do you want to consider?', ('All time', 'Last 9 months', 'Last 12 months', 'Last 18 months'))
    if timeDuration != 'All time':
        months = int(timeDuration.split(' ')[1])
        otp_dataset_filtered = filterDatasets(otp_dataset_filtered, 'month_start', datetime.now() - relativedelta(months=months))

    # filter the stops data
    stops = stops_dataset.drop_duplicates('stop_name')[['stop_name', 'latitude', 'longitude', 'routes_ser']]
    stops['routes'] = stops.apply(lambda x: x['routes_ser'].split(','), axis=1)
    exploded_stops = stops.explode('routes').set_index('routes').drop(columns = ['routes_ser'])
    
    # weight the rows of otp dataset (for weekdays vs weekends)
    a = otp_dataset_filtered[['route','otp(weighted)', 'day_weight']].groupby(by = ['route']).aggregate(np.sum).reset_index()
    a['on_time_percent'] = a['otp(weighted)']/a['day_weight']
    a = a.set_index('route')
    a = a.drop(columns = ['otp(weighted)', 'day_weight'])
    
    # combine datasets
    merged_df = a.join(exploded_stops)
    otp_by_stop = merged_df.groupby(by=['stop_name', 'latitude', 'longitude']).aggregate(np.mean).reset_index()

    # plot the otp by stop dataset
    st.header('The distribution')
    elevation = 10
    garage_locations = pd.DataFrame([['Ross', 40.500564, -80.021977, elevation], ['East Liberty', 40.457482, -79.914569, elevation], ['Collier',40.367203,-80.101355, elevation], ['West Mifflin',40.362506,-79.931848,elevation]], columns = ['Garage', 'latitude', 'longitude', 'elevation'])
    st.write(pdk.Deck
        (
            map_style = "mapbox://styles/mapbox/dark-v9",
            map_provider="mapbox",
            api_keys={'mapbox': 'sk.eyJ1IjoiamF5YW50c3JhdmFuIiwiYSI6ImNrdXZkNXExYzRibG4ycG14Z2F1cm51bm0ifQ.RrWvP4I6NbRpVyQ5fZfTTg'},
            initial_view_state = pdk.ViewState(
                latitude = 40.443903,
                longitude = -79.950834,
                zoom = 9.5,
                pitch = 40
            ),
            layers = [
                pdk.Layer(
                    "HexagonLayer",
                    data = otp_by_stop,
                    pickable = True,
                    extruded = True,
                    get_position = ['longitude', 'latitude'],
                    get_weight = "on_time_percent",
                    cell_size = 400,
                    elevation_scale = 10,
                    opacity = 0.7
                ),
                pdk.Layer(
                    "ColumnLayer",
                    data = garage_locations,
                    pickable = True,
                    extruded = True,
                    get_position = ['longitude', 'latitude'],
                    get_weight = "elevation",
                    radius = 500,
                    elevation_scale = 15
                )
            ]
        )
    )
    f"**Fig 1:** *Geographic Distribution of OTP in Pittsburgh city during {', '.join(dayFilter)} \
        for {', '.join(garages)} garages (resresented as black bars) in {timeDuration.lower()}.*"

    showDistributionData = st.checkbox("Show Data")
    if showDistributionData:
        otp_by_stop = otp_by_stop.set_index('stop_name')
        otp_by_stop

# time distribution page
def time_distribution(otp_dataset, stops_dataset):
    st.title('Time distribution of OTP')

    st.header('Filter the data')

    otp_dataset = otp_dataset[otp_dataset['on_time_percent']>0]
    otp_dataset_filtered = otp_dataset.copy()
    otp_dataset_filtered['month_start'] = pd.to_datetime(otp_dataset_filtered['month_start'], infer_datetime_format=True)

    # Filter the data and sort based on perspectives
    perspectives = ['Routes', 'Weekday/Weekends', 'Garages']
    perspective = st.selectbox("Pick your perspective", perspectives)

    # create pandas dataframe with week data as columns
    def create_and_render_chart(otp_dataset_filtered, column, values):
        list_of_series = []
        values = list(values)
        if values.count(np.nan):
            values.remove(np.nan)
        for value in values:
            a = otp_dataset_filtered[otp_dataset_filtered[column] == value][['on_time_percent', 'month_start']].groupby(by = 'month_start').aggregate(np.mean).rename(columns = {'on_time_percent':value})
            list_of_series.append(a)
        day_wise_data = pd.concat(list_of_series, axis = 1)
        st.header('The time distribution')
        st.line_chart(day_wise_data)
        f"**Fig 2:** *Time Distribution of OTP in Pittsburgh city for {', '.join(values)}.*"
        showData = st.checkbox("Show Data")
        if showData:
            day_wise_data
    
    # act based on the choice made
    if perspective == perspectives[0]:
        column_values = list(otp_dataset_filtered['route'].unique())
        if column_values.count(np.nan):
            column_values.remove(np.nan)
        routes = st.multiselect('Select 1-5 routes', column_values)
        route_len = len(routes)
        if route_len<1 or route_len>5:
            # error message
            st.warning(f"Select any number of routes between 1 and 5. There are {int(route_len)} routes are currently selected.")
        else:
            create_and_render_chart(otp_dataset_filtered, 'route', routes)
    elif perspective == perspectives[1]:
        column_values = otp_dataset_filtered['day_type'].unique()
        create_and_render_chart(otp_dataset_filtered, 'day_type', column_values)
    elif perspective == perspectives[2]:
        column_values = otp_dataset_filtered['current_garage'].unique()
        create_and_render_chart(otp_dataset_filtered, 'current_garage', column_values)

# Sidebar and navigation
st.sidebar.title('Navigation')
pages = ['Introduction', 'Geographic distribution of OTP', 'Time distribution of OTP']
page = st.sidebar.radio('Go to:', pages)
if page == pages[0]:
    introduction(otp_dataset, stops_dataset)
elif page == pages[1]:
    geographic_distribution(otp_dataset, stops_dataset)
elif page == pages[2]:
    time_distribution(otp_dataset, stops_dataset)