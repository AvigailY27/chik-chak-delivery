import osmnx as ox
import networkx as nx
import pandas as pd
import os
from yoloFile import newyolo as yolov
from osmFile import speedkh as speed


#   יעד -מחלקת צומת
class Intersection:
    def __init__(self, idins):
        self.id = idins
        self.connected_edges = []  # קשתות מחוברות לצומת


# מחלקה שמייצגת קשת (כביש)במסלול
class Edge:
    def __init__(self, length, lanes, from_intersection, to_intersection, direction, load, timest):
        self.length = round(length)  # אורך הכביש
        self.lanes = lanes  # כמות נתיבים
        self.from_intersection = from_intersection  # צומת התחלה
        self.to_intersection = to_intersection  # צומת סיום
        self.direction = direction  # 'forward' או 'backward'
        self.load = load  # העומס בקשת
        self.times = timest


#  פונקציה לחישוב עומס
def calculate_load(num_vehicles, length, lanes):
    # חישוב עומס לפי הנוסחה: (מספר רכבים * אורך כביש) / מספר נתיבים
    if lanes == 0 or num_vehicles == 0 or length == 0:
        return 0
    return round(float(num_vehicles) / float(lanes) * length)


#  יצירת גרף ממקום מסוים
def map_mapping_graf(place_name):
    graphmap = ox.graph_from_place(place_name, network_type="drive")
    nodes, edges = ox.graph_to_gdfs(graphmap)
    return graphmap, nodes, edges


def calculate_travel_time(distance_km, speed_kmh, traffic_factor=1.0):
    """
    מחשבת זמן נסיעה בכביש לפי מרחק, מהירות מותרת ועומס תנועה.

    :param distance_km: אורך הכביש בקילומטרים
    :param speed_kmh: מהירות מותרת בקמ"ש
    :param traffic_factor: מקדם עומס תנועה (ערך בין 0 ל-1, שבו 1 = תנועה זורמת, 0.5 = עומס גבוה)
    :return: זמן נסיעה משוער בדקות
    """

    if speed_kmh is None or speed_kmh <= 0:
        raise ValueError("המהירות חייבת להיות חיובית")

    actual_speed = speed_kmh * traffic_factor  # מהירות בפועל לפי עומס תנועה

    if actual_speed <= 0:
        raise ValueError("המהירות בפועל נמוכה מדי, כנראה פקק מוחלט")

    time_hours = distance_km / actual_speed  # זמן בשעות
    time_minutes = time_hours * 60  # המרה לדקות
    return time_minutes


# אם אין ערך ב-lanes, נשתמש בנתון highway כדי להעריך
def estimate_lanes(edge_data):
    highway_type = edge_data.get('highway', 'unknown')

    # מיפוי לפי סוג הדרך
    highway_lanes = {
        'motorway': 4,
        'trunk': 3,
        'primary': 3,
        'secondary': 2,
        'tertiary': 2,
        'residential': 1,
        'service': 1
    }
    return highway_lanes.get(highway_type, 1)  # ברירת מחדל: 1 נתיב


video_path = "E:\לימודים\יד\פרויקט גמר\קצר.mp4"
output_file = "E:\לימודים\יד\פרויקט גמר\קצר.txt"
lanswidth = 420
langthveicle = 220


#  סיווג צמתים ושיוך קשתות
def classify_intersections(graphmap):
    intersections = {}

    for node in graphmap.nodes():
        intersection = Intersection(node)
        connected_edges = list(graphmap.edges(node, keys=True))
        #  הוספת הקשתות המחוברות לצומת
        for u, v, key in connected_edges:
            edge_data = graphmap.get_edge_data(u, v, key) or {}
            print(edge_data)
            # print(edge_data.keys())
            # print(edges[['lanes']])
            #         edge_data = graphmap.get_edge_data(u, v, k)
            # נוודא שנקבל את ה-lanes בצורה נכונה
            lanes = estimate_lanes(edge_data)
            # lanes = edge_data.get('lanes', 1)
            length = (edge_data.get('length', 1))
            direction = 'forward' if edge_data.get('oneway', False) else 'backward'
            sumveicle = yolov.analyze_traffic(video_path, output_file, lanswidth, lanes, langthveicle, 200)
            print("סכום")
            print(sumveicle)
            #  נישמור במשתנה load את העומס בקשת שלו לפי ניתוח סירטון שהתקבל ממצלמות
            load = calculate_load(sumveicle, length, lanes)
            timest = calculate_travel_time(length, speed.get_edge_speed(edge_data))
            # עדכון משקל הקשת לפי זמן נסיעה
            nx.set_edge_attributes(graphmap, {(u, v, 0): {'weight': timest}})
            edge = Edge(length, lanes, u, v, direction, load, timest)
            intersection.connected_edges.append(edge)
            intersections[node] = intersection
        return intersections  # מחזיר את כל הצמתים ואיזה קשתות מחובורת לכל צומת


#  שמירת הצמתים ל-CSV (ללא כפילויות)
filename1 = r"C:\Users\WIN 11\PycharmProjects\pythonProjectyolo\intersections_data.csv"


def save_intersections_to_csv(intersections, filename=filename1):
    data = []
    for node, intersection in intersections.items():
        for edge in intersection.connected_edges:
            data.append({
                "צומת": node,
                "מצומת": edge.from_intersection,
                "אל צומת": edge.to_intersection,
                "אורך הכביש (מ')": edge.length,
                "מספר נתיבים": edge.lanes,
                "חד/דו סטרי": "חד-סטרי" if edge.direction == "forward" else "דו-כיווני",
                "עומס": edge.load,
                "זמן נסיעה": edge.times
            })

    new_data = pd.DataFrame(data)

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            old_data = pd.read_csv(filename, encoding="utf-8-sig")
            combined_data = pd.concat([old_data, new_data], ignore_index=True).drop_duplicates()
        except Exception as e:
            print(f"שגיאה בקריאת הקובץ: {e}")
            combined_data = new_data
    else:
        combined_data = new_data

    combined_data.to_csv(filename, index=False, mode='w', encoding="utf-8-sig")  # כתיבה מחדש בלי כפילות
    print(f" הנתונים נשמרו בהצלחה  ")


"""
# ✅ הפעלת כל החלקים
place_name = "אלעד, ישראל"
graphmaps, nodes, edges = map_mapping_graf(place_name)
intersections = classify_intersections(graphmaps)
# save_intersections_to_csv(intersections)  # שמירה לקובץ

# ✅ הדפסת נתונים
for node, intersections in intersections.items():
    print(f"\nצומת {intersections.id} | קשתות מחוברות: {len(intersections.connected_edges)}")
for edge in intersections.connected_edges:
    print(f" ️קשת: אורך {edge.length} מ', נתיבים: {edge.lanes}, חד סטרי/דו סטרי: {edge.direction}, "
          f"עומס: {edge.load}, זמן נסיעה: {edge.times}")

    #  הצגת המפה
# fig, ax = ox.plot_graph(graphmaps, show=True, close=False)
"""
