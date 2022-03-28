import cv2
import math

class ToolsManager():
    shared_instance = None

    def __init__(self , whiteboard):

        # Singleton Pattern
        if ToolsManager.shared_instance != None:
            raise Exception("Cannot create another instance as ToolsManager is a singleton class and it should have only onle instance!!! ")
        else :
            ToolsManager.shared_instance = self

        self.whiteboard = whiteboard
        self.pen = Pen(whiteboard)
        self.eraser = Eraser(whiteboard)
        self.shapes = Shapes(whiteboard)
        self.text = Text(whiteboard)
        self.laser = Laser(whiteboard)
        self.tools = [self.pen , self.eraser , self.shapes , self.text , self.laser] 
        self.currentToolID = 0

    @staticmethod
    def GetInstance():
        if ToolsManager.shared_instance == None:
            return None
        return ToolsManager.shared_instance

    def UseCurrentTool(self):
        self.tools[self.currentToolID].Use()

    def SetCurrentTool(self , id):
        # Stop Using previous tool and start using the selected tool
        self.tools[self.currentToolID].StopUse()
        if id < len(self.tools):
            self.currentToolID = id  
    
    def SetCurrentShape(self , id):
        self.shapes.shapeID = id

    def OnClickDown(self):
        self.tools[self.currentToolID].OnClickDown()
    
    def OnClickUp(self):
        self.tools[self.currentToolID].OnClickUp()

    def SetCurrentToolSize(self , size):
        self.tools[self.currentToolID].SetSize(int(size))

    def SetToolSize(self , toolID , size) :
        try:
            self.tools[toolID].SetSize(int(size))
        except:
            return
    
    def SetToolColor(self ,toolID, color):
        try:
            self.tools[toolID].color = color
        except :
            return
    
    def OnSecondaryClick(self ):
        self.tools[self.currentToolID].OnSecondaryClick()

    def GetSize(self):
        if self.currentToolID == 0 or self.currentToolID == 1 or self.currentToolID == 2 or self.currentToolID == 4:
            return self.tools[self.currentToolID].thickness
        elif self.currentToolID == 3:
            return self.tools[self.currentToolID].size
    
    def GetUseStatus(self):
        if self.tools[self.currentToolID].isUsed :
            return "Active"
        else :
            return "Inactive"
    
    def GetCurrentToolColor(self):
        return self.tools[self.currentToolID].color

    def StopUse(self):
        self.tools[self.currentToolID].StopUse()


class Pen():
    def __init__(self , whiteboard):
        # Initialize
        self.prev_xpos , self.prev_ypos = (0,0)
        self.color = (0,0,255)
        self.thickness = 5
        self.wb = whiteboard
        self.isUsed = False

    def Use(self ) :
        if not self.isUsed:
            # Update previous position of the pen
            self.prev_xpos , self.prev_ypos = self.wb.currentLmList[8][1:]
        else:
            # Draw
            fingerPos = self.wb.currentLmList[8][1:]
            cv2.line(self.wb.canvas, (self.prev_xpos, self.prev_ypos),
                    (fingerPos[0], fingerPos[1]), self.color , self.thickness, cv2.LINE_AA)
            self.prev_xpos, self.prev_ypos = fingerPos[0], fingerPos[1]

    def OnClickDown(self):
        pass

    def OnClickUp(self):
        # Toggle use state
        if self.isUsed :
            self.isUsed = False
        else:
            self.isUsed = True
    
    def SetSize(self , size):
        self.thickness = size
    
    def StopUse(self):
        self.isUsed = False

    def OnSecondaryClick(self ):
        # To break the ink and to let the user shift to another position for drawing
        self.prev_xpos , self.prev_ypos = self.wb.currentLmList[8][1:]

class Eraser():
    def __init__(self , whiteboard ):
        # Initialize
        self.prev_xpos , self.prev_ypos = (0,0)
        self.thickness = 5
        self.wb = whiteboard
        self.isUsed = False
        self.color = [0,0,0]
        
    def Use(self):
        if not self.isUsed:
            # Update previous position of the eraser
            self.prev_xpos , self.prev_ypos = self.wb.currentLmList[8][1:]
        else:
            fingerPos = self.wb.currentLmList[8][1:]
            cv2.line(self.wb.canvas, (self.prev_xpos, self.prev_ypos),
                    (fingerPos[0], fingerPos[1]), self.color, self.thickness, cv2.LINE_AA)
            self.prev_xpos, self.prev_ypos = fingerPos[0], fingerPos[1]

    def SetSize(self , size):
        self.thickness = size

    def OnClickDown(self):
        pass

    def OnClickUp(self):
        # Toggle use state
        if self.isUsed :
            self.isUsed = False
        else:
            self.isUsed = True

    def StopUse(self):
        self.isUsed = False

    def OnSecondaryClick(self):
        self.prev_xpos , self.prev_ypos = self.wb.currentLmList[8][1:]

class Shapes():
    def __init__(self , whiteboard):
        # Initialize
        self.startPoint = (0,0)
        self.shapeID = 0
        self.thickness = 10
        self.color = (0,0,255)
        self.wb = whiteboard
        self.canvasCopy = []
        self.isUsed = False

    def Use(self):
        if not self.isUsed:
            # Update the local copy of the canvas and the starting position of the shape 
            self.startPoint = self.wb.currentLmList[8][1:]
            self.canvasCopy = self.wb.canvas.copy()

        else:
            fingerPos = self.wb.currentLmList[8][1:]
            # To draw the shape according to the current finger position, we have to remove the shape drawn in the previous frame 
            # and draw the shape again according to the current finger position
            if self.shapeID == 0:
                center = ( ( self.startPoint[0] + fingerPos[0] ) // 2 , ( self.startPoint[1] + fingerPos[1] ) // 2)
                radius = int(math.dist(center , fingerPos))
                
                self.wb.canvas[: , : , :] = cv2.circle( self.canvasCopy.copy() , center , radius , self.color , self.thickness )

            elif self.shapeID == 1:                
                self.wb.canvas[: , : , :] = cv2.line( self.canvasCopy.copy() , self.startPoint , fingerPos , self.color , self.thickness )

            elif self.shapeID == 2:                
                self.wb.canvas[: , : , :] = cv2.rectangle( self.canvasCopy.copy() , self.startPoint , fingerPos , self.color , self.thickness )
                

            elif self.shapeID >= 3:
                self.shapeID = 1
    
    def OnClickDown(self):
        pass

    def OnClickUp(self):
        if self.isUsed :
            self.isUsed = False
        else:
            self.isUsed = True
            
    def SetSize(self , size):
        self.thickness = size
    
    def StopUse(self):
        self.isUsed = False

    def OnSecondaryClick(self ):
        self.startPoint = self.wb.currentLmList[8][1:]    

class Text():
    def __init__(self , whiteboard , startPoint = (0,0) , size = 3 ,color = [0,0,255]):
        # Initialize
        self.startPoint = startPoint
        self.size = size
        self.color = color
        self.keyboard = Keyboard()
        self.isUsed = False
        self.clickedDown = False
        self.wb = whiteboard
    
    def Use(self):
        # If in use
        if self.isUsed:
            # if the finger is on a key, then change the key's color to green
            self.keyboard.activeKey = self.keyboard.FindActiveKey( self.wb.currentLmList[8][1:] )
            if not self.clickedDown and self.keyboard.activeKey is not None:
                self.keyboard.activeKeyColor = (0 , 255 , 0)

            self.wb.DrawKeyboard()
            # Write the text written with the keyboard on the selected position of the canvas with a cursor "|" at the end 
            # and within the a rectangle to show that the person is still writing.

            text = ""
            for i in self.keyboard.text:
                text += i
            text += "|"
            rectPt1 = (self.keyboard.frameWidth - (self.startPoint[0] + self.size * 10) , self.startPoint[1] - 2 * self.size * 10)
            rectPt2 = (self.keyboard.frameWidth - (self.startPoint[0] - len(text) * self.size * 10) , self.startPoint[1] + self.size * 10)
            canvas = cv2.rectangle(self.canvasCopy.copy()  ,rectPt1 , rectPt2 , self.color , 5 ) 
            self.wb.canvas[:,:,:] = cv2.flip(cv2.putText(canvas , text , (self.keyboard.frameWidth - self.startPoint[0] , self.startPoint[1]) , cv2.FONT_HERSHEY_PLAIN, self.size , self.color , 3 ) , 1)
        else:
            # update the copy of the canvas
            self.canvasCopy = cv2.flip(self.wb.canvas.copy() , 1)
            self.keyboard.text = []
        
    def OnClickDown(self ):
        # if it is not used then start using
        self.clickedDown = True
        if not self.isUsed:   
                self.startPoint = self.wb.currentLmList[8][1:]
                self.isUsed = True
        # if it is used then find the key which was pressed and and change its color to red
        else:
            kb = self.keyboard
            if kb.activeKey is not None:
                kb.activeKeyColor = (0,0,200)
                    
    def OnClickUp(self):
        if self.clickedDown:
            self.clickedDown = False
            kb = self.keyboard
            if kb.activeKey is not None:
                # if return button is not pressed
                if kb.activeKey.text != "->":
                    # find the key that was pressed and add its text to the keyboard
                    kb.AddText( kb.activeKey.text)
                else:
                    self.OnClickReturn()

    def OnClickReturn(self):
        if self.isUsed and self.wb.currentLmList is not None :
            # self.keyboard.activeKey = self.keyboard.FindActiveKey( self.wb.currentLmList[8][1:] )
            # Add the text to the canvas without rectangle and cursor "|" to show that the user has finished writing
            text = ""
            for i in self.keyboard.text:
                text += i
            self.wb.canvas[:,:,:] = cv2.flip(cv2.putText(self.canvasCopy.copy() , text , (self.keyboard.frameWidth - self.startPoint[0] , self.startPoint[1]) , cv2.FONT_HERSHEY_PLAIN, self.size , self.color , 3) , 1)
        self.isUsed = False
        self.wb.DestroyKeyboard()

    def SetSize(self , size):
        self.size = size

    def StopUse(self):
        self.OnClickReturn()

    def OnSecondaryClick(self ):
        self.startPoint = self.wb.currentLmList[8][1:]
        self.wb.DestroyKeyboard()

class Keyboard():

    class Button():
        def __init__(self, posStart , text,size = [50 , 50] , color = (255,0,255)):
            # Initialize
            self.size = size
            self.posStart = posStart
            self.posEnd = ( (self.posStart[0] + self.size[0]) , (self.posStart[1] + self.size[1]) )
            self.text = text
            self.color = color

        def DrawButton(self , img):

            cv2.rectangle(img, self.posStart , self.posEnd, self.color , cv2.FILLED  )
            cv2.putText(img , self.text , (self.posStart[0] + 10 , self.posStart[1] + 30) , cv2.FONT_HERSHEY_PLAIN , 2 , [255,255,255] , 3 )

    def __init__(self , img = [] ,startPos = [150 , 300], length = 1700 , color = [255,0,255] , activeKeyColor = [0,255,0] , padding = 5):
        self.img = img
        self.KEYS = [ ["Q" , "W" , "E" , "R" , "T" , "Y" , "U" , "I" , "O" , "P"],
                  ["A" , "S" , "D" , "F" , "G" , "H" , "J" , "K" , "L" , "->" ],
                  ["Z" , "X" , "C" , "V" , "B" , "N" , "M" , "<-" , "_"]   ]
        self.startPos = startPos
        self.frameWidth = 0     #Width of the image frame
        self.buttons = []
        self.length = length
        self.color = color
        self.padding = padding
        self.text = []
        self.activeKey = None
        self.activeKeyColor = activeKeyColor
        self.isActive = False
        
        
    def init_Buttons(self):
        self.buttonLength = (self.length - 9 * self.padding) // 10
        for i in range(len(self.KEYS)):
            for j in range(len(self.KEYS[i])):
               self.buttons.append(Keyboard.Button( ( ((j * (self.buttonLength + self.padding) + self.startPos[0]) , (i * (self.buttonLength + self.padding) + self.startPos[1]) )  ) , self.KEYS[i][j] , size = [self.buttonLength , self.buttonLength] )) 

    def Draw(self ,img ):
        for i in self.buttons:
            i.DrawButton(img )
        cv2.rectangle(img , (self.startPos[0] , self.startPos[1] - 80 ) , (self.startPos[0] + self.length , self.startPos[1] - 20) , (255,0,255) , cv2.FILLED)
        text = ""
        for i in self.text:
            text += i
        text += "|"
        cv2.putText(img , text, (self.startPos[0] + 20 , self.startPos[1] - 40) , cv2.FONT_HERSHEY_PLAIN , 2 , [255,255,255] , 3 )
    
    def FindActiveKey(self , fingerPos):
        key = None
        for i in self.buttons:
            if (i.posStart[0] < self.frameWidth - fingerPos[0] and i.posEnd[0] > self.frameWidth - fingerPos[0]) and (i.posStart[1] < fingerPos[1] and i.posEnd[1] > fingerPos[1]):
                key = i
                i.color = self.activeKeyColor
            else:
                i.color = self.color
        return key
    
    def AddText(self ,text):
        if text == "<-" :
            if len(self.text) > 0:
                self.text.pop()
        elif text == "_":
            self.text.append(" ")
        else:
            self.text.append(str(text))

class Laser():
    def __init__(self , whiteboard):
        self.color = (0,0,255)
        self.wb = whiteboard
        self.thickness = 10
        self.borderThickness = -1
        self.isUsed = False
        self.canvasCopy = []

    def Use(self ) :
        if self.isUsed:
            fingerPos = self.wb.currentLmList[8][1:]
            self.wb.canvas[:, :, :] = cv2.circle(self.canvasCopy.copy(),(fingerPos[0], fingerPos[1]), self.thickness ,self.color , self.borderThickness  )
        else : 
            self.canvasCopy = self.wb.canvas.copy()
            self.isUsed = True
        

    def OnClickDown(self):
        if self.borderThickness == -1:
            self.thickness += 5
            self.borderThickness = 2

    def OnClickUp(self):
        self.thickness -= 5
        self.borderThickness = -1
    
    def SetSize(self , size):
        self.thickness = size
    
    def StopUse(self):
        if len(self.canvasCopy) != 0 and self.isUsed :
            self.wb.canvas[ : , : , : ] = self.canvasCopy
        self.isUsed = False
    
    def OnSecondaryClick(self):
        self.OnClickDown()        
        self.Use()
        self.thickness -= 5
        self.borderThickness = -1
        
