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
from direct.stdpy.file import open,exists
from direct.task import Task

from game_text_box import GameTextBox
from story_view import StoryView,StoryViewItemEntry,SVIC

import runtime_data

sogalscrpathes = ['scenes/','']
sogalscrtypes = ['.sogal','']

pscriptpathes = ['scenes/','scenes/scripts/','']
pscriptpathes = ['.py','']




        

class StoryManager(DirectObject):
    """Story controller of Sogal
    Controls the whole story scene.
    Mainly for logic control
    And graphics is on other  
    Attributes:
    gameTextBox: the current GameTextBox, useful for user scripting
    storyView: the current StoryView, useful for user scripting
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
            
        self.gameTextBox = None
        
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
        self.gameTextBox = GameTextBox(currentData = runtime_data.RuntimeData.current_text)
        self.storyView = StoryView()
        taskMgr.add(self.loopTask,'storyManagerLoop',sort = 2,priority = 1)  # @UndefinedVariable 傲娇的pydev……因为panda3D的"黑魔法"……
        #self.loopTask = 
        self._inputReady = True
        
        
    def clicked(self):
        if not self.getSceneReady():
            self.storyView.quickfinish()
            self.gameTextBox.quickFinish()
        else:
            self.setInputReady(True)
                
                
    def getSceneReady(self):
        '''Get if the scene is ready'''
        textbox_ready = False
        view_ready = False
        
        if not self.gameTextBox.getIsWaiting():
            textbox_ready = True
            
        if not self.storyView.getIsWaiting():
            view_ready = True
            
        if textbox_ready and view_ready:
            return True
        return False
    
    def getInputReady(self):
        '''define is user's 'next' command given'''
        return self._inputReady
    
    def setInputReady(self, value):
        self._inputReady = value
    

    def forward(self,is_user = False):
        '''run nextCommand() or finish current operations quickly
        @param is_user: define if this operation is started by the player 
        '''
        if self.getSceneReady() and self.getInputReady():
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
        
        def seval(str):
            return eval(str,runtime_data.RuntimeData.script_space)
        
        self.storyView.clearQuickItems()  #clear out quick items
        
        name = ''
        text = ''
        continuous = False
        is_script = False
        spaceCutter = self.__spaceCutter
        
        cleared = False

            
        
        #read command line
        if command.command:
            commands = command.command.split(',')
            comm = ''
            for item in commands:
                comm = item.strip()
                if comm:
                    messenger.send('sogalcommand',[comm]) #allow other tools to deal with it
                #名字设置命令
                if comm.startswith('name ') or comm.startswith('name='): 
                    nameCutter = re.compile(ur'name *=?',re.UNICODE) 
                    name = nameCutter.split(comm,1)[1].strip()
        
                #改变文本框格式命令
                elif comm.startswith('textboxstyle '):
                    if self.gameTextBox:
                        self.gameTextBox.setTextBoxStyle(spaceCutter.split(comm, 1)[1])
                
                #文本框分段命令
                elif comm == 'p':
                    if self.gameTextBox:
                        self.gameTextBox.paragraphSparator()
                
                #文本框属性设置命令
                elif comm.startswith('textbox '):
                    temp = spaceCutter.split(comm,2)
                    if temp[1] == 'apply':
                        self.gameTextBox.applyTextBoxProperties()
                    elif len(temp)>=3:
                        self.gameTextBox.setTextBoxProperty(temp[1],seval(temp[2]))
                    else:
                        print('Not enough: ' + comm)
                        
                #背景设置命令
                elif comm.startswith('bg '):
                    temp = spaceCutter.split(comm,2)
                    if len(temp) >= 3:
                        fadein = seval(temp[2])
                    else: fadein = 0
                    self.storyView.changeBackground(temp[1],fadein)
                
                #图片显示命令
                elif comm.startswith('p '):
                    temp = spaceCutter.split(comm,6)
                    if len(temp) >= 7:
                        fadein = seval(temp[6])
                    else:
                        fadein = 0
                    if len(temp) >= 6:
                        scale = seval(temp[5])
                    else:
                        scale = 1
                    if len(temp) >= 5:
                        location = (seval(temp[3]),0,seval(temp[4]))
                    else:
                        if self.storyView.itemEntries.has_key(temp[1]):
                            location = self.storyView.itemEntries[temp[1]].pos
                        else: location = (0,0,0)
                    svie = StoryViewItemEntry(temp[1],temp[2],SVIC.FG,pos = location,scale = (scale,scale,scale),color = (1,1,1,1),fadein = fadein)
                    self.storyView.newItem(svie)
                    
                elif comm.startswith('del '):
                    temp = spaceCutter.split(comm,2)
                    if len(temp)>=3:
                        self.storyView.deleteItem(temp[1], seval(temp[2]))
                    else:
                        self.storyView.deleteItem(temp[1])
                    
                elif comm.startswith('ploc '):
                    temp = spaceCutter.split(comm,5)
                    if len(temp) >= 5:
                        location =  (seval(temp[2]),seval(temp[3]),seval(temp[4]))
                    else:
                        location =  (seval(temp[2]),0,seval(temp[3]))
                    if len(temp) >= 6:
                        fadein = seval(temp[5])
                    else: fadein = 0
                    self.storyView.changePosColorScale(temp[1], pos = location,time = fadein)
                    
                elif comm.startswith('pcolor '):
                    temp = spaceCutter.split(comm,6)
                    color = (seval(temp[2]),seval(temp[3]),seval(temp[4]),seval(temp[5]))
                    if len(temp) >= 7:
                        fadein = seval(temp[6])
                    else: fadein = 0
                    self.storyView.changePosColorScale(temp[1], color = color, time = fadein)
                    
                elif comm.startswith('pscale '):
                    temp = spaceCutter.split(comm,5)
                    if len(temp) >= 5:
                        scale = (seval(temp[2]),seval(temp[3]),seval(temp[4]))
                    else: scale = (seval(temp[2]),seval(temp[2]),seval(temp[2]))
                    if len(temp) == 6:
                        fadein = seval(temp[5])
                    elif len(temp) == 4:
                        fadein = seval(temp[3])
                    else: fadein = 0
                    self.storyView.changePosColorScale(temp[1], scale = scale, time = fadein)
                
                elif comm.startswith('o3d '):
                    temp = spaceCutter.split(comm)
                    svie = StoryViewItemEntry(temp[1],temp[2],SVIC.O3D,pos = (seval(temp[3]),seval(temp[4]),seval(temp[5]))
                                              ,scale = (seval(temp[10]),seval(temp[11]),seval(temp[12])),color = (seval(temp[6]),seval(temp[7]),seval(temp[8]),seval(temp[9])))
                    self.storyView.newItem(svie)
                
                elif comm.startswith('o2d '):
                    temp = spaceCutter.split(comm)
                    svie = StoryViewItemEntry(temp[1],temp[2],SVIC.O2D,pos = (seval(temp[3]),seval(temp[4]),seval(temp[5]))
                                              ,scale = (seval(temp[10]),seval(temp[11]),seval(temp[12])),color = (seval(temp[6]),seval(temp[7]),seval(temp[8]),seval(temp[9])))
                    self.storyView.newItem(svie)
                    
                elif comm.startswith('pa '):
                    temp = spaceCutter.split(comm)
                    if len(temp) >= 8:
                        fadein = seval(temp[7])
                    else: fadein = 0
                    svie = StoryViewItemEntry(temp[1],temp[2],SVIC.AFG,pos = (seval(temp[3]),0,seval(temp[4]))
                                              ,scale = (seval(temp[5]),1,seval(temp[6])),fadein = fadein)
                    self.storyView.newItem(svie)
                
                elif comm == 'clear':
                    cleared = True
                    self.storyView.clear()
                    
                elif comm.startswith('clear '):

                    cleared = True
                    temp = spaceCutter.split(comm,2)
                    if len(temp)>=3:
                        self.storyView.clear(seval(temp[1]),temp[2])
                    elif len(temp)==2:
                        self.storyView.clear(seval(temp[1]))
                    else:
                        self.storyView.clear()
                        
                elif comm.startswith('delbg '):
                    temp = spaceCutter.split(comm,1)
                    if len('temp')>=2:
                        self.storyView.deleteItem('__bg__', seval(temp[1]))
                    else:
                        self.storyView.deleteItem('__bg__')
                        
                elif comm.startswith('qp '):
                    temp = spaceCutter.split(comm,3)
                    svie = StoryViewItemEntry('quickitem',temp[1],SVIC.FG,
                                              pos = (seval(temp[2]),0,seval(temp[3])),
                                              quickitem = True
                                              )
                    self.storyView.newItem(svie)
                
                
                else: 
                    if comm:
                        print('extra command: ' + comm)
                        
                        
                
                
                        
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
            
            self.gameTextBox.pushText(text = text, speaker = name, continuous = continuous)
            self._inputReady = False
            self.gameTextBox.show()
            
        else:
            if cleared:
                self.gameTextBox.hide()    #better to hide the textbox when 'vclear'
        
        
    def addScriptData(self,fileName):
        '''Load target .sogal script file and add it to the non-processed queue.
        '''
        runtime_data.RuntimeData.commands_in_queue.extend(loadScriptData(fileName))
  
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

def loadScriptData(fileName):
    '''Load the sogal script file (.sogal) 
    returns a list of StoryCommands indicating different commands
    divided by empty lines and continuous rows of @ symbol
    读取sogal脚本，将不同的命令区分成很多StoryCommand但是不做解析，仅仅是简单地区分开命令行和文本行
    参见 game_entities.StoryCommand
    '''
    fileloc = None
    for pt in ((path,type) for path in sogalscrpathes for type in sogalscrtypes):
        if exists(pt[0]+fileName+pt[1]):
            fileloc = pt[0]+fileName+pt[1]
    
  
    fileHandle = open(fileloc)   #for 'from direct.stdpy.file import open', this 'open' is panda3d opereation and not the standard python operation

    
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
       
        
    
    

        