from datetime import datetime, timedelta
import newnewosm as newosm
import deliver
import listupupdet
from global_state import get_or_create_courier , graphmaps

MAX_ALLOWED_DELAY = 15  # דקות עיכוב 
from datetime import datetime, timedelta
import newnewosm as newosm
import deliver
import listupupdet
from global_state import get_or_create_courier, graphmaps

MAX_ALLOWED_DELAY = 15  # דקות עיכוב 

def optimize_route(courier):
    """
    שיפור המסלול על ידי הכנסת משלוחים בין יעדים קיימים
    """
    courier_data = get_or_create_courier(courier['phone'])
    delivery_list = courier_data['delivery_list']
    delay_heap = courier_data['delay_heap']
    delay_heap.update_delays(0)
    
    current_node = delivery_list.head if delivery_list.head else None
    courier['current_time'] = datetime.now().time()
    print(f"Courier current time: {courier['current_time']}")

    while current_node and current_node.next:
        noded = delivery_list.head
        while noded:
            # ודא שאת לא מנסה להכניס את current_node או current_node.next עצמן
            if noded != current_node and noded != current_node.next:
                print(f"Checking delivery: {noded.delivery.destination} between {current_node.delivery.destination} and {current_node.next.delivery.destination}")

                time_to_candidate = newosm.calculate_travel_time_between_coordinates(
                    graphmaps, current_node.delivery.destination, noded.delivery.destination
                )
                time_from_candidate_to_next = newosm.calculate_travel_time_between_coordinates(
                    graphmaps, noded.delivery.destination, current_node.next.delivery.destination
                )
                original_time = newosm.calculate_travel_time_between_coordinates(
                    graphmaps, current_node.delivery.destination, current_node.next.delivery.destination
                )

                alternative_time = time_to_candidate + time_from_candidate_to_next

                start_time = datetime.strptime(noded.delivery.start, '%H:%M').time()
                end_time = datetime.strptime(noded.delivery.end, '%H:%M').time()

                courier_datetime = datetime.combine(datetime.today(), courier['current_time'])
                arrival_time = courier_datetime + timedelta(minutes=alternative_time)
                arrival_time_only = arrival_time.time()

                print(f"Alternative travel time: {alternative_time}, Original travel time: {original_time}")
                print(f"Delivery time window: {start_time} to {end_time}")
                print(f"Expected arrival time: {arrival_time_only}")

                allowed_delay = max(delay_heap.peek_min()[0], MAX_ALLOWED_DELAY)

                if alternative_time <= original_time or (alternative_time - original_time) <= allowed_delay:
                    if start_time <= arrival_time_only <= end_time:
                        if (alternative_time - original_time) <= delay_heap.peek_min()[0]:
                            print(f"Adding delay to heap: {alternative_time - original_time}")
                            delay_heap.update_delays(alternative_time - original_time)
                            delivery_list.add_between(current_node, current_node.next, noded.delivery)
                            print(f"Inserted delivery {noded.delivery.destination} between {current_node.delivery.destination} and {current_node.next.delivery.destination}")

                            # הסרה של הצומת מהמיקום הקודם
                            if noded.prev:
                                noded.prev.next = noded.next
                            if noded.next:
                                noded.next.prev = noded.prev
                            if noded == delivery_list.head:
                                delivery_list.head = noded.next
                            if noded == delivery_list.tail:
                                delivery_list.tail = noded.prev
                            noded.prev = None
                            noded.next = None
                            break
            noded = noded.next
        current_node = current_node.next
        print(f"Moving to next delivery: {current_node.delivery.destination if current_node else 'None'}")

    print("Route optimization completed.")
    print(delivery_list)
    return delivery_list
