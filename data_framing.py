import json
from flask import Flask, jsonify, json
from flask_cors import CORS


# writing to json
app = Flask(__name__)
app.debug = True
CORS(app)

POINTS = []

def load_json_to_mem() -> None:
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
    for i in range(len(latitude)):
        if id[i] == 'AB017276':
            longitude[i] = (-1)*longitude[i]
        POINTS.append({'Latitude': latitude[i], 'Longitude': longitude[i], 'Brand': brand[i], 'Street': street[i],
                        'Town': town[i], 'Country': country[i], 'PostCode': postcode[i], 'SupportedLanguages': languages[i],
                        'SupportedCurrency': currencies[i], 'ATMServices': services[i], 'ID': id[i]})



@app.route('/latlng')
def get_atm_latlng():



    # initializing lists
    id = []
    latitude = []
    longitude = []
    # separating data into lists
    for pt in POINTS:
        id.append(pt['ID'])
        latitude.append(pt['Latitude'])
        longitude.append(pt['Longitude'])

    # for i in range(len(latitude)):
    #     if id[i] == 'AB017276':
    #         longitude[i] = (-1)*longitude[i]
    #     point.append({'id': id[i], 'lats':latitude[i], 'longs': longitude[i]})

    data = []
    for i in range(len(latitude)):
        data.append({'id':id[i], 'lats':latitude[i], 'longs': longitude[i]})

    return jsonify({'ATMs': data})

@app.route('/')
def get_atms():
    return jsonify({'ATMs': POINTS})


if __name__ == '__main__':
    load_json_to_mem()
    app.run(host="0.0.0.0", port=80)
