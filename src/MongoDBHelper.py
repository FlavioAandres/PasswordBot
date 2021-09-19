import pymongo
import os 

MONGODB_HOST = os.environ['MONGODB_HOST']; 
MONGODB_PORT = os.environ['MONGODB_PORT']; 
MONGODB_USER = os.environ['MONGODB_USER']; 
MONGODB_PASSWORD = os.environ['MONGODB_PASSWORD']; 
MONGODB_REPLICASET = os.environ['MONGODB_REPLICASET']
MONGO_URI=f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}/test?retryWrites=true&w=majority&ssl=true&authSource=admin"

client = None; 

def connect(): 
    try: 
        client = pymongo.MongoClient(
            host=MONGO_URI,
            replicaSet=MONGODB_REPLICASET
        );
        return client.test; 
    except Exception as error: 
        print('MongoDBHelper::' + str(error)); 

def disconnect(): 
    if(client):     
        client.close(); 