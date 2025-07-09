import osmnx as ox
import matplotlib.pyplot as plt
# אולי נכתוב בC
# מקבלת 2 כתובות ומחזירה מסלוול קצר בינהם
#אפשרי מטריצת סמיכיות ין כל יעד מי סמוך אליו
import networkx as nx

def get_shortest_route_and_length(graph, source_node, target_node, weight='length'):
    try:
        path = nx.shortest_path(graph, source=source_node, target=target_node, weight=weight)
        length = nx.shortest_path_length(graph, source=source_node, target=target_node, weight=weight)
        return {
            'path': path,
            'length': length
        }
    except nx.NetworkXNoPath:
        return {
            'error': f"No path found between {source_node} and {target_node}"
        }
# קריאה לפונקציה כך: result = get_shortest_route_and_length(graphmaps, node1, node2)

destinations = []  # סתםםםםםםםםם
graph = 0 #סתםםםם
labels = 0 #סתםםםם
# הוספת תוויות ליעדים
node_labels = {dest[0]: dest[1] for dest in destinations}

# צביעת היעדים לפי קלסטרים
node_colors = ['red' if label == 0 else 'blue' for label in labels]

# חישוב המסלול הכולל בין היעדים
route = nx.shortest_path(graph, source=destinations[0][0], target=destinations[1][0], weight='length')
for i in range(1, len(destinations) - 1):
    next_route = nx.shortest_path(graph, source=destinations[i][0], target=destinations[i + 1][0], weight='length')
    route.extend(next_route[1:])  # הוספת המסלול הבא ללא הצומת הראשון (כבר נוסף)

# הצגת הגרף עם היעדים והמסלול
fig, ax = ox.plot_graph(graph, node_size=10, node_color='gray', edge_color='gray', show=False, close=False)
ox.plot_graph_route(graph, route, route_color='green', route_linewidth=2, ax=ax)
ox.plot_graph(graph, node_size=100, node_color=node_colors, node_edgecolor='black',
              nodelist=[dest[0] for dest in destinations], node_zorder=3, ax=ax)
for dest in destinations:
    x, y = dest[2][1], dest[2][0]
    ax.text(x, y, dest[1], fontsize=12, ha='right', color='black',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
plt.show()
