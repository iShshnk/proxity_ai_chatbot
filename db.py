from flask import Flask, jsonify
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

try:
  client = pymongo.MongoClient("mongodb+srv://mayank:digital-me@medical-records.rewhmdm.mongodb.net/?retryWrites=true&w=majority")
  
# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  
db = client["medical-records"]
current_collection = db["medicalRecords"]

# root route
@app.route('/')
def hello_world():
	return 'Hello, World!'
  
@app.route('/<id>', methods=['GET'])
def retrieve_data(id):
  unique_id = str(id)
  data = current_collection.find_one({ '_id': ObjectId(unique_id) })
  # return jsonify({"Age":data['Age'],"Diastolic":data['Diastolic'],"Gender":data['Gender'],
  #                 "Height":data['Height'],"LastName":data['LastName'],"Location":data['Location'],
  #                 "SelfAssessedHealthStatus":data['SelfAssessedHealthStatus'],"Smoker":data['Smoker'],
  #                 "Systolic":data['Systolic'],"Weight":data['Weight']})
  return data

'''
Data entries:
Age
Diastolic
Gender
Height
LastName
Location
SelfAssessedHealthStatus
Smoker
Systolic
Weight
'''

if __name__ == '__main__':
	app.run()