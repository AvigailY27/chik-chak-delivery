import cv2
from ultralytics import YOLO

# הגדרת מודל YOLO
model = YOLO('yolov8n.pt')  # מודל YOLOv8 קטן ומהיר


def define_roi(frame, lane_width, num_lanes, vehicle_length, lane_start_offset=0):
    """
    מגדירה אזור עניין (ROI) בהתבסס על מספר נתיבים, רוחב נתיב ואורך כלי רכב.
    """
    frame_height, frame_width = frame.shape[:2]
    roi_x1 = int(lane_start_offset)  # התחלת ה-ROI לפי ההסטה
    roi_x2 = int(roi_x1 + (lane_width * num_lanes))  # סוף ה-ROI לפי רוחב כל הנתיבים
    roi_y1 = int(lane_start_offset)  # אזור בגובה אורך הרכב
    roi_y2 = int(roi_y1 + (vehicle_length * 2))  # תחתית התמונה
    return roi_x1, roi_y1, roi_x2, roi_y2


def analyze_frame(frame, roi_x1, roi_y1, roi_x2, roi_y2):
    """
    פונקציה לניתוח פריים ומציאת רכבים באזור עניין
    """
    # חיתוך הפריים לפי אזור ה-ROI
    roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]

    # זיהוי אובייקטים בפריים
    results = model(roi)

    # סינון רכבים
    vehicles = [res for res in results[0].boxes if res.cls in [2, 3, 5, 7]]  # מכוניות, משאיות, אופנועים

    return len(vehicles)


# הגדרת נתיב לוידיאו
video_path = "F:\\קצר.mp4"
cap = cv2.VideoCapture(video_path)

# הגדרת פרמטרים (ניתנים לשינוי לפי הצורך)
LANE_WIDTH = 420  # רוחב נתיב בפיקסלים
NUM_LANES = 2  # מספר נתיבים
VEHICLE_LENGTH = 500  # אורך ממוצע של כלי רכב בפיקסלים
LANE_START_OFFSET = 40  # אופציונלי: התחלה מנתיב ספציפי

# ניתוח וידאו פריים אחרי פריים
prev_vehicle_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # חישוב ROI עבור כל פריים
    roi_x1, roi_y1, roi_x2, roi_y2 = define_roi(frame, LANE_WIDTH, NUM_LANES, VEHICLE_LENGTH, LANE_START_OFFSET)

    # ניתוח פריים
    vehicle_count = analyze_frame(frame, roi_x1, roi_y1, roi_x2, roi_y2)

    # הדפסת מצב העומס
    if vehicle_count > prev_vehicle_count:
        status = "עומס גבוה יותר"
    elif vehicle_count < prev_vehicle_count:
        status = "עומס מופחת"
    else:
        status = "מצב קבוע"

    print(f"מספר רכבים: {vehicle_count}, מצב תנועה: {status}")
    prev_vehicle_count = vehicle_count
    # ניתוח הפריים עם YOLO

    # הצגת פריים עם אזור עניין מסומן
    results = cv2.rectangle(model(frame), (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
    # הצגת תוצאות על הפריים
    for result in results:
        annotated_frame = result.plot()  # ציור התוצאות על הפריים
    cv2.imshow("Traffic Analysis", frame)

    # יציאה בלחיצה על Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
