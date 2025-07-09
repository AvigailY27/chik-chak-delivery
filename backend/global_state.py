from deliveryList import DeliveryLinkedList
from heapqstruct import DelayHeap
import newnewosm as osm1
# גרף כולל של כל האזורים – ניתן לטעון פעם אחת ולעבוד איתו
PLACE_NAME = "אלעד, ישראל"
graphmaps, nodes, edges = osm1.map_mapping_graf(PLACE_NAME)

# מילון של שליחים -> לכל שליח רשימה וערימת עיכובים משלו
courier_state = {}

# מילון של אזורים: לכל אזור נשמרת הרשימה שלו וערימת העיכובים שלו
delivery_state_by_area = {}
def get_or_create_courier(phone):
    if phone not in courier_state:
        courier_state[phone] = {
            "delivery_list": DeliveryLinkedList(),
            "delay_heap": DelayHeap()
        }
    return courier_state[phone]
#גישה לרשימה של שליח
# איפשהו בקוד שלך:
courier_data = get_or_create_courier("0548408327")
# courier_data["delivery_list"].append(new_delivery)
# courier_data["delay_heap"].insert(new_delivery)
