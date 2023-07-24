import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb+srv://mayank:digital-me@cluster0.a1zgw44.mongodb.net/?retryWrites=true&w=majority")
  
db = client["RediMinds-Employees-Database"]
current_collection = db["EmpDataset"]
current_collection2 = db["ChatDataset"]

def retrieve_data(email_id):
  data = current_collection.find_one({ 'Email': email_id })
  return data

def retrieve_admin_data(email_id):
  collection_name = db["AdminDataset"]
  data = collection_name.find_one({ 'Email': email_id })
  return data

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
  
  admin_collection.update_one({ 'Email': admin_email }, {'$push': {'permission': user_email}})
  user_collection.update_one({ 'Email':  user_email}, {'$push': {'bot_available': admin_email}})
