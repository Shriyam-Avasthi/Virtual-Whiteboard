from ui_GUI import *
# from PySide2 import *
import sys 
import cv2
from PySide2.QtGui import QPixmap
from PySide2 import QtGui
from functools import partial
import numpy as np
import mouse
from MultiThreading import MainThread
from Whiteboard import WhiteBoard
from Tools import ToolsManager

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)   

        #Basic Window setup
        self.setWindowFlags(Qt.FramelessWindowHint) 

        self.setAttribute(Qt.WA_TranslucentBackground)
      
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 92, 157, 550))
         
        self.ui.centralwidget.setGraphicsEffect(self.shadow)

        self.ui.minimizeButton.clicked.connect(lambda: self.showMinimized())

        self.ui.closeButton.clicked.connect(lambda: self.close())

        self.ui.minimizeButton.clicked.connect(lambda: self.showMinimized())

        self.ui.closeButton.clicked.connect(lambda: self.close())

        # Add click event/Mouse move event/drag event to the top header to move the window
        self.ui.mainHeader.mouseMoveEvent = self.moveWindow

        #Left Menu toggle button
        self.ui.menuButton.clicked.connect(lambda: self.slideLeftMenu())
        
        ui = self.ui

        self.buttons = [ui.penButton, ui.eraserButton, ui.shapesButton, ui.textButton, ui.laserButton]
        self.shapeButtons = [ui.CircleButton , ui.LineButton , ui.RectangleButton]
        self.sliders = [ui.penSizeSlider , ui.eraserSizeSlider , ui.shapesThicknessSlider , ui.textSizeSlider , ui.laserSizeSlider]
        self.dials = [ui.penColorDial, QDial() , ui.shapesColorDial,ui.textColorDial, ui.laserColorDial]
        self.lcds = [ui.penSizeLCD , ui.eraserSizeLCD , ui.shapesThicknessLCD , ui.textSizeLCD , ui.laserSizeLCD]
        self.displayModeIcons = [u":/icons/Icons/video.svg" , u":/icons/Icons/cast.svg" , u":/icons/Icons/video-off.svg"]
        

        for i,j in enumerate(self.buttons):
            j.clicked.connect(partial(self.SelectTool , i ))
        for i,j in enumerate(self.shapeButtons):
            j.clicked.connect(partial(self.SelectShape , i))
        for i,j in enumerate(self.sliders):
            j.valueChanged.connect(partial(self.SetToolSize , i))
        for i,j in enumerate(self.dials):
            j.valueChanged.connect(partial(self.SetToolColor , i))

        self.ui.broadcastButton.clicked.connect( self.ChangeDisplayMode )
        self.ui.eraseAllButton.clicked.connect( self.EraseOnScreen)

        #Initialize MainThread class to run the main code of the application
        self.mainThread = MainThread()
        self.mainThread.start()
        self.mainThread.signals.change_pixmap_signal.connect(self.ShowFrame)
        self.mainThread.signals.changeToolSize_signal.connect(self.ChangeSliderPos)
        self.mainThread.signals.moveMouse_signal.connect(self.MoveMouse)
        self.mainThread.signals.changeStatus_signal.connect(self.ChangeUseStatus)
        img = self.mainThread.videoGet.frame
        self.windowWidth = img.shape[1]
        self.windowHeight = img.shape[0] + 200
        self.setFixedSize(self.windowWidth , self.windowHeight)

    # Slide left menu function
    def slideLeftMenu(self):
        width = self.ui.menu.width()
        # If minimized
        if width == 0:
            # Expand menu
            newWidth = 400
            newWinWidth = self.windowWidth + newWidth
            self.setFixedSize(newWinWidth , self.windowHeight)
            self.slideAnimation = QPropertyAnimation(self.ui.menu, b"minimumWidth")     #Animate minimumWidht
            self.slideAnimation.setDuration(250)
            self.slideAnimation.setStartValue(width)        #Start value is the current menu width
            self.slideAnimation.setEndValue(newWidth)       #end value is the new menu width
            self.slideAnimation.setEasingCurve(QEasingCurve.InOutQuart)
            self.slideAnimation.start()
            self.ui.menuButton.setIcon(QtGui.QIcon(u":/icons/Icons/chevron-left.svg"))
        # If maximized
        else:
            # Restore menu
            newWidth = 0
            newWinWidth = self.windowWidth
            self.slideAnimation = QPropertyAnimation(self.ui.menu, b"minimumWidth")     #Animate minimumWidht
            self.slideAnimation.setDuration(250)
            self.slideAnimation.setStartValue(width)        #Start value is the current menu width
            self.slideAnimation.setEndValue(newWidth)       #end value is the new menu width
            self.slideAnimation.setEasingCurve(QEasingCurve.InOutQuart)
            self.slideAnimation.start()
            self.slideAnimation.finished.connect(lambda : self.setFixedSize(newWinWidth , self.windowHeight))
            self.ui.menuButton.setIcon(QtGui.QIcon(u":/icons/Icons/align-left.svg"))

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()


    def moveWindow(self,e):

        if self.isMaximized() == False: #Not maximized

            if e.buttons() == Qt.LeftButton:  
                #Move window 
                self.move(self.pos() + e.globalPos() - self.clickPosition),
                self.clickPosition = e.globalPos()
                e.accept()

    def SelectTool(self,toolID):
        # Iterate through all the buttons of the tools
        for i,j in enumerate(self.buttons):
            if i == toolID:     # Tool to be selected
                j.setChecked(True)
                ToolsManager.GetInstance().SetCurrentTool(i)
                self.ui.stackedToolsMenu.setCurrentIndex(i)
                self.ui.useStatus.setText(ToolsManager.GetInstance().GetUseStatus())
                self.ui.bottomCurrentSizeLCD.display(str(ToolsManager.GetInstance().GetSize()))
            else:
                j.setChecked(False)
            
            # Set Color of the bottomCurrentColorButton of Bottom Status bar to show current color of the selected tool 
            color = ToolsManager.GetInstance().GetCurrentToolColor()
            style = f"background-color: rgb({color[2]}, {color[1]}, {color[0]});"
            self.ui.bottomCurrentColorButton.setStyleSheet(style)

    def SelectShape(self , toolID):
        # Iterate through the shapeButtons list
        for i,j in enumerate(self.shapeButtons):
            if i == toolID:             #Shape to be selected
                j.setChecked(True)
                ToolsManager.GetInstance().SetCurrentShape(i)
            else :
                j.setChecked(False)
            
    
    def SetToolSize(self , toolID , size):
        toolsManager = ToolsManager.GetInstance()
        toolsManager.SetToolSize(toolID ,size)
        # Set the display number of LCD Component of the current menu
        self.lcds[toolsManager.currentToolID].display(str(size))
        # Set the display number of LCD Component of the bottom Status bar
        self.ui.bottomCurrentSizeLCD.display(str(toolsManager.GetSize()))
        
    def SetToolColor(self,toolID , hue):
        # Create color of maximum saturation and value with given hue
        color = QColor.fromHsv( hue , 255 , 255 )
        ToolsManager.GetInstance().SetToolColor(toolID , [color.blue() , color.green() , color.red()])
        # Set the color of bottomCurrentColorButton of bottom status bar
        style = f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
        self.ui.bottomCurrentColorButton.setStyleSheet(style)

    def ChangeDisplayMode(self):
        showMode = self.mainThread.videoShow.showMode
        if showMode < 2 :
            showMode += 1
        else:
            # as there are only 3 display modes, defined in videoShow Class
            showMode = 0
        self.mainThread.videoShow.showMode = showMode
        self.ui.broadcastButton.setIcon(QIcon( self.displayModeIcons[ self.mainThread.videoShow.showMode ] ))
        status = ""
        if showMode == 0 :
            status = "Full Video Broadcast"
        elif showMode == 1:
            status = " Mini-Video Broadcast"
        else:
            status = "Only Canvas Broadcast"
        self.ui.videoStatusLabel.setText(status)

    def EraseOnScreen(self):
        # clear the sub array of canvas that is visible on screen
        WhiteBoard.GetInstance().canvas[ : , : , : ] = np.zeros(WhiteBoard.GetInstance().canvas.shape)
        
    @Slot(np.ndarray)
    def ShowFrame(self , frame):
        self.display_width , self.display_height = self.ui.videoLabel.size().toTuple()
        qt_img = self.convert_cv_qt(frame)
        # Set the video frame as pixmap to videoLabel component
        self.ui.videoLabel.setPixmap(qt_img)

    @Slot(int)
    def ChangeSliderPos(self , size):
        toolsManager = ToolsManager.GetInstance()
        # Animate the slider
        self.sliderAnimation = QPropertyAnimation(self.sliders[toolsManager.currentToolID], b"sliderPosition")
        self.sliderAnimation.setDuration(50)
        self.sliderAnimation.setStartValue(self.sliders[toolsManager.currentToolID].value())
        self.sliderAnimation.setEndValue(size)
        self.sliderAnimation.start()
        # Set LCD display number of current menu and bottom status bar
        self.lcds[toolsManager.currentToolID].display(str(size))
        self.ui.bottomCurrentSizeLCD.display(str(toolsManager.GetSize()))
        
    @Slot( bool , list )
    def MoveMouse(self , clicked , fingerPos):
        # Get position of central frame with respect to the origin of the screen
        minMousePos = self.ui.Central.mapToGlobal(QPoint(0,0)).toTuple()
        # Size of the central frame of the main window
        winSize =  self.ui.Central.size().toTuple()
        # End coordinates of the main window
        maxMousePos = (minMousePos[0] + winSize[0] , minMousePos[1] + winSize[1] )
        # Get position of video label with respect to the origin of the screen
        minVideoLabelPos = self.ui.videoLabel.mapToGlobal(QPoint(0,0)).toTuple()
        # size of video label
        videoLabelSize = self.ui.videoLabel.size().toTuple()
        
        maxVideoLabelPos = (minVideoLabelPos[0] + videoLabelSize[0] , minVideoLabelPos[1] + videoLabelSize[1])
        # As the video is flipped (refer to videoshow class), to get the position of finger with respect to the origin of the video label component
        fingerPos_local = ( videoLabelSize[0] - fingerPos[0] , fingerPos[1] )
        # Position of the finger with respect to the origin of the screen 
        globalFingerPos = (minVideoLabelPos[0] + fingerPos_local[0] , minVideoLabelPos[1] + fingerPos_local[1])

        # Convert the given finger position to global mouse position such that the mouse always remains inside the window
        mousePosx = np.interp( globalFingerPos[0] , [minVideoLabelPos[0] , maxVideoLabelPos[0]] , [minMousePos[0] , maxMousePos[0]] )
        mousePosy = np.interp( globalFingerPos[1] , [minVideoLabelPos[1] , maxVideoLabelPos[1]] , [minMousePos[1] , maxMousePos[1]] )
        if clicked:
            mouse.press()
        else:
            mouse.release()
        mouse.move ( mousePosx , mousePosy)

    @Slot( str )
    def ChangeUseStatus(self, text):
        self.ui.useStatus.setText(text)
        
    def convert_cv_qt(self, img):
        # Convert from an opencv image to QPixmap
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def closeEvent(self, event):
        self.mainThread.quit()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())
