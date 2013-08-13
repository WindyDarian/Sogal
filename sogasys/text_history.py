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
Created on Apr 13, 2013
Text history form
@author: Windy Darian (大地无敌)
'''

from panda3d.core import TextNode,NodePath,TextProperties,TextPropertiesManager
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectScrolledFrame import DirectScrolledFrame

from sogal_form import SogalForm
from sogasys import color_themes
from cgitb import text



WORDWRAP = 30
MAXENTITIES = 500

FRAMESIZE = (-1.35,1.35,-0.95,0.95)
CANVASSIZE = (0,2.55, 1 ,0)
TOP = 0.1
AUTO_HIDE_SCROLLBARS = True
TEXTLEFT = 0.4
SPACING = 0.04

prop_set_up = False

class TextHistory(SogalForm):
    '''
    Text history form
    '''


    def __init__(self):
        '''
        Constructor
        '''
        SogalForm.__init__(self, fading = True, fading_duration = 0.3, enableMask = True,backgroundColor = (0,0,0,0.6))
        self.reparentTo(aspect2d,sort = 101)
        

        self.frame = DirectScrolledFrame(parent = self, canvasSize = CANVASSIZE, 
                                         frameSize = FRAMESIZE, 
                                         autoHideScrollBars = AUTO_HIDE_SCROLLBARS,
                                         **base.getStyle('frame'))
        
        self.height = TOP
        self.shiftedHeight = 0
        self.shifter = NodePath('text_history_shifter')
        self.shifter.reparentTo(self.frame.getCanvas())
        
        if not prop_set_up:
            nameprops = TextProperties()  # @UndefinedVariable
            nameprops.setTextScale(0.75)
            TextPropertiesManager.getGlobalPtr().setProperties("th_name", nameprops)  # @UndefinedVariable
 
        self.labels = []
        
    def destroy(self):
        self.labels = []
        self.shifter.removeNode()
        SogalForm.destroy(self)
        
    def append(self,text,speaker,voiceName):
        if len(self.labels) >= MAXENTITIES:
            self.removeHead()
            
        label = TextHistoryLabel(text, speaker, voiceName, parent = self.shifter, height=self.height)
        self.height += label.getLabelHeight() + SPACING
        
        self.labels.append(label)
        self.resetCanvasSize()
        #print len(self.labels)
            
    def removeHead(self):
        removing = self.labels.pop(0)
        
        h = removing.getLabelHeight() + SPACING
        self.shiftedHeight += h
        self.shifter.setZ(self.shifter.getZ() + h)
        #shift the parent NodePath to move all labels up
        
        removing.destroy()
        
        self.frame.verticalScroll.setValue(1)
        
    def resetCanvasSize(self):
        self.frame['canvasSize'] = (CANVASSIZE[0],CANVASSIZE[1],- TOP - self.height + self.shiftedHeight, 0)
        self.frame.verticalScroll.setValue(1)
        
    def roll(self,value):
        if self.labels:
            self.frame.verticalScroll.setValue(self.frame.verticalScroll.getValue() + value*2.0/len(self.labels))
        
    def focused(self):
        self.accept('mouse1', self.hide)
        self.accept('mouse2', self.hide)
        self.accept('mouse3', self.hide)
        self.accept('escape', self.hide)
        self.accept('wheel_up', self.roll, [-1.0])
        #self.accept('wheel_down', self.wheeldown)
        self.accept('wheel_down', self.roll, [1.0])
        self.accept('arrow_up-repeat', self.roll, [-1.0])
        self.accept('arrow_down-repeat', self.roll, [1.0])
        self.accept('arrow_up', self.roll, [-1.0])
        self.accept('arrow_down', self.roll, [1.0])
        self.accept('w-repeat', self.roll, [-1.0])
        self.accept('s-repeat', self.roll, [1.0])
        self.accept('w', self.roll, [-1.0])
        self.accept('s', self.roll, [1.0])
        SogalForm.focused(self)
        
    def defocused(self):
        self.ignore('mouse1')
        self.ignore('mouse2')
        self.ignore('mouse3')
        self.ignore('escape')
        self.ignore('wheel_up')
        self.ignore('wheel_down')
        self.ignore('arrow_up-repeat')
        self.ignore('arrow_down-repeat')
        self.ignore('arrow_up')
        self.ignore('arrow_down')
        self.ignore('w-repeat')
        self.ignore('s-repeat')
        self.ignore('w')
        self.ignore('s')
        SogalForm.defocused(self)
        
    def hide(self):
        self.removeFocus()
        SogalForm.hide(self)
        
    def wheeldown(self):
        if self.frame.verticalScroll.getValue() < 1:
            self.roll(1.0)
        else: self.hide()
        
        
class TextHistoryLabel(NodePath):
    def __init__(self, text, speaker = None, voiceName = None, parent = None, height = 0):
        #TODO add a voice button in it
        NodePath.__init__(self,'texthistorylabel')
        
        self.parent = parent or aspect2d
        self.reparentTo(parent)
        
        if speaker:
            text = '\1th_name\1(' + speaker.strip() + ')\n\2' + text
        
        self.textcontent = OnscreenText(text = text,align = TextNode.ALeft, pos = (TEXTLEFT,-height),
                                   wordwrap = WORDWRAP, parent = self, **base.getStyle('historytext'))
        
        self.labelHeight = self.textcontent.textNode.getHeight() * self.textcontent.getScale()[1]

        
    def destroy(self):
        self.textcontent.destroy()
        self.removeNode()
        
    def getLabelHeight(self):
        return self.labelHeight
        
        