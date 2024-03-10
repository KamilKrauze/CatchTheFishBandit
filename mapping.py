import folium
import geocoder
import pandas as pd


# getting data from csv
marker_points = pd.read_csv('atms.csv', sep=',', header=0)
marker_points = marker_points.values.tolist()

# getting current location
location = geocoder.ip('me').latlng
city = geocoder.ip('me').city
country = geocoder.ip('me').country
#location = [51.496049, -0.123580] #london

# creating map
m = folium.Map(location, zoom_start=10)

# initializing location
popup = folium.Popup(
    html=city + ", " + country,
    max_width=500,
)
folium.Marker(
    location=location,
    tooltip="Current Location",
    popup=popup,
    icon=folium.Icon(color="blue"),
).add_to(m)

# creating location markers
for marker_point in marker_points:

    # stuff for gui
    languages = ", ".join(marker_point[7])
    languages = languages.upper()
    currencies = ", ".join(marker_point[8])
    services = ", ".join(marker_point[9])

    popup = folium.Popup(
        html="Bank: " + marker_point[2] + "<br>Address: " + marker_point[3] + ", " + marker_point[4] + ", " + marker_point[5] +
             "<br>Postcode: " + marker_point[6] + "<br>Id: " + marker_point[10],
        max_width=500,
    )
    if marker_point[10] != 'AB017276':
        folium.Marker(
            location=[marker_point[0], marker_point[1]],
            tooltip=marker_point[4] + ", " + marker_point[5],
            popup=popup,
            icon=folium.Icon(color="green"),
        ).add_to(m)
    else:
        folium.Marker(
            location=[marker_point[0], (-1)*marker_point[1]],
            tooltip=marker_point[4] + ", " + marker_point[5],
            popup=popup,
            icon=folium.Icon(color="green"),
        ).add_to(m)

m.save("index.html")