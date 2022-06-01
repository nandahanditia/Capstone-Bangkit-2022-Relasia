from flask import Blueprint, request, jsonify
from firebase_admin import firestore

db = firestore.client()
foundation_Ref = db.collection('foundation')
volunteer_Ref = db.collection('volunteer')

foundationRoutes = Blueprint('foundationRoutes', __name__)


@foundationRoutes.route('/', methods=["POST"])
def addFoundation():
    try:
        foundation_id = request.json["id"]
        foundation_data = request.json["data"]
        foundation_Ref.document(foundation_id).set(foundation_data)

        # HTTP response code: 201 Created
        return jsonify(message="Successfully Created"), 201

    except Exception as e:
        return f"An Error Occurred: {e}"


@foundationRoutes.route('/<string:foundation_id>', methods=['PUT'])
def validateMember(foundation_id):
    try:
        foundation = foundation_Ref.document(foundation_id).get()
        print(foundation.to_dict())
        volunteer_id = request.json['volunteer']
        volunteer = volunteer_Ref.document(volunteer_id).get()
        status = request.json['status']

        if foundation.exists and volunteer.exists:
            # Update members status in foundation collection
            foundation_data = foundation.to_dict()
            foundation_data["volunteers"][volunteer_id] = status
            foundation_Ref.document(foundation_id).update(foundation_data)

            # Update volunteers verified status in volunteer collection
            if status == "accepted":
                volunteer_data = volunteer.to_dict()
                volunteer_data["verified"] = "true"
                volunteer_Ref.document(volunteer_id).update(volunteer_data)

            # HTTP response code: 200 OK
            return jsonify(message="Successfully Updated"), 200
        else:
            # HTTP response code: 400 Bad Request
            return jsonify(message="Bad Request"), 400

    except Exception as e:
        return f"An Error Occurred: {e}"


@foundationRoutes.route("/", methods=['PUT'])
def editFoundation():
    try:
        foundation_id = request.json["id"]
        foundation = foundation_Ref.document(foundation_id).get()

        if foundation.exists:
            foundation_Ref.document(foundation_id).update(request.json["data"])

            # HTTP response code: 200 OK
            return jsonify(message="Successfully Updated"), 200
        else:
            # HTTP response code: 400 Bad Request
            return jsonify(message="Bad Request"), 400

    except Exception as e:
        return f"An Error Occurred: {e}"


@foundationRoutes.route('/', methods=['DELETE'])
def deleteFoundation():
    try:
        foundations_id = request.json["id"]
        foundation = foundation_Ref.document(foundations_id).get()

        if foundations_id:
            foundation_data = foundation.to_dict()
            members = foundation_data["volunteers"]

            for volunteer_id in members.keys():
                volunteer = volunteer_Ref.document(volunteer_id).get()

                if volunteer.exists:
                    # Update foundation of volunteer on volunteer collection
                    volunteer_data = volunteer_Ref.document(
                        volunteer_id).get().to_dict()
                    volunteer_data["foundations"].remove(foundations_id)
                    volunteer_Ref.document(volunteer_id).update(volunteer_data)

            foundation_Ref.document(foundations_id).delete()
            # HTTP response code: 200 OK
            return jsonify(message="Successfully Updated"), 200
        else:
            # HTTP response code: 400 Bad Request
            return jsonify(message="Bad Request"), 400
    except Exception as e:
        return f"An Error Occurred: {e}"


@foundationRoutes.route('/', methods=["GET"])
def getFoundations():
    try:
        try:
            foundation_id = request.json["id"]
        except:
            foundation_id = ""

        if foundation_id:
            foundation_data = foundation_Ref.document(
                foundation_id).get().to_dict()

            # Get all volunteer of foundation from volunteer collection
            volunteers = foundation_data["volunteers"]
            foundation_data["volunteers"] = {}

            for volunteer_id in volunteers:
                volunteer_data = volunteer_Ref.document(
                    volunteer_id).get().to_dict()
                foundation_data["volunteers"][volunteer_id] = volunteer_data

            # HTTP response code: 200 OK
            return foundation_data, 200
        else:
            # Get all foundations from foundation collection
            all_foundations = [doc.to_dict()
                               for doc in foundation_Ref.stream()]

            response = {
                "length" : len(all_foundations),
                "data" : all_foundations,
            }

            # HTTP response code: 200 OK
            return jsonify(response), 200

    except Exception as e:
        return f"An Error Occurred: {e}"