from pymongo import MongoClient
from user import User
import datetime
client = MongoClient('mongodb+srv://mohit:vmbXc8pzgJzhiRNa@cluster0.tbarxzw.mongodb.net/')

chat_db = client.get_database("chatDB")
users_collection = chat_db.get_collection("userData")
rooms_collection = chat_db.get_collection("roomsData")
room_member_collection = chat_db.get_collection("roomsMembersData")


def save_user(username, password):
    #password_hash = bcrypt.hashpw(password, bcrypt.gensalt()) 
    #password_hash = generate_password_hash(password)
    if users_collection.find_one({'_id': username}):  
        print("User already exists. You might want to update instead.")  
    else:  
        users_collection.insert_one({'_id': username,'password': password})

def get_user(username):
    user_data = users_collection.find_one({'_id':username})
    return User(user_data['_id'],user_data['password']) if user_data else None

def add_room_member(room_id,room_name,username,added_by, is_room_admin = False):
    room_member_collection.insert_one({'_id':{'room_id':room_id, 'username':username},'added_by':added_by,'added_at':datetime.now(),'is_room_admin':is_room_admin})
        
def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one(
        {'room_name':room_name,'created_by':created_by,'created_at':datetime.now()}).inserted_id
    add_room_member(room_id,room_name,created_by,is_room_admin=True)
 
def add_room_members(room_id, room_name, usernames, added_by):
    room_member_collection.insert_many(
        [{'_id':{'room_id':room_id, 'username':username},
          'room_name':room_name,'added_by':added_by,'added_at':datetime.now(), 'is_room_admin':False} for username in usernames]
    )
    
def get_room(room_id):
    rooms_collection.find_one({'_id':ObjectId(room_id)})


def get_room_members(room_id):
    room_member_collection.find({'_id.room_id':room_id})
    
def get_rooms_for_user(username):
    room_member_collection.find({'_id.username':username})


def is_room_member(room_id, username):
    room_member_collection.count_documents({'_id':{'room_id':room_id, username:username}})

def is_room_admin(room_id, username):
   room_member_collection.count_documents({'_id':{'room_id':room_id, username:username},'is_room_admin':True})

def update_room(room_id,room_name):
    rooms_collection.update_one({'_id':ObjectId(room_id)},{'$set':{'name': room_name}})   
    
def remove_room_members(room_id,usernames):
    room_member_collection.delete_many({'_id':{'$in':[{'room_id':room_id,'username':username} for username in usernames]}})
#save_user('jonsnow','palmohit9@gmail.com','abc')
