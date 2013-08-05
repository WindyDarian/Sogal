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
Created on Apr 4, 2013
Saving/Loading Window
@author: Windy Darian (大地无敌)
'''
from datetime import datetime

from panda3d.core import NodePath,TextNode
from direct.stdpy.file import open, exists
from direct.stdpy import pickle
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectScrolledFrame import DirectScrolledFrame


from runtime_data import game_settings
from sogal_form import SogalForm
from layout import HLayOut,VLayout
import color_themes


#pos = (-0.57,0,0.67)
hspacing = 1.33
vspacing = 0.4
FRAMESIZE = (-1.35,1.35,-0.95,0.95)
LOAD_CANVAS_SIZE = (-0.05,2.55,-vspacing*101 ,vspacing/2)
SAVE_CANVAS_SIZE = (-0.05,2.55,-vspacing*100 ,vspacing/2)
AUTO_HIDE_SCROLLBARS = True


class SavingInfo(object):
    '''Info for saving data'''
    def __init__(self,text,time):
        self.text = text
        self.time = time
        

class SaveLoadLabel(NodePath):
    '''
    A data label of save/load scene
    '''

    def __init__(self, command = None, always_enable = False, fileName = None, head = '',extraArgs = None,style = color_themes.ilia_button):
        self.__exists = False
        self.__command = command
        self.__always_enable = always_enable
        self.__fileName = fileName
        self.__head = head
        if not extraArgs: self.__extraArgs = []
        else: self.__extraArgs = extraArgs
        NodePath.__init__(self,'SaveLoadLabel')
        
        self.__button = DirectButton(parent = self, command = command,  extraArgs = self.__extraArgs, frameSize = (0,1.2,-0.33,0), **style) 
        self.__text = OnscreenText(parent = self,font = base.textFont, pos = (0.05, -0.10), align = TextNode.ALeft, **color_themes.system_text) # @UndefinedVariable
        
        self.reload()
        
    def reload(self):
        if self.__always_enable:
            self.__button['state'] = DGG.NORMAL
        else: self.__button['state'] = DGG.DISABLED
        datafile = game_settings['save_folder']+ self.__fileName + game_settings['save_type']
        infofile = game_settings['save_folder']+ self.__fileName + game_settings['save_infotype']
        if exists(datafile) and exists(infofile):
            infostream = open(game_settings['save_folder']+ self.__fileName + game_settings['save_infotype'],'rb')
            info = pickle.load(infostream)
            infostream.close()
            text = info.text.splitlines()[0]
            if len(text)>15:
                text = text[0:13] + '...'
            self.__text.setText(self.__head+'\n'+info.time.strftime('%Y-%m-%d %H:%M')+'\n'+'  '+text)
            self.__button['state'] = DGG.NORMAL
            self.__exists = True
        else: 
            self.__text.setText(self.__head + '\n    NO DATA')
            self.__exists = False
        
    def getExists(self):
        return self.__exists
    
    def getFileName(self):
        return self.__fileName
       

class SaveForm(SogalForm):
    '''
    Form of saving
    '''

    def __init__(self):
        '''
        Constructor
        '''
        SogalForm.__init__(self, fading = True, fading_duration = 0.5, enableMask = True)
        self.reparentTo(aspect2d,sort = 100)
        self.frame = DirectScrolledFrame(parent = self, canvasSize = SAVE_CANVAS_SIZE, 
                                         frameSize = FRAMESIZE, 
                                         autoHideScrollBars = AUTO_HIDE_SCROLLBARS,
                                         **color_themes.ilia_frame)

        self.labels = []
        self.labelDict = {}
        self.vbox = VLayout(parent = self.frame.getCanvas(), margin = vspacing)
        hbox = None
        self.__dumped = None
        for i in range(1,201):
            label = SaveLoadLabel(command = self.save, always_enable = True, fileName = 'save' + str(i), head = str(i),extraArgs = [i],)
            self.labels.append(label)
            self.labelDict[label.getFileName()] = label
            if not hbox:
                hbox = HLayOut(margin = hspacing)
                self.vbox.append(hbox)
                hbox.append(label)
            else:
                hbox.append(label)
                hbox = None
                
    def roll(self,value):
        self.frame.verticalScroll.setValue(self.frame.verticalScroll.getValue() + value)
                
    def setData(self,dumped,message):
        self.__dumped = dumped
        self.__message = message
        
    def reload(self):
        for label in self.labels:
            label.reload()
    
    def reloadMember(self,key):
        if self.labelDict.has_key(key):
            self.labelDict[key].reload()
    
    def save(self,i):
        if not self.__dumped:
            return
        else:
            messenger.send('save_data',[self.__dumped,'save' + str(i),self.__message])
            self.labels[i].reload()
        
    def focused(self):
        self.accept('mouse3', self.hide)
        self.accept('wheel_up', self.roll, [-0.04])
        self.accept('wheel_down', self.roll, [0.04])
        self.accept('arrow_up-repeat', self.roll, [-0.04])
        self.accept('arrow_down-repeat', self.roll, [0.04])
        self.accept('arrow_up', self.roll, [-0.04])
        self.accept('arrow_down', self.roll, [0.04])
        self.accept('w-repeat', self.roll, [-0.04])
        self.accept('s-repeat', self.roll, [0.04])
        self.accept('w', self.roll, [-0.04])
        self.accept('s', self.roll, [0.04])
        
    def defocused(self):
        self.ignore('mouse3')
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
        
        
class LoadForm(SogalForm):
    '''
    Form of saving
    '''

    def __init__(self):
        '''
        Constructor
        '''
        SogalForm.__init__(self, fading = True, fading_duration = 0.5, enableMask = True)
        self.reparentTo(aspect2d,sort = 100)

        self.frame = DirectScrolledFrame(parent = self, canvasSize = LOAD_CANVAS_SIZE, 
                                         frameSize = FRAMESIZE, 
                                         autoHideScrollBars = AUTO_HIDE_SCROLLBARS,
                                         **color_themes.sirius_frame)
 
        self.labels = []
        self.labelDict = {}
        self.vbox = VLayout(parent = self.frame.getCanvas(), margin = vspacing)
        
        hbox = None
        self.__dumped = None
        for i in range(1,201):
            label = SaveLoadLabel(command = self.load, always_enable = False,
                                  fileName = 'save' + str(i), head = str(i),extraArgs = [i],style = color_themes.sirius_button)
            self.labels.append(label)
            self.labelDict[label.getFileName()] = label
            if not hbox:
                hbox = HLayOut(margin = hspacing)
                self.vbox.append(hbox)
                hbox.append(label)
            else:
                hbox.append(label)
                hbox = None
                
        #QuickSave label
        qs = SaveLoadLabel(command = self.quickLoad, always_enable = False, fileName = 'quick_save', 
                           head = 'QuickSave',style = color_themes.sirius_button)
        hbox = HLayOut(margin = hspacing)
        self.vbox.append(hbox)
        hbox.append(qs)
        self.labels.append(qs)
        self.labelDict[qs.getFileName()] = qs
        
    def roll(self,value):
        self.frame.verticalScroll.setValue(self.frame.verticalScroll.getValue() + value)
                
    def setData(self,dumped,message):
        self.__dumped = dumped
        self.__message = message
        
    def reload(self):
        for label in self.labels:
            label.reload()
            
    def reloadMember(self,key):
        if self.labelDict.has_key(key):
            self.labelDict[key].reload()
    
    def load(self,i):
        messenger.send('load_data',['save' + str(i)])  
        self.hide()
            
    def quickLoad(self):
        messenger.send('load_data',['quick_save'])
        self.hide()
        
    def focused(self):
        self.accept('mouse3', self.hide)
        self.accept('wheel_up', self.roll, [-0.04])
        self.accept('wheel_down', self.roll, [0.04])
        self.accept('arrow_up-repeat', self.roll, [-0.04])
        self.accept('arrow_down-repeat', self.roll, [0.04])
        self.accept('arrow_up', self.roll, [-0.04])
        self.accept('arrow_down', self.roll, [0.04])
        self.accept('w-repeat', self.roll, [-0.04])
        self.accept('s-repeat', self.roll, [0.04])
        self.accept('w', self.roll, [-0.04])
        self.accept('s', self.roll, [0.04])
        
    def defocused(self):
        self.ignore('mouse3')
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