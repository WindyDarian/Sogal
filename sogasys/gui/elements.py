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

from panda3d.core import NodePath
from direct.showbase.DirectObject import DirectObject

class GuiElement(DirectObject, NodePath):
    """
    The basement of Sogal gui elements
    """
    #TODO: align and center offset and getCenter()
    def __init__(self, size = (0,0), name = None):
        name = name or self.__class__.__name__
        NodePath.__init__(self, name)
        DirectObject.__init__(self)
        self._width = size[0]
        self._height = size[1]
        
        
class MenuElement(GuiElement):
    """
    The menu element (a option row in option menu or ) base class 
    contains a text and a optional NodePath of the control component
    """
    def __init__(self, *args, **kwargs):
        GuiElement.__init__(self, *args, **kwargs)