import cv2
import numpy as np

my_photo = cv2.imread('envilop.jpg')
img_grey = cv2.cvtColor(my_photo,cv2.COLOR_BGR2GRAY)

#зададим порог
thresh = 100

#получим картинку, обрезанную порогом
ret,thresh_img = cv2.threshold(img_grey, thresh, 255, cv2.THRESH_BINARY)

#надем контуры
contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#создадим пустую картинку
img_contours = np.zeros(my_photo.shape)

#Подготовим новые размеры
final_wide = 200
r = float(final_wide) / my_photo.shape[1]
dim = (final_wide, int(my_photo.shape[0] * r))

#отобразим контуры
cv2.drawContours(img_contours, contours, -1, (255,255,255), 1)

cv2.imshow('contours', img_contours) # выводим итоговое изображение в окно
resized = cv2.resize(img_contours, dim, interpolation = cv2.INTER_AREA)
cv2.imshow("Resized image", resized)


cv2.waitKey()
cv2.destroyAllWindows()