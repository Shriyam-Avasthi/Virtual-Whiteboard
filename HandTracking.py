import cv2
import mediapipe as mp
import time
import numpy as np
from google.protobuf.json_format import MessageToDict

class SelfieSegmentor():
    def __init__(self , model = 1):
        self.model = model 
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.selfieSegmentation = self.mp_selfie_segmentation.SelfieSegmentation(self.model)
    
    def RemoveBG(self , img , bgColor = [0,0,0] , threshold = 0.1):
        imgRGB = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
        results = self.selfieSegmentation.process(imgRGB)
        condition = np.stack(
            (results.segmentation_mask,) * 3, axis=-1) > threshold
    
        bg_image = np.zeros(img.shape, dtype=np.uint8)
        bg_image[:] = bgColor
        output_image = np.where(condition, img, bg_image)
        return output_image

        

class HandDetector():

    def __init__(self, mode = False , maxHands = 1 , detectionCon = 0.5 , trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
    
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode , self.maxHands , self.detectionCon , self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.fingerTips = [ 4 , 8 , 12 , 16 , 20 ]
        self.results = None
        self.segmentor = SelfieSegmentor()

    def DrawHands(self , img , draw = True):
        # imgBgRemoved = self.segmentor.RemoveBG(img)
        imgRGB = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if (self.results.multi_hand_landmarks):
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img , handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def GetHandedness(self):
        handedness = []
        if(self.results.multi_handedness):
            for id , h in enumerate(self.results.multi_handedness):
                handedness_dict = MessageToDict(h)
                handedness.append(handedness_dict["classification"][0]["label"])
        return handedness

    def FindPosition(self, img ,  handNo = 0 , draw = True):
        lmList = []
        if (self.results.multi_hand_landmarks):
            if(len(self.results.multi_hand_landmarks) > handNo):
                myHand = self.results.multi_hand_landmarks[handNo]
                for id,lm in enumerate(myHand.landmark):
                    # print(id,lm)

                    h , w, c = img.shape
                    cx , cy = int(lm.x * w) , int(lm.y * h)
                    lmList.append([id,cx,cy])
                    if draw:
                        cv2.circle(img , (cx,cy) , 7 , (255,0,0) , cv2.FILLED)
        return lmList 

    def GetFingersUp( self , lmList , handedness):
        fingersUp = []

        if(len(lmList) != 0 and len(handedness) != 0):
            if handedness[0] == "Right" :
                #------------For Right Palm side------------------
                #For Thumb
                if( lmList[self.fingerTips[0]][1] < lmList[self.fingerTips[0] - 1][1]) :
                    fingersUp.append(1)
                else :
                    fingersUp.append(0)

                #For Fingers
                
                for id in self.fingerTips[1:5]:
                    if( lmList[id][2] < lmList[id - 2][2] ):
                        fingersUp.append(1)
                    else:
                        fingersUp.append(0)

            if handedness[0] == "Left":
                #------------For Left Palm side------------------
                #For Thumb
                if( lmList[self.fingerTips[0]][1] > lmList[self.fingerTips[0] - 1][1]) :
                    fingersUp.append(1)
                else :
                    fingersUp.append(0)

                #For Fingers
                
                for id in self.fingerTips[1:5]:
                    if( lmList[id][2] < lmList[id - 2][2] ):
                        fingersUp.append(1)
                    else:
                        fingersUp.append(0)

        return fingersUp

def main():
    pTime = 0
    cTime = 0   
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    while True:
        success , img = cap.read()
        if success:
            img = cv2.flip(img , 1)
            img = detector.DrawHands(img)
            # lmList = detector.FindPosition(img)
            # if len(lmList) != 0:
                # print(lmList[4])
            cTime = time.time()
            fps = 1/(cTime-pTime)
            pTime = cTime
            # handedness = detector.GetHandedness()
            cv2.putText(img , str(int(fps)) , (10,70) , cv2.FONT_HERSHEY_PLAIN , 3,(255,0,255) , 3)

            cv2.imshow("Video" , img)
        if cv2.waitKey(1) == ord("q"):
            break

if __name__ == "__main__":
    main()