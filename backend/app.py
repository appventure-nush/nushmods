from flask import Flask, request, jsonify
import csv

# Load CSV file

with open("pos.csv", encoding="UTF-8") as f:
    csv_reader = csv.DictReader(f)

    global module_data # yes
    module_data = [row for row in csv_reader]
        
    

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def api():
    response = jsonify(module_data)
    response.headers.add('Access-Control-Allow-Origin', '*') # TODO: Change this?
    return response


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=3202)