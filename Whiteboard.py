import math
import numpy as np
import time
from ui_GUI import *
from Tools import ToolsManager
from HUD import HUDManager
from PySide2.QtCore import Signal


class CanvasMover():
    def __init__(self , whiteboard):
        self.startPoint = (0,0)
        self.isUsed = False
        self.whiteboard = whiteboard
        self.scrollSpeed = 10
        self.minScrollDelta = 10
        self.minScrollTime = 1/self.scrollSpeed
        self.lastScrollTimeElapsed = 0
        self.cTime = time.time()
        self.maxPos = ( whiteboard.wholeCanvas.shape[0] - whiteboard.canvas.shape[0] , whiteboard.wholeCanvas.shape[1] - whiteboard.canvas.shape[1] )

    def Use(self ):
        
        def Signum(n , threshold):
            if n > threshold :
                return n - threshold
            elif n < -threshold :
                return n - threshold
            else : 
                return 0
                
        if self.isUsed:
            deltaPos = (self.startPoint[0] - self.whiteboard.currentLmList[0][1:][0] , self.startPoint[1] - self.whiteboard.currentLmList[0][1:][1])
            if  self.lastScrollTimeElapsed >= self.minScrollTime:
                canvasShape = self.whiteboard.canvas.shape
                newCanvasStartPoint = [self.whiteboard.currentCanvasStartPoint[0] + Signum(deltaPos[0] , self.minScrollDelta) , self.whiteboard.currentCanvasStartPoint[1] + Signum(deltaPos[1] , self.minScrollDelta ) ]
                if newCanvasStartPoint[0] >= 0 and newCanvasStartPoint[1] >= 0 and newCanvasStartPoint[1] < self.maxPos[0] and newCanvasStartPoint[0] < self.maxPos[1]:
                    self.whiteboard.currentCanvasStartPoint = newCanvasStartPoint
                    self.whiteboard.canvas = self.whiteboard.wholeCanvas[ newCanvasStartPoint[1] : newCanvasStartPoint[1] + canvasShape[0] , newCanvasStartPoint[0] : newCanvasStartPoint[0] + canvasShape[1] , :]
                self.lastScrollTimeElapsed = 0
            cTime = time.time()
            self.lastScrollTimeElapsed += cTime - self.cTime
            self.cTime = cTime
        else:
            self.startPoint = self.whiteboard.currentLmList[0][1:]
            self.isUsed = True


class Signals(QObject):
    shared_instance = None
    change_pixmap_signal = Signal(np.ndarray)
    changeToolSize_signal = Signal(int)  
    moveMouse_signal = Signal(bool , list)
    changeStatus_signal = Signal(str)

    def __init__(self):
        if Signals.shared_instance != None:
            raise Exception("Cannot create another instance as Signals is a singleton class and it should have only one instance!!! ")
        else :
            Signals.shared_instance = self
        super().__init__()

    @staticmethod
    def GetInstance():
        if Signals.shared_instance == None:
            return None
        return Signals.shared_instance

class WhiteBoard():
    WCAM, HCAM = 1920, 1080

    shared_instance = None

    def __init__(self ,  VideoShape=(HCAM, WCAM, 3)):

        # Singleton Pattern
        if WhiteBoard.shared_instance != None:
            raise Exception("Cannot create another instance as WhiteBoard is a singleton class and it should have only onle instance!!! ")
        else :
            WhiteBoard.shared_instance = self
        
        # Initialize
        self.wholeCanvas = np.zeros( (VideoShape[0] * 20 , VideoShape[1] * 20 , VideoShape[2] ), dtype=np.uint8)
        self.currentCanvasStartPoint = (0 , 0)
        self.canvas = self.wholeCanvas[ : VideoShape[0] , : VideoShape[1] , :]
    
        self.canvasMover = CanvasMover(self)
        self.hudImg =  np.zeros(VideoShape, dtype=np.uint8) 
        self.SizeChangeSignal = Signal(int)       
        self.Manager = ToolsManager( self )  
        self.hud = HUDManager(self.hudImg.shape)
        self.lastClickTimeElapsed = 0.5
        self.lastMouseMoveTimeElapsed = 0.1
        self.sizeChangeTimeElapsed = 1
        self.cTime = 0
        self.clickDist = 0
        self.clicked = False
        self.currentLmList = []

    @staticmethod
    def GetInstance():
        if WhiteBoard.shared_instance == None:
            return None
        return WhiteBoard.shared_instance

    def CallAppropriateMethod(self , fingersUp , lmList):
        self.currentLmList = lmList
        cTime = time.time()
        self.lastClickTimeElapsed += cTime - self.cTime

        palmLength = self.GetDistance(lmList[0][1:] , lmList[5][1:])
        self.clickDist = (75/100) * palmLength

        upIndices = [i for i in range(len(fingersUp)) if fingersUp[i] == 1]

        # Change Use modes and tools according to the number of fingers which are open.
        if len(upIndices) == 0:
            self.Manager.StopUse()
            self.canvasMover.Use()

        elif len(upIndices) == 1 :
            self.canvasMover.isUsed = False

            if upIndices[0] == 1:
                self.Manager.UseCurrentTool()
                self.sizeChangeTimeElapsed = 0           

            if(self.GetDistance(lmList[8][1:] , lmList[5][1:]) < self.clickDist):
                if (not self.clicked):
                    self.Manager.OnClickDown()

                    self.clicked = True
                
            else:
                if self.lastClickTimeElapsed >= 0.5 and self.clicked:
                    self.Manager.OnClickUp()
                    self.lastClickTimeElapsed = 0
                    self.clicked = False
                    Signals.GetInstance().changeStatus_signal.emit(self.Manager.GetUseStatus())


        elif len(upIndices) == 2:
            self.canvasMover.isUsed = False

            if (upIndices[0] == 0 and upIndices[1] == 1):
                self.sizeChangeTimeElapsed += cTime - self.cTime
                if self.sizeChangeTimeElapsed >= 1:
                    length = self.GetDistance(lmList[4][1:] , lmList[8][1:])
                    size = np.interp(int(length) , [ 40/180 * palmLength , 200/180 * palmLength ] , [5,25])
                    self.Manager.SetCurrentToolSize(int(size))
                    Signals.GetInstance().changeToolSize_signal.emit(int(size))
                    
                    

            elif(upIndices[0] == 1 and upIndices[1] == 2):
                if(self.GetDistance(lmList[8][1:] , lmList[5][1:]) < self.clickDist):
                    clicked = True
                else:
                    clicked = False

                self.lastMouseMoveTimeElapsed += cTime - self.cTime
                if self.lastMouseMoveTimeElapsed >= 0.05:
                    Signals.GetInstance().moveMouse_signal.emit( clicked , lmList[12][1:])
                    self.lastMouseMoveTimeElapsed = 0

            elif upIndices[0] == 1 and upIndices[1] == 4 :
                self.Manager.OnSecondaryClick()
            
        else:
            self.canvasMover.isUsed = False
        self.cTime = cTime

    def GetDistance(self, point1 , point2):
        base , perp = ( abs(point1[0] - point2[0]) , abs(point1[1] - point2[1]) )
        return math.hypot(perp , base)
    
    def DrawKeyboard(self):
        self.hud.DrawKeyboard(self.hudImg)
    
    def DestroyKeyboard(self):
        self.hud.DestroyKeyboard(self.hudImg)
