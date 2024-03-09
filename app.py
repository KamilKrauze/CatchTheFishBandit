import requests
import json
from flask import Flask

app = Flask(__name__)
app.debug = True

@app.route('/')
def home_page():
    return '<h1>Hello world!</h1>'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)