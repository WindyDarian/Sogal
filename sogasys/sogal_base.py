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
Created on Jul 27, 2013

@author: Windy Darian (大地无敌)
'''
import os
from StringIO import StringIO

from panda3d.core import loadPrcFile,WindowProperties # @UnresolvedImport
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase

from direct.filter.FilterManager import FilterManager
from direct.stdpy.file import open,exists
from direct.stdpy import threading
from direct.stdpy import pickle

from story_manager import StoryManager
from runtime_data import game_settings,loadDefaultSettings,loadRuntimeData,restoreRuntimeData
from audio_player import AudioPlayer
 
class SogalBase(ShowBase): 
    "The ShowBase of the sogal"

    def __init__(self):
        "初始化"
        #读取设置文件
        loadPrcFile("config/PandaConfig.prc")
        
        #构造Panda3D的ShowBase
        ShowBase.__init__(self)
        
        props = WindowProperties( self.win.getProperties() )
        props.setSize(int(game_settings['screen_resolution'][0]),int(game_settings['screen_resolution'][1]))
        if game_settings['full_screen'] and not props.getFullscreen():
            props.setFullscreen(True)
        self.win.requestProperties(props)
        
        self.cam2dp.node().getDisplayRegion(0).setSort(-20)  #Set render2dp to background
        self.disableMouse() #Disable panda3d's default mouse control
        self.cam.node().getDisplayRegion(0).setActive(0) #disable default camera
        self.audioPlayer = AudioPlayer()
       
        dir = os.path.dirname(game_settings['save_folder'])

        if not os.path.exists(dir):
            os.makedirs(dir)
        
        #Font setting
        self.textFont = loader.loadFont('fonts/DroidSansFallbackFull.ttf') # @UndefinedVariable
        self.textFont.setPixelsPerUnit(60)
        self.textFont.setPageSize(512,512)
        self.textFont.setLineHeight(1.2)
        self.textFont.setSpaceAdvance(0.5)
            
        
        
        #背景设置
        self.setBackgroundColor(0,0,0,1); 
        self.backgroundImage = None
        
        self.storyManager = StoryManager();
        self.storyManager.start();
        
        self.accept('alt-enter', self.toggleFullScreen)
        self.accept('save_data', self.save)
        self.accept('load_data', self.load)
        
        
    def setGameBackgroundImage(self,path):
        ''' Load a total background image '''
        if self.backgroundImage:
            self.backgroundImage.destroy()
        self.backgroundImage = OnscreenImage(parent=aspect2dp, image=path)  # @UndefinedVariable
        
    def save(self,saving,fileName):
        f = open(game_settings['save_folder']+fileName,'wb')
        pickle.dump(saving, f, 2)
        f.close()
        
    def load(self,fileName):
        self.storyManager.destroy()
        self.audioPlayer.stopAll(0.5)
        f = open(game_settings['save_folder']+fileName,'rb')
        loadRuntimeData(f)
        f.close() 
        self.audioPlayer.reload()
        
        self.storyManager = StoryManager();    
        self.storyManager.start()
        
        #self.storyManager.reload()
        
        
    #def loadData(self,fileName):
        
    
    def toggleFullScreen(self):
        props = WindowProperties( self.win.getProperties() )
        if not props.getFullscreen():
            props.setSize(int(game_settings['screen_resolution'][0]),int(game_settings['screen_resolution'][1]))
            props.setFullscreen(True)
        else:
            props.setFullscreen(False)
        self.win.requestProperties(props)
    
    
if __name__ == '__main__':
    SogalBase().run()