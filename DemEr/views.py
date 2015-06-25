from flask import render_template as template
from flask import session, redirect, url_for

from DemEr import app
import helpers

@app.route('/')
def index():
    if 'user' in session: #logged in
        return redirect('/dashboard')
    return template('index.html')

@app.route('/dashboard')
def dashboard():
    #user is logged out now
    if 'user' not in session:
        return redirect('/')
    
    patients = helpers.getPatientData()
    doctors = helpers.getDoctorData()
    return template('dashboard.html', #filled in
                    clinic = session['user']['clinic'],
                    patients = patients,
                    doctors = doctors)

@app.route('/confirmation/<ID>')
def confirmation(ID):
    worked, clinic, ownership = helpers.confirmUser(ID)
    return template('confirmation.html', worked = worked,
                    clinic = clinic, ownership = ownership)
