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
Created on Sep 18, 2013
SOGAL's Controls. 
@author: Windy Darian (大地无敌)
'''

from panda3d.core import NodePath

import direct.gui.DirectGuiGlobals as DGG
from direct.gui.OnscreenImage import OnscreenImage

from elements import GuiElement
from direct_controls import SDirectCheckBox, SDirectOptionMenu

class CheckBox(GuiElement):
    '''simpify, specified interface'''
    
    def __init__(self, uncheckedImage = 'ui/default/checkbox_unchecked.png', checkedImage = 'ui/default/checkbox_checked.png', 
                 uncheckedGeom = None, checkedGeom = None, scale = 0.05):
        
        GuiElement.__init__(self, size=(2,2))
        self.__cleanup = False
        self.child = SDirectCheckBox(uncheckedImage = uncheckedImage, checkedImage = checkedImage, 
                 uncheckedGeom = uncheckedGeom, checkedGeom = checkedGeom, scale = 1)
        self.setScale(scale)
        self.child.reparentTo(self)
        
    def destroy(self):
        if not self.__cleanup:
            self.__cleanup = True
            self.child.destroy()
            self.child = None
            self.removeNode()
            
    def get(self):
        return self.child['isChecked']
    
    def set(self, ischecked):
        self.child['isChecked'] = ischecked
            
class OptionMenu(GuiElement):
    def __init__(self, items = [], itemcontent = None, initialitem = 0, command = None):
        GuiElement.__init__(self)
        self.child = SDirectOptionMenu(
                                       scale=0.1,items = items, initialitem=initialitem,
                                       itemcontent = itemcontent,
                                       command = command,
                                       highlightColor = base.getStyle('color')['frame_highlight'],
                                       item_relief = DGG.FLAT,
                                       frameColor = base.getStyle('color')['frame'],
                                       item_frameColor = base.getStyle('color')['frame2'],
                                       text_font = base.getStyle('font'),
                                       item_text_font = base.getStyle('font'),
                                       item_text_fg = base.getStyle('color')['fg_button'],
                                       text_fg = base.getStyle('color')['fg_button'],
                                       item_scale = 0.95
                                       )
        self.child.reparentTo(self)
        
    def set(self, index, fcommand = 1):
        self.child.set(index, fcommand)
        
    def get(self):
        return self.child.get()
        

"""class TextButton(GuiElement):
    '''text button'''
    def __init__(self, color):
"""