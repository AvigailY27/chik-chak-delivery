from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
from datetime import datetime
import main
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ליצור תיקייה אם אינה קיימת
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part in request")
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        print("No selected file")
        return jsonify({"message": "No selected file"}), 400

    if file:
        # יצירת שם קובץ עם תאריך
        today_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"delivery best{today_date}.csv"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # בדיקה אם הקובץ כבר קיים
        if os.path.exists(filepath):
            print(f"File {filename} already exists. Appending data...")
            # הוספת הנתונים לקובץ הקיים
            with open(filepath, 'a', newline='', encoding='utf-8') as existing_file:
                reader = csv.reader(file.stream.read().decode('utf-8').splitlines())
                writer = csv.writer(existing_file)
                next(reader, None)  # דילוג על הכותרת
                for row in reader:
                    writer.writerow(row)
        else:
            print(f"Creating new file: {filename}")
            
            # שמירת קובץ חדש
            with open(filepath, 'w', newline='', encoding='utf-8') as new_file:
                reader = csv.reader(file.stream.read().decode('utf-8').splitlines())
                writer = csv.writer(new_file)
                for row in reader:
                    writer.writerow(row)
    print("Calling main.main()...")
    try:
        main.main()
        #צריך שמכאן יחזיר מפה עם המסלול לריאקט אולי דרך הmain
        print("main.main() executed successfully.")
    except Exception as e:
        print(f"Error while running main.main(): {e}")
    print(f"File saved at: {filepath}")
    return jsonify({"message": f"הקובץ '{filename}' נשמר בהצלחה במערכת. תודה על שיתוף הפעולה!"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)