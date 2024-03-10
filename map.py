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

app = Flask(__name__, template_folder="templates")

def load_atms():
    url = "http://geodata-api.quack-team.com/"
    response = requests.get(url)
    df = pd.DataFrame(columns=pd.Index(['Identification', 'Latitude', 'Longitude', 'Brand', 'Address', 'Services', 'Languages', 'Currencies'], name='ATMs'))
    loc = 0

    if response.status_code == 200:
        data = json.loads(response.text)   
        atms = data['ATMs']

        for atm in atms:
            services = ','.join(atm['ATMServices'])
            languages = ','.join(atm['SupportedLanguages'])
            currencies = ','.join(atm['SupportedCurrency'])
            df.loc[loc] = [atm['ID'], atm['Latitude'], atm['Longitude'], atm['Brand'], atm['Street'] + ', ' + atm['PostCode'] + ', '  + atm['Town'] + ', ' + atm['Country'], services, languages, currencies]
            loc += 1

    return df

df_sites = load_atms()

geolocator = Photon(user_agent="measurements")

distance = 0
duration = 0

def get_directions_response(lat1, long1, lat2, long2):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    key = "5b3ce3597851110001cf62487cb2a27671a54cb8856efc18b1f4874d"
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
    key = "5b3ce3597851110001cf62487cb2a27671a54cb8856efc18b1f4874d"
    params = {"api_key": key, "start": str(long1) + "," + str(lat1), "end": str(long2) + "," + str(lat2)}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        travel_data = data["features"][0]["properties"]["segments"][0]

        return travel_data["duration"]
    else:
        return 0

def get_popup(atmid): 
    html = '''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
                <title>ATM Data</title>
            </head>
            <body class="bg-gray-200 p-6">
                <div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl">
                    <div class="md:flex">
                        <div class="p-8">
                            <div class="uppercase tracking-wide text-sm text-indigo-500 font-semibold">ATM Identification: '''+atmid+'''</div>
                            <p class="text-black font-bold">Supported Languages: <span class="text-gray-500 text-sm">'''+df_sites[df_sites.Identification==atmid].Languages.item()+'''</span></p>
                            <p class="text-black font-bold">ATM Services: <span class="text-gray-500 text-sm">'''+df_sites[df_sites.Identification==atmid].Services.item()+'''</span></p>
                            <p class="text-black font-bold">Supported Currencies: <span class="text-gray-500 text-sm" >'''+df_sites[df_sites.Identification==atmid].Currencies.item()+'''</span> </p>
                            <p class="text-black font-bold">Branch Identification: <span class="text-gray-500 text-sm">'''+df_sites[df_sites.Identification==atmid].Brand.item()+'''</span></p>
                            <p class="text-black font-bold">Location: <span class="text-gray-500 text-sm">'''+df_sites[df_sites.Identification==atmid].Address.item()+'''</span></p>
                            <p class="text-black font-bold">GeoLocation: <span class="text-gray-500 text-sm">Latitude:''' + str(df_sites[df_sites.Identification==atmid].Latitude.item()) + ''', Longitude:''' + str(df_sites[df_sites.Identification==atmid].Longitude.item()) +'''</span></p>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        '''
    return html

def create_map(location, limit):
    global distance
    global duration
    visited_atms = []

    current_longitude = location[1]
    current_latitude = location[0]
    

    while len(visited_atms) <= int(limit) and len(visited_atms) < df_sites.shape[0]:
        current_distance = 10000000000
        temp_position = "start"
        temp_longitude = current_longitude
        temp_latitude = current_latitude 
        for atm_1 in df_sites.itertuples(): 
            this_distance = great_circle([current_latitude, current_longitude], [atm_1.Latitude, atm_1.Longitude]).km
            if this_distance < current_distance and atm_1.Identification not in visited_atms:
                current_distance = this_distance
                temp_position = atm_1.Identification
                temp_latitude = atm_1.Latitude
                temp_longitude = atm_1.Longitude
        visited_atms.append(temp_position)
        current_longitude = temp_longitude
        current_latitude = temp_latitude
        distance += current_distance


    # initialize the map and store it in a m object
    m = folium.Map(location = [location[0], location[1]], zoom_start = 10)
    
    folium.Marker(location=[location[0], location[1]],tooltip="Current location",icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine(get_directions_response(location[0], location[1], df_sites[df_sites.Identification==visited_atms[0]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[0]].Longitude.item())).add_to(m) 
    duration += get_duration(location[0], location[1], df_sites[df_sites.Identification==visited_atms[0]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[0]].Longitude.item())

    for index, atm in enumerate(visited_atms): 
        curr_atm = df_sites[df_sites['Identification'] == atm]
        popup_html = get_popup(atm)
        # create an IFrame using the HTML content
        iframe = IFrame(html=popup_html, width=500, height=300)
        # create a Popup using the IFrame
        popup = folium.Popup(iframe, max_width=500)
        folium.Marker(location=[curr_atm.Latitude, curr_atm.Longitude],popup=popup,tooltip=atm,icon=folium.Icon(color='blue')).add_to(m)

        if index + 1 < len(visited_atms):
            folium.PolyLine(get_directions_response(df_sites[df_sites.Identification==atm].Latitude.item(), df_sites[df_sites.Identification==atm].Longitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Longitude.item())).add_to(m) 
            duration += get_duration(df_sites[df_sites.Identification==atm].Latitude.item(), df_sites[df_sites.Identification==atm].Longitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Latitude.item(), df_sites[df_sites.Identification==visited_atms[index+1]].Longitude.item())
    
    folium.map.Marker((location[0]+0.1, location[1]-0.1),
        icon=DivIcon(html='<div style="background-color: #EBEBEB; width:200px;"><div style="font-size: 10pt">Total distance: ' + str(round(distance)) + 'km</div><div style="font-size: 10pt">Total duration: ' + str(round(duration/60)) + 'h</div></div>'),
        icon_size=(100, 100),
        icon_anchor=(0, 0)
        ).add_to(m)

    return m.get_root().render()

@app.route('/id/<atmid>/<limit>')
def atmid_search(atmid, limit):
    return create_map([df_sites[df_sites.Identification==atmid].Latitude.item(), df_sites[df_sites.Identification==atmid].Longitude.item()], limit)

@app.route('/id/<atmid>/<limit>/distanceandduration')
def atmid_dump(atmid, limit):
    create_map([df_sites[df_sites.Identification==atmid].Latitude.item(), df_sites[df_sites.Identification==atmid].Longitude.item()], limit)
    return json.dumps('distance: ' + str(distance) + 'duration: ' + str(duration))

@app.route('/address/<address>/<limit>')
def addr_search(address, limit):
    location = geolocator.geocode(address)
    return create_map([location.latitude, location.longitude], limit)

@app.route('/address/<address>/<limit>/distanceandduration')
def addr_dump(address, limit):
    location = geolocator.geocode(address)
    create_map([location.latitude, location.longitude], limit)
    return json.dumps('distance: ' + str(distance) + 'duration: ' + str(duration))

@app.route('/<limit>')
def home(limit):
    return create_map(geocoder.ip("me").latlng, limit)

@app.route('/<limit>/distanceandduration')
def home_dump(limit):
    create_map(geocoder.ip("me").latlng, limit) 
    return json.dumps('distance: ' + str(distance) + 'duration: ' + str(duration))

if __name__ == '__main__':
    app.run(port=80, host="0.0.0.0", debug=True)