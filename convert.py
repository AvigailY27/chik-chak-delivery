import csv
import json

# קריאה מקובץ CSV
with open(r"backend\uploads\delivery_best_2025-06-08.csv", mode='r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    data = list(reader)

# כתיבה לקובץ JSON
with open('data.json', mode='w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

print("המרה הושלמה בהצלחה!")
