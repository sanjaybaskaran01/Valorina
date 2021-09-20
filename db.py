from typing import Collection
import discord
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()
MONGO = os.getenv('MONGO')
KEY = (os.getenv('KEY')).encode('utf-8')
cluster = MongoClient(MONGO)
db = cluster["discord"]

def addUserDb(username,password,region):
    if not checkUser(username,region):
        collection = db[region]
        password=encryptPass(password)
        user={
            "username":username,
            "password":password
            }
        collection.insert_one(user)
        return True

def encryptPass(password):
    password=Fernet(KEY).encrypt(password.encode('utf-8'))
    return password

def checkUser(username,region):
    if getUser(username,region):
        return True
    else:
        return False

def updatePass(username,password,region):
    if checkUser(username,region):
        password=encryptPass(password)
        collection=db[region]
        collection.update_one(
            {'username':username},
            {"$set":{'password':password}})
        return True

def getUser(username,region):
    collection=db[region]
    user = collection.find_one({"username": username})
    if user==None:
        return False
    user["password"]=(Fernet(KEY).decrypt(user["password"])).decode('utf-8')
    return user
        
def addReminder(username,region,discord_id,weapon):    
    collection = db['reminders']
    data={
            "username":username,
            "region":region,
            "discord_id":discord_id,
            "weapon":weapon,
            }
    collection.insert_one(data)
    return True

def getReminders():    
    collection = db['reminders']
    reminders = []
    cursor = collection.find({})
    for document in cursor:
          reminders.append(document)
    return reminders

def getUserReminders(discord_id):    
    collection = db['reminders']
    reminders = []
    cursor = collection.find({"discord_id":discord_id})
    for document in cursor:
          reminders.append(document)
    return reminders

def delReminder(username, region, discord_id, weapon):    
    collection = db['reminders']
    res = collection.delete_one({"username":username, "region": region, "discord_id": discord_id, "weapon": weapon})
    return True