from flask import jsonify

def pd2resp(df):
    response = jsonify(df.to_dict("records"))
    response.headers.add('Access-Control-Allow-Origin', '*')  # TODO: Change this?
    return response
