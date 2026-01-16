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

# --------------------------------
# ADD PET API
# --------------------------------
@app.route("/add-pet", methods=["POST"])
def add_pet():
    # Get JSON data from request
    data = request.get_json()

    # Extract pet details
    user_id = data.get("user_id")   # logged-in user id
    name = data.get("name")
    age = data.get("age")
    breed = data.get("breed")

    # Validate input
    if not user_id or not name or not age or not breed:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    try:
        # Create DB connection
        db = get_db_connection()
        cursor = db.cursor()

        # Insert pet into pets table
        cursor.execute(
            "INSERT INTO pets (user_id, name, age, breed) VALUES (%s, %s, %s, %s)",
            (user_id, name, age, breed)
        )

        # Save changes
        db.commit()

        # Close connection
        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Pet added successfully"
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# --------------------------------
# ADD REMINDER API
# --------------------------------
@app.route("/add-reminder", methods=["POST"])
def add_reminder():
    # Get JSON data from request
    data = request.get_json()

    # Extract reminder details
    pet_id = data.get("pet_id")
    vaccine_name = data.get("vaccine_name")
    due_date = data.get("due_date")  # format: YYYY-MM-DD

    # Validate input
    if not pet_id or not vaccine_name or not due_date:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    try:
        # Create DB connection
        db = get_db_connection()
        cursor = db.cursor()

        # Insert reminder into database
        cursor.execute(
            "INSERT INTO reminders (pet_id, vaccine_name, due_date) VALUES (%s, %s, %s)",
            (pet_id, vaccine_name, due_date)
        )

        # Save changes
        db.commit()

        # Close DB connection
        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Reminder added successfully"
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
# --------------------------------
# VIEW REMINDERS FOR A PET
# --------------------------------
@app.route("/reminders/<int:pet_id>", methods=["GET"])
def view_reminders(pet_id):
    try:
        # Create DB connection
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fetch reminders for the pet
        cursor.execute(
            "SELECT vaccine_name, due_date FROM reminders WHERE pet_id = %s",
            (pet_id,)
        )

        reminders = cursor.fetchall()

        # Close DB connection
        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "reminders": reminders
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
# --------------------------------
# ADD BOARDING REQUEST API
# --------------------------------
@app.route("/boarding-request", methods=["POST"])
def boarding_request():
    # Get JSON data from request
    data = request.get_json()

    # Extract request details
    user_id = data.get("user_id")
    pet_id = data.get("pet_id")
    start_date = data.get("start_date")  # YYYY-MM-DD
    end_date = data.get("end_date")      # YYYY-MM-DD

    # Validate input
    if not user_id or not pet_id or not start_date or not end_date:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    try:
        # Create DB connection
        db = get_db_connection()
        cursor = db.cursor()

        # Insert boarding request
        cursor.execute(
            """
            INSERT INTO boarding_requests (user_id, pet_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, pet_id, start_date, end_date)
        )

        # Save changes
        db.commit()

        # Close DB connection
        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Boarding request submitted"
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
# --------------------------------
# VIEW BOARDING REQUESTS FOR USER
# --------------------------------
@app.route("/boarding/<int:user_id>", methods=["GET"])
def view_boarding_requests(user_id):
    try:
        # Create DB connection
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fetch boarding requests for user
        cursor.execute(
            """
            SELECT br.id, br.start_date, br.end_date, br.status, p.name AS pet_name
            FROM boarding_requests br
            JOIN pets p ON br.pet_id = p.id
            WHERE br.user_id = %s
            """,
            (user_id,)
        )

        requests = cursor.fetchall()

        # Close DB connection
        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "requests": requests
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
