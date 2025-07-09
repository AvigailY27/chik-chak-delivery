import newnewosm as osm1
import deliver as deliver
import kmeans1 as kmeans1
from process import process_input_file
from datetime import datetime
import exampleme as exampleme
import ctypes
import heapq
from pprint import pprint
import shortpathme as sp
import listbuild as listbuild
import listupupdet as listupupdet
import deliveryList as deliveryList   
import heapqstruct as heapqstruct
import process as process
import sys
import os
from bidi.algorithm import get_display
import arabic_reshaper
import networkx as nx

    # להוסיף את תקיית השורש של הפרויקט (הכוללת את backend)
    #data_source זה ניתוב לקובץ שהועלה
    #table_data זה נתונים שהוזנו בטופס
def main(data_source=None, table_data=None):
        if data_source:
            print(f"Processing data from source: {data_source}")
            deliveries = process_input_file(data_source)
        elif table_data:
            print("Processing data from table:")
            deliveries = [
                deliver.Delivery(row['destination'], row['timeMax'], row['startTime'], row['endTime'])
                for row in table_data
            ]
        else:
            print("No data source or table data provided.")
            return

        if not deliveries:
            print("No deliveries found.")
            return

        addresses = [delivery.destination for delivery in deliveries]
        print("Original addresses:", addresses)
        # דוגמה ליצירת שליחים רק בעיר אלעד ובין השעות 08:00-16:00
        couriers = [deliver.DeliveryPerson(1, "דני כהן", "08:00", "16:00", "אבן גבירול 3, אלעד"),
            deliver.DeliveryPerson(2, "חיים לוי", "08:00", "16:00", "ניסים גאון   12, אלעד"),
            deliver.DeliveryPerson(3, "יוסי ישראלי", "08:00", "16:00", "רבי יהודה הנשיא 15, אלעד")]
        # הדפסה של כל השליחים
        for courier in couriers:
            print(courier)

        
        # הפעלת כל החלקים
        place_name = "אלעד, ישראל"
        graphmaps, nodes, edges = osm1.map_mapping_graf(place_name)
        print("Graph created successfully.")
        print("Number of nodes:", len(nodes))
        print("Number of edges:", len(edges))
        # #לעדכון את הגרף עם זמני הנסיעה
        # intersections, graphmaps = osm1.classify_intersections(graphmaps)  # רשימת צמתים ופרטים על העומסים בקשתות של כל צומת
        #   #השינוים של עדכון משקל- לזמני נסיעה, טעינת הגרף מחדש
        # graphmaps = nx.read_graphml("graphmap.graphml")
        # osm1.save_intersections_to_csv(intersections)  # שמירה לקובץ
        # חישוב כמות השליחים הנדרשת, חלוקת משלוחים ואיזון עומס העבודה
        num_couriers, courier_workload = deliver.calculate_clusters_and_balance_workload(
            graphmaps, deliveries, max_distance=2, max_deliveries_per_courier=2,
        )
        print(f"מספר השליחים הנדרש: {num_couriers}")


       
        count = len(couriers) # מספר האזורים לפי מספר שליחים
        # הפעלת מסלול לכל שליח- חלוקה לאזורים ושליח לכל אזור
        clusters_info = kmeans1.set_coordinates(graphmaps, addresses, count)
        for index,(cluster, items) in enumerate(clusters_info.items()):
            print(f"\n{cluster}:")
            # שלב 1: הפקת כתובות המשלוחים לאזור זה
            cluster_addresses = [item['address'] for item in items]
            courier = couriers[index]
            print(f"שליח לאזור {cluster}: {courier.name}")
            if not cluster_addresses or courier is None:
                print(f"  או שליח לא נמצאו משלוחים לאזור {cluster}.")
                continue
           
            # שלב 2: הפקת אובייקטי משלוח לאזור זה
            cluster_deliveries = [delivery for delivery in deliveries if delivery.destination in cluster_addresses]
            filtered_cluster_deliveries, not_relevant = listupupdet.filter_deliveries_by_courier_hours(
                cluster_deliveries, courier.start, courier.end)
            if not_relevant:
                print("משלוחים שמחוץ לטווח שעות פעילות השליח ונמחקו:")
                for d in not_relevant:
                    print(d)                   
            cluster_deliveries = filtered_cluster_deliveries
            # שלב 3: בניית תור משלוחים לאזור
            update_queue = deliver.update_delivery_queue(graphmaps, courier.current_location, cluster_deliveries)
            print(f"נמצאו {len(cluster_deliveries)} משלוחים בתור לאזור {cluster}.")
            print(f"המשלוחים בתור לאזור {cluster}:", str(update_queue))
            #סינון לפי זמן/עדיפות
            cluster_deliveries, not_relevant1= listupupdet.filter_deliveries_by_time_and_priority(           
            graphmaps, courier.current_location, update_queue,courier.current_time)
            print("משלוחים שניתן לבצע:", [d.destination for d in cluster_deliveries])
            if not_relevant1: 
                not_relevant.extend(not_relevant1)
                print("משלוחים שלא ניתן לבצע:", [d.destination for d in not_relevant])
            
            #מחדש לפי מי שבטווח שבpossible ולפי מי שאינו חורג בזמן update_queue עכשיו ניבנה את
            
            sum_minutes = 0
            start_dt = datetime.strptime(courier.start, "%H:%M")
            end_dt = datetime.strptime(courier.end, "%H:%M")
            max_minutes = int((end_dt - start_dt).total_seconds() // 60)
            executed_deliveries = []
            not_relevant_deliveries = []
            current_location = courier.current_location

            for delivery in cluster_deliveries:
                travel_time = osm1.calculate_travel_time_between_coordinates(
                    graphmaps, current_location, delivery.destination
                )
                if travel_time is not  None:
                    sum_minutes += travel_time
                if sum_minutes > max_minutes:
                    print(f"המשלוח {delivery.destination} לא ניתן לביצוע (חריגה מהזמן).")
                    # כל המשלוחים שלא בוצעו (כולל הנוכחי) - לא ניתן לבצע
                    #not_relevant_deliveries = cluster_deliveries[cluster_deliveries.index(delivery):]
                    break
                executed_deliveries.append(delivery)
                current_location = delivery

            # אם לא הייתה חריגה, כל המשלוחים בוצעו
            if sum_minutes <= max_minutes:
                not_relevant_deliveries = []

            # עכשיו:
            # executed_deliveries - משלוחים שבוצעו בפועל
            # not_relevant_deliveries - משלוחים שלא ניתן לבצע (להוסיף ל-not_relevant)

            print("משלוחים שיבוצעו:", [d.destination for d in executed_deliveries])
            print("משלוחים שלא ניתן לבצע:", [d.destination for d in not_relevant_deliveries])

            # אפשר להוסיף ל-not_relevant הכל כך:
            #not_relevant.extend(not_relevant_deliveries)
            update_queue = executed_deliveries
            cluster_deliveries = executed_deliveries
            #    not_relevant נימצאים ב  #ניתן להתיחס למשלוחים שלא הוספו לתור אולי בהמשך...
            # courier.current_location = courier.start
            

            # שלב 4: בניית ערימת עיכובים
            #בנית ערימת המתנה לשעת פתיחה
            waiting_heap = heapqstruct.WaitingHeap()
            waiting_heap.update_waiting_times(0)
           
            # בניית ערימת עיכובים לשעת סגירה
            delay_heap = heapqstruct.DelayHeap()
            delay_heap.update_delays(0)

            # בניית ערימת עיכובים עם זמני העיכוב של המשלוחים בתור
            delay_heap = delay_heap.build_heap(update_queue, graphmaps, delay_heap)
            
            # שלב 5: בניית רשימה דו-כיוונית למסלול
            delivery_list = deliveryList.DeliveryLinkedList()
            delivery_list.build_list_from_queue(update_queue)
            #כאן יהיה לולאה לכל עדכון יעד הבא יוריד את היעד שעבר ויחשב מחדש אם יש מסלול משופר,
            #  יעדכן קודם זמני עומס
            delivery_list.optimize_route(courier, delivery_list, delay_heap) 
            #לשנות את זמן נסיעה של השליח לפי כל יעד שעובר
            #לעדכן כל יעד את זמן הנסיעה בכל קשת מחדש לפי עומס נוכחי מיולו
        
            # בניית רשימה דו-כיוונית עם המשלוחים בתור לפי עדכון זמן אמת
            #delivery_list, update_queue = listupupdet.listupupdet(graphmaps, update_queue,waiting_heap, delay_heap, cluster_deliveries)
            print(f"המשלוחים שנמצאו ברשימה הדו-כיוונית לאזור {cluster}:", str(delivery_list))
            print(f"המשלוחים שנשארו בתור לאזור {cluster}:", update_queue)

        
        
        # שלב 6: ציור מסלול
        address = [delivery.destination for delivery in delivery_list]
        print(f"כתובות המשלוחים לאזור {cluster}:", address)
        sp.draw_ordered_route(graphmaps, address,courier.current_location)

       


    #בכל עדכון משליח שעובר ליעד הבא נצטרך לשלוח אותו שוב  לחיפוש מסלול אופטיצלי- לעדכון התור 
    # בכל קריאה לעדכון מסלול - לעדכן את הגרף עם הזמני נסיעה עכשיו- לקרוא שוב ליצירת גרף- שינוים רק על הזמן 
        intersections, graphmaps = osm1.classify_intersections(graphmaps)  # רשימת צמתים ופרטים על העומסים בקשתות של כל צומת
        #  השינוים של עדכון משקל- לזמני נסיעה, טעינת הגרף מחדש
        graphmaps = nx.read_graphml("graphmap.graphml")
        osm1.save_intersections_to_csv(intersections)  # שמירה לקובץ
        # מעבר על האזורים וכל צומת באזור לחפש אותה ב-intersections ולראות מה זמן נסיעה על הקשת שלה
        for node, intersection in intersections.items():
            intersection_text = get_display(arabic_reshaper.reshape(f"צומת {intersection.id} | קשתות מחוברות: {len(intersection.connected_edges)}"))
            print(f"\n{intersection_text}")
        for edge in intersection.connected_edges:
            edge_text = get_display(arabic_reshaper.reshape(
                f"קשת: אורך {edge.length} מ', נתיבים: {edge.lanes} חד סטרי/ דו סטרי: {edge.direction}, עומס: {edge.load}, זמן נסיעה: {edge.times}"
            ))
            print(f"  {edge_text}")
        return num_couriers

        # מעבר על האזורים וכל צומת באזור לחפש אותה ב-intersections ולראות מה זמן נסיעה על הקשת שלה
        # שזמן ההגעה מהמחסן לכל הקודקודים לכל אחד זמן הכי קצר..

# if __name__ == "__main__":
#     main()
