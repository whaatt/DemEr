#this file defines AJAX routes and validates shit
from flask import session, redirect, url_for, request, jsonify

from DemEr import app
import helpers
import re

#this file is particularly ugly, but it mostly just validates
#user API requests, dispatches them to the correct helper, and
#returns the appropriate response. validation is a real PITA

def isString(param): #parameter validation
    return isinstance(param, (str, unicode))

def clean(params, include):
    #filter dictionary keys using the passed array of includes
    return {k : v for k, v in params.items() if k in include}

def error(message):
    err = {'success' : False, 'error' : message}
    return jsonify(err) #sets mimetype correctly

def success(data):
    resp = {'success' : True, 'data' : data}
    return jsonify(resp) #sets mimetype correctly

#right now we only validate the input parameters but in the
#future we might want to move permissions validation to the
#API itself. cannot think of compelling arguments for either
    
@app.route('/api/clinic/<ID>')
def getClinicName(ID): #AJAX registration helper
    worked = helpers.getClinicName(ID) #None or clinic name
    if not worked: return error('No clinic found.')
    return success(worked)

#not user agnostic, so weird but this makes
#for the cleanest code at this point in time
@app.route('/api/clinic', methods = ['PUT'])
def editClinicName():
    params = request.get_json(force = True)
    if 'group' not in params:
        error('You must provide a new clinic name.')
    if not isString(params['group']) or not (4 <= len(params['group']) <= 40):
        return error('Your group name had an invalid length.')
    
    worked = helpers.editClinicName(params['group'])
    if not worked: return error('Incorrect permissions.')
    return success(worked)

@app.route('/api/user/create', methods = ['POST'])
def register(): #AJAX user sign up
    params = request.get_json(force = True)
    if ('email' not in params or 'password' not in params or
       'first' not in params or 'last' not in params or not
       (('group' not in params) ^ ('code' not in params))):
        return error('You must fill out all required fields.')
    if not isString(params['password']) or not (8 <= len(params['password']) <= 40):
        return error('Your password had an invalid length.')
    if not isString(params['first']) or not (2 <= len(params['first']) <= 30):
        return error('Your first name had an invalid length.')
    if not isString(params['last']) or not (2 <= len(params['last']) <= 30):
        return error('Your last name had an invalid length.')
    if not isString(params['email']) or not (6 <= len(params['email']) <= 50):
        return error('Your email had an invalid length.')
    if 'group' in params and (not isString(params['group'])
        or not (4 <= len(params['group']) <= 40)):
        return error('Your group name had an invalid length.')
    
    group = None
    code = None
    
    #TODO: do we want to validate emails server-side?
    if 'group' in params: group = params['group']
    if 'code' in params: code = params['code']
    
    #remove any invalid parameters quietly before we add to DB
    params = clean(params, ['email', 'password', 'first', 'last'])
    
    if group:
        worked = helpers.createUser(params, group = group) #new group
        if not worked: return error('Duplicate email or group.')
        return success(None)
        
    elif code:
        worked = helpers.createUser(params, code = code) #join group
        if not worked: return error('Invalid code or duplicate email.')
        return success(None)

@app.route('/api/user/forgot', methods = ['POST'])
def forgotUser(): #forgot user password
    params = request.get_json(force = True)
    if 'email' not in params:
        return error('Please provide the account email to reset your password.')
    worked = helpers.resetPassword(params['email'])
    if not worked: return error('Invalid email provided.')
    return success('Please check your email for a new password.')
        
@app.route('/api/user', methods = ['GET'])
def getUser(): #get current user
    user = helpers.getUser() #watered down mongo object
    if not user: return error('Not authenticated.')
    return success(user)

@app.route('/api/user', methods = ['PUT'])
def editUser(): #see note for editClinicName
    params = request.get_json(force = True)
    if 'current' not in params:
        return error('You did not enter your current password.')
    if 'password' in params and (not isString(params['password'])
        or not (8 <= len(params['password']) <= 40)):
        return error('Your new password had an invalid length.')
    if 'first' in params and (not isString(params['first'])
        or not (2 <= len(params['first']) <= 30)):
        return error('Your first name had an invalid length.')
    if 'last' in params and (not isString(params['last'])
        or not (2 <= len(params['last']) <= 30)):
        return error('Your last name had an invalid length.')
    
    #verify current password
    current = params['current']
    
    #remove any invalid parameters quietly before we edit DB
    params = clean(params, ['password', 'first', 'last'])
    
    worked = helpers.editUser(current, params) #can edit self
    if worked is None: return error('Incorrect permissions.')
    elif not worked: return error('Incorrect password.')
    return success(None)

@app.route('/api/user/<ID>/approve', methods = ['POST'])
def approveUser(ID): #AJAX doctor approval
    params = request.get_json(force = True)
    if 'accept' not in params:
        return error('You did not approve or reject.')
    if not isinstance(params['accept'], bool):
        return error('Your approval value was faulty.')
    
    worked = helpers.approveUser(ID, params['accept'])
    if not worked: return error('Incorrect permissions.')
    return success(None)

@app.route('/api/login', methods = ['POST'])
def login(): #AJAX user login
    params = request.get_json(force = True)
    if 'user' in session: return success('/dashboard')
    if 'email' not in params or 'password' not in params:
        return error('You must fill out all required fields.')
    params = clean(params, ['email', 'password'])
    
    worked = helpers.loginUser(params) #sets session variable too
    if worked is None: return error('Incorrect login credentials.')
    if not worked: return error('Unconfirmed or unapproved login credentials.')
    return success('/dashboard') #redirect user on front end

@app.route('/logout')
def logout(): #redirect to home always
    helpers.logoutUser()
    return redirect('/')

@app.route('/api/patient/create', methods = ['POST'])
def addPatient(): #AJAX add patient [TrueVault]
    params = request.get_json(force = True)
    if ('first' not in params or 'last' not in params or
       'times' not in params or 'phone' not in params):
        return error('You must fill out all required fields.')
    if not isString(params['first']) or not (2 <= len(params['first']) <= 30):
        return error('Your first name had an invalid length.')
    if not isString(params['last']) or not (2 <= len(params['last']) <= 30):
        return error('Your last name had an invalid length.')
    if not (0 < len(params['times']) <= 3):
        return error('You must set between one and three reminder times.')
    if not (re.match('^((([1-9])|(1[0-2])):([0-5])([0-9])\s(A|P)M)$', params['times'][0])):
        return error('One or more reminder times were improperly formatted.')
    if (len(params['times']) > 1 and
        not (re.match('^((([1-9])|(1[0-2])):([0-5])([0-9])\s(A|P)M)$', params['times'][1]))):
        return error('One or more reminder times were improperly formatted.')
    if (len(params['times']) > 2 and
        not (re.match('^((([1-9])|(1[0-2])):([0-5])([0-9])\s(A|P)M)$', params['times'][2]))):
        return error('One or more reminder times were improperly formatted.')
    if not (len(params['phone']) == 10 and params['phone'].isdigit()):
        return error('You must enter an American ten-digit phone number.')
    
    params['phone'] = ','.join(params['phone']) #no arrays in TrueVault
    params = clean(params, ['first', 'last', 'times', 'phone'])
    
    worked = helpers.createPatient(params)
    if not worked: return error('An unknown error occurred.')
    return success(worked) #patient data in worked

@app.route('/api/patient/<ID>', methods = ['PUT'])
def editPatient(ID): #AJAX edit patient [TrueVault]
    params = request.get_json(force = True)
    if ('first' not in params or 'last' not in params or
       'times' not in params or 'phone' not in params):
        return error('You must fill out all required fields.')
    if not isString(params['first']) or not (2 <= len(params['first']) <= 30):
        return error('Your first name had an invalid length.')
    if not isString(params['last']) or not (2 <= len(params['last']) <= 30):
        return error('Your last name had an invalid length.')
    if not (0 < len(params['times']) <= 3):
        return error('You must set between one and three reminder times.')
    if not (re.match('^((([1-9])|(1[0-2])):([0-5])([0-9])\s(A|P)M)$', params['times'][0])):
        return error('One or more reminder times were improperly formatted.')
    if (len(params['times']) > 1 and
        not (re.match('^((([1-9])|(1[0-2])):([0-5])([0-9])\s(A|P)M)$', params['times'][1]))):
        return error('One or more reminder times were improperly formatted.')
    if (len(params['times']) > 2 and
        not (re.match('^((([1-9])|(1[0-2])):([0-5])([0-9])\s(A|P)M)$', params['times'][2]))):
        return error('One or more reminder times were improperly formatted.')
    if not (len(params['phone']) == 10 and params['phone'].isdigit()):
        return error('You must enter an American ten-digit phone number.')
    
    params['phone'] = ','.join(params['phone']) #no arrays in TrueVault
    params = clean(params, ['first', 'last', 'times', 'phone'])
    
    worked = helpers.editPatient(params, ID)
    if not worked: return error('Incorrect permissions.')
    return success(worked) #patient data in worked

@app.route('/api/patient/<ID>', methods = ['DELETE'])
def deletePatient(ID): #AJAX delete patient [TrueVault]
    worked = helpers.deletePatient(ID)
    if not worked: return error('Incorrect permissions.')
    return success(None) #delete succeeded
