from flask import Flask, request, redirect, current_app
from flask_cors import CORS, cross_origin
import flask
from functools import wraps
from pymongo import MongoClient
import requests
import json
import time
import datetime

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods=['GET','POST'])
@cross_origin()
def homepage():
	
	return "hello"

if name == "__main__":
	app.run()