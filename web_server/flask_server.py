from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from datetime import datetime
import certifi

app = Flask(__name__)

client = MongoClient('mongodb+srv://jungbin1486:j3727416!!@cluster0.auzrugj.mongodb.net/', tlsCAFile=certifi.where())
db = client['focus_data']
collection = db['student_data']

@app.route('/')
def index():
    data = list(collection.find())
    return render_template('seconds.html', data=data)

@app.route('/api/get_focus_percentage', methods=['GET'])
def get_focus_percentage():
    try:
        lecture_name = request.args.get('lecture_name')

        query = {"lecture_name": lecture_name}

        data = list(collection.find(query))

        total_students = 0
        total_unfocused_students = 0
        focus_data = []

        for entry in data:
            total_students += entry['students']
            total_unfocused_students += entry['unfocused_students']
            focus_percentage = (entry['students'] - entry['unfocused_students']) / entry['students'] * 100 if entry['students'] > 0 else 0
            focus_data.append({
                "date": entry['date'].strftime('%Y-%m-%d'),
                "focus_percentage": focus_percentage
            })

        average_focus_percentage = (total_students - total_unfocused_students) / total_students * 100 if total_students > 0 else 0

        return jsonify({
            "average_focus_percentage": average_focus_percentage,
            "total_students": total_students,
            "focus_data": focus_data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_lectures', methods=['GET'])
def get_lectures():
    pipeline = [
        {
            "$group": {
                "_id": "$lecture_name"
            }
        }
    ]
    lectures = list(collection.aggregate(pipeline))

    lecture_names = [lecture['_id'] for lecture in lectures]

    return jsonify(lecture_names)

if __name__ == '__main__':
    app.run(debug=True, port=5004)
