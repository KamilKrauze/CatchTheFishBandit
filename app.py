import requests
import json
from flask import Flask, render_template

app = Flask(__name__, static_folder='static/css')
app.debug = True

@app.route('/')
def home():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
