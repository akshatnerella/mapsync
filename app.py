from flask import Flask, request, jsonify

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
