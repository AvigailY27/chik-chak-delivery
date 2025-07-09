import process as process
import deliveryList as deliveryList
import deliver as deliver
import listupupdet as listupupdet
import os as os
from bidi.algorithm import get_display
import arabic_reshaper
import heapqstruct as heapqstruct
import newnewosm as newnewosm
# def main():
#     place_name = "אלעד, ישראל"
#     graphmaps, nodes, edges = newnewosm.map_mapping_graf(place_name)
#     # קבלת משלוחים מהקובץ
#     deliveries = [
#         deliver.Delivery("שמעון הצדיק אלעד", 2, 8, 14),
#         deliver.Delivery("בן קיסמא אלעד", 3, 9, 15),
#         deliver.Delivery("שמעון בן שטח אלעד", 4, 10, 16),
#     ]
#     current_location = deliver.Delivery("יהודה הנשיא 53, אלעד", 0, 0, 0)  # המרת המיקום הנוכחי לאובייקט Delivery

#     # בנית תור המשלוחים לפי זמן סיום ומשקל
#     update_queue = deliver.update_delivery_queue(graphmaps,current_location, deliveries)
#     print(get_display(arabic_reshaper.reshape(f"Updated deliveries: {update_queue}")))

#     # יצירת רשימה דו-כיוונית
#     delivery_list = deliveryList.DeliveryLinkedList()

#     # בנית ערימת מינימום של זמני עיכוב אפשרים לכל משלוח     
#     #נעבור על כל משלוח וניראה זמן עיכוב אפשרי עד אליו מהראשון  לפי הפונקציה:calculate_delay_time
#     delay_heap = heapqstruct.DelayHeap()
#     print(delay_heap)
#     for delivery in update_queue:
#         # חישוב זמן עיכוב אפשרי בנית ערימת מינימום של  הזמן
#         time = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location, delivery)
#         if time is None:
#             print(f"לא ניתן לחשב זמן נסיעה בין {current_location} ל-{delivery}.")
#             continue
#         if time < 0:
#             print(f"זמן הנסיעה בין {current_location} ל-{delivery} הוא שלילי. לא ניתן להוסיף משלוח זה.")
#             continue
#         if delivery.get_end_time()- delivery.get_start_time()< time :
#             print(f"זמן העיכוב של {delivery} הוא שלילי. לא ניתן להוסיף משלוח זה.")
#             continue
#         else:
#             #עדכון בחוליה זמן נסיעה למשלוח
#             delivery.sum_time = time 
#             delivery_list.add_delivery(delivery)  # הוספת המשלוח לרשימה
#             delay_heap.add_node(delivery.get_end_time() - time, delivery.destination)  # הוספת המשלוח לערימה עם זמן העיכוב האפשרי
#             print(get_display(arabic_reshaper.reshape(f"delivery: {delivery}")))
            
            
#            # בניית ערימת מינימום של זמני עיכוב אפשריים לכל משלוח
#     delay_heap = heapqstruct.DelayHeap()
#     for delivery in update_queue:
#         time_to_delivery = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location, delivery)
#         if time_to_delivery is None:
#             print(f"לא ניתן לחשב זמן נסיעה בין {current_location} ל-{delivery}.")
#             continue
#         print(get_display(arabic_reshaper.reshape(f"delivery: {delivery}"))) 
#         delay_time = delivery.end - time_to_delivery
#         if delay_time > 0:
#             delay_heap.add_node(delay_time, delivery)

#     # מעבר על התור ובדיקת כל משלוח
#     while update_queue:
#         next_delivery = update_queue.pop(0)  # הוצאת המשלוח הבא מהתור
#         travel_time = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location, next_delivery)

#         if travel_time is not None:
#             # קריאה לפונקציה שבודקת אם להכניס את המשלוח לרשימה
#             updated_list = build_route_with_delays(
#                 graphmaps,
#                 current_location,
#                 next_delivery,
#                 travel_time,
#                 update_queue,
#                 delivery_list,
#                 delay_heap
#             )

#             # עדכון הרשימה הדו-כיוונית
#             delivery_list = updated_list

#             # עדכון המיקום הנוכחי
#             current_location = next_delivery

#     print("מסלול שנבנה:")
#     delivery_list.print_list()

# def build_route_with_delays(graphmaps, delivery_queue,waiting_heap, delay_heap):
#     """
#     בונה רשימה בין המיקום הנוכחי ליעד, תוך בדיקת זמני עיכוב ואפשרות להוסיף משלוחים נוספים למסלול.
#     """
#     current_location = delivery_queue[0]  # המשלוח הראשון בתור
#     target_location = delivery_queue[1]  # היעד הבא בתור

#     # # המרת המיקום הנוכחי והיעד לאובייקטים של Delivery
#     # print(get_display(arabic_reshaper.reshape(f"current_location: {current_location}")))
#     # print(get_display(arabic_reshaper.reshape(f"target_location: {target_location}")))
   
#     # יצירת רשימה דו-כיוונית למסלול
#     delivery_list = deliveryList.DeliveryLinkedList()
#     # הוספת היעד הנוכחי והיעד הסופי לרשימה
#     delivery_list.add_delivery(current_location)
#     delivery_list.add_delivery(target_location)
#     travel_time = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location._destination, target_location._destination)
   
   
#     # #קריאה לעדכון הגרף עם המשקלים ואז בדיקה נוספת
#     # travel_time_now = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location._destination, target_location._destination)
#     # if travel_time_now is None or travel_time == travel_time_now:
#     #     print(f"לא ניתן לחשב זמן נסיעה בין {current_location._destination} ל-{target_location._destination}.")
#     #     return delivery_list, delivery_queue
#     # delheap = travel_time_now + min_delay
#     # if delheap < travel_time:


#     # שליפת זמן העיכוב המינימלי מהערימה
#     if not delay_heap.is_empty():
#         min_delay = delay_heap.peek_min()[0]  # שליפת זמן העיכוב המינימלי בלבד (ללא הסרתו)

#         # מעבר על כל המשלוחים בתור
#         for candidate_delivery in delivery_queue:
#             # חישוב זמן נסיעה למסלול חילופי דרך המשלוח הנוסף
#             time_to_candidate = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location._destination, candidate_delivery._destination)
#             time_from_candidate_to_target = newnewosm.calculate_travel_time_between_coordinates(graphmaps, candidate_delivery._destination, target_location._destination)
#             alternative_time = time_to_candidate + time_from_candidate_to_target
#             # בדיקה אם המסלול החלופי עומד בזמנים או לא פוגע בעיכובים
#             if alternative_time is None:    
#                 print(f"לא ניתן לחשב זמן נסיעה בין {current_location._destination} ל-{candidate_delivery}.")
#                 continue
#             # בדיקה אם הזמן החלופי עומד בזמנים 
#             #אני בספק על זה לבדוק...........?????
#             if alternative_time <= travel_time and alternative_time <= min_delay:
#                 # הוספת המשלוח בין הנוכחי ליעד               
#                 delivery_list.add_between(current_location, target_location, candidate_delivery)
#                 #הסרה מהתור
#                 delivery_queue.remove(candidate_delivery)
#                 # עדכון המיקום הנוכחי
#                 current_location = candidate_delivery
#                 # עדכון זמן הנסיעה
#                 travel_time = alternative_time
#                 # עדכון זמני העיכוב בערימה
#                 update_heap(delay_heap, delivery_list, graphmaps, current_location, target_location, travel_time)
#     #מי שנישאר בתור נעתיק אותו לפי הסדר בתור לרשימה שנבנתה
#     for delivery in delivery_queue:
#             delivery_list.add_delivery(delivery)  # הוספת המשלוח לרשימה
#     return delivery_list, delivery_queue  # החזרת הרשימה והמשלוחים שנותרו בתור

def update_heap(delay_heap, delivery_list, graphmaps, current_location, target_location, travel_time):
    """
    מעדכנת את ערימת המינימום עם זמני העיכוב החדשים.
    """
    for delivery in delivery_list:
        time_to_delivery = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location._destination, delivery._destination)
        time_from_delivery_to_target = newnewosm.calculate_travel_time_between_coordinates(graphmaps, delivery._destination, target_location._destination)

        if time_to_delivery is not None and time_from_delivery_to_target is not None:
            total_time = time_to_delivery + time_from_delivery_to_target
            delay_time = float(listupupdet.time_to_minutes(target_location._end)) - float(travel_time + total_time)

            if delay_time > 0:
                delay_heap.add_node(delay_time, delivery)
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    #קריאה ל
             #מעבר על הרשימה ובדיקה מה ניתן להכניס על הדרך, לפי זמן עיכוב מינימלי ביעד
             # תוך כדי בדיקה אם הזמן נסיעה הוא יגיע בטווח שעות הפעילות נכון לגבי הראשון
        


        #מעבר # הוספת המשלוח עם זמן העיכוב האפשרי לערימה
#print(get_display(arabic_reshaper.reshape(f" delay_heap: {delay_heap}")))
        #בדיקת הזמן אם  יספיק ואם יש זמן עיכוב אפשרי
        #calculate_travel_time_between_coordinates(graphmaps, )
    # // הוספת המשלוחים הנוספים לרשימה לפי התור להמשיך מכאן....
    # // להמשיך מעבר על התוא ובנית ערימת זמן מינימום+ בדיקתת זמן עיכוב אם אפשרי או שפוגע...
    # //להמשיך אחר כך עם הוספת המשלוחים לרשימה
    # # הוספת המשלוחים הנוספים לרשימה לפי התור לזכור להוריד מהתור מי שעובר לרשימה קומפלט



if __name__ == "__main__":
    main()