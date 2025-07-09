import heapq
import newnewosm as newnewosm
import listupupdet as listupupdet

class DelayHeap:
    def __init__(self):
        self.heap = []

    def add_node(self, delay_time, node):
        heapq.heappush(self.heap, (delay_time, node))

    def pop_min(self):
        if self.heap:
            return heapq.heappop(self.heap)
        return None

    def peek_min(self):
        if self.heap:
            return self.heap[0]
        return None

    def is_empty(self):
        return len(self.heap) == 0

    def build_heap(self, update_queue, graphmaps):
        for delivery in update_queue:
            current_location = update_queue[0]
            time = newnewosm.calculate_travel_time_between_coordinates(
                graphmaps, current_location._destination, delivery._destination)
            if time is None or time < 0:
                print(f"Cannot calculate travel time between {current_location._destination} and {delivery}.")
                continue
            delivery_end = listupupdet.time_to_minutes(delivery.end)
            delivery_start = listupupdet.time_to_minutes(delivery.start)
            if float(delivery_end) - float(delivery_start) < time:
                print(f"Negative delay time for delivery {delivery}. Cannot add this delivery.")
                continue
            else:
                self.add_node(delivery_end - delivery_start - time, delivery.destination)

    def update_delays(self, decrement):
        updated_heap = []
        while self.heap:
            delay_time, node = heapq.heappop(self.heap)
            new_delay_time = delay_time - decrement
            if new_delay_time < 0:
                print(f"Cannot update heap: negative delay time at node {node}")
            updated_heap.append((new_delay_time, node))
        self.heap = updated_heap
        heapq.heapify(self.heap)
    def remove_node(self, destination_to_remove):
        updated_heap = []
        removed = False
        while self.heap:
            delay_time, node = heapq.heappop(self.heap)
            if node == destination_to_remove:
                removed = True
                print(f"Removed node '{node}' from heap.")
                continue  # מדלג על הוספתו לרשימה החדשה
            updated_heap.append((delay_time, node))
        self.heap = updated_heap
        heapq.heapify(self.heap)
        if not removed:
            print(f"Node '{destination_to_remove}' not found in heap.")
    