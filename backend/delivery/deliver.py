import heapq
from geopy.distance import geodesic
from typing import List, Tuple
from kmeansFile import kmeans1 as kmeans1


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

    def add_constraint(self, constraint):
        """הוספת אילוץ נוסף למשלוח"""
        self.constraints.append(constraint)


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
    def __init__(self, destination, deadline, start, end):
        self.destination = destination  # נקודת מסירה (קואורדינטות או כתובת)
        self.deadline = deadline
        # datetime.strptime(deadline, "%Y-%m-%d %H:%M")  # זמן
        self.start = start  # טווח שעות הפעילות של הלקוח
        self.end = end

    def __repr__(self):
        return (f"Delivery(id={self.package_id}, destination='{self.destination}', "
                f", deadline='{self.deadline}', ")


# הפונקציה בונה תור עדיפיות ליעדים לפי השעת סיום כדי שנוכל לקחת את השעה הראשונה כדחופה
# deliveries_list סוג משלוח, צריך לקבל
def prioritize_deliveries(deliveries_list):
    priority_queue = []
    sorted_deliveries = sorted(deliveries_list, key=lambda d1: d1.deadline)
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

def update_delivery_queue(current_locations, deliveries: List[Delivery1]) -> List[Delivery1]:
    heap = []
    for j, delivery in enumerate(deliveries):
        heapq.heappush(heap, (delivery.deadline, j, delivery))  # הוספה עם אינדקס למניעת שגיאות

    updatedeliveries = []

    while heap:
        min_deadline, _, first_delivery = heapq.heappop(heap)
        candidates = [(min_deadline, _, first_delivery)]

        # נבדוק את כל מי שהדדלין שלו עד הדדלין הזה
        while heap and heap[0][0] <= min_deadline:
            candidates.append(heapq.heappop(heap))

        # נמצא את הקרוב ביותר למיקום הנוכחי
        # נשנה לקרוב גם מבחינת זמן
        min_distance = float('inf')
        best_index = 0
        for i, (_, _, delivery) in enumerate(candidates):
            distance = geodesic(kmeans1.get_coordinates(current_locations),
                                kmeans1.get_coordinates(delivery.destination)).meters
            if distance < min_distance:
                min_distance = distance
                best_index = i

        # נבחר את הכי קרוב ונעביר אותו לראש התור
        best_delivery = candidates.pop(best_index)[2]
        updatedeliveries.append(best_delivery)
        current_locations = best_delivery

        # את כל השאר נחזיר לתור
        for item in candidates:
            heapq.heappush(heap, item)

    return updatedeliveries

# דוגמא לנתוני משלוחים
deliveries = [
    Delivery1( "אבן גבירול 3 , אלעד", "6", "7:00", "8"),
    Delivery1("הרב שלום שבזי 1, ראש העין", "6", "7:00", "8"),
    Delivery1( "רמבם 1, אלעד", "6", "7:00", "8"),
    Delivery1( "בעלי התוספות 10, אלעד", "6", "8:00", "8")
]
current_location = "רבי יוסי בן קיסמא 36 ,אלעד"

# עדכון התור עם המשלוחים הממוינים
updated_deliveries = update_delivery_queue(current_location, deliveries)

# הדפסת המשלוחים בסדר האופטימלי
for i, d in enumerate(updated_deliveries):
    print(f"מסלול {i + 1}: {d.destination}, דדלין: {d.deadline}")

# זוהי רשימת כתובות לאזור נגיד- לבחירה
