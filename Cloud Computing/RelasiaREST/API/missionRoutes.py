from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import datetime
import hashlib

# Initialization Database Reference
db = firestore.client()
volunteer_Ref = db.collection('volunteer')
helpseeker_Ref = db.collection('helpseeker')
mission_Ref = db.collection('mission')

missionRoutes = Blueprint('missionRoutes', __name__)


@missionRoutes.route('/', methods=['POST'])
def addMission():
    try:
        # Composite mission_id from hash(helpseeker_id$title)
        title = request.json['title']
        helpseeker_id = request.json['id']
        mission_id = hashlib.sha1(
            (helpseeker_id + "$" + title).encode("utf-8")).hexdigest()

        helpseeker = helpseeker_Ref.document(helpseeker_id).get()
        if helpseeker.exists:
            mission = mission_Ref.document(mission_id).get()
            if mission.exists:
                # HTTP response code: 409 Conflict
                return jsonify(message="Mission Exists"), 409
            else:
                # Add new mission to mission collection
                mission_data = request.json
                mission_data["timestamp"] = datetime.datetime.now()
                mission_Ref.document(mission_id).set(mission_data)

                # Add new mission to helpseeker collection
                helpseeker_data = helpseeker.to_dict()
                helpseeker_data["missions"].append(mission_id)
                helpseeker_Ref.document(helpseeker_id).update(helpseeker_data)

                # HTTP response code: 201 Created
                return jsonify(message="Successfully Created"), 201
        else:
            return f"Something error or user doesn't exist"
    except Exception as e:
        return f"An Error Occurred: {e}"


@missionRoutes.route('/', methods=['POST'])
def addMission():
    try:
        # Composite mission_id from hash(helpseeker_id$title)
        title = request.json['title']
        helpseeker_id = request.json['id']
        mission_id = hashlib.sha1(
            (helpseeker_id + "$" + title).encode("utf-8")).hexdigest()

        helpseeker = helpseeker_Ref.document(helpseeker_id).get()
        if helpseeker.exists:
            mission = mission_Ref.document(mission_id).get()
            if mission.exists:
                # HTTP response code: 409 Conflict
                return jsonify(message="Mission Exists"), 409
            else:
                # Add new mission to mission collection
                mission_data = request.json
                mission_data["timestamp"] = datetime.datetime.now()
                mission_Ref.document(mission_id).set(mission_data)

                # Add new mission to helpseeker collection
                helpseeker_data = helpseeker.to_dict()
                helpseeker_data["missions"].append(mission_id)
                helpseeker_Ref.document(helpseeker_id).update(helpseeker_data)

                # HTTP response code: 201 Created
                return jsonify(message="Successfully Created"), 201
        else:
            return f"Something error or user doesn't exist"
    except Exception as e:
        return f"An Error Occurred: {e}"


@missionRoutes.route('/', methods=['PUT'])
def editMission():
    try:
        mission_id = request.json["id"]
        mission = mission_Ref.document(mission_id).get()

        if mission.exists:
            # Update a mission
            mission_data = request.json["data"]
            mission_Ref.document(mission_id).update(mission_data)

            # HTTP Response Code: 200 OK
            return jsonify(message="Successfully Updated"), 200
        else:
            # HTTP response code: 400 Bad Request
            return jsonify(message="Bad Request"), 400
    except Exception as e:
        return f"An Error Occurred: {e}"


@missionRoutes.route('/<string:mission_id>', methods=['PUT'])
def confirmVolunteers(mission_id):
    try:
        mission = mission_Ref.document(mission_id).get()
        volunteer_id = request.json['volunteer']
        volunteer = volunteer_Ref.document(volunteer_id).get()
        status = request.json['status']

        if mission.exists and volunteer.exists:
            # Update Volunteers Status
            mission_data = mission.to_dict()
            mission_data["volunteers"][volunteer_id] = status
            mission_Ref.document(mission_id).update(mission_data)

            # HTTP Response Code: 200 OK
            return jsonify(message="Successfully Updated"), 200
        else:
            # HTTP response code: 400 Bad Request
            return jsonify(message="Bad Request"), 400
    except Exception as e:
        return f"An Error Occurred: {e}"


@missionRoutes.route('/', methods=['DELETE'])
def deleteMission():
    try:
        # Update mission on volunteer collection
        mission_id = request.json["mission"]
        mission_data = mission_Ref.document(mission_id).get().to_dict()
        volunteers = mission_data["volunteers"]
        for volunteer_id in volunteers.keys():
            volunteer = volunteer_Ref.document(volunteer_id).get()
            if volunteer.exists:
                volunteer_data = volunteer.to_dict()
                volunteer_data["missions"].remove(mission_id)
                volunteer_Ref.document(volunteer_id).update(volunteer_data)

        # Update mission on helpseeker collection
        helpseeker_id = mission_data["id"]
        helpseeker = helpseeker_Ref.document(helpseeker_id).get()
        if helpseeker.exists:
            helpseeker_data = helpseeker.to_dict()
            helpseeker_data["missions"].remove(mission_id)
            helpseeker_Ref.document(helpseeker_id).update(helpseeker_data)

        mission_Ref.document(mission_id).delete()

        # HTTP Response Code: 200 OK
        return jsonify(message="Successfully Deleted"), 200
    except Exception as e:
        return f"An Error Occurred: {e}"


@missionRoutes.route('/', methods=['GET'])
def getMission():
    try:
        try:
            mission_id = request.json["id"]
        except:
            mission_id = ""

        if mission_id:
            mission_data = mission_Ref.document(mission_id).get().to_dict()

            # Get Helpseeker who request the mission from helpseeker collection
            helpseeker_id = mission_data["id"]
            helpseeker = helpseeker_Ref.document(helpseeker_id).get().to_dict()
            mission_data["id"] = helpseeker

            # Get all volunteers who join a mission from volunteer collection
            volunteers = mission_data["volunteers"]
            mission_data["volunteers"] = {}
            for volunteer_id, status in volunteers.items():
                volunteer = volunteer_Ref.document(volunteer_id).get()
                if volunteer.exists:
                    volunteer_data = volunteer.to_dict()
                    volunteer_data['status'] = status
                    mission_data["volunteers"][volunteer_id] = volunteer_data

            # HTTP Response Code: 200 OK
            return mission_data, 200
        else:
            # Get all missions from mission collection
            all_mission = [doc.to_dict() for doc in mission_Ref.stream()]
            # HTTP Response Code: 200 OK
            return jsonify(all_mission), 200
    except Exception as e:
        return f"An Error Occurred: {e}"
