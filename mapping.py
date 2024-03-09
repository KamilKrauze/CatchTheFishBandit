import json
import folium

# Define JSON file
with open("HSBC_atms.json", "r") as json_file:

    # Convert JSON file to Python
    data = json.load(json_file)
    data = data['data'][0]['Brand']

    # initializing lists
    latitude = []
    longitude = []
    id = []
    street = []
    town = []
    postcode = []
    brand = []
    country = []
    languages = []
    services = []
    currencies = []

    # separating data into lists
    for i in data:
        for j in i['ATM']:
            id.append(j['Identification'])
            languages.append(j['SupportedLanguages'])
            services.append(j['ATMServices'])
            currencies.append(j['SupportedCurrencies'])
            brand.append(i['BrandName'])
            country.append(j['Location']['PostalAddress']['Country'])
            street.append(j['Location']['PostalAddress']['StreetName'])
            town.append(j['Location']['PostalAddress']['TownName'])
            latitude.append(j['Location']['PostalAddress']['GeoLocation']['GeographicCoordinates']['Latitude'])
            longitude.append(j['Location']['PostalAddress']['GeoLocation']['GeographicCoordinates']['Longitude'])
            postcode.append(j['Location']['PostalAddress']['PostCode'])

latitude = list(map(float, latitude))
longitude = list(map(float, longitude))

# removing extra fluff
sep = ','
for s in range(len(street)):
    street[s] = street[s].split(sep, 1)[0]

for t in range(len(town)):
    town[t] = town[t].split(sep, 1)[0]
    town[t] = town[t].title()

# making marker points list
marker_points = list(zip(latitude, longitude, brand, street, town, country, postcode, languages, currencies, services, id))

# getting current location
import geocoder
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