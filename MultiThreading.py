from threading import Thread
import cv2
import HandTracking as ht
import pyvirtualcam
from PySide2.QtCore import QThread
import numpy as np
from Whiteboard import WhiteBoard,Signals
import time



class MainThread(QThread):
    def __init__(self):
        # Run all threads and initialize all classes
        super().__init__()
        self.signals = Signals()
        self.videoGet = VideoGet().start()
        
        self.processHands = ProcessHands(self.videoGet.frame).start()

        self.whiteBoard = WhiteBoard(VideoShape=self.videoGet.frame.shape)
        self.videoShow = VideoShow( self.videoGet.frame.shape)
        self.videoShow.start()

        self.pTime = 0
        self.cTime = 0
        
    
    def run(self):
        while True:

            success, img = self.videoGet.success, self.videoGet.frame

            if(success):

                handDetector = self.processHands.handDetector

                # Get the processed image from the hand processing thread and send another frame to process
                if self.processHands.processedImg is not None:
                    img = self.processHands.processedImg.copy()
                self.processHands.img = self.videoGet.frame.copy()

                if handDetector.results is not None:
                    handedness = handDetector.GetHandedness()
                    if(len(handedness) == 1):
                        lmList = handDetector.FindPosition(img)
                        fingersUp  = handDetector.GetFingersUp(lmList, handedness)
                        self.whiteBoard.CallAppropriateMethod(fingersUp , lmList)

                if img is not None:
                    # As the video is captured from front facing webcam, so it will be laterally inverted. 
                    # So flip the image so that it aligns with the users view
                    img = cv2.flip(img, 1)
                    self.videoShow.video = img
                    # As video is flipped, so we need to flip the canvas to align it with the video
                    self.videoShow.canvas = cv2.flip(self.whiteBoard.canvas.copy(), 1)
                    self.videoShow.hud = self.whiteBoard.hudImg.copy()

                if not self.videoGet.running or not self.videoShow.running:
                    # If any of the thread is not running, stop the whole program
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
        # Set CAP_DSHOW to access the webcam faster
        self.cap = cv2.VideoCapture(source , cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FPS, 120)
        self.success , self.frame = self.cap.read()

    def start(self):
        Thread(target = self.run).start()
        return self

    def run(self):
        while( self.running and self.cap.isOpened() ):
            self.success , self.frame = self.cap.read()
        self.Stop()

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
        try : 
            with pyvirtualcam.Camera( height = self.imgShape[0] , width = self.imgShape[1], fps=60) as cam:
                while self.running :
                    if len(self.video) and len(self.canvas) and len(self.hud):
                        # Show Mode = 0 to show user's image on full screen
                        # Show Mode = 1 to show user's image on one-third screen
                        # Show mode = 2 to only show canvas without the image of user
                        if self.showMode == 0: 
                            broadcastImg = self.BlendImg(self.video , self.canvas)
                            outImg = self.BlendImg(broadcastImg , self.hud)
                            broadcastImg = cv2.cvtColor(broadcastImg , cv2.COLOR_BGR2RGB)
                            self.change_pixmap_signal.emit(outImg)
                            cam.send(broadcastImg)
                        
                        elif self.showMode == 1:
                            videoShape = self.video.shape
                            broadcastImg = np.zeros(videoShape , dtype=np.uint8 )
                            # Get the dimensions of the one-third image
                            newShape = (videoShape[0] // 3 , videoShape[1] // 3 ) 
                            # Resize to the new dimension
                            video_resized = cv2.resize(self.video , ( newShape[1] , newShape[0] ) )          #resize takes width x height and img is height x width
                            # Find the new position of the one-third image so that it is at the bottom right of the screen
                            resizedVideoPos = ( videoShape[0] - video_resized.shape[0] , videoShape[1] - video_resized.shape[1])
                            broadcastImg[ resizedVideoPos[0] : , resizedVideoPos[1] : , : ] = video_resized
                            broadcastImg = self.BlendImg(broadcastImg , self.canvas)

                            outImg = self.BlendImg( self.BlendImg(self.video , self.canvas) , self.hud)
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
                    # If the thread runs continuously, it emits too many change_pixmap signals
                    time.sleep(1/120)
                self.Stop()
        # If the OBS Camera is not setup
        except : 
            while self.running :
                if len(self.video) and len(self.canvas) and len(self.hud):
                    outImg = outImg = self.BlendImg( self.BlendImg(self.video , self.canvas) , self.hud)
                    self.change_pixmap_signal.emit(outImg)
                    time.sleep(1/120)
            self.Stop()

    def Stop(self):
        self.running = False
    
    def BlendImg( self ,mainImg , overlayImg):
        # To blend image, we take one image; convert it into grayscale
        # Then we do inverse binary thresholding i.e., to set the pixels with any value other than 0, to 0 and
        # the pixels having value 0, to 255 (inverse Binary thresholding)
        # Thus, we get the places where we have drawn
        # Now, using bitwise_and, we get an image with black pixels for every point where we have drawn
        # Using bitwise_or, we change the black pixels to the color with which we have drawn.

        imgGray = cv2.cvtColor( overlayImg , cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray , 1 , 255 , cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv , cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and( mainImg , imgInv)
        img = cv2.bitwise_or(img , overlayImg)
        return img
    

class ProcessHands():
    def __init__(self , img):
        # Initialize HandDetector class of HandTrackingModule
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
