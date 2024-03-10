
from geopy.geocoders import Nominatim
import pandas as pd
import requests
import folium
from folium import IFrame
import time

def get_location_coordinates(address):
   geolocator = Nominatim(user_agent="(mail@example.com)")
   location = geolocator.geocode(address)
   time.sleep(1)
   return location.latitude, location.longitude

def get_directions_response(address1, address2, mode='drive'):
   lat1, long1 = get_location_coordinates(address1)
   lat2, long2 = get_location_coordinates(address2)
   url = "https://route-and-directions.p.rapidapi.com/v1/routing"
   key = "0a4691d35dmshb7a10d79387befdp140ee4jsnfd9a573b3f96"
   host = "route-and-directions.p.rapidapi.com"
   headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
   querystring = {"waypoints":f"{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}","mode":mode}
   response = requests.request("GET", url, headers=headers, params=querystring)
   return response

response = get_directions_response("19 Brown Street, Dundee", "10 Downing Street, London")

def create_map(response):
   # use the response
   mls = response.json()['features'][0]['geometry']['coordinates']
   points = [(i[1], i[0]) for i in mls[0]]
   m = folium.Map()
   # add marker for the start and ending points
   for point in [points[0], points[-1]]:
     # read the content of popup.html
     with open('./templates/popup.html', 'r') as f:
        popup_html = f.read()
     # create an IFrame using the HTML content
     iframe = IFrame(html=popup_html, width=500, height=300)
     # create a Popup using the IFrame
     popup = folium.Popup(iframe, max_width=500)
     folium.Marker(
        location=point,
        popup=popup,
        tooltip='tooltip text'
     ).add_to(m)
   # add the lines
   folium.PolyLine(points, weight=5, opacity=1).add_to(m)
   # create optimal zoom
   df = pd.DataFrame(mls[0]).rename(columns={0:'Lon', 1:'Lat'})[['Lat', 'Lon']]
   sw = df[['Lat', 'Lon']].min().values.tolist()
   ne = df[['Lat', 'Lon']].max().values.tolist()
   m.fit_bounds([sw, ne])
   return m

m = create_map(response)
m.save('static/maps/map.html')
