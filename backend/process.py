import csv
from datetime import datetime
import deliver as deliver
import osmnx as ox  


def process_input_file(file_path):
    deliveries = []
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader, None)  # דילוג על שורת הכותרת
        for row in reader:
            # דילוג על שורות ריקות
            if not any(row):
                continue
            
            # בדיקה אם חסרים נתונים
            if len(row) < 4:
                print(f"שורה עם נתונים חסרים: {row}")
                continue
            
            # יצירת אובייקט משלוח
            delivery = deliver.Delivery1(row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip())
            deliveries.append(delivery)
    return deliveries