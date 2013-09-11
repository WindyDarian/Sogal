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
import sys 

reload(sys) 
sys.setdefaultencoding('utf-8')


from sogasys.sogal_base import SogalBase
from sogasys.runtime_data import game_settings,loadDefaultSettings
from sogasys.main_menu import MainMenu
 
class SogalEntry(SogalBase): 
    "游戏框架，继承自ShowBase"

    def __init__(self):

        SogalBase.__init__(self)

        mainMenu = MainMenu('prologue/init')
        self.initMainMenu(mainMenu)


SogalEntry().run()