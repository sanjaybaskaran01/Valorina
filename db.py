import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO = os.getenv('MONGO')

cluster = MongoClient(MONGO)
db = cluster["discord"]

def addUserDb(username,password,region):
    if not checkUser(username,region):
        collection = db[region]
        user={
            "username":username,
            "password":password
            }
        collection.insert_one(user)
        return True

def checkUser(username,region):
    if getUser(username,region):
        return True
    else:
        return False

def getUser(username,region):
    collection=db[region]
    return collection.find_one({"username": username})
        


