import heapq
import deliver as deliver
import kmeans1 as kmeans1
import newnewosm as newosm
from datetime import datetime, timedelta
import networkx as nx
class DeliveryNode:
    def __init__(self, delivery, serial_number):
        self.delivery = delivery  # אובייקט משלוח
        self.serial_number = serial_number  # מספר סידורי
        self.prev = None  # מצביע לחוליה הקודמת
        self.next = None  # מצביע לחוליה הבאה
class DeliveryLinkedList:
    def __init__(self):
        self.head = None  # החוליה הראשונה ברשימה
        self.tail = None  # החוליה האחרונה ברשימה
        self.serial_counter = 1  # מונה מספר סידורי
        self.current_time = datetime.now()  # הזמן הנוכחי
        self.sum_time =0
    def __iter__(self):
        current = self.head
        while current:
            yield current  # תחזירי את החוליה, לא את המשלוח
            current = current.next
    def to_list(self):
        result = []
        current = self.head
        while current:
            delivery = current.delivery
            result.append({
                'destination': delivery.destination,
                'start': delivery.start,
                'end': delivery.end,
                'timeMax': delivery.timeMax
            })
            current = current.next
        return result
    def remove_delivery_by_destination(self, destination_to_remove):
        current = self.head
        while current:
            if current.delivery.destination == destination_to_remove:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next  

                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev  

                print(f"Delivery to '{destination_to_remove}' removed from the list.")
                return True  # נמצא והוסר
            current = current.next
        print(f"Delivery to '{destination_to_remove}' not found in the list.")
        return False  # לא נמצא

    def __str__(self):
        deliveries = []
        current = self.head
        while current:
            deliveries.append(str(current.delivery))  # או str(current) אם הנתונים ישירות בחוליה
            current = current.next
        return " -> ".join(deliveries)
    def __repr__(self):
        return f"Delivery(destination='{self.destination}', start='{self.start}', end='{self.end}')"
    def add_delivery(self, delivery):
        """
        הוספת משלוח חדש לרשימה
        """
        new_node = DeliveryNode(delivery, self.serial_counter)
        self.serial_counter += 1

        if not self.head:  # אם הרשימה ריקה
            self.head = new_node
            self.tail = new_node
        else:  # הוספה לסוף הרשימה
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
    def add_between(self, previous_node, next_node, new_delivery):
        """
        הוספת משלוח חדש בין שני משלוחים קיימים ברשימה
        """
        if not previous_node or not next_node:
            print("לא ניתן להוסיף בין משלוחים שאינם קיימים.")
            return

        # חישוב מספר סידורי חדש כממוצע בין שני המספרים הסידוריים
        new_serial = (previous_node.serial_number + next_node.serial_number) / 2
        new_node = DeliveryNode(new_delivery, new_serial)

        # עדכון קשרים ברשימה
        previous_node.next = new_node
        new_node.prev = previous_node
        new_node.next = next_node
        next_node.prev = new_node

        #צריך להוסיף בדיקה אם כדי לי להתעכב לחכות לזמן פתיחה או לעכב את כולם תלוי כמה זמן זה עם 5 דקות עד 15 דקות זה בסדר 
    def print_list(self):
        """
        הדפסת כל המשלוחים ברשימה
        """
        current = self.head
        while current:
            print(f"מספר סידורי: {current.serial_number}, כתובת: {current.delivery.destination}")
            current = current.next
    
    def build_list_from_queue(self,delivery_queue):
            """
            מעבירה את תור המשלוחים לרשימה דו-כיוונית לפי סדר התור.
            :param delivery_queue: תור המשלוחים (רשימה של אובייקטי Delivery)
            :return: רשימה דו-כיוונית של משלוחים
            """
            # מעבר על התור והוספת כל משלוח לרשימה
            for delivery in delivery_queue:
                self.add_delivery(delivery)

            return self
    def travel(self,graph, source, destination, delivery_queue):
        """
        מחשבת מסלול בין מקור ליעד ובודקת אם יש משלוחים נוספים בדרך.
        :param graph: גרף NetworkX
        :param source: כתובת מקור
        :param destination: כתובת יעד
        :param delivery_queue: תור המשלוחים
        :return: רשימת משלוחים שנמצאים בדרך
        """
        # המרת כתובות לצמתים
        source_node = kmeans1.get_node_id(graph, *kmeans1.get_coordinates(source))
        destination_node = kmeans1.get_node_id(graph, *kmeans1.get_coordinates(destination))

        # חישוב המסלול
        if not nx.has_path(graph, source_node, destination_node):
            print(f"אין מסלול בין {source} ל-{destination}.")
            return []

        path = nx.shortest_path(graph, source_node, destination_node, weight='length')
        print(f"מסלול בין {source} ל-{destination}: {path}")

        # בדיקת משלוחים שנמצאים בדרך
        deliveries_on_path = []
        for delivery in delivery_queue:
            # המרת כתובת המשלוח לצומת
            lat, lon = kmeans1.get_coordinates(delivery.destination)
            if lat  is None or lon is None:
                print(f"לא נמצאו קואורדינטות עבור הכתובת: {delivery.destination}")
                continue
            delivery_node = kmeans1.get_node_id(graph, lon, lat)
            if delivery_node in path:
                deliveries_on_path.append(delivery)

        return deliveries_on_path
    def calculate_delay_time(self,start_time, arrive_time, travel_time_minutes): 
        """
        הכל בדקות, מחשבת את זמן העיכוב האפשרי.
        :param arrive_time: שעת ההגעה המתוכנן (datetime)
        :param exit_time:   של השליח מהראשון ברשימה  שעת היציאה (datetime)
        :param travel_time_minutes: זמן
        הנסיעה בדקות (int)
        :return: זמן העיכוב האפשרי בדקות (int)
        travel_time_minutes של המסלול של הקודם +הנסיעה של המסלול הנוכחי
        """
        
        # חישוב זמן ההגעה בפועל
        delay_time =  arrive_time - (start_time + travel_time_minutes)

        # actual_arrive_time = arrive_time-exit_time
        # # חישוב זמן העיכוב
        # delay_time = arrive_time*60 - actual_arrive_time

        # אם זמן העיכוב שלילי, אין זמן לעיכוב
        return max(0, int(delay_time))

 #//פונקציה  מחשבת את זמן העיכוב האפשרי.
 # //לפני השימוש בדיקה שהזמן נסיעה בדקות אפשרי בטווח בין יציאה ליעד 
 # -calculate_travel_time_between_coordinatesשימוש לפני כן בפונקציה שמחזירה זמן נסיעה בין 2 כתובות ב NEWOSM 

def process_delivery_queue(delivery_queue):

    addresses = [delivery.destination for delivery in delivery_queue]
    listcity = deliver.prioritize_deliveries(addresses)
    return listcity, delivery_queue
# חישוב המסלול הקצר ביותר
def shortpath(graph, source_coords, destination_coords):
    if source_coords in graph and destination_coords in graph:
        total_travel_time = nx.shortest_path_length(graph, source_coords, destination_coords, weight='weight')
    else:
        raise ValueError(f"One of the nodes {source_coords} or {destination_coords} is not in the graph.")

        return total_travel_time
#הדפסת הצמתים במסלול 
    def print_path(path):
        print("מסלול:")
        for node in path:
            print(node)



# // זמן נסיעה במסלול בין 2 כתובות 
#// שמירה זמן 
# //שומרת את זה בערימת מינימום של מפתח וערך של צומת וזמן נסיעה שניתן להרוויח- זמן להתעכב למשלוח נוסף על הדרך
# //הערימה מסודרת לפי זמן נסיעה
# //כל פעם שנירצה להוסיף מישהו ניראה שהזמן מה הזמן נסיעה המינימלי שאפשר להתעכב ואם הואצומת אחרי הצומת הנוכחי אם לפני זה לא רלוונטי נעבור הלאה ונחפש
# //ברגע שמתווסף מישהו למסלול בדרך אז מעדכנים את הזמן התעכבות - מורידים מכולם- יש לבדוק שאין זמן מינוס,
# //יהיה רשימה עם טווח משלוחים יעדים שהסטטוס שלהם חובה ומ ומי שמתווסף סיניהם הוא מקבל ערך ממוצע ביניהם ויורד מהמקום שלו שהיה
# //ונעדכן שמהמקום שלו הכל יורד באחד .
# //הנקודה הראשונה זה המחסן
# time= newosm.calculate_travel_time_between_coordinates  #  והמסלול הקצר ביניהם, חישוב זמן הנסיעה הכולל לפי המשקלים המעודכנים
# יצירת ערימת מינימום
# delay_heap = DelayHeap()
# calculate_delay_time פונקציה לחישוב זמן העיכוב האפשרי
