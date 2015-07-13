import requests
import random
import string
import time
import json

#TODO: we should store this somewhere safer
KEY = 'b966a6c5-4a37-40a6-8e35-4c375f60ae77'
BASE = 'https://api.truevault.com/v1'

def toBase64JSON(object):
    str = json.dumps(object)
    return str.encode('base64')

def randomSalt(length): #because TrueVault is a bitch about vault names
   return ''.join(random.choice(string.lowercase) for i in range(length))

def createClinic(original):
    original += ' [' + randomSalt(6) + ']'
    payload = {'name' : original}
    
    req = requests.post(BASE + '/vaults',
        auth = (KEY, ''), data = payload)
    if req.status_code != 200: return False
    
    resp = req.json() #JSON encoded response
    return resp['vault']['id']

def createPatient(vault, data):
    payload = {'document' : toBase64JSON(data)}
    req = requests.post(BASE + '/vaults/' + vault + '/documents',
        auth = (KEY, ''), data = payload) #vault is a clinic
    if req.status_code != 200: return False
    
    resp = req.json() #JSON encoded response
    return resp['document_id']

def editPatient(vault, patient, data):
    payload = {'document' : toBase64JSON(data)}
    req = requests.post(BASE + '/vaults/' + vault + '/documents/' +
        patient, auth = (KEY, ''), data = payload) #vault is a clinic
    if req.status_code != 200: return False
    
    resp = req.json() #JSON encoded response
    return resp['document_id']

def getPatients(vault):
    payload = {'full' : True, 'per_page' : 1000}
    req = requests.get(BASE + '/vaults/' + vault + '/documents',
        auth = (KEY, ''), data = payload) #vault is a clinic
    if req.status_code != 200: return False
    
    resp = req.json() #JSON encoded response
    return resp['data']['items']
