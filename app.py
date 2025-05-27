from flask import Flask, request, jsonify
from firebase_admin import auth, initialize_app, firestore
from flask_cors import CORS
import random
import string
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "https://mapsyncfrontend-chi.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize Firebase with a default app if credentials are not available
try:
    initialize_app()
    db = firestore.client()
except Exception as e:
    print(f"Warning: Running without Firebase: {e}")
    db = None

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

if __name__ == "__main__":
    app.run(debug=True)
