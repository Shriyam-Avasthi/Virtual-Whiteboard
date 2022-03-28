import cv2
import mediapipe as mp
import time
import numpy as np
from google.protobuf.json_format import MessageToDict
  
class HandDetector():

    def __init__(self, mode = False , maxHands = 1 , detectionCon = 0.5 , trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # Access the mediapipe hands API
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode , self.maxHands , self.detectionCon , self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.fingerTips = [ 4 , 8 , 12 , 16 , 20 ]
        self.results = None

    def DrawHands(self , img , draw = True):
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
            # Access the Message to dict function from google.protobuf.json_format to decode the message to identify the hand as Left or Right
            for id , h in enumerate(self.results.multi_handedness):
                handedness_dict = MessageToDict(h)
                handedness.append(handedness_dict["classification"][0]["label"])
        return handedness

    def FindPosition(self, img ,  handNo = 0 , draw = True):
        lmList = []
        if (self.results.multi_hand_landmarks):
            if(len(self.results.multi_hand_landmarks) >= handNo):
                myHand = self.results.multi_hand_landmarks[handNo]
                for id,lm in enumerate(myHand.landmark):
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
                    if( lmList[id][2] < lmList[id - 3][2] ):
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
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    while True:
        success , img = cap.read()
        if success:
            img = cv2.flip(img , 1)
            img = detector.DrawHands(img)
            cv2.imshow("Video" , img)
        if cv2.waitKey(1) == ord("q"):
            break

if __name__ == "__main__":
    main()