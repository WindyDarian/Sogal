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
Created on Sep 16, 2013

@author: Windy Darian (大地无敌)
'''

from panda3d.core import NodePath, Vec4
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText

import color_themes


class ALIGN():
    CENTER = 0
    LEFTCENTER = 1
    RIGHTCENTER = 2


class GuiElement(DirectObject, NodePath):
    '''
    The basement of Sogal gui elements
    Attributes:
    size/align/centerOffset: They are for layout management (see layout.py); 
                             If you don't work with this attributes, you can just override
                             getSize, getCenter and get getFrameSize
        
    '''
    #TODO: getCenter()
    def __init__(self, size = (0.0,0.0), align = ALIGN.CENTER, centerOffset = (0,0) , name = None):
        
        self._width = size[0]
        self._height = size[1]
        self._align = align
        self._centerOffset = centerOffset
        self.__cleanup = False
        
        name = name or self.__class__.__name__
        NodePath.__init__(self, name)
        DirectObject.__init__(self)
        
    def destroy(self):
        if not self.__cleanup:
            self.__cleanup = True
            self.removeNode()

        
    def getSize(self):
        return (self._width * self.getSx(), self._height * self.getSz())
    
    def getCenter(self):
        return (self._centerOffset[0] * self.getSx(), self._centerOffset[1] * self.getSz())
        
    
    def getFrameSize(self):
        """
        Returns the (Left, Right, Bottom, Top) value of the frame judged by size, align, and centerOffset.
        Scaled.
        """
        size = self.getSize()
        width = size[0]
        height = size[1]
        center = self.getCenter()
        ox = center[0]
        oz = center[1]
        offset = Vec4(-ox, -ox, -oz, -oz)
        if self._align == ALIGN.LEFTCENTER:
            halfh = height * 0.5
            frame = Vec4(0, width, -halfh, halfh)
        elif self._align == ALIGN.RIGHTCENTER:
            halfh = height * 0.5
            frame = Vec4(-width, 0, -halfh, halfh)
        else:
            #CENTER
            halfw = width * 0.5
            halfh = height * 0.5
            frame = Vec4(-halfw, halfw, -halfh, halfh)
        
        rsize = frame + offset
        sx = self.getSx()
        sz = self.getSz()
        return Vec4(rsize[0] * sx, rsize[1] * sx, rsize[2] * sz, rsize[3] * sz)
        
        
class MenuElement(GuiElement):
    """
    The menu element (a option row in option menu or ) base class 
    contains a text and a optional NodePath of the control component
    """
    def __init__(self, *args, **kwargs):
        GuiElement.__init__(self, *args, **kwargs)
        
class OptionLabel(GuiElement):
    '''
    one option label in options menu
    size is the size of the text and the controlNP is normally outside the box
    (for a better align)
    '''
    #TODO: inherit this from a 'MenuElement' liked class?
    def __init__(self, configForm, text , controlNP = None, controlOffset = 0.35 , size = (0.4,0.15)):
        
        GuiElement.__init__(self, size = size)
        
        self.text = text
        self.controlNP = controlNP
        self._controlOffset = controlOffset
        
        #TODO: textNP as a button-like, commonly use in menus
        self.textNP = OnscreenText(font = color_themes.default_font, text = text, scale = 0.07, fg = (1,1,1,1) )
        
        self.textParentNP = NodePath('tpnp')
        self.textParentNP.reparentTo(self)
        self.textNP.reparentTo(self.textParentNP)
        self.controlParentNP = NodePath('cpnp')
        self.controlParentNP.setPos(self._controlOffset,0,0)
        self.controlParentNP.reparentTo(self)
        self.controlNP.reparentTo(self.controlParentNP)
        
    def destroy(self):
        if self.textNP:
            self.textNP.destroy()
        if self.controlNP:
            self.controlNP.destroy()
        self.textNP = None
        self.controlNP = None
        self.textParentNP = None
        self.controlParentNP = None
        GuiElement.destroy(self) 

        