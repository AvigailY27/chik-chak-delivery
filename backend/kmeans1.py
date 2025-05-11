import numpy as np
import osmnx as ox
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim
import json
# פונקציה הממירה כתובת לקורדיננטות
def get_coordinates(address):
    """
    ממיר כתובת לקואורדינטות (Latitude, Longitude).
    """
    geolocator = Nominatim(user_agent="MyDeliveryApp", timeout=10)
    location = geolocator.geocode(address)
    if location:
        print(f"כתובת: {address}, קואורדינטות: (Latitude: {location.latitude}, Longitude: {location.longitude})")
        return location.latitude, location.longitude
    else:
        print(f"כתובת לא נמצאה: {address}")
        return None

# פונקציה המחזירה צומת הקרובה לקורדיננטה - למיקום גאוגרפי  get_node_id-

def get_node_id(graph, lon, lat):
    """
    ממיר קואורדינטות לצומת הקרובה ביותר בגרף, תוך שימוש במסלול קצר ביותר.
    """
    try:
        # מציאת הצומת הקרובה ביותר מבחינה גיאוגרפית
        #nearest_node = ox.distance.nearest_nodes(graph, lon, lat)
        nearest_node = find_connected_nearest_node(graph, lon, lat)
        print(f"צומת גיאוגרפית קרובה: {nearest_node}")
        return nearest_node
    except Exception as e:
        print(f"שגיאה במציאת צומת עבור קואורדינטות (Longitude: {lon}, Latitude: {lat}): {e}")
        return None
import math
import networkx as nx

def haversine(lat1, lon1, lat2, lon2):
    """
    מחשבת את המרחק הגיאוגרפי (Haversine) בין שתי נקודות.
    """
    R = 6371  # רדיוס כדור הארץ בקילומטרים
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_nearest_node(graph, lon, lat):
    """
    מוצאת את הצומת הקרובה ביותר לכתובת על סמך מרחק גיאוגרפי ובדיקת חיבוריות.
    """
    min_distance = float('inf')
    nearest_node = None

    for node, data in graph.nodes(data=True):
        if 'x' in data and 'y' in data:
            node_lon, node_lat = data['x'], data['y']
            distance = haversine(lat, lon, node_lat, node_lon)
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
    return nearest_node
def find_connected_nearest_node(graph, lon, lat):
    """
    מוצאת את הצומת הקרובה ביותר לכתובת ומוודאת שהיא מחוברת בגרף.
    """
    nearest_node = find_nearest_node(graph, lon, lat)
    if nearest_node and nx.has_path(graph, nearest_node, list(graph.nodes)[0]):
        return nearest_node
    else:
        print(f"צומת {nearest_node} אינה מחוברת בגרף.")
        return None
# import requests

# def get_node_id(address):
#     """
#     מוצאת את Place ID של כתובת באמצעות Overpass API.
#     :param address: כתובת לחיפוש
#     :return: Place ID
#     """
#     url = "https://nominatim.openstreetmap.org/search"
#     params = {
#         "q": address,
#         "format": "json",
#         "addressdetails": 1
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200 and response.json():
#         place_id = response.json()[0].get("place_id")
#         print(f"Place ID עבור הכתובת '{address}': {place_id}")
#         return place_id
#     else:
#         print(f"לא נמצא Place ID עבור הכתובת '{address}'")
#         return None

def count_unique_cities(addresses):
    cities = set()
    for address in addresses:
        address = address.strip()  # הסרת רווחים מיותרים מהכתובת
        if ',' in address:
            city = address.split(',')[-1].strip()  # חילוץ שם העיר והסרת רווחים
            print(f"Extracted city: {city}")  # הדפסת שם העיר שחולץ
            cities.add(city)
        else:
            print(f"Warning: Address '{address}' does not contain a comma.")
    return len(cities), list(cities)

# חלוקה לאזורים
def set_coordinates(graph, addressess, count):
 
# המרת כתובות לקואורדינטות
    num_clusters = count
    coords_with_addresses = [(addr, get_coordinates(addr)) for addr in addressess]
    coords = np.array([c for addr, c in coords_with_addresses if c is not None])
    filtered_addresses = [addr for addr, c in coords_with_addresses if c is not None]
    if len(coords) < num_clusters:
        return "לא ניתן לחלק את הכתובות לאזורים, מספר האשכולות גדול ממספר הכתובות"    # חלוקה לאשכולות עם KMeans
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(coords)

    # ציור הגרף עם אשכולות
    ox.plot_graph(graph, show=False, close=False)
    colors = ['orange', 'blue', 'green', 'purple', 'red']
    plotted_labels = set()
    for i, (lat, lon) in enumerate(coords):
        cluster_id = labels[i]
        color = colors[cluster_id]
        label = f"אזור {cluster_id}" if cluster_id not in plotted_labels else None
        plt.scatter(lon, lat, color=color, s=300, edgecolors='red', label=label)
        plotted_labels.add(cluster_id)

    # יצירת מבנה האשכולות
    clusters_info = {f"Cluster_{i}": [] for i in range(num_clusters)}

    for i, (lat, lon) in enumerate(coords):
        cluster_id = labels[i]
        node_id = ox.distance.nearest_nodes(graph, lon, lat)
        clusters_info[f"Cluster_{cluster_id}"].append({
            "address": filtered_addresses[i],
            "coordinates": (lat, lon),
            "node_id": node_id
        })

    # שמירת נתונים לקובץ JSON
    with open("cluster_nodes.json", "w", encoding='utf-8') as f:
        json.dump(clusters_info, f, ensure_ascii=False, indent=4)
    return clusters_info  # מחזיר את המידע על האשכולות והצמתים


if __name__ == "__main__":
    G = ox.graph_from_place("אלעד, ישראל", network_type='drive')
    addresses = [
        "רבי מאיר 1, אלעד",
        "רבי יהודה הנשיא 12, אלעד",
        "אליהו הנביא 7, ראש העין",

    ]
    clusters_info = set_coordinates(G, addresses,2)
    # הצגת מידע
    for cluster, items in clusters_info.items():
        print(f"\n{cluster}:")
        for item in items:
            print(f"  Address: {item['address']}, Node: {item['node_id']}")
    plt.gcf().canvas.manager.set_window_title("מפה של אלעד")
    plt.title("Delivery in Map")
    plt.margins(x=0.1, y=0.1)  # מגדיל את התצוגה ב-10% לכל כיוון
    plt.show()


"""
# זה הרצה של כל אזור המרכז ושמירה ואז כל פעם קריאה מהקובץ שנישמר
graph_path = os.path.join(os.getcwd(), "central_israel.graphml")


def load_central_israel_graph():
    north, south = 32.2, 31.9
    east, west = 35.0, 34.75

    print("Downloading graph for central Israel...")
    g = ox.graph_from_bbox(bbox=(north, south, east, west), network_type='drive')
    ox.save_graphml(g, "central_israel.graphml")
    print("Graph saved as central_israel.graphml")


if __name__ == "__main__":
    if not os.path.exists(graph_path):
        print("Creating graph...")
        load_central_israel_graph()
    G1 = ox.load_graphml(graph_path)
    print("Graph loaded.")
"""
