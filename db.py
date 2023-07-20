from flask import Flask, jsonify
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://mayank:digital-me@cluster0.a1zgw44.mongodb.net/?retryWrites=true&w=majority")
  
db = client["RediMinds-Employees-Database"]
current_collection = db["EmpDataset"]
current_collection2 = db["ChatDataset"]

# root route
@app.route('/')
def hello_world():
	return 'Hello, World!'
  
@app.route('/<email_id>', methods=['GET'])
def retrieve_data(email_id):
  email = email_id
  data = current_collection.find_one({ 'Email': email })
  # return jsonify({"email":data['Email'],"Name":data['Name'],"Gender":data['Gender'],
  #                 "age":data['Age'],"job_role":data['Job Role'],"about":data['About'],
  #                 "fun_story":data['Fun Story'],"educational_qualification":data['Educational Qualification'],
  #                 "skills":data['Skills']})
  return data

@app.route('/update/<id>', methods=['POST'])
def update_summary(email_id, summary):
    email = email_id
    query = {'Email': email}
    new_values = {"$set": {"Last Conversation Summary": summary}}
    current_collection.update_one(query, new_values)
    return 'Summary Updated!'
  
def save_media(data, email_id):
  email = email_id
  collection_name = db["AdminDataset"]
  current_data = collection_name.find_one({ 'Email': email })
  current_data.setdefault('data', [])
  current_data['data'].append(data)
  collection_name.update_one({'Email': email}, {'$set': current_data}, upsert=True)
  
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


if __name__ == '__main__':
	app.run()