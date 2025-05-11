import cv2
import numpy as np


# מודל YOLO שהורד מראש
MODEL_CONFIG = 'yolov4.cfg.txt'
MODEL_WEIGHTS = 'yolov4.weights'
COCO_NAMES = 'coco.names'

# טעינת שמות המחלקות (כגון רכב, אופניים וכו')
with open(COCO_NAMES, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# טעינת המודל
net = cv2.dnn.readNet(MODEL_WEIGHTS, MODEL_CONFIG)
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# פתיחת וידאו בזמן אמת (החליף לכתובת הזרמת וידאו או מצלמת רשת)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape

    # הכנת התמונה לניתוח
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # ניתוח פלט
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # זיהוי רכבים (ביטחון מעל 50%)
            if confidence > 0.5 and classes[class_id] in ['car', 'truck', 'bus']:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # תיחום התמונה
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # הסרת חפיפות
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # ציור תיחום הרכבים
    for i in indexes.flatten():
        x, y, w, h = boxes[i]
        label = str(classes[class_ids[i]])
        confidence = confidences[i]
        color = (0, 255, 0)  # ירוק

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"{label} {int(confidence * 100)}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # הצגת מספר רכבים ממתינים
    car_count = len(indexes)
    cv2.putText(frame, f"Vehicles Detected: {car_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # הצגת התמונה
    cv2.imshow("Traffic Light Camera", frame)

    # יציאה
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
