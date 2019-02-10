import os
import numpy as np
import cv2 as cv2 
from numpy import genfromtxt

img_dir = "/home/student/dataset/"
new_img_dir = "/home/student/Data-Aug/"

def hsv(image,value = 30):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value
    final_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

def add_to_folder(list, path):
    counter = 0
    for img in list:
        cv2.imwrite(path+str(counter)+".jpg", img)
        counter +=1


for img_folder in os.listdir(img_dir):
    img_file_path = img_dir+img_folder+"/"
    f_list = []

    for img_file in os.listdir(img_file_path):
        if img_file.endswith(".jpg"):
            img_file_csv = (img_file_path+img_file).replace('.jpg','.csv')
            image = cv2.imread(img_file_path+img_file)
            my_data = genfromtxt(img_file_csv, delimiter=',')
            top = int(my_data[0])
            bottom = int(my_data[1])
            left = int(my_data[2])
            right = int(my_data[3])
            f_list.append(image[top:bottom,left:right])
            f_list.append(hsv(f_list[-1]))
            f_list.append(image[int(top*1.2):bottom,left:right])
            f_list.append(hsv(f_list[-1]))
            f_list.append(image[top:int(bottom*0.8),left:right])
            f_list.append(hsv(f_list[-1]))
            f_list.append(image[top:bottom,int(left*1.2):right])
            f_list.append(hsv(f_list[-1]))
            f_list.append(image[top:bottom,left:int(right*0.8)])
            f_list.append(hsv(f_list[-1]))

    add_to_folder(f_list, new_img_dir+img_folder+"/")



