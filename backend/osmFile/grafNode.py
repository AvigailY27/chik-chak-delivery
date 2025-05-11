import osmnx as ox
import math
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString
def map_mapping_graf(place_name):
    graphmap = ox.graph_from_place(place_name, network_type="drive")
    nodes, edges = ox.graph_to_gdfs(graphmap)

    # המרת הגרף לצמתים וקשתות
    #  nodes, edges = ox.graph_to_gdfs(graphmap, nodes=True, edges=True)

    # הצגת עשרת הצמתים הראשונים
    print((nodes.head(10)))
    # הדפסת מידע בסיסי
    print(f"מספר הצמתים בגרף: {len(graphmap.nodes)}")
    print(f"מספר הנתיבים בגרף: {len(graphmap.edges)}")
    return graphmap, nodes, edges

    # דוגמה: בדיקת כיוון של כביש מתוך הגרף#


""" for _, edge in edges.iterrows():
      lat1, lon1 = nodes.loc[edge["u"], ["y", "x"]]
      lat2, lon2 = nodes.loc[edge["v"], ["y", "x"]]
      bearing = calculate_bearing(lat1, lon1, lat2, lon2)
      direction = get_direction(bearing)
      print(f"Road from ({lat1}, {lon1}) to ({lat2}, {lon2}) is heading {direction} ({bearing}°)")
"""

# הצגת המפה


"""  fig, ax = ox.plot_graph(graphmap, figsize=(10, 10), node_size=15, node_color="red", edge_color="blue",
                           bgcolor="white")
   plt.show()
"""


def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    פונקציה לחישוב הכיוון (bearing) בין שתי נקודות
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing


def get_direction(bearing):
    """
    ממיר זווית לאחת מארבע רוחות השמיים
    """
    directions = ["North", "Northeast", "East", "Southeast", "South", "Southwest", "West", "Northwest"]
    index = round(bearing / 45) % 8
    return directions[index]


# בדיקת כיוון
# 📌 חישוב כיוון בין שתי קואורדינטות
"""
def get_direction(geometry):
    if isinstance(geometry, LineString):  # לוודא שזה כביש (קו)
        coords = list(geometry.coords)  # רשימת הקואורדינטות

        if len(coords) >= 2:  # צריך לפחות 2 נקודות
            lon1, lat1 = coords[0]  # נקודת התחלה
            lon2, lat2 = coords[-1]  # נקודת סוף
    angle = math.degrees(math.atan2(lat2 - lat1, lon2 - lon1))
    direction = " "
    if -45 <= angle < 45:
        direction = "מזרח"
    elif 45 <= angle < 135:
        direction = "צפון"
    elif 135 <= angle or angle < -135:
        direction = "מערב"
    else:
        direction = "דרום"
    return direction

"""


# פונקציה לניתוח צומת ספציפי לפי OSMID
def analyze_intersection(graph, osmid):
    # לטבלה קבלת הצמתים מהגרף
    nodes = ox.graph_to_gdfs(graph, nodes=True, edges=False)
    print(nodes.columns)
    # לטבלה קבלת הקשתות מהגרף
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
    print(edges.columns)
    # בדיקה  אם עמודת 'osmid' קיימת. אם לא - נשתמש באינדקס כ-'osmid'
    if 'osmid' not in nodes.columns:
        nodes['osmid'] = nodes.index

    # מציאת הצומת לפי ה-OSMID
    intersection = nodes[nodes['osmid'] == osmid]

    if intersection.empty:
        raise ValueError(f"צומת עם OSMID {osmid} לא נמצא בגרף.")
    #   חישוב מספר הקשתות הנכנסות והיוצאות
    in_degree = graph.in_degree[osmid]
    out_degree = graph.out_degree[osmid]

    # ניתוח הצומת לפי צומת שהמזהה OSMID
    intersection_info = {
        'intersection_osmid': osmid,
        'geometry': intersection.iloc[0]['geometry'],
        'street_count': int(intersection.iloc[0]['street_count']),  # כמות רחובות נפגשים בצומת
        'in_edges': in_degree,  # מספר קשתות נכנסות
        'out_edges': out_degree,  # מספר קשתות יוצאות
        'connected_streets': [],  # שמןת רחובות מחוברים
        'direct': [],
        'lanes_per_direction': {},  # מספר נתיבים לכיוון
        'connected_edges': [],  # מילון של קשתות לצומת עם פרטיהם: אורך, נתיבים
        'turns': [],
        'crossings': [],
        'intersection_type': []  # סוג צומת
    }

    # איסוף נתונים על הרחובות והנתיבים
    connected_edges_len = list(graph.edges(osmid, data=True))  # מקבל את מספר הקשתות שנפגשות בצומת
    for u, v, data in connected_edges_len:
        street_name = data.get('name', 'Unnamed Street')
        lanes = data.get('lanes', 1)  # לראות אם ברירת מחדל זה 0 או 1
        intersection_info['connected_streets'].append(street_name)
        intersection_info['lanes_per_direction'][(u, v)] = lanes
        #      זיהוי סוג הצומת (T, Y, צלב, רב צמתי)
        if len(connected_edges_len) == 2:
            intersection_info['intersection_type'] = 'T'
        elif len(connected_edges_len) == 3:
            intersection_info['intersection_type'] = 'Y'
        elif len(connected_edges_len) == 4:
            # צומת צלב
            intersection_info['intersection_type'] = 'צלב'
        elif len(connected_edges_len) > 4:
            intersection_info['intersection_type'] = 'רב צמתי'
        else:
            intersection_info['intersection_type'] = 'צומת בלי רמזור'
    # intersection_info['direct'] = get_direction(intersection_info['geometry'])
    # 4.2.2 לבדוק אם יש פניות
    if 'turn' in data:
        intersection_info['turns'].append(data['turn'])
    # 4.2.3 אם יש מעברי חציה (crossings)
    if 'crossing' in data:
        intersection_info['crossings'].append(data['crossing'])
    # קבלת מידע על הקשתות המחוברות
    connected_edges = []
    for u, v, dataEd in graph.edges(osmid, data=True):
        edge_info = {
            "to_node": v,
            "length": int(dataEd.get("length", "Unknown")),  # אורך הכביש
            "lanes": int(dataEd.get("lanes", 1))  # מספר נתיבים (ברירת מחדל 1)
        }
    connected_edges.append(edge_info)
    intersection_info['connected_edges'] = connected_edges

    return intersection_info


"""


def analyze_intersection(graph, osmid):
    # לטבלה קבלת הצמתים מהגרף
    nodes = ox.graph_to_gdfs(graph, nodes=True, edges=False)
    print(nodes.columns)
    # לטבלה קבלת הקשתות מהגרף
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
    print(edges.columns)

    # בדיקה אם עמודת 'osmid' קיימת. אם לא - נשתמש באינדקס כ-'osmid'
    if 'osmid' not in nodes.columns:
        nodes['osmid'] = nodes.index

    # מציאת הצומת לפי ה-OSMID
    intersection = nodes[nodes['osmid'] == osmid]

    if intersection.empty:
        raise ValueError(f"צומת עם OSMID {osmid} לא נמצא בגרף.")

    # חישוב מספר הקשתות הנכנסות והיוצאות
    in_degree = graph.in_degree[osmid]
    out_degree = graph.out_degree[osmid]

    # ניתוח הצומת לפי צומת שהמזהה OSMID
    intersection_info = {
        'intersection_osmid': osmid,
        'geometry': intersection.iloc[0]['geometry'],
        'street_count': int(intersection.iloc[0]['street_count']),  # כמות רחובות נפגשים בצומת
        'in_edges': in_degree,  # מספר קשתות נכנסות
        'out_edges': out_degree,  # מספר קשתות יוצאות
        'connected_streets': [],  # שמות רחובות מחוברים
        'lanes_per_direction': {},  # מספר נתיבים לכיוון
        'connected_edges': [],  # מילון של קשתות לצומת עם פרטיהם: אורך, נתיבים
        'turns': [],  # אם יש פניות
        'crossings': [],  # אם יש מעברי חציה
        'intersection_type': []  # סוג צומת
    }

    # איסוף נתונים על הרחובות והנתיבים
    connected_edges_len = list(graph.edges(osmid, data=True))  # מקבל את מספר הקשתות שנפגשות בצומת
    for u, v, data in connected_edges_len:
        street_name = data.get('name', 'Unnamed Street')
        lanes = data.get('lanes', 1)  # מספר נתיבים (ברירת מחדל 1)
        intersection_info['connected_streets'].append(street_name)
        intersection_info['lanes_per_direction'][(u, v)] = lanes

    # זיהוי סוג הצומת (T, Y, צלב, רב צמתי)
    if len(connected_edges_len) == 2:
        intersection_info['intersection_type'] = 'T'
    elif len(connected_edges_len) == 3:
        intersection_info['intersection_type'] = 'Y'
    elif len(connected_edges_len) == 4:
        intersection_info['intersection_type'] = 'צלב'
    elif len(connected_edges_len) > 4:
        intersection_info['intersection_type'] = 'רב צמתי'
    else:
        intersection_info['intersection_type'] = 'צומת בלי רמזור'

    # חיפוש הקשתות היוצאות (outgoing_edges) והנכנסות (incoming_edges)
    outgoing_edges = edges[edges["u"] == osmid]  # קשתות שיוצאות מהצומת
    incoming_edges = edges[edges["v"] == osmid]  # קשתות שנכנסות לצומת

    # הצגת המידע על הקשתות היוצאות והנכנסות
    print(f"🔹 קשתות יוצאות ({len(outgoing_edges)}):")
    print(outgoing_edges[["v", "name", "length"]])  # לאן מוביל הכביש, שם הכביש ואורכו

    print(f"\n🔹 קשתות נכנסות ({len(incoming_edges)}):")
    print(incoming_edges[["u", "name", "length"]])  # מאיפה הכביש מגיע

    # קבלת מידע על הקשתות המחוברות
    connected_edges = []
    for u, v, dataEd in graph.edges(osmid, data=True):
        edge_info = {
            "to_node": v,
            "length": int(dataEd.get("length", "Unknown")),  # אורך הכביש
            "lanes": int(dataEd.get("lanes", 1))  # מספר נתיבים (ברירת מחדל 1)
        }
        connected_edges.append(edge_info)

    intersection_info['connected_edges'] = connected_edges

    return intersection_info

"""
dict_analysis = {}  # מילון של כל הצמתים שנותחו עם המידע


def main():
    # יצירת גרף דרכים
    place_name = "ראש העין, ישראל"
    graphmap, nodes, edges = map_mapping_graf(place_name)
    # בחירת צומת אקראית
    osmid = list(graphmap.nodes)[67]
    osmedges = list(graphmap.edges)[67]

    try:
        # ניתוח הצומת
        intersection_info = analyze_intersection(graphmap, osmid)
        dict_analysis[osmid] = intersection_info
        dict_analysis[osmedges] = intersection_info
        # חיפוש הקשתות (כבישים) שיוצאות מהצומת
        # outgoing_edges = edges[edges["u"] == osmid]

        # חיפוש הקשתות שנכנסות לצומת
        # incoming_edges = edges[edges["v"] == osmid]
        # הצגת המידע
        print(intersection_info)

    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
