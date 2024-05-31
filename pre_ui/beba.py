import cv2
import numpy as np

# Функция для оценки средней скорости движения объектов в пикселях на кадр
def estimatespeed(points0, points1, dt=1.0, scale=1.0):
    # Вычисление евклидовых расстояний между начальными и конечными точками
    distances = np.linalg.norm(points1 - points0, axis=1)
    # Вычисление средней скорости
    avgspeed = np.mean(distances) / dt * scale
    return avgspeed

def main(videopath):
    # Инициализация захвата
    cap = cv2.VideoCapture(video_path)
    # Чтение первого кадра
    ret, old_frame = cap.read()
    # Проверка успешности чтения первого кадра
    if not ret:
        print("Не удалось загрузить видео")
        return

    # Параметры для детекции углов ShiTomasi
    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)

    # Параметры для алгоритма Lucas-Kanade  
    lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, **feature_params)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

 
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, lk_params)

   
        good_new = p1[st == 1]
        good_old = p0[st == 1]
        print(good_new)
        print(good_old)

        speed = estimatespeed(good_old, good_new)
        print(f"Оценочная скорость: {speed} пикселей/кадр")

        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)

    cap.release()

if __name__ == "__main__":
    video_path = 'C:\\Users\\kames\\OneDrive\\Рабочий стол\\поезд\\VID_20240304_095227.mp4'
    main(video_path)