#this file just retrieves and sets DB stuff
from flask.ext.pymongo import PyMongo
from passlib.hash import pbkdf2_sha256

from DemEr import app
mongo = PyMongo(app)
import check

#database helpers
with app.app_context():
    users = mongo.db.users
    clinics = mongo.db.clinics
    messages = mongo.db.messages

def preserve(params, exclude):
    #filter dictionary keys using the passed array of excludes
    return {k : v for k, v in params.items() if k not in exclude}

def getPatientData():
    #TODO: complete
    return None

#data pertaining to doctors in YOUR clinic
#returns data with perms or None otherwise
@check.loggedIn(error = None)
@check.ownership(error = None)
def getDoctorData():
    doctors = mongo.db.users.find({
        'clinic' : session['user']['clinic'],
        'confirmed' : True
    }) #is this the Pythonic way
    
    #filter to exclude amy sensitive fields
    doctors = preserve(doctors, ['password'])
    return doctors

#return None or clinic name
def getClinicName(ID):
    #code is the human readable clinic ID [not Mongo]
    clinic = mongo.db.clinics.findOne({'code' : ID})
    if clinic: return clinic.name
    return None

#return None or name
@check.loggedIn(error = None)
@check.ownership(error = None)
def editClinicName(name):
    #try to update the name in the database
    result = mongo.db.clinics.update_one(
        {'_id' : session['user']['clinic']},
        {'set' : {'name' : name}})
    
    if result.modified_count == 1: return name
    return None #something messed up

#returns true on success or false on failure
def createUser(info, group = None, code = None):
    #TODO: complete
    return False

#returns None if invalid creds
#returns false if unconfirmed
#returns true on successful login
def loginUser(info):
    passW = pbkdf2_sha256.encrypt(info['password'],
        rounds = 200000, salt_size = 16) #strong!
    info['password'] = passW #store hashed
    
    user = mongo.db.users.findOne(info)
    if not user: return False
    session['user'] = user
    return True

#no explicit return
def logoutUser():
    session['user'] = None

#returns boolean success value
@check.loggedIn(error = None)
def editUser(info):
    result = mongo.db.users.update_one(
        {'_id' : session['user']['_id']},
        {'set' : info}) #update fields
    
    if result.modified_count == 1: return True
    return False #something messed up

#returns boolean again
@check.loggedIn(error = None)
@check.ownership(error = None)
def approveUser(ID):
    result = mongo.db.users.update_one(
        {'_id' : ID, 'confirmed' : True,
         'clinic' : session['user']['clinic']},
        {'set' : {'approved' : True}})
    
    if result.modified_count == 1: return True
    return False #something messed up

#returns patient info?
def createPatient(info):
    #TODO: complete
    return None

#returns patient info?
def editPatient(info, ID):
    #TODO: complete
    return None

#returns a boolean success
def deletePatient(ID):
    #TODO: complete
    return False

def confirmUser(ID):
    #TODO: complete
    return False, None
