from python.config import app
import simplejson as json 
from flask import render_template, request, session
import pandas as pd
from io import StringIO

@app.route('/file', methods=['POST', 'GET'])
def file():
    rawFile = request.files['file']
    df = pd.read_csv(StringIO(rawFile.read().decode('utf-8')))
    jsonDf = df.to_json()
    df = df.iloc[:5]
    rawColumns = list(df.columns)
    if len(rawColumns)>3:
        columns = rawColumns[:3]
        columns.append('...')
    data = []
    for i in range(len(df)):
        row = df.iloc[i].values.tolist()
        if len(row)>3:
            row = row[:3]
            row.append('...')
        data.append(row)
    return render_template('file.html', columns = columns, rawColumns=rawColumns, data = data, jsonDf=jsonDf)
