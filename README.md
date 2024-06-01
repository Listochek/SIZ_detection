# Оглавление
1. [4,5 часов сна](#45-часа-сна)
2. [Описание решения](#описание-решения)
3. [Как запустить](#как-запустить)
3. [Модели](#модели)
5. [Киллер фича](#киллер-фича)

# 4,5 часа сна
__Наша команда состоит из 4 человек__

___РОЛИ___

_Макар_ - Дизайнер

_Алекскандер_ - Frontend

_Артем_ - Fullstack

_Владислав_ - TeamLead, ML-enginer

[К оглавлению](#оглавление)
# Описание решения

Наше решение основывается на модели __YOLOv8__, которая обучена на такие классы:
* Train - поезд
* Human - человек
* Cap - шапка
* Vest - желет
* Rail - рельсы

Каждая отдельная ситуация по нарушению техники безопасности имеет свой алгоритм.

Интерфейс был реализован на __PyQt5__, в нем есть три уровня доступа, 
* Первый уровень - Работник, может загружать видеофайлы в приложение.
* Второй уровень - Смотрящий, может отсматривать интересующие моменты видео, имеются таймкоды, также может отправить _уведомление в Telegram_ своему начальнику, с диаграмой, в которой можно узнать колличество нарушений, а также их отношение в процентах.
* Третий уровень - Администратор, может добавлять и удалять сотрудников из базы данных, которая работает на _sqlite3_, также может менять уровень доступа сотрудников

# Как запустить
Для __запуска програмы__ вам нужно установить все нужные библиотеки и расширения:

``sys, os, cv2, cvzone, PyQt5, sqlite3, ultralytics, sqlite3, collections, matplotlib, telebot``

После установки, можно запустить главный файл, который отвечает за всю работу приложения 

После установки, можно запустить главный файл, который отвечает за всю работу приложения 

``` 
main.py
 ```
[К оглавлению](#оглавление)
# Модели
В итоговом решении мы имеем 2 модели обученные на базе Yolov8n и Yolov8m


|Model      | колличество эпох | вес моделей | 
|----------    |----------|----------|
| 01_nano_2757     | 150     | 6 мб   |
| 02_medium_2757.pt   | 150       | 50 мб   |
[К оглавлению](#оглавление)

# Киллер фича

 TO DO

[К оглавлению](#оглавление)