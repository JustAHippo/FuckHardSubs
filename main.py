import cv2
import pytesseract
import numpy as np
import time

pytesseract.pytesseract.tesseract_cmd = 'TESSERACT PATH\\tesseract.exe'

vidcap = cv2.VideoCapture('PATH TO VIDEO')
success,image = vidcap.read()
c = 0
while success:
  #cv2.destroyAllWindows()
  success,image = vidcap.read()
  img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  w = img.shape[1]
  h = img.shape[0]
  # img[y:y+h, x:x+w]
  #img = cv2.convertScaleAbs(img, alpha=3, beta=100)

  cropped_image = img[int(1/1.2*h):h, int(1/4 * w):int(2/2.6 * w)]
  gray_img_copy = np.copy(cropped_image)
  gray_img_copy[gray_img_copy[:, :] < 250] = 0
  cv2.imshow('current frame', gray_img_copy, )
  cv2.waitKey(1)



  print(pytesseract.image_to_string(gray_img_copy, lang='eng', config="--psm 6 --oem 1" ))
  print(c)
  # time.sleep(0.25)
  c += 1

# img = cv2.imread(image)
