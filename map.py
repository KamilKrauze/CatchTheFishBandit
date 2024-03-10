# import the folium, pandas libraries
import pandas as pd
from folium.features import DivIcon
import folium
import geocoder
from geopy.distance import great_circle 
import requests
import json
from flask import Flask
from geopy.geocoders import Photon
from folium import IFrame

app = Flask(__name__)

df_sites = pd.DataFrame(
        [['A24A0579',              52.926777, -1.215878],
        ['AH323609',              51.1488168, 0.8735929],
        ['AB421861',              52.9200018, -1.4757001],
        ['AE540873',              53.2274933, -4.1245217],
        ['AD003631',              50.8551456, 0.5774327]],
        columns=pd.Index(['Identification', 'Latitude', 'Longitude'], name='ATMs')
    )

geolocator = Photon(user_agent="measurements")

distance = 0
duration = 0

def get_directions_response(lat1, long1, lat2, long2):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    key = "5b3ce3597851110001cf62481da466da01ce401fb67b1356de21d338"
    params = {"api_key": key, "start": str(long1) + "," + str(lat1), "end": str(long2) + "," + str(lat2)}
    response = requests.get(url, params=params)
    points = [(lat2, long2)]

    if response.status_code == 200:
        data = json.loads(response.text)
        mls = data['features'][0]['geometry']['coordinates']
        points = [t[::-1] for t in mls]

    return points

def get_duration(lat1, long1, lat2, long2):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    key = "5b3ce3597851110001cf62481da466da01ce401fb67b1356de21d338"
    params = {"api_key": key, "start": str(long1) + "," + str(lat1), "end": str(long2) + "," + str(lat2)}
    response = requests.get(url, params=params)
    time_traveled = 0

    if response.status_code == 200:
        data = json.loads(response.text)
        time_traveled = data["features"][0]["properties"]["segments"][0]["duration"]

    return time_traveled

def create_map(location):
    global distance
    global duration
    visited_atms = []

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
        distance += current_distance


    # initialize the map and store it in a m object
    m = folium.Map(location = [location[0], location[1]], zoom_start = 10)
    
    m.add_child(folium.Marker(location=[location[0], location[1]],tooltip="Current location",icon=folium.Icon(color='red')))
    folium.PolyLine(get_directions_response(location[0], location[1], df_sites[df_sites.Identification==visited_atms[0]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[0]].Longitude.item())).add_to(m) 
    duration += get_duration(location[0], location[1], df_sites[df_sites.Identification==visited_atms[0]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[0]].Longitude.item())

    for index, atm in enumerate(visited_atms): 
        curr_atm = df_sites[df_sites['Identification'] == atm]

        with open('home/popup.html', 'r') as f:
            popup_html = f.read()
        # create an IFrame using the HTML content
        iframe = IFrame(html=popup_html, width=500, height=300)
        # create a Popup using the IFrame
        popup = folium.Popup(iframe, max_width=500)
        m.add_child(folium.Marker(location=[curr_atm.Latitude, curr_atm.Longitude],popup=popup,tooltip=atm,icon=folium.Icon(color='blue')))

        if index + 1 < len(visited_atms):
            folium.PolyLine(get_directions_response(df_sites[df_sites.Identification==atm].Latitude.item(), df_sites[df_sites.Identification==atm].Longitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Longitude.item())).add_to(m) 
            duration += get_duration(df_sites[df_sites.Identification==atm].Latitude.item(), df_sites[df_sites.Identification==atm].Longitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Longitude.item())
    
    return m.get_root().render()

@app.route('/id/<atmid>')
def atmid_search(atmid):
    return create_map([df_sites[df_sites.Identification==atmid].Latitude.item(), df_sites[df_sites.Identification==atmid].Longitude.item()])

@app.route('/id/<atmid>/distanceandduration')
def atmid_dump(atmid):
    create_map([df_sites[df_sites.Identification==atmid].Latitude.item(), df_sites[df_sites.Identification==atmid].Longitude.item()])
    return json.dumps('distance: ' + str(distance) + 'duration: ' + str(duration))

@app.route('/address/<address>')
def addr_search(address):
    location = geolocator.geocode(address)
    return create_map([location.latitude, location.longitude])

@app.route('/address/<address>/distanceandduration')
def addr_dump(address):
    location = geolocator.geocode(address)
    create_map([location.latitude, location.longitude])
    return json.dumps('distance: ' + str(distance) + 'duration: ' + str(duration))

@app.route('/')
def home():
    return create_map(geocoder.ip("me").latlng)

@app.route('/distanceandduration')
def home_dump():
    create_map(geocoder.ip("me").latlng) 
    return json.dumps('distance: ' + str(distance) + 'duration: ' + str(duration))

if __name__ == '__main__':
    app.run(port=80, host="0.0.0.0", debug=True)