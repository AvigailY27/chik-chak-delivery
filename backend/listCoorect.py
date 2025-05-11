import heapq
import deliver as deliver
import kmeans1 
import osmnx as ox
import networkx as nx
import newnewosm as newosm
from datetime import datetime, timedelta

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
        self.sum_time =0
    def __iter__(self):
        current = self.head
        while current:
            yield current.delivery  # או yield current אם הנתונים נמצאים ישירות בחוליה
            current = current.next
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
    def add_between(self, previous_delivery, next_delivery, new_delivery):
        """
        מוסיפה משלוח חדש בין שני משלוחים קיימים ברשימה.
        """
        # מציאת המיקום של previous_delivery ו-next_delivery
        current_node = self.head
        while current_node:
            if current_node == previous_delivery:
                # יצירת קשרים חדשים
                new_node = DeliveryNode(new_delivery)
                new_node.next = current_node.next
                current_node.next = new_node
                if new_node.next:
                    new_node.next.previous = new_node
                new_node.previous = current_node
                break
            current_node = current_node.next
    def add_first_two_deliveries(self, delivery_queue):
        """
        הוספת שני המשלוחים הראשונים מתוך תור המשלוחים לרשימה
        """
        if len(delivery_queue) < 2:
            print("אין מספיק משלוחים בתור להוספה.")
            return

        # הוספת שני המשלוחים הראשונים
        self.add_delivery(delivery_queue.pop(0))
        self.add_delivery(delivery_queue.pop(0))
        return
    def print_list(self):
        """
        הדפסת כל המשלוחים ברשימה
        """
        current = self.head
        while current:
            print(f"מספר סידורי: {current.serial_number}, כתובת: {current.delivery.destination}")
            current = current.next
def travel(graph, source, destination, delivery_queue):
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
        delivery_node = kmeans1.get_node_id(graphmaps, lon, lat)
        if delivery_node in path:
            deliveries_on_path.append(delivery)

    return deliveries_on_pathdef

 #//פונקציה  מחשבת את זמן העיכוב האפשרי.
 # //לפני השימוש בדיקה שהזמן נסיעה בדקות אפשרי בטווח בין יציאה ליעד 
 # -calculate_travel_time_between_coordinatesשימוש לפני כן בפונקציה שמחזירה זמן נסיעה בין 2 כתובות ב NEWOSM 
def calculate_delay_time(start_time, arrive_time, travel_time_minutes): 
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

# יצירת תור משלוחים
class Delivery:
    def __init__(self, destination):
        self.destination = destination

delivery_queue = [
    Delivery("שמעון הצדיק, אלעד"),
    Delivery("בן קיסמא, אלעד"),
    Delivery("רחוב הרצל 10, תל אביב"),
    Delivery("רחוב דיזנגוף 20, תל אביב")
]
def main():
        # יצירת רשימה דו-כיוונית
        delivery_list = DeliveryLinkedList()

        # הוספת שני המשלוחים הראשונים לרשימה
        # הוספת שני המשלוחים הראשונים לרשימה
        delivery_list.add_first_two_deliveries(delivery_queue)

        # הדפסת הרשימה
        delivery_list.print_list()

        # חישוב מסלול ובדיקת משלוחים נוספים בדרך
        source = "שמעון בן שטח , אלעד"
        destination = "בן קיסמא, אלעד"
        intersections , graph = newosm.classify_intersections(graph)  # רשימת צמתים ופרטים על העומסים בקשתות של כל צומת
        # # בדיקת המשקלות בגרף
        # for u, v, key, data in graph.edges(keys=True, data=True):
        #     print(f"קשת מ-{u} ל-{v}, משקל: {data.get('weight')}")
        lat1, lon1= kmeans1.get_coordinates(source)
        lat2 , lon2= kmeans1.get_coordinates(destination)
        time= newosm.calculate_travel_time_between_coordinates(graph,kmeans1.get_node_id(graph,lon1, lat1), kmeans1.get_node_id(graph,lon2, lat2 ))
        delay= calculate_delay_time(8, 10, time)
        print(f"זמן עיכוב אפשרי: {delay} דקות")
        print(f"זמן נסיעה בין {source} ל-{destination}: {time} דקות")  
        # יצירת ערימת מינימום
        #delay_heap = DelayHeap()
        #delay_heap = delay_heap.update_delays(0)  # אתחול הערימה
        # הוספת המשלוחים לערימה       

def process_delivery_queue(delivery_queue):
    listcity = delivery.prioritize_deliveries(addresses)
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
