from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

DATA_FILE = 'students.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            return data.get('students', [])
        except json.JSONDecodeError:
            return []

def save_data(students):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'students': students}, f, ensure_ascii=False, indent=2)

def get_next_id(students):
    if not students:
        return 1
    return max(s['id'] for s in students) + 1

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/students', methods=['GET'])
def list_students():
    students = load_data()
    return jsonify(students)

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    students = load_data()
    student = next((s for s in students if s['id'] == student_id), None)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data or 'nom' not in data or 'prenom' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    students = load_data()
    student = {
        'id': get_next_id(students),
        'nom': data['nom'],
        'prenom': data['prenom'],
        'classe': data.get('classe', ''),
        'age': data.get('age')
    }
    students.append(student)
    save_data(students)
    return jsonify(student), 201

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    students = load_data()
    student = next((s for s in students if s['id'] == student_id), None)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    student.update({
        'nom': data.get('nom', student['nom']),
        'prenom': data.get('prenom', student['prenom']),
        'classe': data.get('classe', student.get('classe', '')),
        'age': data.get('age', student.get('age'))
    })
    save_data(students)
    return jsonify(student)

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    students = load_data()
    new_students = [s for s in students if s['id'] != student_id]
    if len(new_students) == len(students):
        return jsonify({'error': 'Student not found'}), 404
    save_data(new_students)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
