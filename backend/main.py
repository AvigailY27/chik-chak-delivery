import newnewosm as osm1
import folium
import deliver as deliver
import kmeans1 as kmeans1
from process import process_input_file
from datetime import datetime
import exampleme as exampleme
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import osmnx as ox
import ctypes
import heapq
from pprint import pprint
import shortpathme as sp
import listbuild as listbuild
import listupupdet as listupupdet
import listCoorect as listCoorect   
import heapqstruct as heapqstruct
import process as process
import sys
import os
from bidi.algorithm import get_display
import arabic_reshaper
# להוסיף את תקיית השורש של הפרויקט (הכוללת את backend)
def main():
        # מוסיף את הנתיב של תיקיית backend לרשימת החיפושים של פייתון
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        # יצירת שם קובץ דינמי על בסיס התאריך הנוכחי
        today_date = datetime.now().strftime('%Y-%m-%d')
        file_name = f"delivery best{today_date}.csv"
        uploads_folder = os.path.join(os.path.dirname(__file__), "uploads")
        file_path = os.path.join(uploads_folder, file_name)


        print("Starting the program...")
        # עיבוד נתוני הקובץ
        deliveries = process_input_file(file_path)
        if not deliveries:
            print("No deliveries found in the file.")
            return
        addresses = [delivery.destination for delivery in deliveries]
        deliveries, not_relevant = listupupdet.filter_deliveries_by_courier_hours(deliveries, "08:00", "14:00")
        if not_relevant:
            print("משלוחים שמחוץ לטווח שעות פעילות השליח ונמחקו:")
            for d in not_relevant:
                print(d)
        print("Original addresses:", addresses)
        # הפעלת כל החלקים
        place_name = "אלעד, ישראל"
        graphmaps, nodes, edges = osm1.map_mapping_graf(place_name)
        #intersections, graphmaps = osm1.classify_intersections(graphmaps)  # רשימת צמתים ופרטים על העומסים בקשתות של כל צומת
         #  השינוים של עדכון משקל- לזמני נסיעה, טעינת הגרף מחדש
        #graphmaps = nx.read_graphml("graphmap.graphml")
        #osm1.save_intersections_to_csv(intersections)  # שמירה לקובץ
        count = 1 # מספר האזורים לפי מספר שליחים
        #חלוקה לאזורים ושליח לכל אזור
        clusters_info = kmeans1.set_coordinates(graphmaps, addresses, count)
        for cluster, items in clusters_info.items():
            print(f"\n{cluster}:")
            # שלב 1: הפקת כתובות המשלוחים לאזור זה
            cluster_addresses = [item['address'] for item in items]
            # שלב 2: הפקת אובייקטי משלוח לאזור זה
            cluster_deliveries = [delivery for delivery in deliveries if delivery.destination in cluster_addresses]
            # שלב 3: בניית תור משלוחים לאזור
            warehouse = deliver.Delivery1("בן קיסמא 36 , אלעד", 3, "08:00", "16:00")
            if not cluster_deliveries or not cluster_addresses:
                print(f"לא נמצאו משלוחים לאזור {cluster}.")
                continue
            update_queue = deliver.update_delivery_queue(graphmaps, warehouse, cluster_deliveries)
            print(f"נמצאו {len(cluster_deliveries)} משלוחים בתור לאזור {cluster}.")
            print(f"המשלוחים בתור לאזור {cluster}:", str(update_queue))
            # שלב 4: בניית ערימת עיכובים
            delay_heap = heapqstruct.DelayHeap()
            delay_heap.update_delays(0)
            # שלב 5: בניית רשימה דו-כיוונית למסלול
            delivery_list = listCoorect.DeliveryLinkedList()
            if not update_queue or len(update_queue) < 2:
                for delivery in cluster_deliveries:
                    delivery_list.add_delivery(delivery)
                print(f" נמצאו פחות מ- 2 משלוחים בתור לאזור {cluster}.")
                continue
            delivery_list, update_queue = listupupdet.listupupdet(graphmaps, cluster_deliveries, update_queue, delay_heap)
            print(f"המשלוחים שנמצאו ברשימה הדו-כיוונית לאזור {cluster}:", str(delivery_list))
            print(f"המשלוחים שנשארו בתור לאזור {cluster}:", update_queue)
            # שלב 6: ציור מסלול
            address = [delivery.destination for delivery in delivery_list]
            print(f"כתובות המשלוחים לאזור {cluster}:", address)
            sp.draw_ordered_route(graphmaps, address, warehouse.destination)



        # intersections, graphmaps = osm1.classify_intersections(graphmaps)  # רשימת צמתים ופרטים על העומסים בקשתות של כל צומת
        # #  השינוים של עדכון משקל- לזמני נסיעה, טעינת הגרף מחדש
        # graphmaps = nx.read_graphml("graphmap.graphml")
        # osm1.save_intersections_to_csv(intersections)  # שמירה לקובץ
        # # מעבר על האזורים וכל צומת באזור לחפש אותה ב-intersections ולראות מה זמן נסיעה על הקשת שלה
        # for node, intersection in intersections.items():
        #     intersection_text = get_display(arabic_reshaper.reshape(f"צומת {intersection.id} | קשתות מחוברות: {len(intersection.connected_edges)}"))
        #     print(f"\n{intersection_text}")
        # for edge in intersection.connected_edges:
        #     edge_text = get_display(arabic_reshaper.reshape(
        #         f"קשת: אורך {edge.length} מ', נתיבים: {edge.lanes} חד סטרי/ דו סטרי: {edge.direction}, עומס: {edge.load}, זמן נסיעה: {edge.times}"
        #     ))
        #     print(f"  {edge_text}")


        # מעבר על האזורים וכל צומת באזור לחפש אותה ב-intersections ולראות מה זמן נסיעה על הקשת שלה
        # שזמן ההגעה מהמחסן לכל הקודקודים לכל אחד זמן הכי קצר..

if __name__ == "__main__":
    main()
