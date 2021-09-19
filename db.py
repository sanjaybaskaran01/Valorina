import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import bcrypt

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

def hashPass(password):
    hashed_pass=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt(10))
    print(hashed_pass)
    return hashed_pass

def checkUser(username,region):
    if getUser(username,region):
        return True
    else:
        return False

def updatePass(username,password,region):
    if checkUser(username,region):
        collection=db[region]
        collection.update_one(
            {'username':username},
            {"$set":{'password':password}})
        return True

def getUser(username,region):
    collection=db[region]
    return collection.find_one({"username": username})
        


