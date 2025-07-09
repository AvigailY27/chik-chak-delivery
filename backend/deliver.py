import heapq
from typing import List, Tuple
import kmeans1 as kmeans1
import newnewosm as newnewosm
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
import json
import os
from datetime import datetime, timedelta
# מחלקה של שליח
class DeliveryPerson:
    def __init__(self, person_id, phone, start, end, current_location, current_time):
        self.person_id = person_id
        self.phone = phone
        self.start = start  # שעת התחלה ("08:00")
        self.end = end      # שעת סיום ("18:00")
        self.current_location = current_location
        self.current_time = current_time  # אפשר לשנות לפי הצורך

    # מאפיין current_location
    @property
    def current_location(self):
        return self._current_location

    @current_location.setter
    def current_location(self, value):
        self._current_location = value

    # מאפיין current_time
    @property
    def current_time(self):
        return self._current_time

    @current_time.setter
    def current_time(self, value):
        self._current_time = value

    # מאפיין phone
    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        self._phone = value

    def __lt__(self, other):
        return str(self.destination) < str(other.destination)
    def __str__(self):
        return f" מזהה: {self.person_id}, שעות פעילות: {self.start} עד {self.end}, מיקום נוכחי: {self.current_location}"
    def __repr__(self):
        return (f"DeliveryPerson(person_id='{self.person_id}', "
            f"phone='{self.phone}', start='{self.start}', end='{self.end}', "
            f"location='{self.current_location}', current_time='{self.current_time}')")


class Delivery:
    def __init__(self, destination, timeMax, start, end):
        self._destination = destination  # משתנה פרטי
        self._timeMax = timeMax
        self._start = start
        self._end = end

    @property
    def destination(self):
        return self._destination

    # @destination.setter
    # def destination(self, value):
    #     self._destination = value

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
        return (f"Delivery(destination='{self.destination}', "
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

    def to_dict(self):
        return {
            "destination": self.destination,
            "timeMax": self.timeMax,
            "start": self.start,
            "end": self.end
        }


def convert_to_delivery_objects(deliveries_dict_list):
    delivery_objects = []
    for d in deliveries_dict_list:
        delivery = Delivery(
            destination=d.get("כתובת"),
            timeMax=d.get("שעות פעילות מקסמלי"),
            start=d.get("שעת התחלה"),
            end=d.get("שעת סיום")
        )
        delivery_objects.append(delivery)
    return delivery_objects

# הפונקציה בונה תור עדיפיות ליעדים לפי השעות סיום כדי שנוכל לקחת את השעה הראשונה כדחופה
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

#פונקציה שבונה תור עדיפיות של המשלוחים המסודרים לפי דדלין ומי הכי קרוב
def update_delivery_queue(graph, current_location, deliveries: List[Delivery]) -> List[Delivery]:
    updated_queue = []
    heap = []
    for j, delivery in enumerate(deliveries):
            #שם בתור עדיפיות זמן סיום, אינדקס, פרטי משלוח 
        heapq.heappush(heap, (delivery.end, j, delivery))  # הוספה עם אינדקס למניעת שגיאות
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
                graph, current_location, delivery.destination)
            time = int(time) if time is not None else float('inf')
            print(f"זמן הנסיעה בין {current_location} ל-{delivery.destination} הוא {time} דקות.")
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


import os
import json

def load_existing_couriers(file_path="couriers.json"):
    """
    טוען שליחים מקובץ JSON אם הוא קיים ותקין.
    מחזיר -1 במקרה של שגיאה או קובץ ריק.
    """
    if not os.path.exists(file_path):
        return -1

    try:
        if os.path.getsize(file_path) == 0:
            print(f"שגיאה: הקובץ {file_path} ריק.")
            return -1

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                print(f"שגיאה: הקובץ {file_path} לא מכיל רשימת שליחים תקינה.")
                return -1
    except (json.JSONDecodeError, IOError) as e:
        print(f"שגיאה בטעינת הקובץ {file_path}: {e}")
        return -1
    
def save_couriers(couriers, file_path="couriers.json"):
    """
    שומר את רשימת השליחים בקובץ JSON.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(couriers, file, ensure_ascii=False, indent=4)

def calculate_clusters_and_balance_workload(graphmaps, deliveries, max_distance=2, max_deliveries_per_courier=3):
    coordinates = [kmeans1.get_coordinates(delivery.destination) for delivery in deliveries]
    coordinates = np.array(coordinates)

    # קביעת מספר אשכולות מינימלי שיכסה את כל המשלוחים לפי מרחק מקסימלי
    num_clusters = 1
    while True:
        kmeans = KMeans(n_clusters=num_clusters, random_state=0)
        kmeans.fit(coordinates)
        cluster_centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        
        covered = all(
            np.linalg.norm(coord - cluster_centers[labels[i]]) <= max_distance
            for i, coord in enumerate(coordinates)
        )

        if covered:
            break
        else:
            num_clusters += 1

    # חלוקה לקלאסטרים
    clusters = {}
    for i, label in enumerate(labels):
        clusters.setdefault(label, []).append(deliveries[i])


    # טעינת שליחים קיימים
    existing_couriers = load_existing_couriers()
   

    existing_count = len(existing_couriers) if existing_couriers != -1 else 0

    if existing_count < num_clusters:
        missing = num_clusters - existing_count
        print(f"חסרים {missing} שליחים")
        return -1, None, missing
    # הכנה לשיבוץ שליחים
    couriers = [
        DeliveryPerson(
            person_id=c["id"],
            phone=c["phone"],
            start=c["start"],
            end=c["end"],
            current_location=c["current_location"],
            current_time=c["current_time"]
        )
        for c in existing_couriers
    ]
    print(existing_couriers)
    courier_workload = {c.person_id: [] for c in couriers}
    unassigned_deliveries = []

    for cluster_id, cluster_deliveries in clusters.items():
        for delivery in cluster_deliveries:
            closest_courier = None
            min_distance = float('inf')

            for courier in couriers:
                travel_time = newnewosm.calculate_travel_time_between_coordinates(
                    graphmaps, courier.current_location, delivery.destination
                )
                courier_current_time = datetime.strptime(courier.start, "%H:%M")
                courier_end_time = datetime.strptime(courier.end, "%H:%M")
                travel_time_delta = timedelta(minutes=travel_time)

                if courier_current_time + travel_time_delta > courier_end_time:
                    continue
                if len(courier_workload[courier.person_id]) >= max_deliveries_per_courier:
                    continue
                if travel_time < min_distance:
                    min_distance = travel_time
                    closest_courier = courier
            if closest_courier:
                courier_workload[closest_courier.person_id].append((delivery, min_distance))
            else:
                unassigned_deliveries.append(delivery)

    return num_clusters, courier_workload, 0  # 0 = לא חסרים שליחים
