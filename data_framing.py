import json
import pandas as pd
from flask import Flask, jsonify, request

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
marker_points = []
for i in range(len(latitude)):
    marker_points.append({'Latitude': latitude[i], 'Longitude': longitude[i], 'Brand': brand[i], 'Street': street[i],
                          'Town': town[i], 'Country': country[i], 'PostCode': postcode[i], 'SupportedLanguages': languages[i],
                          'SupportedCurrency': currencies[i], 'ATMServices': services[i], 'ID': id[i]})

# writing to json
app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_atms():
    if request.method == 'GET':
        return jsonify({'ATMs': marker_points})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)

# writing to csv
#markers = pd.DataFrame(marker_points, columns=['Latitude', 'Longitude', 'Brand', 'Street', 'Town', 'Country', 'PostCode',
                                               #'SupportedLanguages', "SupportedCurrency", "ATMServices", "ID"])
#markers.to_csv('atms.csv', index=False)