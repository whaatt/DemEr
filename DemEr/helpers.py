#this file just retrieves and sets DB stuff
from passlib.hash import pbkdf2_sha256
from bson.objectid import ObjectId
from pymongo import MongoClient
from flask_mail import Message
from flask import session

#to store emails in a clean separated format
from flask import render_template as template

from DemEr import app, mail, title
client = MongoClient()
db = client.ReMed
import check

def getPatientData():
    #TODO: complete
    return None

#data pertaining to doctors in YOUR clinic
#returns data with perms or None otherwise
@check.loggedIn(error = None)
@check.ownership(error = None)
def getDoctorData():
    doctors = db.users.find({
        'clinic' : session['user']['clinic'],
        'confirmed' : True}) #a little ugly
    
    #cursor to a list
    doctors = list(doctors)
    
    #filter to exclude any sensitive fields [just password]
    for i in range(len(doctors)): del doctors[i]['password']
    return doctors

#return None or clinic name
def getClinicName(ID):
    #do we want a more human-readable clinic code in the future?
    #this is good because we don't need to fuck with autoincrement
    clinic = db.clinics.find_one({'_id' : ObjectId(ID)})
    if clinic: return clinic.name
    return None

#return None or name
@check.loggedIn(error = None)
@check.ownership(error = None)
def editClinicName(name):
    #try to update the name in the database
    result = db.clinics.update_one(
        {'_id' : session['user']['clinic']},
        {'$set' : {'name' : name}})
    
    if result.modified_count == 1: return name
    return None #something messed up

#returns true on success or false on failure
def createUser(info, group = None, code = None):
    userExist = db.users.find_one({'email' : info['email']})
    if userExist: return False #user previously exists
    
    if not code: #new group must be created
        newClinic = db.clinics.insert_one({'name' : group})
        if not newClinic: return False
        code = str(newClinic.inserted_id)
        
        #you created it
        info['owner'] = True
        info['approved'] = True
        
    else: #verify that desired clinic exists
        oldClinic = db.clinics.find_one({
            '_id' : ObjectId(code)})
        if not oldClinic: return False
        
        #joining something
        info['owner'] = False
        info['approved'] = False
    
    info['confirmed'] = False
    info['clinic'] = ObjectId(code)
    
    hash = pbkdf2_sha256.encrypt(info['password'], rounds = 100000, salt_size = 10)
    info['password'] = hash #store password in an encrypted, salted form
    user = db.users.insert_one(info)
    if not user: return False
    
    userMsg = Message('Your ' + title + ' Account', #app title
        sender = ('Example Administrator', 'test@example.com'),
        recipients = [(info['first'] + ' ' + info['last'], info['email'])])
    
    userMsg.body = template('newUser.txt', user = info, ID = user.inserted_id)
    userMsg.html = template('newUser.html', user = info, ID = user.inserted_id)
    mail.send(userMsg)
    
    if not info['owner']:
        owner = db.users.find_one({'clinic' : ObjectId(code)})
        appMsg = Message('Signup Notification', #approval queue
            sender = ('Example Administrator', 'test@example.com'),
            recipients = [(owner['first'] + ' ' + owner['last'], owner['email'])])
        
        appMsg.body = template('approveUser.txt', owner = owner, user = info)
        appMsg.html = template('approveUser.html', owner = owner, user = info)
        mail.send(appMsg)
    
    #email validation?
    return True

#returns None if invalid creds
#returns false if unconfirmed
#returns true on successful login
def loginUser(info):
    passW = info['password']
    del info['password']
    
    user = db.users.find_one(info)
    if not user: return None
    
    if not pbkdf2_sha256.verify(passW, user['password']):
        return None #password was incorrect
    
    if not user['confirmed']: return False
    if not user['approved']: return False
    session['user'] = user
    return True

#no explicit return
def logoutUser():
    del session['user']

#returns boolean success value
@check.loggedIn(error = None)
def editUser(current, info):
    user = db.users.find_one({
        #find the user to verify password
        '_id' : session['user']['_id']})
    
    if not pbkdf2_sha256.verify(current, user['password']):
        return False #password was incorrect
        
    result = db.users.update_one(
        {'_id' : session['user']['_id']},
        {'$set' : info}) #update fields
    
    if result.modified_count == 1: return True
    return False #something messed up

#returns boolean again
@check.loggedIn(error = None)
@check.ownership(error = None)
def approveUser(ID):
    result = db.users.update_one(
        {'_id' : ObjectId(ID), 'confirmed' : True,
         'clinic' : session['user']['clinic']},
        {'$set' : {'approved' : True}})
    
    if result.modified_count == 1:
        info = db.users.find_one({'_id' : ObjectId(ID)})
        if not info: return False #cover all of our bases
        
        userMsg = Message('Account Request Approved', #app title
            sender = ('Example Administrator', 'test@example.com'),
            recipients = [(info['first'] + ' ' + info['last'], info['email'])])
        
        userMsg.body = template('finalUser.txt', user = info)
        userMsg.html = template('finalUser.html', user = info)
        mail.send(userMsg)
        return True
    
    #something messed up
    return False

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

#tries to confirm user and returns
#firstly, whether successful confirm
#secondly, whether user is the owner
#thirdly, what clinic user belongs to
def confirmUser(ID):
    if not ObjectId.is_valid(ID):
        return False, False, None
    
    user = db.users.find_one({
         '_id' : ObjectId(ID),
        'confirmed' : False})
    
    if not user: #no such user
        return False, False, None
    
    #user already confirmed so give an error page
    if user['confirmed']: return False, False, None
    
    result = db.users.update_one(
        {'_id' : ObjectId(ID)},
        {'$set' : {'confirmed' : True}})
    
    #no result: something really weird happened with Mongo
    if result.modified_count != 1: return False, False, None
    
    clinic = db.clinics.find_one({'_id' : ObjectId(user['clinic'])})
    if not clinic: return False, False, None
    return True, user['owner'], clinic['name']
