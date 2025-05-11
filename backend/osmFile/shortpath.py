import newnewosm as osm
import osmnx as ox
import kmeans1 as kmeans1
import matplotlib.pyplot as plt
import networkx as nx


# חלוקת  אזורים  וחיפוש מי הקרוב ביותר למיקום שלי איזה אזור ובתוך האזור איזה כתובת

def main():
    #  הפעלת כל החלקים
    place_name = "אלעד, ישראל"
    graphmaps, nodes, edges = osm.map_mapping_graf(place_name)

    addresses = [
        "רבי מאיר 1, אלעד",
        "רבי יהודה הנשיא, אלעד",
        "אליהו הנביא 7, ראש העין",

    ]

    clusters_info = kmeans1.set_coordinates(graphmaps, addresses)
    warehouse = "בן קיסמא, אלעד"
    lat, lon = kmeans1.get_coordinates(warehouse)
    my_node = ox.distance.nearest_nodes(graphmaps, lon, lat)

    closest_nodes_per_area = []
    for cluster_name, area_nodes in clusters_info.items():
        print(f"Processing {cluster_name}: {area_nodes}")
        closest = min(area_nodes,
                      key=lambda node_info: nx.shortest_path_length(graphmaps, my_node, node_info['node_id'],
                                                                    weight='length'))
        closest_nodes_per_area.append(closest['node_id'])  # שמור רק את ה-Node ID

    distances = [
        nx.shortest_path_length(graphmaps, my_node, node_id, weight='length')
        for node_id in closest_nodes_per_area
    ]
    best_area_index = distances.index(min(distances))
    best_start_node = closest_nodes_per_area[best_area_index]
    route = nx.shortest_path(graphmaps, my_node, best_start_node, weight='length')
    print(route)
    print("מסלול של הקרוב ביותר באזור:")
    ox.plot_graph_route(graphmaps, route, route_color='blue')
    # הצגת מידע
    for cluster, items in clusters_info.items():
        print(f"\n{cluster}:")
        for item in items:
            print(f"  Address: {item['address']}, Node: {item['node_id']}")
    plt.gcf().canvas.manager.set_window_title("מפה של אלעד")
    plt.title("Delivery in Map")
    plt.show()


def draw_ordered_route(graph, addresses, start_address):
    # המרת הכתובת ההתחלתית לצומת
    lat, lon = kmeans1.get_coordinates(start_address)
    start_node = kmeans1.get_node_id(graph, lon, lat)

    # המרת כל כתובת ברשימה לצומת
    address_nodes = []
    node_to_address = {}
    for address in addresses:
        lat, lon = kmeans1.get_coordinates(address)
        node = kmeans1.get_node_id(graph, lon, lat)
        address_nodes.append(node)
        node_to_address[node] = address

    # בניית המסלול לפי הסדר
    full_route = []
    current_node = start_node
    for next_node in address_nodes:
        partial_route = nx.shortest_path(graph, current_node, next_node, weight='length')
        full_route.extend(partial_route[:-1])  # נמנע מכפילות בצומת האחרון
        current_node = next_node
    full_route.append(current_node)  # הוספת הצומת האחרון

    # ציור המסלול
    fig, ax = ox.plot_graph_route(graph, full_route, route_color='blue', node_size=10)

    # תיוג כתובות
    for node in full_route:
        x, y = graph.nodes[node]['x'], graph.nodes[node]['y']
        ax.text(x, y, str(node), fontsize=8, color='red',
                bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))
    node_labels = {node: node_to_address.get(node, "") for node in full_route}
    for node, label in node_labels.items():
        if label:
            x, y = graph.nodes[node]['x'], graph.nodes[node]['y']
            ax.text(x, y, label, fontsize=8, color='red', bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))
    plt.title("Delivery in address")
    plt.show()


if __name__ == "__main__":
    main()
