from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import csv
from datetime import datetime
from deliver import Delivery
import deliver as deliver
import main
import json
import allMain as allMain
from process import process_input_file
import newnewosm as osm1
import kmeans1 as kmeans1
import shortpathme as shortpathme
from flask import Flask,send_file
from flask_cors import CORS
from global_state import graphmaps, nodes, edges, get_or_create_courier
from flask import make_response

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/process_data', methods=['POST'])
def process_data():
    try:
        if 'file' in request.files:
            # טיפול במקרה של העלאת קובץ
            file = request.files['file']
            print("Received file:", file.filename)  # הדפסת שם הקובץ שהתקבל

            if file.filename == '':
                return jsonify({"message": "No selected file"}), 400

            # קריאת תוכן הקובץ
            file_content = file.read().decode('utf-8')
            
            # שמירת הקובץ
            today_date = datetime.now().strftime('%Y-%m-%d')
            filename = f"delivery_best_{today_date}.csv"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(filepath, 'w', newline='', encoding='utf-8') as new_file:
                new_file.write(file_content)

            print(f"File saved successfully at {filepath}")  # הדפסת מיקום הקובץ שנשמר

            # קריאה לפונקציה main.main עם הנתיב של הקובץ
            num_couriers, courier_workload,missing_couriers  = allMain.Cluster(data_source=filepath, graphmaps=graphmaps)
            
            if num_couriers == -1 or not courier_workload:
                return jsonify({"message": "Error processing data. Not enough couriers available.", "couriers_needed":missing_couriers })
            allMain.assign_couriers_to_clusters()
        elif 'tableData' in request.form:
            # טיפול במקרה של מילוי טופס
            table_data = request.form.get('tableData')
            table_data = json.loads(table_data)  # המרת JSON למבנה פייתון
            print("Received table data:", table_data)

            if not table_data:
                return jsonify({"message": "No valid data provided.", "couriers_needed": 0}), 400

            # קריאה לפונקציה main.main עם נתוני הטופס
            num_couriers, courier_workload,missing_couriers  = allMain.Cluster(table_data=table_data, graphmaps=graphmaps)
            if num_couriers == -1 or not courier_workload:
                return jsonify({"message": "Error processing data. Not enough couriers available.", "couriers_needed":missing_couriers })
            allMain.assign_couriers_to_clusters()
        else:
            return jsonify({"message": "No valid data provided."}), 400
        # החזרת תגובה ללקוח
        return jsonify({
            "message": "Data processed successfully!",
            "couriers_needed": num_couriers
        })

    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"message": "Error processing data.", "error": str(e)}), 500
    
@app.route('/couriers', methods=['GET', 'POST'])
def manage_couriers():
    couriers_file = r"C:\Users\WIN 11\PycharmProjects\pythonProjectyolo\delivery-form\chik-chak-delivery\couriers.json"

    if request.method == 'GET':
        if os.path.exists(couriers_file):
            with open(couriers_file, 'r', encoding='utf-8') as file:
                try:
                    couriers = json.load(file)
                except json.JSONDecodeError:
                    couriers = []
            return jsonify({"message": "Existing couriers found.", "couriers": couriers})
        else:
            return jsonify({"message": "No couriers found.", "couriers": []})

    elif request.method == 'POST':
        new_couriers = request.json.get('couriers', [])

        # טען שליחים קיימים (אם קיימים)
        if os.path.exists(couriers_file):
            with open(couriers_file, 'r', encoding='utf-8') as file:
                try:
                    existing_couriers = json.load(file)
                except json.JSONDecodeError:
                    existing_couriers = []
        else:
            existing_couriers = []

        # סינון שליחים שכבר קיימים לפי id
        existing_ids = {c['id'] for c in existing_couriers}
        added_couriers = [c for c in new_couriers if c['id'] not in existing_ids]
        updated_couriers = existing_couriers + added_couriers

        # כתיבה חזרה לקובץ JSON
        with open(couriers_file, 'w', encoding='utf-8') as file:
            json.dump(updated_couriers, file, ensure_ascii=False, indent=4)

        return jsonify({
            "message": f"נשמרו {len(added_couriers)} שליחים חדשים בהצלחה.",
            "total_couriers": len(updated_couriers)
        })
@app.route('/assign_couriers', methods=['POST'])
def assign_couriers():
    try:
        data = request.json
        deliveries = data.get('deliveries', [])
        couriers = data.get('couriers', [])

        # חלוקת המשלוחים לאזורים
        clusters = {}  # מיפוי אזורים לרשימת משלוחים
        for delivery in deliveries:
            cluster = delivery['cluster']
            if cluster not in clusters:
                clusters[cluster] = []
            clusters[cluster].append(delivery)

        # שיוך שליחים לאזורים
        assignments = {}  # מיפוי שליחים לאזורים
        courier_index = 0
        for cluster, cluster_deliveries in clusters.items():
            if courier_index >= len(couriers):
                break
            courier = couriers[courier_index]
            assignments[courier['id']] = {
                'cluster': cluster,
                'deliveries': cluster_deliveries
            }
            courier_index += 1

        # שמירת הנתונים בקובץ JSON
        assignments_file = os.path.join(app.config['UPLOAD_FOLDER'], 'assignments.json')
        with open(assignments_file, 'w', encoding='utf-8') as file:
            json.dump(assignments, file, ensure_ascii=False, indent=4)

        return jsonify({"message": "Couriers assigned successfully!", "assignments": assignments})
    except Exception as e:
        print(f"Error assigning couriers: {e}")
        return jsonify({"message": "Error assigning couriers.", "error": str(e)}), 500

#מחפש את המשלוחים של השליח והאזור שלו
@app.route('/get_deliveries_by_phone/<phone>', methods=['GET'])
def get_deliveries_by_phone(phone):
    try:
        # ניקוי מספר טלפון
        clean_phone = phone.replace("-", "").strip()

        # טען את הקובץ שמכיל גם את השליחים לאזורים
        with open('couriers_with_clusters.json', 'r', encoding='utf-8') as f:
            courier_clusters = json.load(f)

        # מצא את השליח
        courier = next((c for c in courier_clusters if c['phone'].replace("-", "") == clean_phone), None)
        print("Courier raw data:", courier)
        if not courier:
            return jsonify({"message": "מספר הטלפון לא מזוהה במערכת."}), 404

        # קח את האשכול (האזור)
        cluster = courier.get('cluster')
        if not cluster:
            return jsonify({"message": "אין אשכול משויך לשליח. אין לו מסלול היום."}), 404

        # טען את קובץ המשלוחים לפי אזורים
        with open('cluster_nodes.json', 'r', encoding='utf-8') as f:
            cluster_nodes = json.load(f)
        deliveries = cluster_nodes.get(cluster, [])
        if not deliveries:
            return jsonify({"message": "לא נמצאו משלוחים לאשכול שלך."}), 404
        # מסדר את המשלוחים לפי סדר עדיפות
        print("Delivery objects:", deliveries)
        deliveriesOk, not_relevant_with_reason = allMain.sortQueue(courier['phone'], deliveries, graphmaps)
        print("Sorted deliveries:", deliveriesOk)
        print("Not relevant deliveries:", not_relevant_with_reason)
        return jsonify({
            "cluster": cluster,
            "deliveries":[d.to_dict() for d in deliveriesOk],
            "notdeliveries": [d1.to_dict() for d1 in not_relevant_with_reason],
            "courier": courier,
        })

    except Exception as e:
        print(f"שגיאה בשרת: {e}")
        return jsonify({"message": "שגיאה בשרת", "error": str(e)}), 500

@app.route('/get_route', methods=['POST'])
def get_route():
    data = request.get_json()
    deliveries = data.get('deliveries', [])
    courier = data.get('courierInfo')
    courier_data = get_or_create_courier(courier['phone'])
    delay_heap=courier_data['delay_heap']
    delivery_list = courier_data['delivery_list']
    if not deliveries or not courier:
        return jsonify({'message': 'Missing data: deliveries or courier'}), 400

    try:
        # יצירת אובייקט שליח
        deliveries = [
            deliver.Delivery(
                destination=d['destination'],
                timeMax=d['timeMax'],
                start=d['start'],
                end=d['end']
            )
            for d in deliveries
        ]
        print('current_location', courier['current_location'])
        first_destination = deliveries[0].destination
        print('first_destination', first_destination)
        courier['current_location'] = first_destination

        #עדכון המזמני נסיעה על הגרף 
        # allMain.update_graph_with_traffic_weights(graphmaps)

        # אופטימיזציית מסלול: הפעלת כל שלבי העדיפות והאופטימיזציה
        optimal_route_list = allMain.optimize_deliveries_route(deliveries, graphmaps, courier)
        # החזרת המסלול (לפי הסדר האופטימלי)
        print('route', optimal_route_list.to_list())
         #הסרת המשלוח שבוצע 
        success = delivery_list.remove_delivery_by_destination(first_destination)
        print('success', success)
        if not success:
            return jsonify({"error": "Failed to remove delivery"}), 500
        #הסרת משלוח מהערימה
        delay_heap.remove_node(first_destination)
        return jsonify({
            'route': optimal_route_list.to_list(),
            'current_location': courier['current_location'],
        }), 200
    except Exception as e:
        print('Server error:', e)
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500


# 1. נקודה שמייצרת את המפה ושומרת אותה
@app.route('/generate_map', methods=['POST'])
def generate_map():
    data = request.get_json()
    addresses = [d['destination'] for d in data['deliveries']]
    start_address = [data['start_address']]
    print("Start:", start_address)
    print("Addresses:", addresses)
    if not addresses or not start_address:
        return jsonify({'message': 'No valid addresses provided'}), 400
    shortpathme.draw_ordered_route(graphmaps, addresses, start_address)
    return jsonify({'message': 'Map generated'}), 200
# 2. נקודה שמחזירה את הקובץ שנוצר
import os

STATIC_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
MAP_PATH = os.path.join(STATIC_FOLDER, "map_with_route.html")



@app.route('/get_map_html')
def get_map_html():
    response = make_response(send_file(MAP_PATH))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
