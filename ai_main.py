from ultralytics import YOLO
from multiprocessing import Pool
import sys
model = YOLO('yolov8n.pt')
if __name__ == '__main__':
    results = model.train(data="C:\SIZ_detection\data.yaml", epochs=150, imgsz=640, device=[0], model="yolov8n.pt") 