import heapq
import newnewosm as newnewosm


class DelayHeap:
    def __init__(self):
        self.heap = []  # רשימה שמייצגת את הערימה

    def add_node(self, delay_time, node):
        """
        הוספת צומת לערימת המינימום.
        :param delay_time: זמן העיכוב האפשרי (int)
        :param node: מזהה הצומת
        """
        heapq.heappush(self.heap, (delay_time, node))

    def pop_min(self):
        """
        שליפת הצומת עם זמן העיכוב המינימלי.
        :return: זוג (זמן עיכוב, מזהה צומת)
        
        """
        if self.heap:
            return heapq.heappop(self.heap)
        return None

    def peek_min(self):
        """
        הצצה בצומת עם זמן העיכוב המינימלי מבלי להסיר אותו.
        :return: זוג (זמן עיכוב, מזהה צומת)
        """
        if self.heap:
            return self.heap[0]
        return None

    def is_empty(self):
        """
        בדיקה אם הערימה ריקה.
        :return: True אם הערימה ריקה, אחרת False
        """
        return len(self.heap) == 0

    def update_heap(delay_heap, delivery_queue, graphmaps, current_location, target_location, travel_time):
        """
        מעדכנת את ערימת המינימום עם זמני העיכוב החדשים.
        """
        for delivery in delivery_queue:
            time_to_delivery = newnewosm.calculate_travel_time_between_coordinates(graphmaps, current_location, delivery)
            time_from_delivery_to_target = newnewosm.calculate_travel_time_between_coordinates(graphmaps, delivery, target_location)

            if time_to_delivery is not None and time_from_delivery_to_target is not None:
                total_time = time_to_delivery + time_from_delivery_to_target
                delay_time = target_location.get_end_time() - (travel_time + total_time)

                if delay_time > 0:
                    delay_heap.add_node(delay_time, delivery)
    def update_delays(self, decrement):
        """
        עדכון כל זמני העיכוב בערימה על ידי הפחתת ערך מסוים.
        :param decrement: הערך להפחתה מכל זמני העיכוב (int)
        :return: True אם כל הערכים עודכנו בהצלחה, False אם אחד הערכים הפך לשלילי
        """
        updated_heap = []
        while self.heap:
            delay_time, node = heapq.heappop(self.heap)
            new_delay_time = delay_time - decrement
            if new_delay_time < 0:
                print(f"לא ניתן לעדכן את הערימה: זמן עיכוב שלילי בצומת {node}")
                # return False
            updated_heap.append((new_delay_time, node))

        # החזרת הערכים המעודכנים לערימה
        self.heap = updated_heap
        heapq.heapify(self.heap)
        # return True