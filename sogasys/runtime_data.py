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
大部分是runtime_data中的实例集合，所以做到保存了这里面的所有内容就相当于保存
了游戏了的话嗯
@author: Windy Darian (大地无敌)
'''
    
#game settings, this saves in a game_settings.sogdat file
game_settings = {'text_speed':20 #文字速度
                 
                 }

#Properties of game text box, will be loaded into a GameTextBox when GameTextBox is created
#and saved when the text box is destroyed
#None refer to default value
gameTextBox_properties = None

#List of non-processed StoryCommands
commands_in_queue = []

#Stack of loop commands
command_stack = []

#Current text. Index 0 is the text and index 1 is the speaker
current_text = [None,None]

#The python space of the script
script_space = {}

def save_data(fileName):
    ''''''
    pass

def load_data(fileName):
    pass