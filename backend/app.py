from flask import Flask, request, jsonify
import pandas as pd

import pathlib

# Repository Root
data_dir = pathlib.Path(__file__).parent.parent

# Get Module Data
module_data = pd.read_csv(data_dir / "pos.csv").fillna("").to_dict("records")

app = Flask(__name__)

@app.route("/api/modules", methods=["GET"])
def api():
    response = jsonify(module_data)
    response.headers.add('Access-Control-Allow-Origin', '*') # TODO: Change this?
    return response


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
