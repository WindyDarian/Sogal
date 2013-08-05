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
import re,copy

from panda3d.core import NodePath  # @UnresolvedImport
from panda3d.core import TransparencyAttrib  # @UnresolvedImport

#from direct.gui.DirectButton import DirectButton
from direct.stdpy.file import open,exists
from direct.stdpy import threading
from direct.stdpy import pickle
from direct.task import Task
from direct.gui.DirectFrame import DirectFrame
import direct.gui.DirectGuiGlobals as DGG

from game_text_box import GameTextBox
from story_view import StoryView,StoryViewItemEntry,SVIC
from story_menu_bar import StoryMenuBar
from sogal_form import SogalForm

import runtime_data
from sogasys.save_load_form import SaveForm


space_cutter = re.compile(ur'\s+',re.UNICODE)
mark_cutter =  re.compile(ur'mark *:',re.UNICODE)
script_global = {}



class StoryManager(SogalForm):
    """Story controller of Sogal
    Controls the whole story scene.
    Mainly for logic control
    And graphics is on other  
    Attributes:
    gameTextBox: the current GameTextBox, useful for user scripting
    storyView: the current StoryView, useful for user scripting
    """
    script_space = {}
    _currentDump = None
    __destroyed = False
    
    def __init__(self):
        self.step = 0    #shows how many commands line it had run, used to sync data dumps
        self.scrStack = []
        self.commandList = []
        
        
        if not runtime_data.RuntimeData.command_ptr:
            self.scrPtr = 0
        else: self.scrPtr = runtime_data.RuntimeData.command_ptr
        
        if not runtime_data.RuntimeData.command_stack:
            runtime_data.RuntimeData.command_stack = self.scrStack
        else: self.scrStack = runtime_data.RuntimeData.command_stack
        
        if not runtime_data.RuntimeData.command_list:
            runtime_data.RuntimeData.command_list = self.commandList
        else: self.commandList = runtime_data.RuntimeData.command_list
                
        
        self._frame = DirectFrame(parent = aspect2d)  # @UndefinedVariable pydev在傲娇而已不用管
        self._frame.setTransparency(TransparencyAttrib.MAlpha)

        

        
        self.storyView = StoryView()
        self.audioPlayer = base.audioPlayer  # @UndefinedVariable pydev在傲娇而已不用管
        self.menu = StoryMenuBar()
        self.gameTextBox = GameTextBox()
        
        self.button_save = self.menu.addButton(text = 'Save',state = DGG.DISABLED, command = self.save)
        self.button_load = self.menu.addButton(text = 'Load',state = DGG.NORMAL,command = self.load)
        self.button_quicksave = self.menu.addButton(text = 'Quick Save',state = DGG.DISABLED,command = self.quickSave)
        self.button_quickload = self.menu.addButton(text = 'Quick Load',state = DGG.DISABLED,command = self.quickLoad)
        
        self._inputReady = True
        self.__arrow_shown = False
        
        self._currentMessage = ''
        
        self.mapScriptSpace()
        SogalForm.__init__(self)
        self.show()
        taskMgr.add(self.loopTask,'storyManagerLoop',sort = 2,priority = 1)  # @UndefinedVariable 傲娇的pydev……因为panda3D的"黑魔法"……

        
    def focused(self):
        self.accept('mouse1', self.clicked, [1])
        self.accept('mouse3', self.clicked, [3])
        SogalForm.focused(self)
        
    def defocused(self):
        self.ignore('mouse1')
        self.ignore('mouse3')
        SogalForm.defocused(self)
        self.__arrow_shown = False
        self.gameTextBox.hideArrow()
   
        
    def destroy(self):
        self.__destroyed = True
        taskMgr.remove('storyManagerLoop')  # @UndefinedVariable
        if self._frame:
            self._frame.destroy()
            self._frame = None
            
        self.gameTextBox.destroy()
        self.storyView.destroy()
        self.menu.destroy()
        SogalForm.destroy(self)
            
    def loopTask(self,task):
        '''
        The task loop of StoryManager, trying to advance every task frame
        '''
        if not self.__destroyed:
            if self.hasFocus():
                self.forward(False)
            return task.cont
        else: return task.done


        
    def _enableSavingButton(self):
        self.button_save['state'] = DGG.NORMAL
        self.button_quicksave['state'] = DGG.NORMAL

    def _disableSavingButton(self):
        self.button_save['state'] = DGG.DISABLED
        self.button_quicksave['state'] = DGG.DISABLED
    
        
    def presave(self):
        if self.scrPtr:
            runtime_data.RuntimeData.command_ptr = self.scrPtr
        self.gameTextBox.presave()
        self.storyView.presave()
        self.audioPlayer.presave()
        
    def reload(self):
        taskMgr.remove('storyManagerLoop')  # @UndefinedVariable
        self.scrPtr = runtime_data.RuntimeData.command_ptr
        self.mapScriptSpace()
        self.gameTextBox.reload()
        self.storyView.reload()
        self.audioPlayer.reload()
        taskMgr.add(self.loopTask,'storyManagerLoop',sort = 2,priority = 1)  # @UndefinedVariable 傲娇的pydev……因为panda3D的"黑魔法"……
       
      
    def mapScriptSpace(self):
        if runtime_data.RuntimeData.script_space:  #map script space
            self.script_space = runtime_data.RuntimeData.script_space
        else: runtime_data.RuntimeData.script_space = self.script_space 
        script_global['goto'] = self.goto
        script_global['story_manager'] = self    
        script_global['game_text_box'] = self.gameTextBox
        script_global['story_view'] = self.storyView
        script_global['audio_player'] = self.audioPlayer
        
    def quickfinish(self):
        self.storyView.quickfinish()
        self.gameTextBox.quickFinish()        
    
    def clicked(self,key = 1):
        if not self.hasFocus():
            return
        
        if key == 1 :
            if not self.getSceneReady():
                self.quickfinish()
            else:
                self.setInputReady(True)
        elif key == 3:
            self.quickfinish()
            if self.getSceneReady():
                self.menu.show()
                
    def save(self):
        self.menu.hide()
        base.saveForm.setData(self._currentDump, self._currentMessage)
        base.saveForm.show()
        
    def load(self):
        self.menu.hide()
        base.loadForm.show()
            
    def quickSave(self):
        '''quicksave the data'''
        self.menu.hide()
        self.button_quicksave['state'] = DGG.DISABLED
        self.button_quickload['state'] = DGG.DISABLED
        if self._currentDump:
            messenger.send('save_data',[self._currentDump,'quick_save',self._currentMessage])  # @UndefinedVariable
            
    def quickLoad(self):
        if exists(runtime_data.game_settings['save_folder'] + 'quick_save' + runtime_data.game_settings['save_type'] ):
            messenger.send('load_data',['quick_save'])  # @UndefinedVariable
        
                
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
        scene_ready = self.getSceneReady()
        if scene_ready and not self.__arrow_shown:
            self.gameTextBox.showArrow()
            self.__arrow_shown = False
            
        
        if scene_ready and self.getInputReady():
            self.nextCommand()
        
    def nextCommand(self):
        '''Process the next command in the non-processed queue
        '''
        #TODO: 还要添加循环的支持，用到runtime_data.command_stack来暂存需要回跳的命令组和回跳节点
        #TODO：添加对条件和选择的支持
        
        self.__arrow_shown = False
        self.gameTextBox.hideArrow()
        
        #Dumps story data for saving or further use
        if self.__destroyed:
            return
        
        self.step += 1 
        self.presave()
        self._currentDump = copy.deepcopy(runtime_data.RuntimeData)
        
        
        if len(self.commandList) > self.scrPtr:
            handled = False
            if self.commandList[self.scrPtr].command:
                temp = self.commandList[self.scrPtr].command.strip()
                if temp.startswith('mark ')or temp.startswith('mark:'):
                    handled = True
            
            if not handled:
                self.processCommand(self.commandList[self.scrPtr])
            
            self.scrPtr = self.scrPtr + 1
            runtime_data.RuntimeData.command_ptr = self.scrPtr
        
        
        if exists(runtime_data.game_settings['save_folder'] + 'quick_save.dat'):
            self.button_quickload['state'] = DGG.NORMAL 
            
        if self.gameTextBox.newText:
            self._currentMessage = self.gameTextBox.newText
            
        if self._currentDump: 
            
            self._enableSavingButton()
    
    def goto(self, target):
        '''Jump to a mark'''
        for i in range(0, len(self.commandList)):
            if self.commandList[i].command:
                mark = mark_cutter.split(self.commandList[i].command , 1)
                if len(mark) > 1:
                    markText = mark[1].strip()
                    if markText == target:
                        self.scrPtr = i
                        return
        print 'unable to find mark'

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
            return eval(str,script_global,runtime_data.RuntimeData.script_space)
        
        self.storyView.clearQuickItems()  #clear out quick items
        
        name = ''
        text = ''
        continuous = False
        is_script = False
        spaceCutter = space_cutter
        
        cleared = False

        voiceFlag = False                   #it will be True if voice is stopped in this line of command 
                                            #used for disable cross voice of different command lines
                                            #but enable one command line with multiple voices
        
        #read command line
        if command.command:
            commands = command.command.split(',')
            comm = ''
            for item in commands:
                comm = item.strip()
                if comm:
                    messenger.send('sogalcommand',[comm]) #allow other tools to deal with it @UndefinedVariable
                #名字设置命令
                if comm.startswith('name ') or comm.startswith('name='): 
                    nameCutter = re.compile(ur'name *=?',re.UNICODE) 
                    name = nameCutter.split(comm,1)[1].strip()
        
                #改变文本框格式命令
                elif comm.startswith('textboxstyle '):
                    if self.gameTextBox:
                        self.gameTextBox.setTextBoxStyle(spaceCutter.split(comm, 1)[1])
                        self.gameTextBox.applyStyle()
                
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
                
                elif comm.startswith('v '):
                    if not voiceFlag:
                        self.audioPlayer.stopVoice()
                        voiceFlag = True
                    temp = spaceCutter.split(comm , 2)
                    if len(temp)>=3:
                        volume = seval(temp[2])
                    else: volume = 1
                    self.audioPlayer.playVoice(temp[1],volume)
                    
                elif comm.startswith('se '):
                    temp = spaceCutter.split(comm , 2)
                    if len(temp)>=3:
                        volume = seval(temp[2])
                    else: volume = 1
                    self.audioPlayer.playSound(temp[1],volume)
                    
                elif comm == 'vstop':
                    self.audioPlayer.stopVoice()
                    voiceFlag = True
                    
                elif comm == 'sestop':
                    self.audioPlayer.stopSound()
                    
                elif comm.startswith('bgm '):
                    temp = spaceCutter.split(comm , 4)
                    if len(temp)>=3:
                        fadein = seval(temp[2])
                    else: fadein = 0
                    if len(temp)>=4:
                        volume = seval(temp[3])
                    else: volume = 1
                    if len(temp)>=5:
                        loop = bool(seval(temp[4]))
                    else: loop = True
                    self.audioPlayer.playBGM(temp[1], fadein=fadein, volume=volume, loop=loop)      
                    
                elif comm.startswith('env '):
                    temp = spaceCutter.split(comm , 4)
                    if len(temp)>=3:
                        fadein = seval(temp[2])
                    else: fadein = 0
                    if len(temp)>=4:
                        volume = seval(temp[3])
                    else: volume = 1
                    if len(temp)>=5:
                        loop = bool(seval(temp[4]))
                    else: loop = True
                    self.audioPlayer.playENV(temp[1], fadein=fadein, volume=volume, loop=loop)        
                
                elif comm.startswith('bgmstop ') or comm == 'bgmstop':
                    temp = spaceCutter.split(comm , 1)
                    if len(temp)>=2:
                        fadeout = seval(temp[1])
                    else: fadeout = 0
                    self.audioPlayer.stopBGM(fadeout)
                    
                elif comm.startswith('envstop ') or comm == 'envstop':
                    temp = spaceCutter.split(comm , 1)
                    if len(temp)>=2:
                        fadeout = seval(temp[1])
                    else: fadeout = 0
                    self.audioPlayer.stopENV(fadeout)
                    
                elif comm.startswith('audiostop ') or comm == 'audiostop':
                    temp = spaceCutter.split(comm , 1)
                    if len(temp)>=2:
                        fadeout = seval(temp[1])
                    else: fadeout = 0
                    self.audioPlayer.stopAll(fadeout)
                    
                elif comm == 'script':
                    is_script = True
                    
                elif comm.startswith('script '):
                    temp = spaceCutter.split(comm , 1)
                    self.runScriptFile(temp[1])       
                                               
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
            
        if is_script:
            self.runScript(command.text)
        
        if text:
            self.pushText(text = text, speaker = name, continuous = continuous)
            
        else:
            if cleared:
                self.gameTextBox.hide()    #better to hide the textbox when 'vclear'
    
    def pushText(self, text, speaker = None, continuous = False):
        self.gameTextBox.pushText(text = text, speaker = speaker, continuous = continuous)
        self._inputReady = False
        self.gameTextBox.show()        
    
    def runScript(self,pscriptText):
        exec(pscriptText,script_global,self.script_space)
    
    def runScriptFile(self,fileName):
        #'''note that would ignore panda virtual pathes'''
        pathes = runtime_data.game_settings['pscriptpathes']
        types = runtime_data.game_settings['pscripttypes']
        for ft in ((folder,type) for folder in pathes for type in types):
            if exists(ft[0] + fileName + ft[1]):
                handle = open(ft[0] + fileName + ft[1])
                script = handle.read()
                handle.close()
                break
        if script:
            self.runScript(script)
        else:
            print "file not find: "+ fileName
        
    def beginScene(self,fileName):
        '''Load target .sogal script file and go to that file.
        '''
        self.scrPtr = 0
        self.scrStack = []  #used for stack controller pointers
        self.commandList = loadScriptData(fileName)
        runtime_data.RuntimeData.command_stack = self.scrStack
        runtime_data.RuntimeData.command_list = self.commandList
  
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
    for pt in ((path,type) for path in runtime_data.game_settings['sogalscrpathes'] for type in runtime_data.game_settings['sogalscrtypes']):
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
    controlAttribs_startswith = ['if ','while ','elif ']
    controlAttribs_equal = ['else','end']
    
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
                
                #There should be no text in control parts so it it is an control part then push
                for attr in controlAttribs_startswith:
                    if _current_command.startswith(attr):
                        push_current()
                for attr in controlAttribs_equal:
                    if _current_command == attr:
                        push_current()
                
                
            else:    #于是就剩下是文本的情况
                if _current_text:
                    _current_text += '\n'
                else: _current_text = ''
                adding = line_raw.rstrip()
                if adding.startswith('__'):
                    _current_text += ' ' #用一个空格代替空行嗯
                else: _current_text += adding
            
    return loaded_list
       

    
    

        