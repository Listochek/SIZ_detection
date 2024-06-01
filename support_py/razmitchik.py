import cv2
import os


def rename_files(directory):
    # Получаем список файлов в директории
    files = os.listdir(directory)
    # Фильтруем список, оставляя только файлы с расширением .png
    files = [file for file in files if file.endswith('.txt')]
    # Сортируем файлы по имени (опционально)
    files.sort()
    
    # Переименовываем файлы
    for index, file in enumerate(files):
        # Создаем новое имя файла
        new_filename = f"poezd_extra{index + 1}.txt"
        # Старый полный путь к файлу
        old_file = os.path.join(directory, file)
        # Новый полный путь к файлу
        new_file = os.path.join(directory, new_filename)
        # Переименовываем файл
        os.rename(old_file, new_file)
        print(f"Файл {file} переименован в {new_filename}")

# Путь к папке с изображениями
directory = r'C:\SIZ_detection\dataset\dataset_5\labels'
rename_files(directory)