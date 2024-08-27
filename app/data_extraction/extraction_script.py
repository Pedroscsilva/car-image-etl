import easyocr
import cv2
import pandas as pd

reader = easyocr.Reader(['pt', 'en'])
reader.lang_char

img = cv2.imread('app/data_extraction/diagrams/jpg_files/DA4407PE_diagram.pdf-1.jpg')
pd.read_csv('app/data_extraction/roi2024-08-25 00:00:00.csv')

right_side = img[y_r:y_r+h_r, x_r:x_r+w_r]

result = reader.readtext(right_side)
print(result)