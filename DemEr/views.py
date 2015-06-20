from flask import render_template as template
from flask import session, redirect, url_for

from DemEr import app
import helpers

@app.route('/')
def index():
    if 'username' in session: return redirect('/dashboard')
    else: return template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect('/')
    patients = helpers.getPatientData()
    doctors = helpers.getDoctorData()
    return template('dashboard.html', #filled in
                    clinic = session['clinic'],
                    code = session['code'],
                    patients = patients,
                    doctors = doctors)

@app.route('/confirmation/<ID>')
def confirmation(ID):
    worked, owner = helpers.confirmUser(ID)
    return template('confirmation.html',
                    worked = worked,
                    owner = owner)
