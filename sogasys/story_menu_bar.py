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
Created on Jul 31, 2013
Menu in story mode
@author: Windy Darian (大地无敌)
'''

from panda3d.core import NodePath,Vec4,TransparencyAttrib
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton

from direct.interval.LerpInterval import LerpFunc,LerpPosInterval
from direct.interval.FunctionInterval import Func
from direct.interval.IntervalGlobal import Sequence,Parallel

from sogal_form import SogalForm
from layout import DirectVLayout
import color_themesfrom sogasys.save_load_form import FRAMESIZE

BUTTON_SIZE = (-0.2,0.2,-0.03,0.07)

class StoryMenuBar(SogalForm):
    '''
    The menu in story mode
    '''


    def __init__(self):
        self.topdistance = 0.3
        self.rightdistance = 0.3
        #self.rightdistance = 2
        
        SogalForm.__init__(self,
                           fading = True, 
                           fading_position_offset = (0.5,0,0),
                           fading_duration = 0.3)
        
        self._buttonbox = DirectVLayout(parent = self,margin = 0.05)
        self._currentInterval = None
        
        self.resetPos() 
        
        self.bar = NodePath('menubar')
        self.bar.reparentTo(self)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.accept('window-event', self.resetPos)
    
    def focused(self):
        self.accept('mouse3', self.hide)
        SogalForm.focused(self)
    
    def defocused(self):
        self.ignore('mouse3')
        SogalForm.defocused(self)
        
    def resetPos(self,arg = None):
        aspect = base.getAspectRatio()  # @UndefinedVariable
        if aspect > 1:
            self.setPos(1*aspect-self.rightdistance,0,1-self.topdistance)
        elif aspect: 
            self.setPos(1-self.rightdistance,0,1-self.topdistance)
            
    def show(self):
        SogalForm.show(self)
       
    
    def hide(self):
        if self.hasFocus():
            self.removeFocus()
            SogalForm.hide(self)

    def destroy(self):
        SogalForm.destroy(self)
        
    
    def addButton(self,**args):
        '''Add a button and return it'''
        btn = DirectButton(parent = self.bar,**dict(color_themes.ilia_button, frameSize = BUTTON_SIZE, text_font = base.textFont,**args))  # @UndefinedVariable
        
        self._buttonbox.append(btn)
        #self.vbox.pack(btn)
        return btn

    
        
        