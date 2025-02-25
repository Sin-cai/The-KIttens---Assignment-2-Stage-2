from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime

app = Flask(__name__)

# MongoDB connection
uri = "mongodb+srv://kittens:scHC9YuGut4n3T3@cluster0.lu3nj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi("1"))

db = client["sic"]
environmental_collection = db["environmental"]

@app.route("/hello")
def entry_point():
    return "Hello World!"

@app.route("/sensor1/data/avg", methods=["GET"])
def get_data_avg():
    cursor = environmental_collection.find({}, {"_id": 0, "temperature": 1, "humidity": 1})
    data = list(cursor)
    
    if not data:
        return jsonify({"message": "No data found"}), 404
    
    avg_temperature = sum(d["temperature"] for d in data if "temperature" in d) / len(data)
    avg_humidity = sum(d["humidity"] for d in data if "humidity" in d) / len(data)

    return jsonify({"average_temperature": avg_temperature, "average_humidity": avg_humidity})

@app.route("/create", methods=["POST"])
def create_data():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    # city = data.get("city")
    temperature = data.get("temp")
    humidity = data.get("humidity")

    # if not city or temperature is None or humidity is None:
    #     return jsonify({"message": "Missing fields"}), 400

    new_document = { "temperature": temperature, "humidity": humidity}
    environmental_collection.insert_one(new_document)

    return jsonify({"message": "Data inserted successfully"}), 201

@app.route("/api/sensor", methods=["POST"])
def save_data():
    data = request.json
    data["timestamp"] = datetime.datetime.now()

    # Simpan ke MongoDB
    environmental_collection.insert_one(data)
    return jsonify({"message": "Data saved!", "data": data}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)