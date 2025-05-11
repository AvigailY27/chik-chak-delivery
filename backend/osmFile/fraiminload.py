import cv2
from ultralytics import YOLO
import grafNode

# הגדרת מודל YOLO
model = YOLO('yolov8n.pt')  # מודל YOLOv8 קטן ומהיר

# שמות המזהים עבור רכבים
vehicle_names = {2: 'Car', 3: 'Motorbike', 5: 'Bus', 7: 'Truck'}


def define_roi(frame, width_video, height_video, lane_width, num_lanes, vehicle_length, lane_start_offset=0):
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

    return len(vehicles), results


# הגדרת נתיב לוידיאו
video_path = "D:\לימודים\יד\פרויקט גמר\קצר.mp4"
cap = cv2.VideoCapture(video_path)

# הגדרת פרמטרים (ניתנים לשינוי לפי הצורך)
LANE_WIDTH = 420  # רוחב נתיב בפיקסלים
NUM_LANES = 2  # מספר נתיבים
VEHICLE_LENGTH = 500  # אורך ממוצע של כלי רכב בפיקסלים
LANE_START_OFFSET = 200  # אופציונלי: התחלה מנתיב ספציפי
width_video = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height_video = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# ניתוח וידאו פריים אחרי פריים
prev_vehicle_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # חישוב ROI עבור כל פריים
    roi_x1, roi_y1, roi_x2, roi_y2 = define_roi(frame, width_video, height_video, LANE_WIDTH, NUM_LANES, VEHICLE_LENGTH,
                                                LANE_START_OFFSET)

    # ניתוח פריים
    vehicle_count, results = analyze_frame(frame, roi_x1, roi_y1, roi_x2, roi_y2)

    # הדפסת מצב העומס
    if vehicle_count > prev_vehicle_count:
        status = "עומס גבוה יותר"
    elif vehicle_count < prev_vehicle_count:
        status = "עומס מופחת"
    else:
        status = "מצב קבוע"

    print(f"מספר רכבים: {vehicle_count}, מצב תנועה: {status}")
    prev_vehicle_count = vehicle_count

    # הצגת פריים עם אזור עניין מסומן
    cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)

    # ציור תוצאות הזיהוי על הפריים
    for result in results[0].boxes:
        x1, y1, x2, y2 = result.xyxy[0]  # קואורדינטות של ריבוע חיתוך
        cls = result.cls  # מזהה סוג הרכב
        conf = result.conf  # אחוז הזיהוי

        # המרת המזהה לשם רכב
        vehicle_type = vehicle_names.get(int(cls), "Unknown")

        # יצירת תווית עם שם הרכב ואחוז הזיהוי
        label = f"{vehicle_type}: {float(conf) * 100:.2f}%"

        # ציור הריבוע שמסמן את הרכב
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # הצגת התמונה עם תוצאות הזיהוי
    cv2.imshow("Traffic Analysis", frame)

    # יציאה בלחיצה על Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
