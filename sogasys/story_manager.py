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
Created on Jul 3, 2013
SOGAL的故事模式（Galgame通常流程）管理器
@author: 大地无敌
'''


from StringIO import StringIO
import re

from panda3d.core import NodePath  # @UnresolvedImport
from panda3d.core import TransparencyAttrib  # @UnresolvedImport
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
#from direct.gui.DirectButton import DirectButton
from direct.showbase.DirectObject import DirectObject
from direct.stdpy.file import open
from direct.task import Task

from game_text_box import GTBI
from game_text_box import GameTextBox
from game_entities import StoryCommand
from story_view import StoryView

import runtime_data


class StoryManager(DirectObject):
    """Story controller of Sogal
    Controls the whole story scene.
    Mainly for logic control
    And graphics is on other  
    Attributes:
    _frame: main DirectFrame of the StoryManager 
    _textFont: the font for testing information
    """
    

    
    def __init__(self):
        self._textFont = loader.loadFont('fonts/DroidSansFallbackFull.ttf') # @UndefinedVariable
        self._textFont.setPixelsPerUnit(60)
        self._textFont.setPageSize(512,512)
        self.__spaceCutter = re.compile(ur'\s+',re.UNICODE)
        self.__destroyed = False
        self.__prevBackground = None #上一个背景图片，用于渐变效果
        self.__background = None #当前背景图片
        self.__frontCover = None #前景
        #self.__buffer = 
        
        
        
    def destroy(self):
        self.__destroyed = True
        if self._frame:
            self._frame.destroy()
            self._frame = None
            
        self._gameTextBox = None
        
        self.removeNode()
        self.ignoreAll()
        taskMgr.remove('storyManagerLoop')  # @UndefinedVariable
        
    def __del__(self):
        if not self.__destroyed:
            self.destroy()
            
    def loopTask(self,task):
        '''
        The task loop of StoryManager, trying to advance every task frame
        '''
        if not self.__destroyed:
            self.forward(False)
            return task.cont
        else: return task.done

    def start(self,):
        
        self._frame = DirectFrame(parent = aspect2d)  # @UndefinedVariable pydev在傲娇而已不用管
        self._frame.setTransparency(TransparencyAttrib.MAlpha)
        self.accept('mouse1', self.clicked)
        self._gameTextBox = GameTextBox(parent = self._frame,currentData = runtime_data.RuntimeData.current_text)
        self.loopTask = taskMgr.add(self.loopTask,'storyManagerLoop',sort = 2,priority = 1)  # @UndefinedVariable 傲娇的pydev……因为panda3D的"黑魔法"……
        self.__destroyed = False
        self._storyView = StoryView()
        
    def clicked(self):
        if self._gameTextBox:
            self._gameTextBox.input(GTBI.DEFAULT)

    def forward(self,is_user = False):
        '''run nextCommand() or finish current operations quickly
        @param is_user: define if this operation is started by the player 
        '''
        textbox_ready = False
        
        if not self._gameTextBox.getIsWaiting():
            textbox_ready = True
            
        if textbox_ready:     #And other readies
            self.nextCommand()
        
    def nextCommand(self):
        '''Process the next command in the non-processed queue
        '''
        #TODO: 还要添加循环的支持，用到runtime_data.command_stack来暂存需要回跳的命令组和回跳节点
        #TODO：添加对条件和选择的支持
        if runtime_data.RuntimeData.commands_in_queue:
            self.processCommand(runtime_data.RuntimeData.commands_in_queue.pop(0))
            


    def processCommand(self,command):
        '''Process a StoryCommand
        @param command: The StoryCommand to deal with
        '''    
        
        def translate(t):
            '''
            ,实现通配，__代替空行已经在一开始实现
            '''
            return t.replace(ur'\:', ur':').replace(ur'\：',ur'：').replace(ur'\#',ur'#')
        
        name = ''
        text = ''
        continuous = False
        is_script = False
        spaceCutter = self.__spaceCutter
        
        #read command line
        if command.command:
            commands = command.command.split(',')
            comm = ''
            for item in commands:
                comm = item.strip()
                #名字设置命令
                if comm.startswith('name ') or comm.startswith('name='): 
                    nameCutter = re.compile(ur'name *=?',re.UNICODE) 
                    name = nameCutter.split(comm,1)[1].strip()
        
                #改变文本框格式命令
                elif comm.startswith('textboxstyle '):
                    if self._gameTextBox:
                        self._gameTextBox.setTextBoxStyle(spaceCutter.split(comm, 1)[1])
                
                #文本框分段命令
                elif comm == 'p':
                    if self._gameTextBox:
                        self._gameTextBox.paragraphSparator()
                        
                elif comm.startswith('textbox '):
                    temp = spaceCutter.split(comm,2)
                    if temp[1] == 'apply':
                        self._gameTextBox.applyTextBoxProperties()
                    elif len(temp)>=3:
                        self._gameTextBox.setTextBoxProperty(temp[1],eval(temp[2],runtime_data.RuntimeData.script_space))
                    else:
                        print('Not enough: ' + comm)
                
                else: 
                    print('Undefined Sogal command: ' + comm)
                
                
                        
        if command.text:
            if not is_script:
                #检查有无在文本中的name
                #name: formation checking
                textlines = command.text.splitlines()
                first_line = unicode(textlines[0])
                
                #匹配第一行中是否有表示name的冒号，正则表达式表示前面不是\的冒号（@name 命令行的简写形式判断）
                pattern = re.compile(ur'(?<!\\)[:(：)]',re.UNICODE)  
                
                splited = pattern.split(first_line,maxsplit = 1)
                #print(splited)    #测试用，废弃
                
                #如果存在name即分割成功
                if len(splited)>1:
                    name = translate(splited[0])
                    if splited[1].strip():
                        textlines[0] = splited[1]
                    else:
                        textlines[0] = ''

                #生成文本并解决转义符
                #Generate the final text
                for item in textlines:
                    if item:
                        text += translate(item) + '\n'
                    
        if text and not is_script:
            self._gameTextBox.pushText(text = text, speaker = name, continuous = continuous)
        
        
    def addScriptData(self,fileName):
        '''Load target .sogal script file and add it to the non-processed queue.
        '''
        runtime_data.RuntimeData.commands_in_queue.extend(loadScriptData(fileName))
    

def loadScriptData(fileName):
    '''Load the sogal script file (.sogal) 
    returns a list of StoryCommands indicating different commands
    divided by empty lines and continuous rows of @ symbol
    读取sogal脚本，将不同的命令区分成很多StoryCommand但是不做解析，仅仅是简单地区分开命令行和文本行
    参见 game_entities.StoryCommand
    '''
    
    
    try:  
        fileHandle = open('scenes/'+fileName+'.sogal','r',"utf-8")   #for 'from direct.stdpy.file import open', this 'open' is panda3d opereation and not the standard python operation
    except IOError:
        try:
            fileHandle = open('scenes/'+fileName,'r',"utf-8")
        except IOError:
            try:
                fileHandle = open(fileName,'r',"utf-8")
            except IOError:
                fileHandle = open(fileName+'.sogal','r',"utf-8")
    
    io_reader = StringIO(fileHandle.read())
    
    fileHandle.close()
    
    io_reader.seek(0)
    loaded_list = []
    global _current_command   #虽然global很讨厌……
    _current_command = None   #当前的命令文字
    global _current_text
    _current_text = None    #当前的文本
    
    def push_current():
        global _current_command   #如果是python3.0以上在这里用nonlocal就好了……
        global _current_text
        '''将当前命令文本加入到loaded_list末尾'''
        if not _current_command and not _current_text:
            _current_command = None
            _current_text = None
            return
        else:
            loaded_list.append(StoryCommand(command = _current_command, text = _current_text))
            _current_command = None
            _current_text = None
            
    
    while True:
        
         
      
        temp_original = unicode(io_reader.readline().decode('utf-8'))
        if not temp_original:    #文件末
            push_current() 
            break;
        else:
            #textTemp = temp_original.strip('\n')
            notesplit = re.compile(ur'(?<!\\)#|^#',re.UNICODE) 
            #Convert the line to utf-8 and remove the note afterwards
            line_raw = notesplit.split(temp_original,1)[0]
            line = line_raw.strip()
            
            if not line:     #若是空行，则进行push操作
                push_current() 
                
            elif line.startswith('@'):
                if _current_command or _current_text:   
                    #如果在一个命令列前面已经有了内容，则前面已经是完整的一段，所以推入列表
                    push_current() 
                _current_command = line.lstrip('@')
                
            else:    #于是就剩下是文本的情况
                if _current_text:
                    _current_text += '\n'
                else: _current_text = ''
                adding = line_raw.rstrip()
                if adding.startswith('__'):
                    _current_text += ' ' #用一个空格代替空行嗯
                else: _current_text += adding
            
    return loaded_list
       
        
    
    

        