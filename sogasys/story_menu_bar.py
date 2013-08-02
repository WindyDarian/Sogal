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



default_style = {'frameSize':(-0.2,0.2,-0.03,0.07),
                 'frameColor':((36/255.0,195/255.0,229/255.0,0.75),
                               (1.0,1.0,1.0,1),
                               (72/255.0,235/255.0,255/255.0,0.95),
                               (0.5,0.5,0.5,0.75),),
                 'text_scale':0.07,
                 'text_fg':(1,1,1,1),
                 'text_shadow':(0,0,1,1),
                 'relief': DGG.FLAT,
                }

class StoryMenuBar(SogalForm):
    '''
    The menu in story mode
    '''


    def __init__(self):
        self.margin = 0.05
        self.topdistance = 0.3
        self.rightdistance = 0.3
        
        SogalForm.__init__(self,
                           fading = True, 
                           fading_position_offset = (0.5,0,0),
                           fading_duration = 0.3)
        
        self._items = []
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
        btn = DirectButton(parent = self.bar,**dict(default_style,text_font = base.textFont,**args))  # @UndefinedVariable
        if self._items:
            btn.setPos(0,0,self._items[-1].getPos()[2] +
                           self._items[-1]['frameSize'][2] -
                           self.margin -
                           btn['frameSize'][3])
        else:
            btn.setPos(0,0,0)
            
        
        
        self._items.append(btn)
        #self.vbox.pack(btn)
        return btn

    
        
        