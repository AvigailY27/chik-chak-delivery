from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from sklearn.cluster import KMeans
import numpy as np
import folium

# כתובות לדוגמה
addresses = [
    "יהודה הנשיא, אלעד",
    "רבי מאיר, אלעד",
    "בן גוריון 10, פתח תקווה",
    "הרב קוק 15, ראש העין",
    "אלי כהן 7, כפר סבא",
    "ההגנה 30, רמת גן",
]

# 1. המרת כתובות לקואורדינטות
geolocator = Nominatim(user_agent="tzik-tzak")
def address_to_coords(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

coords = [address_to_coords(addr) for addr in addresses]
coords = [c for c in coords if c]  # הסרת None

# 2. מיון לפי קרבה למחסן (לדוגמה: כתובת ראשונה)
origin = coords[0]
sorted_coords = sorted(coords, key=lambda loc: great_circle(origin, loc).km)

# 3. אשכולות לפי מיקום
num_clusters = 3
kmeans = KMeans(n_clusters=num_clusters, random_state=0)
labels = kmeans.fit_predict(np.array(sorted_coords))

# 4. הצגה על מפה
m = folium.Map(location=origin, zoom_start=11)
colors = ["red", "blue", "green", "purple", "orange"]

for (lat, lon), label in zip(sorted_coords, labels):
    folium.CircleMarker(
        location=(lat, lon),
        radius=6,
        color=colors[label % len(colors)],
        fill=True,
        fill_opacity=0.7,
        popup=f"אשכול: {label}"
    ).add_to(m)

# שמירת המפה
m.save("/mnt/data/clustered_map.html")
"/mnt/data/clustered_map.html"
