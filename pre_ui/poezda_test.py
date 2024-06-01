import cv2
from ultralytics import YOLO

# Загрузка модели
model = YOLO('C:/Users/Admin/Desktop/GIT/SIZ_detection/models/03_nano_2757.pt')

# Загрузка изображения
image_path = 'C:/Users/Admin/Desktop/GIT/SIZ_detection/pre_ui/human_train.png'
image = cv2.imread(image_path)

# Выполнение предсказания
results = model(image)
classNames = ['train', 'cap', 'human', 'rail', 'vest']

# Инициализация массивов для хранения координат
human_boxes = []
train_boxes = [(7, 13, 177, 411), (240, 10, 490, 435)]

pogr = 10  # погрешность человека между поездами

# Обработка результатов
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        label = int(box.cls[0].item())  # Получение метки класса и преобразование в целое число
        class_name = classNames[label]  # Получение имени класса
        if label == 2:  # Предположим, что класс 2 - это человек
            human_boxes.append((x1, y1, x2, y2))
        elif label == 0:  # Предположим, что класс 0 - это поезд
            train_boxes.append((x1, y1, x2, y2))
        # Отображение результатов на изображении
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, class_name, (x1, y1 - pogr), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

# Увеличение ббоксов поездов на 10 пикселей с каждой стороны
train_boxes = [(abs(x1 - pogr), abs(y1 - pogr), abs(x2 + pogr), abs(y2 + pogr)) for (x1, y1, x2, y2) in train_boxes]

# Проверка пересечения прямоугольников
def check_intersection(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    return not (x1_max < x2_min or x1_min > x2_max or y1_max < y2_min or y1_min > y2_max)

# Рисование ббоксов из train_boxes
for (x1, y1, x2, y2) in train_boxes:
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Синий цвет для поездов
    cv2.putText(image, 'train', (x1, y1 - pogr), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

# Рисование ббоксов из human_boxes
for (x1, y1, x2, y2) in human_boxes:
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Красный цвет для людей
    cv2.putText(image, 'human', (x1, y1 - pogr), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

# Проверка пересечения и вывод результатов
intersection_count = 0
for train_box in train_boxes:
    for human_box in human_boxes:
        if check_intersection(train_box, human_box):
            print(f"Train box {train_box} intersects with human box {human_box}")
            intersection_count += 1

print(f"Number of train boxes intersecting with human boxes: {intersection_count}")

# Сохранение изображения с предсказаниями
output_image_path = 'C:/Users/Admin/Desktop/GIT/SIZ_detection/pre_ui/human_train_output.png'
cv2.imwrite(output_image_path, image)

# Вывод координат
print("Human boxes:", human_boxes)
print("Train boxes:", train_boxes)