# Import Flask modules
from flask import Flask, jsonify, request

# Import CORS to allow frontend calls
from flask_cors import CORS

# Import password hashing utility
from werkzeug.security import generate_password_hash

# Import database connection function
from db import get_db_connection

# Import password verification utility
from werkzeug.security import check_password_hash


# Create Flask app instance
app = Flask(__name__)

# Enable CORS
CORS(app)

# --------------------------------
# HOME ROUTE (TEST)
# --------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "Pet Care Platform Backend Running"
    })


# --------------------------------
# SIGNUP API (REAL DATABASE)
# --------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    # Get JSON data from request body
    data = request.get_json()

    # Extract user details
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not name or not email or not password:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    # Hash password before storing
    hashed_password = generate_password_hash(password)

    try:
        # Create database connection
        db = get_db_connection()
        cursor = db.cursor()

        # SQL query to insert user
        query = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """

        # Execute query with values
        cursor.execute(query, (name, email, hashed_password))

        # Save changes to DB
        db.commit()

        # Close DB connection
        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "message": "User registered successfully"
        }), 201

    except Exception as e:
        # Handle errors (like duplicate email)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# --------------------------------
# LOGIN API
# --------------------------------
@app.route("/login", methods=["POST"])
def login():
    # Get JSON data from request
    data = request.get_json()

    # Extract login credentials
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required"
        }), 400

    try:
        # Connect to database
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fetch user by email
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        # Close DB connection
        cursor.close()
        db.close()

        # If user not found
        if not user:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        # Verify hashed password
        if not check_password_hash(user["password"], password):
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        # Login successful
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
