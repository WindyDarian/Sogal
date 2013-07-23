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
Created on 2013年7月17日
包含了各种游戏实体数据类型的模块
存储的内容也仅限于其中的类的实体化比较好
The module includes entities of game data that can be used in
game and for serialization
@author: Windy Darian (大地无敌)
'''


class StoryCommand(object):
    ''' A command (or one paragraph) of the script file
    divided into a command section (after @ in one line) and a
    text section (just below the command section without any empty lines)
    A StoryCommand can have a command section only, or a text section only
    啊用双语好麻烦而且大地的英语好烂嘛反正无所谓总之就是这样
    包含一个command和一个text\
    嘛干脆用中文举个例好了……
    比如
    # @name 裸燃, pic 1 lr_naked_burn.png
    #「为什么又拿我当示范」
    中，"name 裸燃, pic 1 lr_naked_burn.png"是command section
    「为什么又拿我当示范」是text section
    另外在特殊请况 
    # @pic 1 lr_naked_burn.png
    # 裸燃：「为什么又拿我当示范」
    中，command section 依然是"pic 1 lr_naked_burn.png"
    在text_section中写入的说话者仍然放在text section中由StoryManager处理
    
    Attributes:
        command: A string indicates the command section (@ symbol excluded)
        text: A string indicates the text section
    '''
    command = None
    text = None
    
    def __init__(self, command = None, text = None):
        '''
        @param command: A string indicates the command section
        @param text: A string indicates the text section
        '''
        self.command = command
        self.text = text
        
    def __repr__(self):
        return 'command: ' + str(self.command) + '\ntext: ' + str(self.text) + '\n\n'
        
