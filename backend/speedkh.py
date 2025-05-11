import osmnx as ox

# מיפוי מהירויות ברירת מחדל לפי סוג הדרך
default_speeds = {
    "motorway": 110, "trunk": 90, "primary": 80, "secondary": 70,
    "tertiary": 60, "residential": 50, "service": 30
}


def get_edge_speed(edge_data):
    """ מחזירה את המהירות של קשת בגרף OSM, עם טיפול במקרה שאין maxspeed """
    maxspeed = edge_data.get("maxspeed")  # שליפת המהירות

    # אם maxspeed הוא רשימה (כבישים דו-נתיביים עם מהירויות שונות), ניקח את הערך הראשון
    if isinstance(maxspeed, list):
        maxspeed = maxspeed[0]

    # ניסיון להמיר maxspeed למספר שלם אם זהו מחרוזת מספרית
    if isinstance(maxspeed, str) and maxspeed.replace(" ", "").isdigit():
        maxspeed = int(maxspeed)
    elif isinstance(maxspeed, int):
        pass  # אם זה כבר מספר שלם, לא צריך להמיר
    else:
        # אם אין מידע, נשתמש במהירות ברירת מחדל לפי סוג הדרך
        highway_type = edge_data.get("highway", "residential")  # אם לא ידוע, נניח אזור מגורים
        maxspeed = default_speeds.get(highway_type[0], 50)  # ברירת מחדל: 50 קמ"ש

    return maxspeed
