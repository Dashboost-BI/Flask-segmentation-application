from python.config import app
import simplejson as json 
from flask import render_template

@app.route('/')
def home():
    return render_template('home.html')
