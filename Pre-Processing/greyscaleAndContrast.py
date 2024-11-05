import cv2
import os

input_dir = 'C:\\Users\\Riley\\Desktop\\TestSet'
output_dir = os.path.join(input_dir, 'ProcessedImages') #makes new folder in OG folder

if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def process_image(image_path, output_path):
    image = cv2.imread(image_path)
    
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    #Saturation params. 1.5 times the sat
    hsv_image[:, :, 1] = cv2.multiply(hsv_image[:, :, 1], 1.5)
    
    saturated_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    
    #greyscale
    grey_image = cv2.cvtColor(saturated_image, cv2.COLOR_BGR2GRAY)
    
    cv2.imwrite(output_path, grey_image)

   

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        process_image(input_path, output_path)

print('Done')
        