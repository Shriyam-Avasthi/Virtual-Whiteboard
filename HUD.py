import numpy as np
from Tools import ToolsManager
class HUDManager():
    shared_instance = None

    def __init__(self , imgShape):

        if HUDManager.shared_instance != None:
            raise Exception("Cannot create another instance as HUDManager is a singleton class and should have only one instace.")
        else:
            HUDManager.shared_instance = self

        HCAM , WCAM = 1080 , 1920
        self.widthScale = imgShape[1] / WCAM
        self.heightScale = imgShape[0] / HCAM

        self.toolManager = ToolsManager.GetInstance()
        kb = self.toolManager.text.keyboard
        kb.frameWidth = imgShape[1]
        kb.length = int( kb.length * self.widthScale)
        kb.startPos = (int( kb.startPos[0] * self.widthScale) , int(kb.startPos[1] * self.heightScale) )
        kb.init_Buttons()

    @staticmethod
    def GetInstance():
        if HUDManager.shared_instance == None:
            return None 
        return HUDManager.shared_instance

    def DrawKeyboard(self , hudImg ):
        self.toolManager.text.keyboard.Draw(hudImg )  

    def DestroyKeyboard(self , hudImg):
        hudImg[ : , : , : ] = np.zeros(hudImg.shape)