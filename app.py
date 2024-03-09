from flask import Flask, render_template, request
import requests
import json
from flask import Flask, render_template

app = Flask(__name__, static_folder='static')
app.debug = True

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/generate_map', methods=['GET', 'POST'])
def map():
    print('Request:', request.form)
    current_location = request.args.get('current_location')
    atm_id = request.args.get('atm_id') #lets assume this is the destination for now eg london
    print('Current Location:', current_location)
    print('ATM ID:', atm_id)
    return render_template('custom_map.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
