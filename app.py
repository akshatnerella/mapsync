from flask import Flask, request, jsonify
from firebase_admin import auth, initialize_app, firestore
from flask_cors import CORS
import random
import string
import os

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "https://mapsyncfrontend-chi.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Firebase only if credentials are available
if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    initialize_app()
    db = firestore.client()
else:
    print("Warning: Running in development mode without Firebase credentials")
    db = None

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

def generate_invite_code(length=6):
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        # Check if code already exists
        existing_trip = db.collection('trips').document(code).get()
        if not existing_trip.exists:
            return code

@app.route("/newtrip", methods=["POST"])
def create_trip():
    data = request.json
    required = ["origin", "destination"]
    if not all(field in data for field in required):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Generate unique invite code
    invite_code = generate_invite_code()
    
    # Create trip document in Firestore
    trip_data = {
        "origin": data["origin"],
        "destination": data["destination"],
        "stops": data.get("stops", []),
        "created_at": firestore.SERVER_TIMESTAMP,
        "participants": []
    }
    
    # Use invite code as document ID
    db.collection('trips').document(invite_code).set(trip_data)
    
    # Create shareable link with the new frontend URL format
    share_link = f"https://mapsyncfrontend-chi.vercel.app/trips/{invite_code}"
    
    return jsonify({
        "status": "success",
        "shareLink": share_link
    })

if __name__ == "__main__":
    app.run(debug=True)
