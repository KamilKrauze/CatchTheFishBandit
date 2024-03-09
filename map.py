# import the folium, pandas libraries
import pandas as pd
import folium
import dijkstra 
from geopy.geocoders import ArcGIS
from geopy.geocoders import Nominatim
from geopy.distance import great_circle 
"""
import urllib2
import json


# Automatically geolocate the connecting IP
f = urllib2.urlopen('http://freegeoip.net/json/')
json_string = f.read()
f.close()
device_location = json.loads(json_string)
starting_coordinates = [device_location['langitude'], device_location['langitude']]
end_coordinates = starting_coordinates
distance = 0
"""

geolocator = Nominatim(user_agent="location_details")
location = geolocator.geocode("Edinburgh")

df_sites = pd.DataFrame(
    [['A24A0579',              52.926777, -1.215878],
     ['AH323609',              51.1488168, 0.8735929],
     ['AB421861',              52.9200018, -1.4757001]],
    columns=pd.Index(['Identification', 'Latitude', 'Longitude'], name='ATMs')
)

visited_atms = []

atm_distances = {}

"""
for atm_1 in df_sites.itertuples(): 
    if great_circle([device_location['langitude'], device_location['langitude']], [atm_1.Latitude, atm_1.Longitude]).km > distance:
        distance = great_circle([device_location['langitude'], device_location['langitude']], [atm_1.Latitude, atm_1.Longitude]).km 
        end_coordinates = [atm_1.Latitude, atm_1.Longitude]
    atm_distances[('start', atm_1.Identification)] = great_circle([device_location['langitude'], device_location['langitude']], [atm_1.Latitude, atm_1.Longitude]).km
    for atm_2 in df_sites.itertuples(): 
        if atm_1 != atm_2:
            atm_distances[atm_1.Identification, atm_2.Identification] = great_circle([atm_1.Latitude, atm_1.Longitude], [atm_2.Latitude, atm_2.Longitude]).km

"""
current_longitude = location.longitude
current_latitude = location.latitude

while len(visited_atms) < df_sites.shape[0]:
    current_distance = 10000000000
    temp_position = "start"
    temp_longitude = current_longitude
    temp_latitude = current_latitude 
    for atm_1 in df_sites.itertuples(): 
        if great_circle([current_latitude, current_longitude], [atm_1.Latitude, atm_1.Longitude]).km < current_distance and atm_1.Identification not in visited_atms:
            current_distance = great_circle([current_latitude, current_longitude], [atm_1.Latitude, atm_1.Longitude]).km
            temp_position = atm_1.Identification
            temp_location = [atm_1.Latitude, atm_1.Longitude]
    visited_atms.append(temp_position)
    current_longitude = temp_longitude
    current_latitude = temp_latitude


# initialize the map and store it in a m object
m = folium.Map(location = [location.latitude, location.longitude], zoom_start = 4)
 
for index, atm in enumerate(visited_atms): 
    curr_atm = df_sites[df_sites['Identification'] == atm]

    m.add_child(folium.Marker(location=[curr_atm.Latitude, curr_atm.Longitude],tooltip=atm,icon=folium.Icon(color='blue')))

    if index + 1 < len(visited_atms):
        # line for the route segment connecting current to next stop
        line = folium.PolyLine(
            locations=[(df_sites.iloc[index]["Latitude"], df_sites.iloc[index]["Longitude"]), (df_sites.iloc[index+1]["Latitude"], df_sites.iloc[index+1]["Longitude"])],
            tooltip=f"{atm} to {visited_atms[index+1]}",
        )

        line.add_to(m)

# show the map
m.save('my_map.html')