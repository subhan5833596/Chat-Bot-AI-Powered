import flask
from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/status')
def status():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)