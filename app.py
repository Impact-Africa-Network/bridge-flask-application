from flask import Flask, request, jsonify, g
import sqlite3
from flask_cors import CORS
from flask_cors import CORS, cross_origin
import jwt
import bcrypt
from functions import token_required
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SECRET_KEY'] = 'KEEP_IT_A_SECRET'
from datetime import datetime, timedelta

cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

# db = SQLAlchemy(app)

CORS(app, resources={r"/*": {"origins": "*"}})



# Or even simpler:
CORS(app)
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("notes.sqlite")
    except sqlite3.error as e:
        print("Error connecting to data {err}".format(err=e))

    return conn
@app.route('/notes', methods=['GET', 'POST'])
@token_required
def get_post_notes():
    conn = db_connection()
    cursor = conn.cursor()
    user = g.user
    user_id = user.get('user_id')

    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM notes where user_id =?", (user_id,))
        notes = [
            dict(id=row[0], title=row[1],detail=row[2],created_at=row[4], user_id=row[3])
            for row in cursor.fetchall()
        ]
        if notes is not None:
            return jsonify(notes)
        else:
            return "No Notes found in database", 200
        
    if request.method == 'POST':
        user = g.user
        user_id = user.get('user_id')
        data =  request.get_json()

        title = data.get('title')
        detail = data.get('detail')

        sql = """INSERT INTO notes (title, detail, user_id)
        VALUES (?, ?, ?)
        """
        cursor.execute(sql, (title, detail, user_id))
        conn.commit()
        return jsonify({
            "id": cursor.lastrowid,
            "title": title,
            "user_id": user_id,
            "detail": detail,
        }), 201

@app.route('/notes/<int:id>', methods=['GET', 'DELETE'])
@token_required
def note_operations(id):
    current_user =  g.user
    conn = db_connection()
    cursor = conn.cursor()
    print('user', current_user)
    if request.method == 'GET':
        cursor.execute("SELECT * FROM notes WHERE id=?", (id,))
        note = cursor.fetchone()
        
        if note is not None:
            return jsonify({
                "id": note[0],
                "title": note[1],
                "detail": note[2],
                "created_at": note[3]
            })
        return jsonify({"message": "Note not found"}), 404

    if request.method == 'DELETE':
        cursor.execute("DELETE FROM notes WHERE id=?", (id,))
        conn.commit()
        
        return jsonify({
            "message": f"Note {id} deleted successfully"
        }), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(k in data for k in ["username", "password"]):
        return jsonify({"error": "Missing username or password"}), 400

    conn = db_connection()
    cursor = conn.cursor()
    
    try:

        # Get user from database
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", 
                      (data["username"],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Check password
        if not bcrypt.checkpw(data["password"].encode('utf-8'), user[2]):
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': user[0],
            'username': user[1],
            'exp': datetime.utcnow() + timedelta(minutes=50)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "token": token,
            "username": user[1]
        }), 200
        
    finally:
        conn.close()

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not all(k in data for k in ["username", "password", "email"]):
            return jsonify({"error": "Missing required fields"}), 400

        hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
        
        conn = db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (data["username"], hashed_password, data["email"])
            )
            conn.commit()
            
            # Get created user
            cursor.execute(
                "SELECT id, username, email FROM users WHERE username = ?",
                (data["username"],)
            )
            user = cursor.fetchone()
            
            return jsonify({
                "id": user[0],
                "username": user[1],
                "email": user[2]
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({"error": "Username or email already exists"}), 409
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

