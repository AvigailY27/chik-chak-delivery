from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import csv
from datetime import datetime
import allMain  # פונקציות ב-Backend

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# נתיב 1: העלאת קובץ משלוחים (מנהל)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file:
        # שמירת הקובץ בתיקייה
        today_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"delivery_best_{today_date}.csv"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            with open(filepath, 'a', newline='', encoding='utf-8') as existing_file:
                file.stream.seek(0)
                reader = csv.reader(file.stream.read().decode('utf-8').splitlines())
                writer = csv.writer(existing_file)
                next(reader, None)  # דילוג על כותרת
                for row in reader:
                    writer.writerow(row)
        else:
            with open(filepath, 'w', newline='', encoding='utf-8') as new_file:
                file.stream.seek(0)
                reader = csv.reader(file.stream.read().decode('utf-8').splitlines())
                writer = csv.writer(new_file)
                for row in reader:
                    writer.writerow(row)

        try:
            # קריאה לפונקציה שמחשבת את מספר השליחים הנדרשים
            num_couriers = allMain(filepath)
            return jsonify({
                "message": "File processed successfully!",
                "couriers_needed": num_couriers
            })
        except Exception as e:
            return jsonify({"message": "Error processing file.", "error": str(e)}), 500

# נתיב 2: מציאת משלוחים לפי אזור (שליח)
@app.route('/deliveries_by_area', methods=['POST'])
def get_deliveries_by_area():
    try:
        data = request.json
        area = data.get('area')  # האזור שבו השליח נמצא
        deliveries = allMain.get_deliveries_by_area(area)  # קריאה לפונקציה ב-Backend
        return jsonify({"deliveries": deliveries})
    except Exception as e:
        return jsonify({"message": "Error fetching deliveries.", "error": str(e)}), 500

# נתיב 3: חישוב מסלול לשליח (שליח)
@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    try:
        data = request.json
        courier_id = data.get('courier_id')  # מזהה השליח
        deliveries = data.get('deliveries')  # רשימת המשלוחים
        route = allMain.calculate_route(courier_id, deliveries)  # קריאה לפונקציה ב-Backend
        return jsonify({"route": route})
    except Exception as e:
        return jsonify({"message": "Error calculating route.", "error": str(e)}), 500

# נתיב 4: הצגת מפה עם מסלול
@app.route('/map')
def get_map():
    return send_from_directory('static', 'map_with_route.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)