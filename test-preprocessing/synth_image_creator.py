import os
import cv2
import math
import glob
import random 
import numpy as np
from tqdm import tqdm
from PIL import Image

orignal_synth_images = images = glob.glob('./dataset/syn_image_train/*')

def make_rectangular_gradient(innerColor, outerColor, imgsize=(250, 250)):

    image = Image.new('RGB', imgsize) #Create the image


    for y in range(imgsize[1]):
        for x in range(imgsize[0]):

            #Find the distance to the closest edge
            distanceToEdge = abs(x - imgsize[0])  + abs(y - imgsize[1]) 

            #Make it on a scale from 0 to 1
            distanceToEdge = float(distanceToEdge) / (imgsize[0] + imgsize[1])
            
            #Calculate r, g, and b values
            r = innerColor[0] * distanceToEdge + outerColor[0] * (1 - distanceToEdge)
            g = innerColor[1] * distanceToEdge + outerColor[1] * (1 - distanceToEdge)
            b = innerColor[2] * distanceToEdge + outerColor[2] * (1 - distanceToEdge)


            #Place the pixel        
            image.putpixel((x, y), (int(r), int(g), int(b)))
            
    return np.array(image)

def make_circular_gradient(innerColor, outerColor, imgsize=(250, 250)):

    image = Image.new('RGB', imgsize) #Create the image


    for y in range(imgsize[1]):
        for x in range(imgsize[0]):

            #Find the distance to the center
            distanceToCenter = math.sqrt((x - imgsize[0]/2) ** 2 + (y - imgsize[1]/2) ** 2)

            #Make it on a scale from 0 to 1
            distanceToCenter = float(distanceToCenter) / (math.sqrt(2) * imgsize[0]/2)

            #Calculate r, g, and b values
            r = outerColor[0] * distanceToCenter + innerColor[0] * (1 - distanceToCenter)
            g = outerColor[1] * distanceToCenter + innerColor[1] * (1 - distanceToCenter)
            b = outerColor[2] * distanceToCenter + innerColor[2] * (1 - distanceToCenter)


            #Place the pixel        
            image.putpixel((x, y), (int(r), int(g), int(b)))
    return np.array(image)

os.makedirs('./dataset/synthetic_images_with_tray_bg', exist_ok=True)

rectangular_white_gray = make_rectangular_gradient([255, 255,255], [128, 128, 128])
rectangular_gray_white = make_rectangular_gradient([128, 128, 128],  [255, 255,255])
circular_white_gray = make_circular_gradient([128, 128, 128],  [255, 255,255])
circular_gray_white = make_circular_gradient([255, 255,255], [128, 128, 128])

for image_path in tqdm(images, total=len(images)):
    label_path = './dataset/segmentation_labels/' + image_path.split("/")[-1].split(".jpg")[0] + '_seg.jpg'
    image = cv2.imread(image_path)
    mask = cv2.imread(label_path)
    if image is None or mask is None:
        continue
    
    mask = mask == 0
    p = random.random()
    if p < .25:
        tray_background = cv2.resize(rectangular_white_gray, image.shape[:2][::-1])
    elif 0.25 <= p < 0.5:
        tray_background = cv2.resize(rectangular_gray_white, image.shape[:2][::-1])
    elif 0.5 <= 0.5 < 0.75:
        tray_background = cv2.resize(circular_white_gray, image.shape[:2][::-1])
    else:
        tray_background = cv2.resize(circular_gray_white, image.shape[:2][::-1])

    image[mask] = tray_background[mask]
    cv2.imwrite(f"./dataset/synthetic_images_with_tray_bg/{image_path.split('/')[-1]}", image)
