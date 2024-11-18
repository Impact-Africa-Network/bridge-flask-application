from flask import Flask, request, jsonify,g
import sqlite3
from flask_cors import CORS
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import jwt
import bcrypt

from functions import token_required

app = Flask(__name__)
app.config['SECRET_KEY'] = '7721288HGHHAGDFGS423212'

cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

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
def get_notes():
    conn = db_connection()
    cursor = conn.cursor()

    user = g.user

    user_id = user['user_id']


    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM notes WHERE user_id=?", (user_id,))
        notes = [
            dict(id=row[0], title=row[1],detail=row[2],created_at=row[3])
            for row in cursor.fetchall()
        ]
        if notes is not None:
            return jsonify(notes)
        else:
            return "No Notes found in database", 200
        
    if request.method == 'POST':
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
    conn = db_connection()
    cursor = conn.cursor()

    user = g.user

    user_id = user['user_id']

    if request.method == 'GET':
        cursor.execute("SELECT * FROM notes WHERE id=? AND user_id=?", (id, user_id))
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

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username =  data['username']
    email =  data['email']
    password =  data['password']
    conn = db_connection()
    cursor =  conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


    try:
        # pass
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email)
            )
            conn.commit()

            cursor.execute(
                "SELECT id, username, email FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()

            return jsonify({
                "id": user[0],
                "username": user[1],
                "email": user[2]
            }), 201
    except sqlite3.IntegrityError:
        return jsonify({
            "error":"username or email already exists"
        }), 409

    finally:
        conn.close()

    pass
@app.route('/login', methods = ['POST'])
def login():
    # get the post data - username and password
    data = request.get_json()

    username =  data['username']
    password =  data['password']
    conn = db_connection()
    cursor =  conn.cursor()
    try:
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", 
                      (username,))       
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"})
        # check if password is correct

        if not bcrypt.checkpw(password.encode("utf-8"), user[2]):
            return jsonify({"error": "Password is not correct"})
    
        token = jwt.encode({
            'user_id': user[0],
            'username': user[1],
            'exp': datetime.utcnow() + timedelta(minutes=50)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "token":token,
            "username": username,
        })
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)

