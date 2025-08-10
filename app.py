from flask import Flask, request, jsonify, render_template
import asyncio
from scraper.attendance_scraper import fetch_attendance, fetch_library_books, fetch_bio_data
from flask_cors import CORS

app = Flask(__name__)

# ✅ Allow all origins — safe for development only
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('P.html')  # Make sure P.html is inside 'templates/'

@app.route('/get-bio-data', methods=['POST'])
def get_bio_data():
    try:
        creds = request.get_json()
        username = creds.get('username')
        password = creds.get('password')

        data = asyncio.run(fetch_bio_data(username, password))
        return jsonify({"data": data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-attendance', methods=['POST'])
def get_attendance():
    try:
        creds = request.get_json()
        username = creds.get('username')
        password = creds.get('password')

        data = asyncio.run(fetch_attendance(username, password))
        return jsonify({"data": data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-library-books', methods=['POST'])
def get_library_books():
    try:
        creds = request.get_json()
        username = creds.get('username')
        password = creds.get('password')

        data = asyncio.run(fetch_library_books(username, password))
        return jsonify({"data": data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
