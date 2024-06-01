from ultralytics import YOLO
import cv2
import cvzone
import math

model = YOLO("models/03_nano_2757.pt")
cap = cv2.VideoCapture("C:/Users/artem\Downloads/train/2_5395803543229709215.mp4")

classNames = ['train', 'cap', 'human', 'rail', 'vest']
cap.set(3, 1280)
cap.set(4, 720)

def main():
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = model(frame)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                
                if cls < len(classNames):
                    class_name = classNames[cls]
                    label = f'{class_name} {conf}'

                    cvzone.cornerRect(frame, (x1, y1, x2 - x1, y2 - y1), l=9, rt=5)
                    cvzone.putTextRect(frame, label, (max(0, x1), max(35, y1)), scale=1, thickness=1)
                else:
                    print(f"Внимание: класс {cls} аут оф ранге!!!")

        cv2.imshow("Processed Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()