# ייבוא כל הקבצים בתיקיית backend
import deliver
import exampleme
import heapqstruct
import kmeans1
import listbuild
import listCoorect
import listupupdet
import main
import newnewosm
import shortpathme
import process

# מילון שמרכז את כל הפונקציות מכל קובץ
functions_registry = {
    "deliver": {
        "update_delivery_queue": deliver.update_delivery_queue,  # פונקציה לעדכון תור משלוחים
        "prioritize_deliveries": deliver.prioritize_deliveries,  # פונקציה למיון משלוחים
    },
    "exampleme": {
        "create_subgraph_from_nodes": exampleme.create_subgraph_from_nodes,  # יצירת תת-גרף מצמתים
    },
    "heapqstruct": {
        "DelayHeap": heapqstruct.DelayHeap,  # מחלקה לערימת עיכובים
    },
    "kmeans1": {
        "set_coordinates": kmeans1.set_coordinates,  # חלוקת כתובות לאזורים
        "get_coordinates": kmeans1.get_coordinates,  # המרת כתובת לקואורדינטות
    },
    "listbuild": {
        "build_route_with_delays": listbuild.build_route_with_delays,  # בניית מסלול עם עיכובים
    },
    "listCoorect": {
        "DeliveryLinkedList": listCoorect.DeliveryLinkedList,  # רשימה דו-כיוונית למשלוחים
    },
    "listupupdet": {
        "listupupdet": listupupdet.listupupdet,  # פונקציה לניהול תור משלוחים
    },
    "main": {
        "main": main.main,  # פונקציה ראשית
    },
    "newnewosm": {
        "map_mapping_graf": newnewosm.map_mapping_graf,  # מיפוי גרף מהמפה
        "calculate_travel_time_between_coordinates": newnewosm.calculate_travel_time_between_coordinates,  # חישוב זמן נסיעה
    },
    "shortpathme": {
        "draw_ordered_route": shortpathme.draw_ordered_route,  # ציור מסלול לפי סדר כתובות
        "addresses_to_nodes": shortpathme.addresses_to_nodes,  # המרת כתובות לצמתים
    },
    "process": {
        "process_input_file": process.process_input_file,  # עיבוד קובץ קלט
    },
}

# פונקציה לקריאה לפונקציה לפי שם הקובץ ושם הפונקציה
def call_function(module_name, function_name, *args, **kwargs):
    """
    קריאה לפונקציה לפי שם המודול ושם הפונקציה.
    :param module_name: שם המודול (לדוגמה: 'deliver')
    :param function_name: שם הפונקציה (לדוגמה: 'update_delivery_queue')
    :param args: ארגומנטים לפונקציה
    :param kwargs: ארגומנטים עם מילות מפתח לפונקציה
    :return: תוצאה מהפונקציה
    """
    try:
        func = functions_registry[module_name][function_name]
        return func(*args, **kwargs)
    except KeyError:
        raise ValueError(f"פונקציה '{function_name}' לא נמצאה במודול '{module_name}'")
    except Exception as e:
        raise RuntimeError(f"שגיאה בהרצת הפונקציה '{function_name}' במודול '{module_name}': {e}")

# דוגמה לשימוש בפונקציה call_function
from functions_registry import call_function

# קריאה לפונקציה update_delivery_queue מתוך המודול deliver
result = call_function(
    "deliver",
    "update_delivery_queue",
    graphmaps,  # ארגומנט 1
    current_location,  # ארגומנט 2
    deliveries  # ארגומנט 3
)
print(result)