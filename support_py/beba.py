import cv2
import numpy as np

def estimate_speed(points0, points1, dt=1.0, scale=1.0):
    # Расчет скорости как среднее перемещение между кадрами
    distances = np.linalg.norm(points1 - points0, axis=1)
    avgspeed = np.mean(distances) / dt * scale
    return avgspeed

def main(videopath):
    cap = cv2.VideoCapture(videopath)
    ret, old_frame = cap.read()
    if not ret:
        print("Не удалось загрузить видео")
        return

    # Параметры для детектора углов ShiTomasi
    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)

    # Параметры для алгоритма Lucas-Kanade
    lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    # Находим углы в первом кадре
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    if p0 is None:
        print("Не найдено достаточно точек для отслеживания.")
        return
    count = 1
    while True:
        
        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Рассчитываем оптический поток
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
            

        if p1 is not None and st is not None:
            # Выбираем хорошие точки
            good_new = p1[st == 1]
            good_old = p0[st == 1]
            print(count)
            # Оцениваем скорость
            speed = estimate_speed(good_old, good_new)
            print(f"Оценочная скорость: {speed} пикселей/кадр")
            print(count) # счетчик
            count += 1
            # Обновляем предыдущий кадр и предыдущие точки
            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1, 1, 2)

        else:
            print("Не удалось рассчитать оптический поток для текущего кадра.")
            
    cap.release()

if __name__ == "__main__":
    video_path = 'C:/Users/Admin/Desktop/train_dataset_rzhd_fix_train/train/VID-20240301-WA0023.mp4'
    main(video_path)