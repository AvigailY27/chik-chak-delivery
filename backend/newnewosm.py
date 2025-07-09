import osmnx as ox
import networkx as nx
import pandas as pd
import os
import newyolo as yolov
import kmeans1 as kmeans1
import speedkh as speedgb
from shapely.geometry import LineString
from shapely.wkt import loads as wkt_loads
import osmnx as ox
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


def calculate_travel_time(distance_km, speed_kmh, traffic_factor):
    """
    מחשבת זמן נסיעה בכביש לפי מרחק, מהירות מותרת ועומס תנועה.
    :param distance_km: אורך הכביש בקילומטרים
    :param speed_kmh: מהירות מותרת בקמ"ש
    :param traffic_factor: מקדם עומס תנועה (ערך בין 0 ל-1, שבו 1 = תנועה זורמת, 0.5 = עומס גבוה)
    :return: זמן נסיעה משוער בדקות
    """
    try:
        speed_kmh = float(speed_kmh)
    except (TypeError, ValueError):
        raise ValueError(f"speed_kmh חייב להיות מספר, קיבלתי: {speed_kmh}")
    if speed_kmh is None or speed_kmh <= 0:
        raise ValueError("המהירות חייבת להיות חיובית")
    actual_speed = speed_kmh * traffic_factor  # מהירות בפועל לפי עומס תנועה
    if actual_speed <= 0:
        raise ValueError("המהירות בפועל נמוכה מדי, כנראה פקק מוחלט")

    time_hours = distance_km / actual_speed  #   לפי הנוסחה דרך\מהירות= זמן בשעות
    time_minutes = time_hours * 60  # המרה לדקות
    # חישוב שעות ודקות
    hours, minutes = divmod(time_minutes, 60)
    hours = int(hours)  # המרת שעות למספר שלם
    minutes = int(minutes)  # המרת דקות למספר שלם
    print(f"זמן נסיעה משוער: {minutes} דקות : {hours}שעות :")
    return time_minutes  # החזרת זמן הנסיעה בדקות


# אם אין ערך ב-lanes, נשתמש בנתון highway כדי להעריך
def estimate_lanes(edge_data):
    highway_type = edge_data.get('highway', 'unknown')
    if isinstance(highway_type, list):
        highway_type = highway_type[0]  # אם יש רשימה, נשתמש באלמנט הראשון
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
def clean_graph_attributes(graph):
    unsupported_types = (list, LineString)  # סוגי נתונים שאינם נתמכים
    for u, v, key, data in graph.edges(keys=True, data=True):
        for attr in list(data.keys()):
            if isinstance(data[attr], unsupported_types):
                del data[attr]  # הסרת המאפיין

    for node, data in graph.nodes(data=True):
        for attr in list(data.keys()):
            if isinstance(data[attr], unsupported_types):
                del data[attr]  # הסרת המאפיין
                
video_path = "F:\לימודים\יד\פרויקט גמר\קצר.mp4"
output_file = "F:\לימודים\יד\פרויקט גמר\קצר.txt"
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
            print(edge_data.keys())
            lanes = estimate_lanes(edge_data)
            # lanes = edge_data.get('lanes', 1)
            length = (edge_data.get('length', 1))
            direction = 'forward' if edge_data.get('oneway', False) else 'backward'
            sumveicle = yolov.analyze_traffic(video_path, output_file, lanswidth, lanes, langthveicle, 200)
            print("סכום")
            print(sumveicle)
            #  נישמור במשתנה load את העומס בקשת שלו לפי ניתוח סירטון שהתקבל ממצלמות
            load = calculate_load(sumveicle, length, lanes)
            timest = calculate_travel_time(length, speedgb.get_edge_speed(edge_data),load)

            # עדכון משקל הקשת לפי זמן נסיעה
            nx.set_edge_attributes(graphmap, {(u, v, key): {'weight': timest}})
            edge = Edge(length, lanes, u, v, direction, load, timest)
            intersection.connected_edges.append(edge)
            intersections[node] = intersection
    # ניקוי מאפיינים שאינם נתמכים
    clean_graph_attributes(graphmap)
    # שמירת הגרף
    nx.write_graphml(graphmap, "graphmap.graphml")
    return intersections , graphmap # מחזיר את כל הצמתים ואיזה קשתות מחובורת לכל צומת
    """
    מחשבת את זמן הנסיעה הכולל בין שתי כתובות.
    :return: זמן נסיעה בדקות 
    """
def calculate_travel_time_between_coordinates(graph, source_address, destination_address):
    try:
        # המרת כתובות לקואורדינטות
        lat_source_coords, lon_source_coords = kmeans1.get_coordinates(source_address)
        lat_destination_coords,lon_destination_coords = kmeans1.get_coordinates(destination_address)
        # בדיקה אם הקואורדינטות תקינות
        if lat_source_coords is None or lon_source_coords is None:
            raise ValueError(f"לא נמצאו קואורדינטות עבור כתובת המקור: {source_address}")
        if lat_destination_coords is None or lon_destination_coords is None:
            raise ValueError(f"לא נמצאו קואורדינטות עבור כתובת היעד: {destination_address}")
        # המרת קואורדינטות לצמתים בגרף
        source_node = kmeans1.get_node_id(graph,lon_source_coords ,lat_source_coords)  # lon, lat
        destination_node = kmeans1.get_node_id(graph, lon_destination_coords, lat_destination_coords)  # lon, lat
        if source_node == destination_node:
            return 0
        try:
            total_travel_time = nx.shortest_path_length(graph, source_node, destination_node, weight='weight')
            return total_travel_time
        except nx.NetworkXNoPath:
            print(f"אין מסלול בין הצמתים {source_node} ל-{destination_node}")
            return None
        except nx.NodeNotFound as e:
            print(f"צומת לא נמצא בגרף: {e}")
            return None
    except Exception as e:
        print(f"שגיאה בחישוב זמן הנסיעה: {e}")
        return None 
    


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

