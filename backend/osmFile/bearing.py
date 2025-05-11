import math
import osmnx as ox
#פונקציות לבדיקת כיוון כביש- זוויות

def map_mapping_graf(place_name):
    graphmap = ox.graph_from_place(place_name, network_type="drive")
    # המרת הגרף לצמתים וקשתות
    nodes, edges = ox.graph_to_gdfs(graphmap)
    # הצגת עשרת הצמתים הראשונים
    print((nodes.head(10)))
    print(edges.columns)
    # הדפסת מידע בסיסי
    print(f"מספר הצמתים בגרף: {len(graphmap.nodes)}")
    print(f"מספר הנתיבים בגרף: {len(graphmap.edges)}")

    # דוגמה: בדיקת כיוון של כביש מתוך הגרף
    for _, edge in edges.iterrows():
        if edge["u"] in nodes.index and edge["v"] in nodes.index:
            lat1, lon1 = nodes.loc[edge["u"], ["y", "x"]]
            lat2, lon2 = nodes.loc[edge["v"], ["y", "x"]]
        else:
            print(f"Skipping edge {edge['osmid']} because nodes are missing")


        #  lat1, lon1 = nodes.loc[edge["osmid"], ["y", "x"]]
        # lat2, lon2 = nodes.loc[edge["v"], ["y", "x"]]
        bearing = calculate_bearing(lat1, lon1, lat2, lon2)
        direction = get_direction(bearing)
        print(f"Road from ({lat1}, {lon1}) to ({lat2}, {lon2}) is heading {direction} ({bearing}°)")
    return graphmap


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


dict_analysis = {}  # מילון של כל הצמתים שנותחו עם המידע


def main():
    # יצירת גרף דרכים
    place_name = "ראש העין, ישראל"
    graph = map_mapping_graf(place_name)
    # בחירת צומת אקראית
    node_id = list(graph.nodes)[67]


if __name__ == "__main__":
    main()
