import csv
from datetime import datetime
import deliver as deliver
import osmnx as ox  


def process_input_file(file_path):
    deliveries = []
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        header = next(reader, None)  # דילוג על שורת הכותרת
        if header is None:
            raise ValueError("The file is empty or missing a header.")

        for row in reader:
            if not any(row) or len(row) < 4:
                print(f"שורה לא תקינה: {row}")
                continue
            delivery = deliver.Delivery(*[col.strip() for col in row[:4]])
            deliveries.append(delivery)
        print(f"Loaded {len(deliveries)} deliveries.")
    return deliveries
