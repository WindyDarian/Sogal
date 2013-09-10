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
import os,sys
from StringIO import StringIO
from datetime import datetime

from panda3d.core import loadPrcFile,WindowProperties,loadPrcFileData# @UnresolvedImport
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase

from direct.filter.FilterManager import FilterManager
from direct.stdpy.file import open,exists
from direct.stdpy.threading import Lock
from direct.stdpy import pickle

from story_manager import StoryManager
from runtime_data import game_settings,read_text,loadDefaultSettings,restoreRuntimeData, getCurrentStyle as rgetStyle, setCurrentStyle as rsetStyle,restoreReadText
from runtime_data import global_data,restoreGlobalData, MAX_AUTOSAVE, MAX_QUICKSAVE
from audio_player import AudioPlayer
from save_load_form import SaveForm,SavingInfo,LoadForm
import color_themes
from safeprint import safeprint
from main_menu import MainMenu
from config_form import ConfigForm


_savingloadinglock = Lock()
def save_data(file_name, data, mode = 2):
    _savingloadinglock.acquire()
    try:
        f = open(file_name,'wb')
        pickle.dump(data, f, mode)
        f.close()
    except Exception as exp: 
        raise exp
    finally:
        _savingloadinglock.release()
        
def load_data(file_name):
    _savingloadinglock.acquire()
    try:
        f = open(file_name,'rb')
        loaded = pickle.load(f)
        f.close()
    except Exception as exp: 
        raise exp
    finally:
        _savingloadinglock.release()
    
    return loaded
 
class SogalBase(ShowBase): 
    "The ShowBase of the sogal"
    

    def __init__(self):
        "初始化"
        #读取设置文件
        loadPrcFile("config/PandaConfig.prc")
        
        loadPrcFileData('', 'win-size ' + str(game_settings['screen_resolution'][0]) + ' ' + str(game_settings['screen_resolution'][1]) )
        
        #构造Panda3D的ShowBase
        ShowBase.__init__(self)
        
        color_themes.initStyles()
        
        props = WindowProperties( self.win.getProperties() )
        props.setSize(int(game_settings['screen_resolution'][0]),int(game_settings['screen_resolution'][1]))
        if game_settings['full_screen'] and not props.getFullscreen():
            props.setFullscreen(True)
        props.setTitle(game_settings['window_title'])
        self.win.requestProperties(props)
        
        self.cam2dp.node().getDisplayRegion(0).setSort(-20)  #Set render2dp to background
        self.disableMouse() #Disable panda3d's default mouse control
        self.cam.node().getDisplayRegion(0).setActive(0) #disable default camera
        self.audioPlayer = AudioPlayer()
        self.focusStack = [] #a stack that shows windowstop window gets focus
        
        self.loadReadText()
        self.loadGlobalData()
        
        dir = os.path.dirname(game_settings['save_folder'])

        if not os.path.exists(dir):
            os.makedirs(dir)
            
        #add event handlers
        self.accept('alt-enter', self.toggleFullScreen)
        self.accept('save_data', self.save)
        self.accept('load_data', self.load)
        self.accept('load_memory', self.loadMemory)
        self.accept('request_focus', self.grantFocus)
        self.accept('remove_focus', self.cancelFocus)
        self.accept('return_to_title', self.returnToTitle)
        self.accept('start_game', self.startGame)
        self.accept('load_game', self.loadGame)
        self.accept('exit_game', self.exit)
        self.accept('quick_save', self.quickSave)
        self.accept('quick_load', self.quickLoad)
        self.accept('auto_save', self.autoSave)
        
        #Font setting
        self.textFont = color_themes.default_font
        
        #背景设置
        self.setBackgroundColor(0,0,0,1); 
        self.backgroundImage = None
            

        
        self.mainMenu = None
        self.storyManager = None
        
    def initGameWindows(self):
        '''
        Initializing the common save, load and config forms
        if you want better customization with them,
        override this!
        '''
        self.saveForm = SaveForm()
        self.loadForm = LoadForm() 
        self.configForm = ConfigForm()
        
        
    def initMainMenu(self,customMainMenu = None):
        '''Call this to initialize and show main menu'''
        
        if not self.mainMenu:
            if not customMainMenu:
                self.mainMenu = MainMenu()
            else: self.mainMenu = customMainMenu
        self.mainMenu.open()
    
    def isStarted(self):
        return bool(self.storyManager)

        
    def getCurrentFocus(self):
        if len(self.focusStack) > 0:
            return self.focusStack[-1]
        else: return None
        
    def hasFocus(self,obj):
        '''returns whether the object is the current focus'''
        return self.getCurrentFocus() == obj
        
    def grantFocus(self,obj):
        pre = self.getCurrentFocus()
        if obj in self.focusStack:
            self.focusStack.remove(obj)
            self.focusStack.append(obj)
        else:
            self.focusStack.append(obj)
        if pre != obj:
            if pre:
                pre.defocused()
            obj.focused()
        
    def cancelFocus(self,obj):
        if obj in self.focusStack:
            self.focusStack.remove(obj)
            obj.defocused()
        cur = self.getCurrentFocus()
        if cur != obj and cur:
            cur.focused()
        
    def setGameBackgroundImage(self,path):
        ''' Load a total background image '''
        if self.backgroundImage:
            self.backgroundImage.destroy()
        self.backgroundImage = OnscreenImage(parent=aspect2dp, image=path)  # @UndefinedVariable
        
    def save(self,saving,fileName,message):
        
        info = SavingInfo(message,datetime.now())
        try:
            save_data(game_settings['save_folder'] + fileName + game_settings['save_type'], saving)
            save_data(game_settings['save_folder'] + fileName + game_settings['save_infotype'], info)
        except Exception as error:
            safeprint(error)
            return
        
        self.saveForm.reloadMember(fileName)
        self.loadForm.reloadMember(fileName)
        
        self.saveReadText()
        self.saveGlobalData()
        
    def quickSave(self, saving, message):
        global_data['currentQuicksave'] += 1
        if global_data['currentQuicksave'] > MAX_QUICKSAVE:
            global_data['currentQuicksave'] = 1
        currentqs = global_data['currentQuicksave']
        self.save(saving, 'quick_save' + str(currentqs), message)
        
    def autoSave(self, saving, message):
        global_data['currentAutosave'] += 1
        if global_data['currentAutosave'] > MAX_AUTOSAVE:
            global_data['currentAutosave'] = 1
        currentas = global_data['currentAutosave']
        self.save(saving, 'auto_save' + str(currentas), message)
        
    def load(self,fileName):
        
        try:
            savedData = load_data(game_settings['save_folder'] + fileName + game_settings['save_type'])
        except Exception as error:
            safeprint(error)
            return
        
        if self.mainMenu:
            self.mainMenu.close()
        if self.storyManager:
            self.storyManager.destroy()
        self.audioPlayer.stopAll(0.5)
        restoreRuntimeData(savedData)
        self.audioPlayer.reload()
        self.storyManager = StoryManager()
        
    def quickLoad(self):
        if self.hasQuickData():
            self.load('quick_save' + str(global_data['currentQuicksave']))
        
    def hasQuickData(self):
        return exists(game_settings['save_folder'] + 'quick_save' + str(global_data['currentQuicksave']) + game_settings['save_type'])
        
    def loadMemory(self,dumped):
        try:
            loaded = pickle.loads(dumped)
        except Exception as exp: 
            safeprint(exp)
            return
        
        self.storyManager.destroy()
        self.audioPlayer.stopAll(0.5)
        restoreRuntimeData(loaded)
        self.audioPlayer.reload()
        self.storyManager = StoryManager()   
             
    def loadReadText(self):
        if not exists(game_settings['save_folder']+ 'read.dat'):
            return
        try:
            read = load_data(game_settings['save_folder']+ 'read.dat')
        except Exception as exp:
            safeprint(exp)
            return
        restoreReadText(read)
        
    def loadGlobalData(self):
        if not exists(game_settings['save_folder']+ 'global.dat'):
            return
        try:
            gdata = load_data(game_settings['save_folder']+ 'global.dat')
        except Exception as exp:
            safeprint(exp)
            return
        restoreGlobalData(gdata)
        
    def saveReadText(self):
        try:
            save_data(game_settings['save_folder']+ 'read.dat', read_text)
        except Exception as exp: 
            safeprint(exp)
            
    def saveGlobalData(self):
        try:
            save_data(game_settings['save_folder']+ 'global.dat', global_data)
        except Exception as exp: 
            safeprint(exp)
        
    def getStyle(self, sheet = None):
        return rgetStyle(sheet)
    
    def setStyle(self,value):
        return rsetStyle(value)
    
    def toggleFullScreen(self):
        props = WindowProperties( self.win.getProperties() )
        if not props.getFullscreen():
            props.setSize(int(game_settings['screen_resolution'][0]),int(game_settings['screen_resolution'][1]))
            props.setFullscreen(True)
        else:
            props.setFullscreen(False)
        self.win.requestProperties(props)
        
    def exitfunc(self, *args, **kwargs):
        self.saveReadText()
        self.saveGlobalData()
        return ShowBase.exitfunc(self, *args, **kwargs)
    
    def startGame(self,scene):
        if self.mainMenu:
            self.mainMenu.close()
        if self.storyManager:
            self.storyManager.destroy()
        self.audioPlayer.stopAll(0.5)
        self.storyManager = StoryManager()
        self.storyManager.beginScene(scene)
        
    def loadGame(self):
        self.loadForm.show()
        
    def exit(self):
        sys.exit()
        
    def returnToTitle(self):
        if self.storyManager:
            self.storyManager.destroy()
        self.audioPlayer.stopAll(0.5)
        if self.mainMenu:
            self.mainMenu.open()
            
            
        
    
