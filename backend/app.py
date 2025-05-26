from flask import Flask, request, jsonify

app = Flask("mapsync")

@app.route("/", methods=["GET"])
def home():
    return "Welcome to MapSync Backend", 200

@app.route("/sync", methods=["POST"])
def sync_google_maps():
    """
    Endpoint to sync a user's Google Maps data and routes.
    Expects a JSON payload with:
      - user_id: The user's identifier.
      - google_maps_data: A dict containing the maps and routes details.
    """
    data = request.get_json()
    if not data or "user_id" not in data or "google_maps_data" not in data:
        return jsonify({"error": "Invalid payload. 'user_id' and 'google_maps_data' required."}), 400

    user_id = data["user_id"]
    maps_data = data["google_maps_data"]

    # TODO: Implement syncing logic with Google Maps API here.

    return jsonify({
        "message": "Data synced successfully",
        "user_id": user_id,
        "maps_data": maps_data
    }), 200

@app.route("/routes", methods=["GET"])
def get_routes():
    """
    Endpoint to retrieve synced routes for a user.
    Expects a query parameter:
      - user_id: The user's identifier.
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing 'user_id' parameter."}), 400

    # TODO: Replace with actual route retrieval logic.
    dummy_routes = [
        {"route_id": 1, "name": "Morning Commute", "distance": "12 km"},
        {"route_id": 2, "name": "Evening Run", "distance": "5 km"}
    ]

    return jsonify({
        "user_id": user_id,
        "routes": dummy_routes
    }), 200

if __name__ == "__main__":
    app.run(debug=True)