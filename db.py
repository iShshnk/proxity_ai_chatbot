from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, jsonify, send_file, Response # Flask libraries for creating web application
from flask_session import Session 
import pymongo
from bson.objectid import ObjectId
from bson import json_util
import json

# create Flask app
app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://mayank:digital-me@cluster0.a1zgw44.mongodb.net/?retryWrites=true&w=majority")
  
db = client["RediMinds-Employees-Database"]
current_collection = db["EmpDataset"]
current_collection2 = db["ChatDataset"]
avatar_info_collection = db["AvatarInfo"]  # New collection

def retrieve_data(email_id):
  data = current_collection.find_one({ 'Email': email_id })
  return data

def retrieve_admin_data(email_id):
  collection_name = db["AdminDataset"]
  data = collection_name.find_one({ 'Email': email_id })
  return data

@app.route('/avatarinfo/<email_id>', methods=['GET'])
def get_avatar_info(email_id):
    data = avatar_info_collection.find_one({ 'Email': email_id })
    if data:
        response = {
            "Email": data.get('Email', ''),
            "Name": data.get('Name', ''),
            "Personality": data.get('Personality', ''),
            "Personal life": data.get('Personal life', ''),
            "Profession": data.get('Profession', '')
        }
        return jsonify(response)
    else:
        return jsonify({"error": "No data found for this email."})

@app.route('/avatarinfo', methods=['POST'])
def insert_avatar_info():
    data = request.json
    avatar_info_collection.insert_one(data)
    return 'Avatar information added!'

@app.route('/avatarinfo/<email_id>', methods=['PUT'])
def update_avatar_info(email_id):
    new_data = request.json
    avatar_info_collection.update_one({'Email': email_id}, {"$set": new_data})
    return 'Avatar information updated!'

@app.route('/avatarinfo/<email_id>', methods=['DELETE'])
def delete_avatar_info(email_id):
    avatar_info_collection.delete_one({'Email': email_id})
    return 'Avatar information deleted!'

@app.route('/update/<id>', methods=['POST'])
def update_summary(email_id, summary):
    query = {'Email': email_id}
    new_values = {"$set": {"Last Conversation Summary": summary}}
    current_collection.update_one(query, new_values)
    return 'Summary Updated!'
  
def save_media(data, email_id):
  collection_name = db["AdminDataset"]
  current_data = collection_name.find_one({ 'Email': email_id })
  current_data.setdefault('data', [])
  current_data['data'].append(data)
  collection_name.update_one({'Email': email_id}, {'$set': current_data}, upsert=True)
  
def save_voice_id(email_id, voice_id):
  collection_name = db["AdminDataset"]
  collection_name.update_one({'Email': email_id}, {'$set': {'voice_id': voice_id}}, upsert=True)
  
def add_permission(admin_email, user_email):
  admin_collection = db["AdminDataset"]
  user_collection = db["EmpDataset"]
  
  current_admin = admin_collection.find_one({ 'Email': admin_email })
  current_user = user_collection.find_one({ 'Email': user_email })
  
  current_admin.update_one({ 'Email': admin_email }, {'$push': {'permission': user_email}})
  current_user.update_one({ 'Email':  user_email}, {'$push': {'bot_availabel': admin_email}})
  
def get_chat_messages(admin_email):
  chat_collection = db["ChatDataset"]
  chats = chat_collection.find({'bot_email': admin_email})
  res = []
  for document in chats:
    print(document)
    res.append(document)

  return json.loads(json_util.dumps(res))


if __name__ == '__main__':
	app.run()
