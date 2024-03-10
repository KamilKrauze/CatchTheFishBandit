import json
from flask import Flask, jsonify, json
from flask_cors import CORS


# writing to json
app = Flask(__name__)
app.debug = True
CORS(app)

@app.route('/latlng')
def get_atm_latlng():

    with open("home/HSBC_atms.json") as json_file:

        # Convert JSON file to Python
        data = json.load(json_file)
        data = data['data'][0]['Brand']

        # initializing lists
        latitude = []
        longitude = []
        id = []

        # separating data into lists
        for i in data:
            for j in i['ATM']:
                id.append(j['Identification'])
                latitude.append(j['Location']['PostalAddress']['GeoLocation']['GeographicCoordinates']['Latitude'])
                longitude.append(j['Location']['PostalAddress']['GeoLocation']['GeographicCoordinates']['Longitude'])

        points = []
        for i in range(len(latitude)):
            if id[i] == 'AB017276':
                longitude[i] = (-1)*longitude[i]
            points.append({'id': id[i], 'lats':latitude[i], 'longs': longitude[i]})

        return jsonify({'ATMs': points})

@app.route('/')
def get_atms():
    # Define JSON file
    with open("home/HSBC_atms.json") as json_file:

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
        if id[i] == 'AB017276':
            longitude[i] = (-1)*longitude[i]
        marker_points.append({'Latitude': latitude[i], 'Longitude': longitude[i], 'Brand': brand[i], 'Street': street[i],
                            'Town': town[i], 'Country': country[i], 'PostCode': postcode[i], 'SupportedLanguages': languages[i],
                            'SupportedCurrency': currencies[i], 'ATMServices': services[i], 'ID': id[i]})

    return jsonify({'ATMs': marker_points})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
