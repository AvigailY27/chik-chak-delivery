import numpy as np
import osmnx as ox
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim
from shapely.geometry import box
import pandas as pd
import json
import requests


# הגדרת פונקציה להמרת כתובת לקואורדינטות
def get_coordinates(address):
    geolocator = Nominatim(user_agent="shipment_cluster")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None


def set_coordinates(graph, addresses, num_clusters):
    # המרת הכתובות לקואורדינטות
    coords = [get_coordinates(addr) for addr in addresses]
    coords = np.array([c for c in coords if c is not None])  # מסנן None
    # ביצוע KMeans Clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(coords)

    # קואורדינטות עבור ראש העין ואלעד
    north, south, east, west = 32.10, 32.04, 34.97, 34.90
    polygon = box(west, south, east, north)

    # הגדרת זמן Timeout ל-requests
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.Session()
    s.mount('http://', requests.adapters.HTTPAdapter(max_retries=5))

    # ציור המשלוחים על המפה עם אשכולות
    fig, ax = ox.plot_graph(graph, show=False, close=False)

    # ציור המשלוחים לפי האשכולות
    colors = ['orange', 'blue', 'green', 'purple', 'red']
    for i, (lat, lon) in enumerate(coords):
        ax.scatter(lon, lat, c=colors[labels[i]], s=100, edgecolors='black', label=f"Cluster {labels[i]}")

    plt.title("Delivery in Map")
    plt.show()

    # שמירת המידע של האשכולות
    clusters = {f"Cluster_{i}": [] for i in range(num_clusters)}

    # שמירה של קואורדינטות וכתובת לפי אשכול
    for i, (lat, lon) in enumerate(coords):
        cluster_id = labels[i]
        clusters[f"Cluster_{cluster_id}"].append({
            "address": addresses[i],  # כתובת מהמרה
            "coordinates": (lat, lon),  # קואורדינטות
        })

    # שמירה בקובץ JSON
    with open("shipment_clusters.json", "w") as f:
        json.dump(clusters, f, ensure_ascii=False, indent=4)

    # שמירה כ-DataFrame
    df = pd.DataFrame(columns=["Cluster", "Address", "Latitude", "Longitude"])

    for cluster_id, cluster_info in clusters.items():
        for item in cluster_info:
            df = df._append({
                "Cluster": cluster_id,
                "Address": item["address"],
                "Latitude": item["coordinates"][0],
                "Longitude": item["coordinates"][1],
            }, ignore_index=True)

    # הצגת ה-DataFrame
    print(df)

    # שמירה כקובץ CSV
    df.to_csv("k_means.csv", index=False)

    # חזרה לגרף המחולק עם יעד ואשכול
    return graph, clusters


"""
# שימוש בפונקציה
addresses = ["ראש העין", "אלעד"]  # לדוגמה, כתובת
num_clusters = 3  # מספר אשכולות
graph = ox.graph_from_place('Israel', network_type='drive')  # שים כאן את הגרף שלך

graph, clusters = set_coordinates(graph, addresses, num_clusters)

# אחרי הקריאה לפונקציה, תוכל להשתמש בגרף המחולק
print(clusters)
"""
