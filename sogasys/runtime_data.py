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
游戏运行中的实时数据 Runtime data for use and for storage
Created on 2013年7月19日
大部分是runtime_data中的实例集合，所以做到保存了这个对象的话就相当于保存
了游戏了的话嗯
@author: Windy Darian (大地无敌)
'''
import re,copy
from direct.stdpy.file import open,exists
from direct.stdpy import pickle

import color_themes

MAX_QUICKSAVE = 10
MAX_AUTOSAVE = 10

#game settings, this saves in a sconf file
game_settings = {'window_title': 'Sogal',
                 'text_speed': 30, #文字速度
                 'full_screen': True, 
                 'screen_resolution': (1280,720),  
                 'music_volume': 0.75,
                 'env_volume': 0.75,
                 'sfx_volume': 1,
                 'voice_volume': 1,
                 'style': 'ilia',
                 'jump_span': 0.1, #jump span for readed text and control force-jump
                 'auto_span' : 1.0, #how many seconds to wait for auto play 
                 'save_folder': 'savedata/',
                 'save_type' : '.dat',
                 'save_infotype' : '.sinf',
                 'sogalscrpathes': ['scenes/',''],
                 'sogalscrtypes': ['.sogal',''],
                 'pscriptpathes': ['scenes/','scenes/scripts/',''],
                 'pscripttypes': ['.py',''],
                 'imagepathes': ['images/','models/',''],
                 'imagetypes': ['.png', '.jpg', '.bmp',''],
                 'modelpathes': ['models/','images/',''],
                 'modeltypes': ['.egg','.egg.pz','.x',''],
                 'musicpathes': ['audio/music/','audio/',''],
                 'envsoundpathes': ['audio/env/','audio/',''],
                 'voicepathes': ['audio/voice/','audio/',''],
                 'sfxpathes':  ['audio/sound/','audio/',''],
                 'soundtypes': ['.wav','.ogg',''],
                }

global_data = {'currentAutosave':0,
              'currentQuicksave':0,
             }

read_text = {}

class _RuntimeData(object):
    '''A class that holds runtime'''
    def __init__(self):
        #Properties of game text box, will be loaded into a GameTextBox when GameTextBox is created
        #and saved when the text box is destroyed
        #if None, it is to use default value (it will just create a reference to GameTextBox.properties)
        self.gameTextBox_properties = None
        
        #As you can see:) StoryView's properties
        self.story_view_properties = None
        
        #The items in StoryView
        self.story_view_itementries = None
        
        #List of non-processed StoryCommands
        self.command_list = []
        
        #command pointer stack for loop 
        self.command_stack = []
        
        #point to current command
        self.command_ptr = 0
        
        #Current text. Index 0 is the text and index 1 is the speaker
        self.current_text = [None,None]
        
        #The python space of the script
        self.script_space = {}
        
        #Current background music
        self.current_bgm = None
        
        #Current environment sound
        self.current_env = None
        
        #current style
        self.current_style = None
        
        #store the copy of last choice
        self.last_choice = None
        
        #the latest text
        self.latest_text = ''
    
    def load(self, loadedInstance):
        self.gameTextBox_properties = loadedInstance.gameTextBox_properties
        self.story_view_itementries = loadedInstance.story_view_itementries
        self.story_view_properties = loadedInstance.story_view_properties
        self.command_list = loadedInstance.command_list
        self.command_stack = loadedInstance.command_stack
        self.command_ptr = loadedInstance.command_ptr
        self.current_text = loadedInstance.current_text
        self.script_space = loadedInstance.script_space
        self.current_bgm = loadedInstance.current_bgm
        self.current_env = loadedInstance.current_env
        self.current_style = loadedInstance.current_style
        self.last_choice = loadedInstance.last_choice
        self.latest_text = loadedInstance.latest_text
    
RuntimeData = _RuntimeData()

def getCurrentStyle(sheet = None):
    if RuntimeData.current_style:
        style = color_themes.styles[RuntimeData.current_style]
    else: style = color_themes.styles[game_settings['style']]
    if not sheet:
        return style
    else: return style[sheet]
    
def setCurrentStyle(value):
    RuntimeData.current_style = value

def loadDefaultSettings(fileName = 'config/default.sconf'):
    '''Load default unserialized settings'''
    global game_settings
    try:
        fileHandle = open(fileName)
        for line in fileHandle:
            spaceCutter = re.compile(ur'\s+',re.UNICODE) 
            splited = spaceCutter.split(line,1)
            game_settings[splited[0]] = eval(splited[1].strip())
    except:
        #raise LoadSettingsException('No such file: ' + fileName)
        pass
    finally:
        fileHandle.close()
    
def restoreSettings(settings):
    '''restore the settings from dumped config data'''
    global game_settings
    for key in settings:
        game_settings[key] = settings[key]
    
def restoreRuntimeData(dumped):
    '''restore the data from dumped runtime data'''
    global RuntimeData
    RuntimeData.load(dumped)
    
def loadRuntimeData(saved):
    '''restore the data from saved runtime data'''
    global RuntimeData
    data = pickle.load(saved)
    RuntimeData.load(data)
    
def restoreReadText(readed):
    '''restore the read text'''
    for key in readed:
        read_text[key] = readed[key]
        
def restoreGlobalData(readed):
    '''restore the global data'''
    for key in readed:
        global_data[key] = readed[key]
        
class LoadSettingsException(Exception):
    def __init__(self, message):
        Exception.__init__(message)
    def __str__(self, *args, **kwargs):
        return Exception.__str__(self, *args, **kwargs)
    