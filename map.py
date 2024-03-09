# import the folium, pandas libraries
import pandas as pd
import folium
import geocoder
from geopy.distance import great_circle 
import requests
import json

def get_directions_response(lat1, long1, lat2, long2, mode='drive'):
   url = "https://api.openrouteservice.org/v2/directions/driving-car"
   key = "5b3ce3597851110001cf62481da466da01ce401fb67b1356de21d338"
   params = {"api_key": key, "start": str(long1) + "," + str(lat1), "end": str(long2) + "," + str(lat2)}
   response = requests.get(url, params=params)
   data = json.loads(response.text)
   mls = data['features'][0]['geometry']['coordinates']
   points = [t[::-1] for t in mls]

   return points

location = geocoder.ip("me").latlng

df_sites = pd.DataFrame(
    [['A24A0579',              52.926777, -1.215878],
     ['AH323609',              51.1488168, 0.8735929],
     ['AB421861',              52.9200018, -1.4757001],
     ['AE540873',              53.2274933, -4.1245217],
     ['AD003631',              50.8551456, 0.5774327]],
    columns=pd.Index(['Identification', 'Latitude', 'Longitude'], name='ATMs')
)

visited_atms = []

atm_distances = {}

current_longitude = location[1]
current_latitude = location[0]

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
m = folium.Map(location = [location[0], location[1]], zoom_start = 10)
 
m.add_child(folium.Marker(location=[location[0], location[1]],tooltip="Current location",icon=folium.Icon(color='red')))
first_line = folium.PolyLine(
    locations=[(location[0], location[1]), (df_sites[df_sites.Identification==visited_atms[0]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[0]].Longitude.item())], 
    tooltip=f"{'Current location'} to {visited_atms[0]}",
)

folium.PolyLine(get_directions_response(location[0], location[1], df_sites[df_sites.Identification==visited_atms[0]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[0]].Longitude.item())).add_to(m) 

for index, atm in enumerate(visited_atms): 
    curr_atm = df_sites[df_sites['Identification'] == atm]

    m.add_child(folium.Marker(location=[curr_atm.Latitude, curr_atm.Longitude],tooltip=atm,icon=folium.Icon(color='blue')))

    if index + 1 < len(visited_atms):
        folium.PolyLine(get_directions_response(df_sites[df_sites.Identification==atm].Latitude.item(), df_sites[df_sites.Identification==atm].Longitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Longitude.item())).add_to(m) 
        

# show the map
m.save('my_map.html')