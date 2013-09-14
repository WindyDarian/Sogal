#-*- coding:utf-8 -*-
'''
====================================================================================

   Copyright 2013, 2014 Windy Darian (大地无敌), Studio "Sekai no Kagami" 
   (世界之镜制作组) of Seven Ocean Game Arts （七海游戏文化社
   , 北京航空航天大学学生七海游戏文化社） @ http://sogarts.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

====================================================================================
Created on Apr 16, 2013
Simple Main Menu
@author: Windy Darian (大地无敌)
'''
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.stdpy.threading import Lock

from sogal_form import SogalForm
from layout import DirectVLayout

BUTTON_SIZE = (-0.4,0.4,-0.04,0.08)
class MainMenu(SogalForm):
    '''
    main menu class
    '''



    
    
    def __init__(self, entry = 'ifselectionjumptest'):
        '''
        Constructor
        '''
        self.entry = entry
        self.closed = True
        
        SogalForm.__init__(self, fading = True, fading_duration = 1.0, backgroundImage = None, backgroundColor = (0,0,0,1), 
                           enableMask = True,
                           hiddenFunc = self.closedFunc, shownFunc = self.openedFunc)
        

        self.addButtonBar()
        
        self.fadinglock = Lock()        #This lock is to prevent open or close failure when the main menu is on fading

        
    def addButtonBar(self):
        self.bar = DirectVLayout(margin= 0.1)
        self.bar.reparentTo(self)        
        


    
    
    def addButtons(self):
        '''
        override this if you want custom buttons
        '''
        #TODO:Continue Button 注意继续的位置可能是从硬盘上读入的也可能是从游戏中返回标题画面的 也有可能是在游戏正常结束之后所以没有Continue数据
        self.addButton(text = 'New Game', state = DGG.NORMAL, command = self._startGame)
        self.addButton(text = 'Load', state = DGG.NORMAL, command = self._load)
        self.addButton(text = 'Config', state = DGG.NORMAL, command = self._config)
        #TODO:Gallery Button
        self.addButton(text = 'Exit', state = DGG.NORMAL, command = self._exit)       

            
    def close(self):
        '''Called by SogalBase. Do something and hide, you will need it if you want a more complex main menu'''
        self.fadinglock.acquire()
        
        if self.closed:
            return
        SogalForm.hide(self)
        self.closed = True
        if self.bar:
            for btn in self.bar:
                btn['state'] = DGG.DISABLED
        
    def open(self):
        '''Called by SogalBase. Do something and show, you will need it if you want a more complex main menu'''
        self.fadinglock.acquire()
        
        if not self.closed:
            return
        SogalForm.show(self)
        self.addButtons()
        self.closed = False
    
    def show(self):
        #redirect show/hide to open/close
        self.open()
    
    def hide(self):
        #redirect show/hide to open/close
        self.close()
        
    def closedFunc(self):
        self.cleanup()
        self.fadinglock.release()
    
    def cleanup(self):
        for btn in self.bar:
            btn.destroy()
        self.bar.removeNode()
        self.addButtonBar()
    
    def openedFunc(self):
        self.fadinglock.release()
        
    def addButton(self,**args):
        '''Add a button and return it'''
        btn = DirectButton(**dict(base.getStyle()['mainMenuButton'], frameSize = BUTTON_SIZE,**args))  # @UndefinedVariable
        
        self.bar.append(btn)
        #self.vbox.pack(btn)
        return btn
        
    def _startGame(self, scene = None):
        if self.closed:
            return
        if not scene:
            messenger.send('start_game', [self.entry])
        else:
            messenger.send('start_game', [scene])
            
    def _load(self):
        if self.closed:
            return
        messenger.send('load_game')
        
    def _exit(self):
        if self.closed:
            return
        messenger.send('exit_game')
        
    def _config(self):
        messenger.send('config_form')