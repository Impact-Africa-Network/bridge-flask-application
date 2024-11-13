from flask import Flask, request, jsonify

app = Flask(__name__)
notes_list = [
        {
            "id": 1,
            "title": "create flask project",
            "detail": "this is more detail on the note"
        },
        {
            "id": 2,
            "title": "setup database",
            "detail": "install SQLAlchemy and create models"
        },
        {
            "id": 3,
            "title": "create API endpoints",
            "detail": "implement REST API for CRUD operations"
        },
        {
            "id": 4,
            "title": "add authentication",
            "detail": "implement JWT authentication system"
        },
        {
            "id": 5,
            "title": "deploy application",
            "detail": "deploy to production server using gunicorn"
        }
    ]
@app.route("/notes", methods=["GET", "POST"])
def get_notes():
    if request.method == 'GET':
        print("here")
        return jsonify(notes_list)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        type = request.form['type']
        id = 'note_'+ str(len(notes_list)+1)

        print("welcome", title, content, type)

        new_obj = {
            'title': title,
            'content': content,
            'type': type,
            'id': id,
        }

        notes_list.append(new_obj)
        return jsonify(new_obj), 201
    
    
@app.route('/notes/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def single_book(id):
    if request.method == 'GET':
        for note in notes_list:
            if note['id'] == id:
                return jsonify(note)
            pass
    
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

