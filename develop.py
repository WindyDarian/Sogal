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
Created on Jul 5, 2013
SOGAL(七海美少女游戏引擎, Seven Ocean Galgame Engine)的主入口点，开发时用所以会经常改动
@author: 大地无敌
'''

from panda3d.core import loadPrcFile  # @UnresolvedImport
from direct.showbase.ShowBase import ShowBase
from sogasys.story_manager import StoryManager


 
class SogalEntry(ShowBase): 
    "游戏框架，继承自ShowBase"

    def __init__(self):
        "初始化"
        #读取设置文件
        loadPrcFile("config/PandaConfig.prc")
        
        #构造Panda3D的ShowBase
        ShowBase.__init__(self)
        
        #背景设置
        self.setBackgroundColor(0,0,0,0); 
        self.storyManager = StoryManager();
        self.storyManager.start();
        self.storyManager.addScriptData('test0')
        
    def setGameBackground(self):
        "设置背景图片"
        pass
    
    storyManager = None
    mainMenu = None


if __name__ == '__main__':
    SogalEntry().run()