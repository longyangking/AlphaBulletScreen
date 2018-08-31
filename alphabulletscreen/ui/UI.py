import numpy as np 
import threading
from . import nativeUI

import sys
from PyQt5.QtWidgets import QApplication

class UI(threading.Thread):
    def __init__(self,pressaction,area,sizeunit=10):
        threading.Thread.__init__(self)
        
        self.app = None
        self.area = area
        self.sizeunit = sizeunit
        self.pressaction = pressaction

        self.UI = None   
    
    def run(self):
        self.app = QApplication(sys.argv)
        self.UI = nativeUI.nativeUI(pressaction=self.pressaction,area=self.area,sizeunit=self.sizeunit)
        self.app.exec_()

    def setarea(self,area):
        while self.UI is None:
            pass
        self.UI.setarea(area=area)
    
    def gameend(self,score):
        while self.UI is None:
            pass
        self.UI.gameend(score=score)