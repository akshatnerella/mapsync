from flask import Flask, request, jsonify
from firebase_admin import auth, initialize_app

app = Flask(__name__)
initialize_app()

@app.route("/auth/verify-token", methods=["POST"])
def verify_token():
    # Verify Firebase ID token
    token = request.json.get('token')
    try:
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        return jsonify({"status": "success", "user_id": user_id})
    except:
        return jsonify({"status": "error", "message": "Invalid token"}), 401

@app.route("/")
def home():
    return "MapSync backend works ✅"

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Placeholder logic
    if email == "test@example.com" and password == "1234":
        return jsonify({"status": "success", "user_id": "dummy_uid"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/trips", methods=["POST"])
def create_trip():
    # Create new trip
    data = request.json
    required = ["origin", "destination"]
    if not all(field in data for field in required):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Generate short invite code
    invite_code = generate_invite_code()  # You'll need to implement this
    
    # Create Google Maps deep link
    maps_link = create_maps_link(data["origin"], data["destination"], data.get("stops", []))
    
    # Save to Firebase
    trip_data = {
        "origin": data["origin"],
        "destination": data["destination"],
        "stops": data.get("stops", []),
        "created_by": request.user_id,  # You'll need middleware for this
        "invite_code": invite_code,
        "maps_link": maps_link,
        "participants": [request.user_id]
    }
    
    return jsonify({
        "status": "success",
        "trip_id": "new_trip_id",
        "invite_code": invite_code,
        "maps_link": maps_link
    })

@app.route("/trips/<trip_id>", methods=["GET"])
def get_trip(trip_id):
    # Fetch trip details
    return jsonify({"status": "success", "trip": trip_data})

@app.route("/trips/join/<invite_code>", methods=["POST"])
def join_trip(invite_code):
    # Join existing trip
    return jsonify({"status": "success", "trip": trip_data})

@app.route("/trips/user/<user_id>", methods=["GET"])
def get_user_trips(user_id):
    # Get user's trip history
    return jsonify({"status": "success", "trips": trips})

if __name__ == "__main__":
    app.run(debug=True)
