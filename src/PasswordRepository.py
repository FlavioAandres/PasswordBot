import datetime
from cryptography.fernet import Fernet
from . import MongoDBHelper; 
import traceback

def store_password(name, password = "", phone=""): 
    db = MongoDBHelper.connect(); 
    key = Fernet.generate_key(); 
    encrypt = Fernet(key);
    try:
        token = encrypt.encrypt(bytes(password, 'utf-8'));
        password_collection = db.passwords;

        result = password_collection.insert_one({
            'name': name, 
            'value': token.decode('utf-8'), 
            'key': key.decode('utf-8'),
            'createdAt': datetime.datetime.now(), 
            'phone': phone
        });
        MongoDBHelper.disconnect(); 
    except Exception as error:
        print("Exeption::" + str(error))
        traceback.print_exc();
        MongoDBHelper.disconnect(); 

def update_password(password, phone, name):
    db = MongoDBHelper.connect(); 
    key = Fernet.generate_key(); 
    encrypt = Fernet(key);
    try:
        token = encrypt.encrypt(bytes(password, 'utf-8'));
        password_collection = db.passwords;

        result = password_collection.update_one({
            'name': name, 
            'phone': phone, 
        }, {
            'value': token.decode('utf-8'), 
            'key': key.decode('utf-8')
        });
        MongoDBHelper.disconnect(); 
    except Exception as error:
        print("Exeption::" + str(error))
        traceback.print_exc();
        MongoDBHelper.disconnect(); 

def get_password(phone,name=""): 
    db = MongoDBHelper.connect(); 
    search = {
        'phone': phone
    }
    if(name != ""): 
        search["name"] = name
    password_collection = db.passwords;
    try:
        password_info = password_collection.find(search)
        password_info = list(password_info)
        if(password_info is None):
            return "Not found"
        
        if(len(password_info) == 1): 
            unique_password = password_info[0]
            stored_key = unique_password['key']; 
            stored_value = unique_password['value']; 
            decrypter = Fernet(bytes(stored_key, encoding='utf8')) 
            result = decrypter.decrypt(bytes(stored_value, encoding="utf8")); 
            return str(result.decode('utf-8')); 
        elif (len(password_info) > 1): 
            return list(map(lambda password: password["name"], password_info)); 
    except Exception as error:
        print(str(error)); 
        traceback.print_exc();
        return None; 
