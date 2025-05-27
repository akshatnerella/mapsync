from flask import Flask, request, jsonify
from firebase_admin import auth, initialize_app, firestore
from flask_cors import CORS
import random
import string
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Determine the environment and set CORS origins accordingly
FLASK_ENV = os.getenv('FLASK_ENV')

if FLASK_ENV == 'production':
    # For production, allow requests from your deployed frontend URL
    CORS(app, resources={r"/*": {"origins": "https://mapsync.onrender.com"}})
    print("CORS configured for production (https://mapsync.onrender.com)")
else:
    # For development, allow requests from localhost:5173
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    print("CORS configured for development (http://localhost:5173)")

# Initialize Firebase Admin SDK conditionally
db = None

if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        print("Please ensure your GOOGLE_APPLICATION_CREDENTIALS environment variable points to a valid service account key file.")
else:
    print("GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
    print("Firebase will not be initialized. Please set the environment variable to enable Firestore access.")

def generate_invite_code(length=6):
    characters = string.ascii_uppercase + string.digits
    if not db:  # If no Firebase, just return a random code
        return ''.join(random.choices(characters, k=length))
    
    while True:
        code = ''.join(random.choices(characters, k=length))
        try:
            existing_trip = db.collection('trips').document(code).get()
            if not existing_trip.exists:
                return code
        except Exception:
            return code  # If Firebase fails, just return the code

@app.route("/newtrip", methods=["POST"])
def create_trip():
    data = request.json
    required = ["origin", "destination", "stops"]
    if not all(field in data for field in required):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Generate unique invite code
    invite_code = generate_invite_code()
    
    # Create trip data matching the frontend Trip interface
    trip_data = {
        "id": invite_code,
        "origin": data["origin"],
        "destination": data["destination"],
        "stops": [{
            "id": f"stop-{i}",
            "name": stop,
            "address": stop
        } for i, stop in enumerate(data["stops"])],
        "createdAt": datetime.utcnow().isoformat(),
        "createdBy": "user123"  # You can update this with actual user ID when auth is implemented
    }
    
    # Try to save to Firebase if available
    if db:
        try:
            db.collection('trips').document(invite_code).set(trip_data)
        except Exception as e:
            print(f"Firebase error: {e}")
            # Continue even if Firebase fails
    
    return jsonify({
        "status": "success",
        "shareLink": f"trips/{invite_code}"
    })

@app.route("/trips/<code>", methods=["GET"])
def get_trip(code):
    print(f"Attempting to fetch trip with code: {code}")  # Debug logging
    
    if not db:
        print("Firestore not initialized (db object is None).")  # More specific logging
        return jsonify({"status": "error", "message": "Database not available. Firebase not initialized."}), 503
    
    try:
        print(f"Querying Firestore for trip: {code}")  # Debug logging
        trip_ref = db.collection('trips').document(code)
        trip_data = trip_ref.get()
        
        if trip_data.exists:
            trip_dict = trip_data.to_dict()
            print(f"Found trip: {trip_dict}")  # Debug logging
            return jsonify({
                "status": "success",
                "trip": trip_dict
            })
        else:
            print(f"Trip not found: {code}")  # Debug logging
            return jsonify({"status": "error", "message": "Trip not found"}), 404
            
    except Exception as e:
        print(f"Error fetching trip: {str(e)}")  # Debug logging
        return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
