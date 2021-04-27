from flask import Flask, request, make_response

# init app.
application = app = Flask(__name__, template_folder='../templates')
app.secret_key = 'BAD_SECRET_KEY'
