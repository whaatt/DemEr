from flask import render_template as template
from flask import session, redirect, url_for

from DemEr import app, title
import helpers

@app.route('/')
def index():
    if 'user' in session: #logged in
        return redirect('/dashboard')
    return template('index.html',
                    title = title)

@app.route('/dashboard')
def dashboard():
    #user is logged out now
    if 'user' not in session:
        return redirect('/')
    
    patients = helpers.getPatientData()
    doctors = [i for i in helpers.getDoctorData()
        if i['email'] != session['user']['email']] #you
    approved = [i for i in doctors if i['approved']]
    pending = [i for i in doctors if not i['approved']]
    
    return template('dashboard.html', #filled in below
                    clinic = session['user']['clinicName'],
                    code = session['user']['clinicCode'],
                    first = session['user']['first'],
                    owner = session['user']['owner'],
                    last = session['user']['last'],
                    patients = patients,
                    approved = approved,
                    pending = pending,
                    title = title)

@app.route('/confirmation/<ID>')
def confirmation(ID):
    worked, ownership, clinic = helpers.confirmUser(ID)
    return template('confirmation.html',
                    title = title, worked = worked,
                    ownership = ownership, clinic = clinic,)
