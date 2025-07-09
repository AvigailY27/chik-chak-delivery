import kmeans1 as kmeans1
import deliver as deliver
import json
import process as process
import listupupdet as listupupdet
from datetime import datetime
import newnewosm as osm1
import json
import os
import networkx as nx
from datetime import datetime
import math 
from global_state import get_or_create_courier ,graphmaps, nodes, edges
import delivery_structures as delivery_structures

# מקבל משלוחים ומחזיר כמה אזורים יש ומסדר לכל אזור משלוחים שלו שומר בקובץ
def Cluster(data_source=None, table_data=None, graphmaps=None):
        print("datasource:", data_source)
        print("table_data:", table_data)
        print("graphmaps:", graphmaps)
        if data_source:
            print(f"Processing data from source: {data_source}")
            deliveries =process.process_input_file(data_source)
            print(f"Number of deliveries processed: {(deliveries)}")
            
        elif table_data:
            print("Processing data from table:")
            deliveries = [
                deliver.Delivery(row['destination'], row['timeMax'], row['start'], row['end'])
                for row in table_data
            ]
        else:
            print("No data source or table data provided.")
            return None, None,0

        if not deliveries:
            print("No deliveries found.")
            return None, None,0
        addresses = [delivery.destination for delivery in deliveries]
        num_couriers, courier_workload, missing = deliver.calculate_clusters_and_balance_workload(
                graphmaps, deliveries, max_distance=2, max_deliveries_per_courier=3)
        if num_couriers == -1 or not courier_workload:
            return -1, None, missing
        # # הפעלת מסלול לכל שליח- חלוקה לאזורים ושליח לכל אזור
        clusters_info = kmeans1.set_coordinates(graphmaps, deliveries, num_couriers)
        return  num_couriers, courier_workload, 0


def assign_couriers_to_clusters(cluster_file="cluster_nodes.json", couriers_file="couriers.json", output_file="couriers_with_clusters.json"):
    """
    מתאימה לכל שליח אזור לפי הסדר ומעדכנת את המידע בקובץ JSON חדש.
    """
    try:
        # קריאת קובץ האזורים
        with open(cluster_file, "r", encoding="utf-8") as file:
            clusters = json.load(file)

        # קריאת קובץ השליחים
        with open(couriers_file, "r", encoding="utf-8") as file:
            couriers = json.load(file)

        # בדיקה אם יש מספיק שליחים לכל האזורים
        if len(couriers) < len(clusters):
            print(f"Warning: Not enough couriers for the number of clusters. {len(clusters) - len(couriers)} couriers are missing.")

        # שיוך שליחים לאזורים לפי הסדר
        cluster_keys = list(clusters.keys())
        for i, courier in enumerate(couriers):
            if i < len(cluster_keys):
                cluster_name = cluster_keys[i]
                courier["cluster"] = cluster_name  # הוספת שדה "cluster" לשליח
            else:
                courier["cluster"] = None  # אם אין מספיק אזורים, השדה יהיה None

        # שמירת המידע המעודכן בקובץ חדש
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(couriers, file, ensure_ascii=False, indent=4)

        print(f"Couriers assigned to clusters successfully! Output saved to {output_file}")

    except Exception as e:
        print(f"Error assigning couriers to clusters: {e}")

def get_courier_by_phone(phone, json_path='couriers_with_clusters.json'):
    """
    מחזירה אובייקט שליח לפי מספר טלפון מתוך קובץ JSON.

    :param phone: מספר טלפון של השליח לחיפוש
    :param json_path: נתיב לקובץ השליחים
    :return: אובייקט השליח (dict) או None אם לא נמצא
    """
    if not os.path.exists(json_path):
        print("הקובץ לא נמצא:", json_path)
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            couriers = json.load(f)

        for courier in couriers:
            if courier.get("phone") == phone:
                return courier

        print(f"שליח עם טלפון {phone} לא נמצא.")
        return None

    except Exception as e:
        print("שגיאה בקריאת הקובץ:", e)
        return None
    
def sortQueue(phone, deliveries, graphmaps):

    courier = get_courier_by_phone(phone)
    deliveries = [
        deliver.Delivery(
            destination=d['destination'],
            timeMax=d['timeMax'],
            start=d['start'],
            end=d['end']
        )
        for d in deliveries
    ]

    if not courier:
        return None
    cluster = courier['cluster']
    print(f"Processing deliveries for cluster {cluster}, courier {courier['phone']}.")
    not_relevant_with_reason = []

    # 1. סינון לפי שעות עבודה
    try:
        filtered_deliveries, out_of_hours = listupupdet.filter_deliveries_by_courier_hours(
            deliveries, courier['start'], courier['end']
        )
        if out_of_hours:
            print("Removed (outside courier hours):", [d.destination for d in out_of_hours])
            not_relevant_with_reason.extend(out_of_hours)
    except Exception as e:
        print("Error in filter_deliveries_by_courier_hours:", e)
    deliveries = filtered_deliveries
    # 2. בניית תור לפי מיקום נוכחי
    initial_queue = deliver.update_delivery_queue(
        graphmaps, courier['current_location'], deliveries
    )

    # 3. סינון לפי זמן ו/או עדיפות
    filtered_by_priority, out_of_time_or_priority = listupupdet.filter_deliveries_by_time_and_priority(
        graphmaps, courier['current_location'], initial_queue, courier['start']
    )

    if out_of_time_or_priority:
        print("Removed (time/priority):", [d.destination for d in out_of_time_or_priority])
        not_relevant_with_reason.extend(out_of_time_or_priority)

    # 4. הגבלת זמן כולל
    executed_deliveries = []
    current_location = courier['current_location']
    total_minutes = 0
    start_time = datetime.strptime(courier['start'], "%H:%M")
    end_time = datetime.strptime(courier['end'], "%H:%M")
    max_minutes = int((end_time - start_time).total_seconds() // 60)

    for delivery in filtered_by_priority:
        try:
            travel_time = osm1.calculate_travel_time_between_coordinates(
                graphmaps, current_location, delivery.destination
            )
            if travel_time is None or math.isinf(travel_time):
                print(f"זמן נסיעה לא תקין עבור {delivery.destination}: {travel_time}")
                not_relevant_with_reason.append(delivery)
                continue
        except Exception as e:
            print(f"שגיאה בחישוב זמן הנסיעה למשלוח ל: {delivery.destination}, {e}")
            not_relevant_with_reason.append(delivery)
            continue
        if total_minutes + travel_time > max_minutes:
            not_relevant_with_reason.append(delivery)
            remaining_deliveries = filtered_by_priority[filtered_by_priority.index(delivery) + 1:]
            not_relevant_with_reason.extend(remaining_deliveries)
            break

        total_minutes += travel_time
        executed_deliveries.append(delivery)
        current_location = delivery.destination

    print("Final route:", [d.destination for d in executed_deliveries])
    remove = [d.destination for d in not_relevant_with_reason]
    print("Removed:", remove)
    executed_deliveries = [
        delivery for delivery in executed_deliveries
        if delivery.destination not in remove
    ]
    return executed_deliveries, not_relevant_with_reason

def update_graph_with_traffic_weights(graphmaps):
    """
    טוענת את הגרף מהקובץ, מחשבת עומסים, ומעדכנת את זמני הנסיעה על כל קשת לפי עומס.
    מחזירה את הגרף עם המשקלים החדשים.
    """
    # מצא צמתים עם קשתות
    intersections, graph = osm1.classify_intersections(graphmaps)
    if not intersections:
        print("No intersections found in the graph.")
    # עדכון משקלי קשתות לפי זמני נסיעה
    for node_id, intersection in intersections.items():
        print(node_id, "intersection:", intersection)
        for edge in intersection.connected_edges:
            u, v = edge.start_node, edge.end_node
            print(edge, "edge:", u, v)
            if graph.has_edge(u, v):
                graph[u][v][0]["weight"] = edge.times
                #הגרף המעודכן נשמר כבר בפונקציה classify_intersections
    print(f"Graph updated with traffic weights and saved to {graph}")


def optimize_deliveries_route(update_queue, graphmaps, courier):
    """
    מקבלת  משלוחים, גרף דרכים ושליח – מחזירה רשימה דו-כיוונית עם המסלול האופטימלי.
    """
    courier_data = get_or_create_courier(courier['phone'])
    delay_heap=courier_data['delay_heap']
    delivery_list = courier_data['delivery_list']
    # שלב 1: בניית ערימת עיכובים לשעת סגירה
    #אין צורך לשעת פתיחה מתחשב כבר בחישוב המסלול 
    delay_heap.update_delays(0)
    # שלב 2: בניית ערימת עיכובים לפי זמני נסיעה
    delay_heap.build_heap(update_queue, graphmaps)
    # שלב 3: בניית רשימה דו-כיוונית מהתור
    if delivery_list.head is None:
        delivery_list.build_list_from_queue(update_queue)
    # שלב 4: אופטימיזציה של המסלול
    delivery_structures.optimize_route(courier)
    print("מסלול אופטימלי נבנה בהצלחה.",delivery_list)
    return delivery_list

# לשים לב , צריך לעדכן עומס בכבישים לפי YOLO
# יש להסיר משלוחים שהיו על הדרך- נסיר מהקובץ משלוחים שבוצעו והיה עדכון 
