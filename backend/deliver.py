import heapq
from geopy.distance import geodesic
from typing import List, Tuple
import kmeans1 as kmeans1
import newnewosm as newnewosm

# מחלקה של משלוח
class Delivery:
    def __init__(self, delivery_id, origin, destination, delivery_time, package_type, weight,
                 constraints=None):
        self.delivery_id = delivery_id  # מזהה ייחודי למשלוח
        self.origin = origin  # כתובת מוצא
        self.destination = destination  # נקודת מסירה (קואורדינטות או כתובת)
        self.delivery_time = delivery_time  # זמן אספקה
        self.package_type = package_type  # סוג החבילה (רגילה, אקספרס וכו')
        self.weight = weight  # משקל החבילה
        self.constraints = constraints if constraints else []  # אילוצים ייחודיים למשלוח (כגון זמני אספקה, דחיפות)


# מחלקה של שליח
class DeliveryPerson:
    def __init__(self, person_id, name, capacity, working_hours):
        self.person_id = person_id  # מזהה ייחודי לשליח
        self.name = name  # שם השליח
        # self.vehicle_type = vehicle_type  # סוג הרכב (רכב, אופנוע, אופניים)
        self.capacity = capacity  # קיבולת הרכב (כמה חבילות יכול לקחת)
        self.working_hours = working_hours  # שעות פעילות (לדוגמה: "08:00-18:00")


class Constraint:
    def __init__(self, constraint_type: str, details: str):
        """
        אתחול מחלקת אילוץ
        :param constraint_type:
        :param details: פרטי האילוץ (למשל, "שעות פעילות: 08:00-18:00")
        """
        self.constraint_type = constraint_type  # סוג האילוץ (למשל, "אילוץ זמן")
        self.details = details  # פרטי האילוץ


class Delivery1:
    def __init__(self, destination, timeMax, start, end):
        self._destination = destination  # משתנה פרטי
        self._timeMax = timeMax
        self._start = start
        self._end = end

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, value):
        self._destination = value

    @property
    def timeMax(self):
        return self._timeMax  # שימוש במשתנה פרטי

    @timeMax.setter
    def timeMax(self, value):
        self._timeMax = value  # עדכון המשתנה הפרטי

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value

    def __str__(self):
        return f"משלוח ל: {self.destination}, זמינות: {self.start} עד {self.end}"

    def __repr__(self):
        return (f"Delivery1(destination='{self.destination}', "
                f"timeMax='{self.timeMax}', "
                f"start='{self.start}', "
                f"end='{self.end}')")
    def add_constraint(self, constraint):
        """הוספת אילוץ נוסף למשלוח"""
        self.constraints.append(constraint)

    def __repr__(self):
        return (f"Delivery( destination='{self.destination}', "
                f", timeMax='{self.timeMax}', "
                f", start='{self.start}', "
                f", end='{self.end}')")


# הפונקציה בונה תור עדיפיות ליעדים לפי השעת סיום כדי שנוכל לקחת את השעה הראשונה כדחופה
# deliveries_list סוג משלוח, צריך לקבל
def prioritize_deliveries(deliveries_list):
    priority_queue = []
    sorted_deliveries = sorted(deliveries_list, key=lambda d1: d1.end)
    for delivery in sorted_deliveries:
        heapq.heappush(priority_queue, delivery)
    return priority_queue


# פונקתיה שמחזירה את פרטי המשלוחים של הכתובות שלה
# מקבלת אזור, רשימת משלוחים -פרטי משלוחים של כולם, מחזירה את המשלוחים של האזור
def get_address_cluster_queue(clus, deliveries):
    clusters_info_address = []
    for delivery in deliveries:
        if delivery.destination == clus[1][0]['address']:
            clusters_info_address.append(delivery)
    return clusters_info_address

# פונקציה שבונה תור עדיפיות של המשלוחים המסודרים לפי דדלין ומי הכי קרוב
#יש להסיר את המשלוחים שזמן ההתחלה או הסיום כבר עבר מזמן יציאת השליח - בקיצור מי שלא יספיק להגיע
def update_delivery_queue(graph, current_locations, deliveries: List[Delivery1]) -> List[Delivery1]:
    updated_queue = []
    heap = []
    for j, delivery in enumerate(deliveries):
        heapq.heappush(heap, (delivery.end, j, delivery))  # הוספה עם אינדקס למניעת שגיאות

    current_location = current_locations  

    while heap:
        min_deadline, _, first_delivery = heapq.heappop(heap)
        candidates = [(min_deadline, _, first_delivery)]

        while heap and heap[0][0] <= min_deadline:
            candidates.append(heapq.heappop(heap))

        # נמצא את הקרוב ביותר למיקום הנוכחי
        min_time = float('inf')
        best_index = 0
        for i, (_, _, delivery) in enumerate(candidates):
            time = newnewosm.calculate_travel_time_between_coordinates(
                graph, current_location.destination, delivery.destination
            )
            time = int(time) if time is not None else float('inf')
            print(f"זמן הנסיעה בין {current_location.destination} ל-{delivery.destination} הוא {time} דקות.")
            if time < min_time:
                min_time = time
                best_index = i

        # הוספת המשלוח הקרוב ביותר לתור
        best_delivery = candidates.pop(best_index)[2]
        updated_queue.append(best_delivery)
        current_location = best_delivery

        # החזרת שאר המשלוחים לערימה
        for item in candidates:
            heapq.heappush(heap, item)

    return updated_queue