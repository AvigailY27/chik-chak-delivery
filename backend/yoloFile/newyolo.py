import cv2
from ultralytics import YOLO

# הגדרת מודל YOLO
model = YOLO('yolov8n.pt')  # מודל YOLOv8 קטן ומהיר

# שמות המזהים עבור רכבים
vehicle_names = {2: 'Car', 3: 'Motorbike', 5: 'Bus', 7: 'Truck'}


def define_roi(frame, width_video, height_video, lane_width, num_lanes, vehicle_length, lane_start_offset=0):
    frame_height, frame_width = frame.shape[:2]
    roi_x1 = int(lane_start_offset)  # התחלת ה-ROI לפי ההסטה
    roi_x2 = int(roi_x1 + (lane_width * num_lanes))  # סוף ה-ROI לפי רוחב כל הנתיבים
    roi_y1 = int(lane_start_offset)  # אזור בגובה אורך הרכב
    roi_y2 = int(roi_y1 + (vehicle_length * 2))  # תחתית התמונה
    return roi_x1, roi_y1, roi_x2, roi_y2


def analyze_frame(frame, roi_x1, roi_y1, roi_x2, roi_y2):
    roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
    results = model(roi)
    vehicles = [res for res in results[0].boxes if res.cls in [2, 3, 5, 7]]  # מכוניות, משאיות, אופנועים
    return len(vehicles), results


def analyze_traffic(video_path, output_file, lane_width, num_lanes, vehicle_length, lane_start_offset):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return 0

    # LANE_WIDTH = 420
    # NUM_LANES = 2
    # VEHICLE_LENGTH = 500
    # LANE_START_OFFSET = 200
    width_video = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height_video = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    sumvehicle = 0
    cntfraim = 0
    with open(output_file, 'a', encoding='utf-8') as f:  # שינוי ל-'a' במקום 'w'
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            roi_x1, roi_y1, roi_x2, roi_y2 = define_roi(frame, width_video, height_video, lane_width, num_lanes,
                                                        vehicle_length, lane_start_offset)
            vehicle_count, results = analyze_frame(frame, roi_x1, roi_y1, roi_x2, roi_y2)
            cntfraim += 1
            sumvehicle += vehicle_count
            # if vehicle_count > prev_vehicle_count:
            #     status = "עומס גבוה יותר"
            # elif vehicle_count < prev_vehicle_count:
            #     status = "עומס מופחת"
            # else:
            #     status = "מצב קבוע"
            #
            # f.write(f"מספר רכבים: {vehicle_count}, מצב תנועה: {status}\n")
            # prev_vehicle_count = vehicle_count

            cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
            for result in results[0].boxes:
                x1, y1, x2, y2 = result.xyxy[0]
                cls = result.cls
                conf = result.conf
                vehicle_type = vehicle_names.get(int(cls), "Unknown")
                label = f"{vehicle_type}: {float(conf) * 100:.2f}%"
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imshow("Traffic Analysis", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
    return round(sumvehicle / cntfraim)
