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


#pos = (-0.57,0,0.67)
hspacing = 1.33
vspacing = 0.4
default_saveloadlabelbutton_style = {'frameSize':(0,1.2,-0.33,0),
                                     'frameColor':((36/255.0,195/255.0,229/255.0,0.75),
                                                   (1.0,1.0,1.0,1),
                                                   (72/255.0,235/255.0,255/255.0,0.95),
                                                   (0.5,0.5,0.5,0.75),),

                                     'relief': DGG.FLAT,
                                     
                                     }
default_saveloadlabel_style = {'scale':0.07,
                               'fg':(1,1,1,1),
                               'shadow':(0.6,0.6,0.5,1),
                               'pos': (0.05, -0.10),
                               'align': TextNode.ALeft,
                               }
default_savingscrollframe_style = {'frameSize': (-1.35,1.35,-0.95,0.95),
                                   'canvasSize' : (-0.05,2.55,-vspacing*100 ,vspacing/2),
                                   'autoHideScrollBars' : True,
                                   'frameColor': (36/255.0,195/255.0,229/255.0,0.3)
                                   }

default_loadingscrollframe_style = {'frameSize': (-1.35,1.35,-0.95,0.95),
                                   'canvasSize' : (-0.05,2.55,-vspacing*101 ,vspacing/2), #Larger for quicksave and autosave
                                   'autoHideScrollBars' : True,
                                   'frameColor': (229/255.0,195/255.0,36/255.0,0.3)
                                   }

class SavingInfo(object):
    '''Info for saving data'''
    def __init__(self,text,time):
        self.text = text
        self.time = time
        

class SaveLoadLabel(NodePath):
    '''
    A data label of save/load scene
    '''
    def __init__(self, command = None, always_enable = False, fileName = None, head = '',extraArgs = None):

        self.__command = command
        self.__always_enable = always_enable
        self.__fileName = fileName
        self.__head = head
        if not extraArgs: self.__extraArgs = [self]
        else: self.__extraArgs = extraArgs
        NodePath.__init__(self,'SaveLoadLabel')
        
        self.__button = DirectButton(parent = self, command = command,  extraArgs = extraArgs, **default_saveloadlabelbutton_style)  # @UndefinedVariable
        self.__text = OnscreenText(parent = self,font = base.textFont, **default_saveloadlabel_style)
        
        
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
        else: self.__text.setText(self.__head + '\n    NO DATA')
       

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
        self.frame = DirectScrolledFrame(parent = self, **default_savingscrollframe_style)
        self.labels = []
        self.vbox = VLayout(parent = self.frame.getCanvas(), margin = vspacing)
        hbox = None
        self.__dumped = None
        for i in range(200):
            label = SaveLoadLabel(command = self.save, always_enable = True, fileName = 'save' + str(i), head = str(i),extraArgs = [i],)
            self.labels.append(label)
            if not hbox:
                hbox = HLayOut(margin = hspacing)
                self.vbox.append(hbox)
                hbox.append(label)
            else:
                hbox.append(label)
                hbox = None
                
    def setData(self,dumped,message):
        self.__dumped = dumped
        self.__message = message
        
    def reload(self):
        for label in self.labels:
            label.reload()
    
    def save(self,i):
        if not self.__dumped:
            return
        else:
            messenger.send('save_data',[self.__dumped,'save' + str(i),self.__message])
            self.labels[i].reload()
        
    def focused(self):
        self.accept('mouse3', self.hide)
        
    def defocused(self):
        self.ignore('mouse3')
        
        
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
        self.frame = DirectScrolledFrame(parent = self, **default_loadingscrollframe_style)
        self.labels = []
        self.vbox = VLayout(parent = self.frame.getCanvas(), margin = vspacing)
        hbox = None
        self.__dumped = None
        for i in range(200):
            label = SaveLoadLabel(command = self.load, always_enable = False, fileName = 'save' + str(i), head = str(i),extraArgs = [i],)
            self.labels.append(label)
            if not hbox:
                hbox = HLayOut(margin = hspacing)
                self.vbox.append(hbox)
                hbox.append(label)
            else:
                hbox.append(label)
                hbox = None
        qs = SaveLoadLabel(command = self.quickLoad, always_enable = False, fileName = 'save', head = 'QuickSave',)
        hbox = HLayOut(margin = hspacing)
        self.vbox.append(hbox)
        hbox.append(qs)
                
    def setData(self,dumped,message):
        self.__dumped = dumped
        self.__message = message
        
    def reload(self):
        for label in self.labels:
            label.reload()
    
    def load(self,i):
        messenger.send('load_data',['save' + str(i)])  
        self.hide()
            
    def quickLoad(self):
        messenger.send('load_data',['quick_save'])
        self.hide()
        
    def focused(self):
        self.accept('mouse3', self.hide)
        
    def defocused(self):
        self.ignore('mouse3')
        