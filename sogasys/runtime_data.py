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


#game settings, this saves in a sconf file
game_settings = {'text_speed': 20, #文字速度
                 'full_screen': True, 
                 'screen_resolution': (1280,720),  
                 'music_volume': 0.75,
                 'env_volume': 0.75,
                 'sfx_volume': 1,
                 'voice_volume': 1,
                 'save_folder': 'savedata/',
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



class _RuntimeData(object):
    '''A class that holds runtime'''
    
    #Properties of game text box, will be loaded into a GameTextBox when GameTextBox is created
    #and saved when the text box is destroyed
    #if None, it is to use default value (it will just create a reference to GameTextBox.properties)
    gameTextBox_properties = None
    
    #As you can see:) StoryView's properties
    story_view_properties = None
    
    #The items in StoryView
    story_view_itementries = None
    
    #List of non-processed StoryCommands
    command_list = []
    
    #command pointer stack for loop 
    command_stack = []
    
    #point to current command
    command_ptr = 0
    
    #Current text. Index 0 is the text and index 1 is the speaker
    current_text = [None,None]
    
    #The python space of the script
    script_space = {}
    
    #Current background music
    current_bgm = None
    
    #Current environment sound
    current_env = None
    
    #TODO: Enable the attributes below
    #only works for saved object
    saved_date = None
    
    #only works for saved object
    saved_title = None
    
    #only works for saved object
    saved_image = None
    
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
        
        
    
RuntimeData = _RuntimeData()

def saveSettings(fileName):
    pass
    

def loadDefaultSettings(fileName):
    if exists(fileName):
        '''Load default unserialized settings'''
        global game_settings
        fileHandle = open(fileName)
        for line in fileHandle:
            spaceCutter = re.compile(ur'\s+',re.UNICODE) 
            splited = spaceCutter.split(line,1)
            game_settings[splited[0]] = eval(splited[1].strip())
    else: raise Exception('No such file: ' + fileName)
    
def restoreRuntimeData(dumped):
    '''restore the data from dumped runtime data'''
    global RuntimeData
    RuntimeData.load(dumped)
    
def loadRuntimeData(saved):
    '''restore the data from saved runtime data'''
    global RuntimeData
    data = pickle.load(saved)
    RuntimeData.load(data)