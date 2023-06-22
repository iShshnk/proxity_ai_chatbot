from flask import Flask, jsonify
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

try:
  client = pymongo.MongoClient("mongodb+srv://mayank:digital-me@cluster0.a1zgw44.mongodb.net/?retryWrites=true&w=majority")
  
# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  
db = client["RediMinds-Employees-Database"]
current_collection = db["EmpDataset"]

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


if __name__ == '__main__':
	app.run()