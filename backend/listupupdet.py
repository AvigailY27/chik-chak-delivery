# בנית תור לפי זמן סיום (לשנות  מי שדדלין ומה לפי מי  ששעת התחלה קרוב לסיום)
#מעבר על התור ובנית רשימה לכל יעד ע"פ העומס בתנועה
#הרשימה נבנית לפי יעדים דחופים בתור+ ומי שמצטרך בחישוב מסלול חילופי כך מעבר על כל היעדים אם יש זמן אפשרי למ
import process as process
import deliveryList as deliveryList
import listbuild as listbuild
import deliver as deliver
import os as os
import shortpathme as sp
import heapqstruct as heapqstruct
import newnewosm as newnewosm
from datetime import datetime, timedelta

def filter_deliveries_by_courier_hours(deliveries, start, end):
    """
    מסיר משלוחים שמחוץ לטווח שעות פעילות השליח.
    """
    start_min = time_to_minutes(start)
    end_min = time_to_minutes(end)
    relevant = []
    not_relevant = []
    for delivery in deliveries:
        delivery_start = time_to_minutes(str(delivery.start))
        delivery_end = time_to_minutes(str(delivery.end))
        if delivery_end < start_min or delivery_start > end_min or delivery_start ==start_min:
            not_relevant.append(delivery)
        else:
            relevant.append(delivery)
    return relevant, not_relevant

#פונקציה לעדכון זמן הגעה לכל משלוח ותוך כדי בדיקה אם לא יספיק את כולם
def calc_arrival_time_str(current_time: datetime, travel_minutes: int) -> str:
    arrival = current_time + timedelta(minutes=travel_minutes)
    return arrival.strftime("%H:%M")

def filter_deliveries_by_time_and_priority(graph, current_location, deliveries, cureant_start_time):
    """
    בודקת אילו משלוחים ניתן להספיק לפי זמני נסיעה, חלונות זמן ועדיפויות.
    מחזירה: (רשימת משלוחים לביצוע, רשימת משלוחים שלא ניתן להספיק)
    """
    possible = []
    not_possible = []
    current_time = datetime.strptime(cureant_start_time, "%H:%M")

    for delivery in deliveries: 
        # נבחר את המשלוח הראשון בתור (לפי סדר עדיפויות)
        travel_time = newnewosm.calculate_travel_time_between_coordinates(
            graph, current_location, delivery.destination
        )
        travel_time = int(travel_time) if travel_time is not None else 0
        arrival_time = current_time + timedelta(minutes=travel_time)
        delivery_start = datetime.strptime(delivery.start, "%H:%M")
        delivery_end = datetime.strptime(delivery.end, "%H:%M")

        # אם מגיעים אחרי הדדליין - אי אפשר להספיק
        if arrival_time > delivery_end:
            not_possible.append(delivery)
            deliveries.pop(0)
            continue

        # אם מגיעים מוקדם מדי
        if arrival_time < delivery_start:
            # בדוק אם יש משלוחים דחופים יותר לפי מספר סידורי קטן יותר
            urgent_found = False
            for i, other in enumerate(deliveries[1:], 1):
                if hasattr(other, "serial_number") and hasattr(delivery, "serial_number"):
                    if other.serial_number < delivery.serial_number:
                        # מצאנו משלוח דחוף יותר, נבצע אותו קודם
                        deliveries[0], deliveries[i] = deliveries[i], deliveries[0]
                        urgent_found = True
                        break
            if urgent_found:
                continue  # ננסה שוב עם המשלוח החדש בראש
            else:
                # אין דחופים יותר, מחכים עד תחילת החלון
                current_time = delivery_start 
                possible.append(delivery)
                current_location = delivery.destination
                deliveries.pop(0)
        else:
            # אפשר לבצע מיד
            current_time = arrival_time 
            possible.append(delivery)
            current_location = delivery.destination
            deliveries.pop(0)

    return possible, not_possible

def time_to_minutes(time_str):
    """
    ממיר שעה בפורמט HH:MM או HH:MM:SS למספר דקות מאז חצות.
    """
    from datetime import datetime
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            time_obj = datetime.strptime(time_str, fmt)
            return time_obj.hour * 60 + time_obj.minute
        except ValueError:
            continue
    print(f"פורמט שעה לא תקין: {time_str}")
    return None