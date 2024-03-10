# path: app.py
from flask import Flask, render_template, request, jsonify
import requests
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_folder='static', template_folder='templates')
debug = True
CORS(app, resources={r"/*": {"origins": "*"}})

def get_map_from_cloud(atm_id):
    # Make a GET request to the cloud server
    url = f"http://34.79.39.138/{atm_id}"
    # url = f"http://route.quack-team.com/{atm_id}/"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the response text (HTML) into a new file
        with open('static/maps/map.html', 'w') as f:
            f.write(response.text)
    else:
        print(f"Request failed with status code {response.status_code}")

def geo_data_from_cloud():
    # Make a GET request to the cloud server
    url = "http://35.233.66.213/"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response text as JSON
        data = response.json()
        return jsonify(data)  # Wrap the data in jsonify to include CORS headers
    else:
        print(f"Request failed with status code {response.status_code}")
        return jsonify({"error": "Request failed"}), 500

def get_distance_and_time(numofatms):
    url = f"http://34.79.39.138/{numofatms}/distanceandduration"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        return jsonify({"error": "Request failed"}), 500

# get_distance_and_time(10)
@app.route('/geo_data', methods=['GET', 'POST'])
@cross_origin()
def geo_data():
    data = geo_data_from_cloud()
    print('Data:', data)
    return data

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/generate_map', methods=['GET', 'POST'])
def map():
    print('Request:', request.form)
    current_location = request.args.get('current_location')
    atm_id = request.args.get('atm_id')
    get_map_from_cloud(atm_id)
    data = get_distance_and_time(atm_id)
    print('Data:', data)
    return render_template('custom_map.html', data=data)

@app.route('/generate_map', methods=['GET', 'POST'])
def map():
    print('Request:', request.form)
    current_location = request.args.get('current_location')
    atm_id = request.args.get('atm_id')
    get_map_from_cloud(atm_id)
    data = get_distance_and_time(atm_id)
    print('Data:', data)
    return render_template('custom_map.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
