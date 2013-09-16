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
Created on Sep 10, 2013
Configuration form.
@author: Windy Darian (大地无敌)
'''
from panda3d.core import NodePath
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.OnscreenText import OnscreenText

from sogal_form import SogalForm
from gui.layout import VLayout
import color_themes

class ConfigForm(SogalForm):
    '''
    The configuration scene 
    '''
    
    class ConfigCard(NodePath):
        def __init__(self, parent = None, layoutMargin = .05):
            self.parent = parent or aspect2d
            NodePath.__init__(self, 'config_card')
            self.layout = VLayout(parent = self, margin = layoutMargin)
            self.layout.setPos(-1.25, 0, 0.67)
            self.reparentTo(self.parent)
            
            
    def __init__(self):
        '''
        Constructor
        '''
        style = base.getStyle()
        
        SogalForm.__init__(self, fading = True, fading_duration = 0.5, enableMask = True, backgroundColor = style['bgColor'], sort = 103)
        
        self._style = style
        
        self._cards = {}
        self._graphics = self.ConfigCard(parent = self)
        self._cards['graphics'] = (self._graphics)   #0, graphics
        
        #TODO: 重写ConfigLabel（一个OnscreenText 和一个控件 一行 ） 实现键盘支持

        #resolution = DirectOptionMenu(text="options", scale=0.1,items=["item1","item2","item3"],initialitem=2,
        resolution_options = DirectOptionMenu(scale=0.1,items=["1280x720","1920x1080",'1024x768'],initialitem=2,
                                      highlightColor=(0.65,0.65,0.65,1))
        self._resolution = ConfigLabel(self, text = 'Resolution', controlNP = resolution_options)
        self.appendConfigLabel('graphics', self._resolution)   #sresolution
        
        
    def focused(self):
        self.accept('mouse3', self.hide)
        self.accept('escape', self.hide)
        
    def defocused(self):
        self.ignore('mouse3')
        self.ignore('escape')
        
    def getStyle(self):
        return self._style
    
    def appendConfigLabel(self, card_key, label):
        '''
        Attach a ConfigLabel to a card.
        @param card_key: defines which card to add this label in.
        @param label: the new label to be added
        Card Keys:
        graphics
        '''
        self._cards[card_key].layout.append(label.frame)
        

        
class ConfigLabel(object):
    '''one config label'''
    
    def __init__(self, configForm, text , controlNP = None, controlOffset = 0.35 , size = (0, 2.0, -0.5, 0)):
        self.text = text
        self.controlNP = controlNP
        self._controlOffset = controlOffset
        self.size = size
        
        self.textNP = OnscreenText(font = color_themes.default_font, text = text, scale = 0.07, fg = (1,1,1,1) )
        
        #TODO: going to deplete 
        """if isinstance(configForm, ConfigForm):
            self.style = configForm.getStyle()
        else:
            self.style = base.getStyle()"""
        
        self.frame = DirectFrame(frameSize = self.size, frameColor = (0,0,0,0), relief = DGG.FLAT)
        
        self.textParentNP = NodePath('tpnp')
        self.textParentNP.reparentTo(self.frame)
        self.textNP.reparentTo(self.textParentNP)
        self.controlParentNP = NodePath('cpnp')
        self.controlParentNP.setPos(self._controlOffset,0,0)
        self.controlParentNP.reparentTo(self.frame)
        self.controlNP.reparentTo(self.controlParentNP)
        
        """if isinstance(configForm, ConfigForm):
            self.style = configForm.getStyle()
        else:
            self.style = base.getStyle()
        """    
            
    
    def appendNodePath(self, np):
        np.reparentTo(self.frame)
            