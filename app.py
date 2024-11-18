from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
from flask_cors import CORS, cross_origin

# malformed json data - validation
# sql injection vulnerability
# improperly handled error message eg for 500 errors
# concurrency issues 
app = Flask(__name__)

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
def get_notes():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM notes")
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

        sql = """INSERT INTO notes (title, detail)
        VALUES (?, ?)
        """
        cursor.execute(sql, (title, detail))
        conn.commit()
        return jsonify({
            "id": cursor.lastrowid,
            "title": title,
            "detail": detail,
        }), 201

@app.route('/notes/<int:id>', methods=['GET', 'DELETE'])
def note_operations(id):
    conn = db_connection()
    cursor = conn.cursor()

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



if __name__ == '__main__':
    app.run(debug=True)

