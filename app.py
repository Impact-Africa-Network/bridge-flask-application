from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("notes.sqlite")
    except sqlite3.error as e:
        print("Error connecting todb {err}").format(err=e), 
    return conn


@app.route("/notes", methods=["GET", "POST"])
def get_notes():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM notes")
        notes = [ 
            dict(id=row[0], title=row[1], detail=row[2], created_at=row[3])
            for row in cursor.fetchall()
        ]
        if notes is not None:
            return jsonify(notes)

    if request.method == 'POST':
        data =  request.get_json()

        title = data.get('title')
        detail = data.get('detail')

        sql = """INSERT INTO notes (title, detail)
        VALUES (?, ?)
        """
        cursor.execute(sql, (title,detail ))
        conn.commit()


        return jsonify({
            "id": cursor.lastrowid
        }), 201
    
    
@app.route('/notes/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def single_book(id):
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor =  conn.execute("SELECT * FROM notes WHERE id = ?", (id,))
        rows =  cursor.fetchall()
        note =  None

        for row in rows:
            note = row
        
        if note is not None:
            return jsonify(note)
        else:
            return "Could not find note", 404
    
    if request.method == 'PUT':
        for index,note in enumerate(notes_list):
            if note['id'] == id:
                data =  request.get_json()
                note['title'] = data.get('title')
                note['detail'] = data.get('detail')
                updated_note = {
                    'id': id,
                    'title': note['title'],
                    'detail': note['detail']
                }

                notes_list[index] = updated_note

                return jsonify(updated_note)
            
    if request.method == 'DELETE':
        for index, note in enumerate(notes_list):
            if note['id'] == id:
                notes_list.pop(index)
                return jsonify(notes_list)


# add here


if __name__ == '__main__':
    app.run(debug=True)

