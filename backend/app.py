from flask import Flask, request, jsonify
import pandas as pd
from pandasql import sqldf

from util import pd2resp

import pathlib


# Repository Root
data_dir = pathlib.Path(__file__).parent / "data"

# Get Data
modules = pd.read_csv(data_dir / "pos.csv").fillna("")
departments = pd.read_csv(data_dir / "departments.csv").fillna("")


# Initiate Flask App
app = Flask(__name__)

@app.route("/api/modules", methods=["GET"])
def get_modules():
    # Get request parameters
    department = request.args.get("department", "", str)
    
    # "Query"
    query = "SELECT * FROM modules" + (f" WHERE department = '{department}'" if department else "")
    
    # Query the Database
    df = sqldf(query)

    return pd2resp(df)

@app.route("/api/departments", methods=["GET"])
def get_departments():
    return pd2resp(departments)
    


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
