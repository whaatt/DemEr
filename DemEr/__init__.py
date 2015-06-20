from flask import Flask, session, redirect, url_for
from flask.ext.session import Session #TODO: HTTPS

app = Flask(__name__)
app.config.from_object(__name__)

#eventually will be Redis here
SESSION_TYPE = 'filesystem'
Session(app) #initialize
session['user'] = None

#canonical Flask way
import DemEr.views
import DemEr.API
