import newnewosm as osm
import osmnx as ox
import kmeans1 as kmeans1
import matplotlib.pyplot as plt
import networkx as nx
import folium
# חלוקת  אזורים
# וחיפוש מי הקרוב ביותר למיקום שלי איזה אזור ובתוך האזור איזה כתובת


def draw_ordered_route(graph, addresses, start_address):
    """
    מחשבת ומציירת מסלול לפי סדר כתובות על מפה אינטראקטיבית.
    """
    # המרת הכתובת ההתחלתית לצומת
    start_node = kmeans1.get_node_id(graph, kmeans1.get_coordinates(start_address)[1], kmeans1.get_coordinates(start_address)[0])
    if start_node is None:
        print(f"כתובת התחלה לא נמצאה או צומת לא נמצא: {start_address}")
        return

    # המרת כל כתובת ברשימה למילון של צמתים וכתובות
    address_nodes = addresses_to_nodes(graph, addresses)
    if not address_nodes:
        print("לא נמצאו כתובות תקינות ליצירת מסלול.")
        return

    # בניית המסלול לפי הסדר
    full_route = []
    current_node = start_node
    for next_node in address_nodes:
        try:
            partial_route = nx.shortest_path(graph, current_node, next_node, weight='length')
            full_route.extend(partial_route[:-1])  # נמנע מכפילות בצומת האחרון
            current_node = next_node
        except nx.NetworkXNoPath:
            print(f"אין מסלול בין {current_node} ל-{next_node}.")
            continue
    full_route.append(current_node)  # הוספת הצומת האחרון

    # יצירת מפה אינטראקטיבית
    start_coords = (graph.nodes[start_node]['y'], graph.nodes[start_node]['x'])
    m = folium.Map(location=start_coords, zoom_start=14)

    # הוספת המסלול למפה
    route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in full_route]
    folium.PolyLine(route_coords, color="blue", weight=2.5, opacity=1).add_to(m)

    # הוספת נקודות עם תיוגים
    for node, label in address_nodes.items():
        if 'x' in graph.nodes[node] and 'y' in graph.nodes[node]:
            lat, lon = graph.nodes[node]['y'], graph.nodes[node]['x']
            folium.Marker(
                location=(lat, lon),
                popup=f"<b>כתובת:</b> {label}<br><b>צומת:</b> {node}",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
    # שמירת המפה כקובץ HTML
    m.save("map_with_route.html")
    print("המפה נשמרה כקובץ map_with_route.html")

def addresses_to_nodes(graph, addresses):
    """
    ממיר רשימת כתובות למילון של צמתים וכתובות בגרף.
    """
    nodes = {}
    for address in addresses:
        # המרת כתובת לקואורדינטות
        lat_lon = kmeans1.get_coordinates(address)
        if lat_lon is None:
            print(f"כתובת לא נמצאה: {address}")
            continue
        lat, lon = lat_lon

        # הדפסת הקואורדינטות
        print(f"כתובת: {address}, קואורדינטות: (Latitude: {lat}, Longitude: {lon})")

        try:
            # המרת קואורדינטות לצומת בגרף
            node = ox.distance.nearest_nodes(graph, lon, lat)  # שים לב: סדר הקואורדינטות הוא (Longitude, Latitude)
            if node not in graph:
                print(f"צומת {node} לא נמצא בגרף עבור הכתובת: {address}")
                continue
            nodes[node] = address  # שמירת הצומת והכתובת במילון
            print(f"כתובת: {address}, צומת: {node}")
        except Exception as e:
            print(f"שגיאה במציאת צומת עבור הכתובת {address}: {e}")
    return nodes