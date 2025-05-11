# בנית תור לפי זמן סיום (לשנות  מי שדדלין ומה לפי מי  ששעת התחלה קרוב לסיום)
#מעבר על התור ובנית רשימה לכל יעד ע"פ העומס בתנועה
#הרשימה נבנית לפי יעדים דחופים בתור+ ומי שמצטרך בחישוב מסלול חילופי כך מעבר על כל היעדים אם יש זמן אפשרי למ
import process as process
import listCoorect as listCoorect
import listbuild as listbuild
import deliver as deliver
import os as os
from bidi.algorithm import get_display
import arabic_reshaper
import shortpathme as sp
import heapqstruct as heapqstruct
import newnewosm as newnewosm
from datetime import datetime

def listupupdet(graphmaps,deliveries, update_queue, delay_heap):
    #  מעבר על המשלוחים לבנית הערימה
    for delivery in update_queue:
        # חישוב זמן עיכוב אפשרי בנית ערימת מינימום של  הזמן
        current_location = update_queue[0]  # המשלוח הראשון בתור
        time = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location._destination, delivery._destination)
        if time is None or time < 0:
            print(f"לא ניתן לחשב זמן נסיעה בין {current_location._destination} ל-{delivery}.")
            continue
        # המרת זמן התחלה וסיום למספר דקות
        delivery_end = time_to_minutes(delivery.end)
        delivery_start = time_to_minutes(delivery.start)
        if float(delivery_end)- float(delivery_start)< time :
            print(f"זמן העיכוב של {delivery} הוא שלילי. לא ניתן להוסיף משלוח זה.")
            continue
        else:
            delay_heap.add_node(delivery_end- time, delivery.destination)
        if  len(update_queue) < 2 or update_queue is None:
            print("אין משלוחים בתור.")
            return
        else:     
            updated_list, update_queue = listbuild.build_route_with_delays(graphmaps, update_queue, delay_heap)
    return updated_list, update_queue


def filter_deliveries_by_courier_hours(deliveries, courier_start, courier_end):
    """
    מסיר משלוחים שמחוץ לטווח שעות פעילות השליח.
    """
    start_min = time_to_minutes(courier_start)
    end_min = time_to_minutes(courier_end)
    relevant = []
    not_relevant = []
    for delivery in deliveries:
        delivery_start = time_to_minutes(str(delivery.start))
        delivery_end = time_to_minutes(str(delivery.end))
        if delivery_end < start_min or delivery_start > end_min:
            not_relevant.append(delivery)
        else:
            relevant.append(delivery)
    return relevant, not_relevant

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