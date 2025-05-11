
"""import heapq
from datetime import datetime

class Shipment:
    def __init__(self, shipment_id, delivery_date, delivery_time, area, priority=0):
        self.shipment_id = shipment_id
        self.delivery_date = datetime.strptime(delivery_date, "%Y-%m-%d")  # תאריך המסירה
        self.delivery_time = datetime.strptime(delivery_time, "%H:%M")  # זמן המסירה
        self.area = area  # אזור המסירה
        self.priority = priority  # עדיפות חצי-קבועה שנקבעה בהתחלה (יכולה להשתנות)

    def __lt__(self, other):
        # הפונקציה משווה בין שני משלוחים לפי סדר הדחיפות על פי הקריטריונים שהגדרת
        if self.delivery_date == other.delivery_date:
            # אם תאריכים שווים, נבדוק לפי שעה
            if self.delivery_time == other.delivery_time:
                # אם גם השעה שווה, נבדוק לפי אזור (למשל: אזור קרוב קודם)
                return self.area < other.area
            return self.delivery_time < other.delivery_time
        return self.delivery_date < other.delivery_date

def sort_shipments_to_priority_queue(shipments):
    # ממיינת את המשלוחים לתור עדיפויות לפי הקריטריונים הדינמיים
    priority_queue = []
    for shipment in shipments:
        heapq.heappush(priority_queue, shipment)
    return priority_queue

# דוגמה לשימוש:
shipments = [
    Shipment(1, "2025-03-08", "14:30", "Tel Aviv"),
    Shipment(2, "2025-03-07", "09:00", "Haifa"),
    Shipment(3, "2025-03-06", "11:00", "Eilat"),
    Shipment(4, "2025-03-07", "11:00", "Ashdod"),
    Shipment(5, "2025-03-07", "14:30", "Haifa"),
]

# מיון המשלוחים לפי דחיפות על פי הקריטריונים
priority_queue = sort_shipments_to_priority_queue(shipments)

# הצגת המשלוחים בתור עדיפויות
while priority_queue:
    shipment = heapq.heappop(priority_queue)
    print(f"Shipment {shipment.shipment_id} - Date: {shipment.delivery_date.date()}, Time: {shipment.delivery_time.strftime('%H:%M')}, Area: {shipment.area}")
"""
import networkx as nx
import newnewosm as osm
from itertools import permutations

def compute_distance_matrix(graph, locations):
    """
    מחשבת מטריצת מרחקים בין כל היעדים בגרף באמצעות דייקסטרה.
    :param graph: גרף הכבישים (מבוסס OSM)
    :param locations: רשימת מזהים (Node IDs) של היעדים
    :return: מילון עם מרחקים בין כל זוגות היעדים
    """
    distance_matrix = {}

    for i, loc1 in enumerate(locations):
        distance_matrix[loc1] = {}
        for j, loc2 in enumerate(locations):
            if i == j:
                distance_matrix[loc1][loc2] = 0
            else:
                distance_matrix[loc1][loc2] = nx.shortest_path_length(graph, loc1, loc2, weight="length")

    return distance_matrix


def solve_tsp_with_constraints(distance_matrix, deliveries, start_location):
    """
    פתרון בעיית הסוכן הנוסע (TSP) עם אילוצי זמן ושעות פעילות.
    :param distance_matrix: מטריצת המרחקים בין כל היעדים
    :param deliveries: רשימת משלוחים עם אילוצים (זמן אספקה, שעות פעילות)
    :param start_location: מיקום השליח בתחילת המסלול
    :return: המסלול האופטימלי
    """
    min_route = None
    min_distance = float("inf")

    for perm in permutations([d["destination"] for d in deliveries]):
        route = [start_location] + list(perm) + [start_location]
        total_distance = sum(distance_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))

        valid = True
        current_time = 0
        for location in route[1:-1]:
            delivery = next(d for d in deliveries if d["destination"] == location)
            arrival_time = current_time + distance_matrix[route[route.index(location) - 1]][location] / 60

            if arrival_time > delivery["deadline"] or arrival_time > delivery["opening_hours"][1]:
                valid = False
                break

            current_time = arrival_time

        if valid and total_distance < min_distance:
            min_distance = total_distance
            min_route = route

    return min_route


# דוגמה לשימוש
place_name = "ראש העין, ישראל"
graphmaps, nodes, edges = osm.map_mapping_graf(place_name)

deliveries = [
    {"destination": "A", "deadline": 12, "opening_hours": (9, 14)},
    {"destination": "B", "deadline": 12.5, "opening_hours": (8, 12.5)},
    {"destination": "C", "deadline": 13, "opening_hours": (10, 20)},
]

locations = ["start"] + [d["destination"] for d in deliveries]
distance_matrix = compute_distance_matrix(graphmaps, locations)
optimal_route = solve_tsp_with_constraints(distance_matrix, deliveries, "start")

print("🔵 המסלול האופטימלי:", optimal_route)
