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

from panda3d.core import NodePath,Vec4
from direct.showbase.DirectObject import DirectObject
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from gui.boxes import VBox



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

class StoryMenuBar(NodePath,DirectObject):
    '''
    The menu in story mode
    '''
    margin = 0.05
    topdistance = 0.3
    rightdistance = 0.3

    def __init__(self,parent = None):
        NodePath.__init__(self,'menubar')
        if not parent:
            self.reparentTo(aspect2d)
        #self.vbox = VBox(margin = 0.05)
        self._items = []
        
        self.resetPos() 
        
        self.bar = NodePath('storymenu')
        self.bar.reparentTo(self)
        self.accept('window-event', self.resetPos)
        
    def resetPos(self,arg = None):
        aspect = base.getAspectRatio()
        if aspect > 1:
            self.setPos(1*aspect-self.rightdistance,0,1-self.topdistance)
        elif aspect: 
            self.setPos(1-self.rightdistance,0,1-self.topdistance)

    def destroy(self):
        self.ignoreAll()
        self.removeNode()
    
    def addButton(self,**args):
        '''Add a button and return it'''
        btn = DirectButton(**dict(default_style,text_font = base.textFont,**args))
        if self._items:
            btn.setPos(0,0,self._items[-1].getPos()[2] +
                           self._items[-1]['frameSize'][2] -
                           self.margin -
                           btn['frameSize'][3])
        else:
            btn.setPos(0,0,0)
        
        btn.reparentTo(self.bar)
        
        self._items.append(btn)
        #self.vbox.pack(btn)
        return btn
        
    
        
        