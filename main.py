import re
import srt
import cv2
import math
import datetime
import pytesseract
import numpy as np
from autocorrect import Speller

def load_words():
  with open('LIST OF WORDS(NOT USED RN)words.txt', "r") as word_file:
    valid_words = set(word_file.read().split())

  return valid_words

def jaccard_similarity(x,y):
  intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
  union_cardinality = len(set.union(*[set(x), set(y)]))
  try:
    return intersection_cardinality/float(union_cardinality)
  except:
    return 0

spell = Speller(only_replacements=True)
startTime = 0.0
textSub = open("finishedSub.srt", "w")
subChangeTrigger = False
parsed = list()
unmodifiedStart = 0.0
unmodifiedEnd = 0.0
def filterText(textIn):
  textOut = textIn
  textOut = spell(textOut)
  textOut = textOut.replace(" ", "")
  textOut = textOut.replace("\r", "")
  textOut = textOut.replace("\n", "")
  textOut = textOut.replace("#", "")
  textOut = textOut.replace("!", "")
  textOut = textOut.replace("'", "")
  textOut = textOut.replace("-", "")
  textOut = textOut.replace("_", "")
  textOut = textOut.replace("*", "")
  textOut = textOut.replace("=", "")
  textOut = textOut.replace("1", "")
  textOut = textOut.replace("2", "")
  textOut = textOut.replace("3", "")
  textOut = textOut.replace("4", "")
  textOut = textOut.replace("5", "")
  textOut = textOut.replace("6", "")
  textOut = textOut.replace("7", "")
  textOut = textOut.replace("8", "")
  textOut = textOut.replace("9", "")
  textOut = textOut.encode("ascii", "ignore")
  textOut = textOut.decode()
  return textOut
def realisticFilter(textIn):
  textOut = textIn
  textOut = textOut.replace("1", "")
  textOut = textOut.replace("2", "")
  textOut = textOut.replace("3", "")
  textOut = textOut.replace("4", "")
  textOut = textOut.replace("5", "")
  textOut = textOut.replace("6", "")
  textOut = textOut.replace("7", "")
  textOut = textOut.replace("8", "")
  textOut = textOut.replace("9", "")
  textOut = textOut.replace("_", "")
  textOut = textOut.replace("*", "")
  textOut = textOut.replace("=", "")
  textOut = textOut.replace("#", "")
  textOut = textOut.replace("¢", "")
  return textOut

english_words = load_words()
pytesseract.pytesseract.tesseract_cmd = 'TESSERACT exe'

vidcap = cv2.VideoCapture('VIDEO')
fps = vidcap.get(cv2.CAP_PROP_FPS)
print("FPS:", str(fps))
success,image = vidcap.read()
c = 0
lastRet = ""
subNumber = 0

while success:
  c += 1
  try:
    #cv2.destroyAllWindows()
    success,image = vidcap.read()
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    w = img.shape[1]
    h = img.shape[0]
    # img[y:y+h, x:x+w]
    #img = cv2.convertScaleAbs(img, alpha=3, beta=100)

    cropped_image = img[int(1/1.2*h):h, int(1/5 * w):int(2/2.3 * w)]
    gray_img_copy = np.copy(cropped_image)
    gray_img_copy[gray_img_copy[:, :] < 252] = 0
    cv2.imshow('current frame', gray_img_copy, )
    cv2.waitKey(1)


    ret = pytesseract.image_to_string(gray_img_copy, lang='eng', config="--psm 6 --oem 1" )
    if subChangeTrigger:
      sentences = [filterText(ret),
                   filterText(lastRet)]
      sim = jaccard_similarity(sentences[0], sentences[1])
      if sim <= 0.7:

        subChangeTrigger = False
        endTime = list(math.modf(c/fps + 2))
        unmodifiedEnd = c/fps + 2
        endTime[0] = int(endTime[0] * 1000000)
        endTime[1] = int(endTime[1])
        if unmodifiedEnd - unmodifiedStart > 0.5:
          print("Stopped at", c / fps, "Seconds in")
          parsed.append(srt.Subtitle(index=subNumber, start=datetime.timedelta(seconds=startTime[1], microseconds=startTime[0]), end=datetime.timedelta(seconds=endTime[1], microseconds=endTime[0]), content=realisticFilter(lastRet), proprietary=""))
        else:
          print("Sub thrown out because it did not last long enough(" + str(unmodifiedEnd - unmodifiedStart) + ") seconds")
    if ret != "":

      sentences = [filterText(ret),
                   filterText(lastRet)]
      sim = jaccard_similarity(sentences[0], sentences[1])

      if sim <= 0.7:
        # subWords = re.split(" +", str(filterText(ret)))
        # print(subWords)
        subNumber += 1
        print("Started at", c/fps, "Seconds in")
        startTime = list(math.modf(c/fps + 2))
        unmodifiedStart = c/fps + 2
        startTime[0] = int(startTime[0] * 1000000)
        startTime[1] = int(startTime[1])
        print(startTime)
        subChangeTrigger = True
        #print(sim, c, filterText(ret), realisticFilter(ret))
        print(realisticFilter(ret))


      lastRet = ret

      # print(c, ret)
    # time.sleep(0.25)

  except Exception as e:
    print(e)
    finished = srt.compose(parsed)
    textSub.truncate(0)
    textSub.write(finished)
    exit()
