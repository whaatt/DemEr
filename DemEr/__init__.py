from flask import Flask, session, redirect, url_for
from flask.ext.session import Session #TODO: HTTPS
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(__name__)
title = 'ReMed' #provisional

#eventually will be Redis based here
app.config['SESSION_TYPE'] = 'filesystem'
Session(app) #initialize

#initialize mail
mail = Mail(app)

#canonical Flask way
import DemEr.views
import DemEr.API
