from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################

@app.route("/picture", methods=["GET"])
def get_pictures():
    return jsonify(data), 200

######################################################################
# GET A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    picture = next((item for item in data if item["id"] == id), None)
    if picture:
        return jsonify(picture), 200
    abort(404, description="Picture not found")

######################################################################
# CREATE A PICTURE
######################################################################

@app.route("/picture", methods=["POST"])
def create_picture():

    if not request.json:
        abort(400, description="Invalid request")
    
    new_picture = request.json

    # Check if the ID already exists in the data
    existing_ids = [pic["id"] for pic in data]
    if new_picture["id"] in existing_ids:
        return jsonify({"Message": f"picture with id {new_picture['id']} already present"}), 302

    data.append(new_picture)
    with open(json_url, 'w') as f:
        json.dump(data, f)
    return jsonify(new_picture), 201

######################################################################
# UPDATE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    picture = next((item for item in data if item["id"] == id), None)
    if not picture:
        abort(404, description="Picture not found")
    if not request.json:
        abort(400, description="Invalid request: no data provided")
     # Update the existing picture object with data from request.json
    picture.update(request.json)

    # Save the updated data list back to the JSON file
    with open(json_url, 'w') as f:
        json.dump(data, f)
    
    return jsonify(picture), 200

######################################################################
# DELETE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    global data
    # Find the picture with the given id
    picture = next((item for item in data if item["id"] == id), None)
    if not picture:
        abort(404, description="Picture not found")
    
    # Remove the picture from the data list
    data = [item for item in data if item["id"] != id]

    # Save the updated data list back to the JSON file
    with open(json_url, 'w') as f:
        json.dump(data, f)
    
    return jsonify({"message": "Picture deleted"}), 204