from threading import Thread
import cv2
import HandTracking as ht
import pyvirtualcam
from PySide2.QtCore import QObject, Signal , QThread
import numpy as np
from Whiteboard import WhiteBoard,Signals
import time



class MainThread(QThread):
    def __init__(self):

        super().__init__()
        self.signals = Signals()
        self.videoGet = VideoGet().start()
    # self.videoGet.start()
        
        self.processHands = ProcessHands(self.videoGet.frame).start()

        self.whiteBoard = WhiteBoard(VideoShape=self.videoGet.frame.shape)
        self.videoShow = VideoShow( self.videoGet.frame.shape)#.start(self.videoGet.frame.shape)
        self.videoShow.start()

        self.pTime = 0
        self.cTime = 0
        
        
    
    # def start(self):
    #     Thread(target = self.run).start()
    #     return self
    
    def run(self):
        while True:

            success, img = self.videoGet.success, self.videoGet.frame

            if(success):

                handDetector = self.processHands.handDetector

                if self.processHands.processedImg is not None:
                    img = self.processHands.processedImg.copy()
                self.processHands.img = self.videoGet.frame.copy()

                if handDetector.results is not None:
                    handedness = handDetector.GetHandedness()
                    # print(len(handedness))
                    if(len(handedness) == 1):
                        lmList = handDetector.FindPosition(img)
                        fingersUp  = handDetector.GetFingersUp(lmList, handedness)
                        self.whiteBoard.CallAppropriateMethod(fingersUp , lmList)
                        

                self.cTime = time.time()
                if self.cTime != self.pTime:
                    fps = 1//(self.cTime - self.pTime)
                else:
                    fps = "Infinite"

                self.pTime = self.cTime

                if img is not None:

                    img = cv2.flip(img, 1)
                    cv2.putText(img, f"FPS: {fps}", (400, 400),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
                    # self.whiteBoard.gui.ShowVideo(img)
                    self.videoShow.video = img
                    self.videoShow.canvas = cv2.flip(self.whiteBoard.canvas.copy(), 1)
                    self.videoShow.hud = self.whiteBoard.hudImg.copy()

                if not self.videoGet.running or not self.videoShow.running:
                    self.videoGet.Stop()
                    self.videoShow.Stop()
                    self.processHands.Stop()
                    cv2.destroyAllWindows()
                    break
    def quit(self):
        self.videoGet.Stop()
        self.videoShow.Stop()
        self.processHands.Stop()
        cv2.destroyAllWindows()

            

class VideoGet():
    def __init__(self , source = 0 ):
        self.running = True
        self.cap = cv2.VideoCapture(source , cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FPS, 120)
        self.success , self.frame = self.cap.read()

    def start(self):
        Thread(target = self.run).start()
        return self

    def run(self):
        while( self.running ):
            self.success , self.frame = self.cap.read()
        self.Stop()
        print("stopped")


    def Stop(self):
        self.running = False
        self.cap.release()

class VideoShow(QThread):
    def __init__(self , imgShape ): 
        super().__init__()
        self.showMode = 0
        self.running = True
        self.video = []
        self.hud = []
        self.canvas = []        
        self.change_pixmap_signal = Signals.GetInstance().change_pixmap_signal
        self.imgShape = imgShape



    def run(self ):
        with pyvirtualcam.Camera( height = self.imgShape[0] , width = self.imgShape[1], fps=60) as cam:
            while self.running :
                if len(self.video) and len(self.canvas) and len(self.hud):
                    if self.showMode == 0:                                                              #i.e, It will show vidoe on full label
                        broadcastImg = self.BlendImg(self.video , self.canvas)
                        outImg = self.BlendImg(broadcastImg , self.hud)
                        # cv2.imshow("Video" , img)
                        broadcastImg = cv2.cvtColor(broadcastImg , cv2.COLOR_BGR2RGB)
                        self.change_pixmap_signal.emit(outImg)
                        cam.send(broadcastImg)
                    
                    elif self.showMode == 1:
                        videoShape = self.video.shape
                        broadcastImg = np.zeros(videoShape , dtype=np.uint8 )
                        newShape = (videoShape[0] // 3 , videoShape[1] // 3 ) 
                        video_resized = cv2.resize(self.video , ( newShape[1] , newShape[0] ) )          #resize takes width x height and img is height x width
                        resizedVideoPos = ( videoShape[0] - video_resized.shape[0] , videoShape[1] - video_resized.shape[1])
                        broadcastImg[ resizedVideoPos[0] : , resizedVideoPos[1] : , : ] = video_resized
                        broadcastImg = self.BlendImg(broadcastImg , self.canvas)

                        outImg = outImg = self.BlendImg( self.BlendImg(self.video , self.canvas) , self.hud)
                        broadcastImg = cv2.cvtColor(broadcastImg , cv2.COLOR_BGR2RGB)
                        self.change_pixmap_signal.emit(outImg)
                        cam.send(broadcastImg)

                    elif self.showMode == 2:
                        outImg = self.BlendImg(self.BlendImg(self.video , self.canvas) , self.hud )
                        self.change_pixmap_signal.emit(outImg)
                        broadcastImg = cv2.cvtColor(self.canvas , cv2.COLOR_BGR2RGB)
                        cam.send(broadcastImg)

                    else:
                        self.showMode = 0

                time.sleep(1/120)
            self.Stop()


    def Stop(self):
        self.running = False
        print("stopped")
    
    def BlendImg( self ,img1 , img2):
        imgGray = cv2.cvtColor( img2 , cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray , 1 , 255 , cv2.THRESH_BINARY_INV)
        # imgInv = cv2.merge([imgInv , imgInv , imgInv])
        imgInv = cv2.cvtColor(imgInv , cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and( img1 , imgInv)
        img = cv2.bitwise_or(img , img2)
        return img
    

class ProcessHands():
    def __init__(self , img):
        self.handDetector = ht.HandDetector(detectionCon= 0.7 )
        self.running = True
        self.img = img
        self.processedImg = None

    def start(self):
        Thread(target = self.Process).start()
        return self

    def Process(self):
        while self.running:
            temp = self.handDetector.DrawHands(self.img , False)
            self.processedImg = temp


    def Stop(self):
        self.running = False

if __name__ == '__main__':
    MainThread().start()
