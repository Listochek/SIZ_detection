import cv2
import os

videopath = "C:/Users/artem\Downloads/train/0000000_00000020240508132920_0006.mp4"
output_folder = "C:/SIZ_detection/dataset/dataset_5"

cap = cv2.VideoCapture(videopath)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

current_frame = 0
while True:
    success, frame = cap.read()

    if not success:
        break

    if current_frame % 10 == 0:
        image_path = os.path.join(output_folder, f"frame{current_frame+3000}.jpg")
        print(image_path)
        cv2.imwrite(image_path, frame)

    current_frame += 1

cap.release()
cv2.destroyAllWindows()