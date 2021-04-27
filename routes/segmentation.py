from python.config import app
import simplejson as json 
from flask import render_template, request, session
import pandas as pd
from io import StringIO
from controllers.segmentation import segmentation

@app.route('/segmentation', methods=["POST", "GET"])
def dashboard():
    if request.method == 'POST':
        indexCol = request.form.get('index_col')
        mainCol = request.form.get('main_col')
        jsonDf = request.form.get('jsonDf')
        df = pd.read_json(jsonDf)
        results = segmentation(df, mainCol, indexCol)
        session['results'] = results
    else:
        results = session['results']
    df = results['df']
    histogramCols = results['features']
    plots = results['plots']
    results = results['results']
    return render_template('dashboard.html', results=results, df=df, plots=plots, histogramCols=histogramCols)
