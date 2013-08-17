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
from direct.stdpy.threading import Lock
from direct.stdpy import pickle
from direct.task import Task
from direct.gui.DirectFrame import DirectFrame
import direct.gui.DirectGuiGlobals as DGG
from direct.interval.FunctionInterval import Wait

from game_text_box import GameTextBox
from story_view import StoryView,StoryViewItemEntry,SVIC
from story_menu_bar import StoryMenuBar
from sogal_form import SogalForm, ConfirmDialog, SogalDialog
from text_history import TextHistory
import runtime_data


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
        self.step = 0    #shows how many commands line it had run
        self.scrStack = []
        self.commandList = []
        
        self.__currentPtr = None
        if not runtime_data.RuntimeData.command_ptr:
            self.nextPtr = 0
        else: self.nextPtr = runtime_data.RuntimeData.command_ptr
        
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
        self.textHistory = TextHistory()
        
        self.button_auto = self.menu.addButton(text = 'Auto',state = DGG.NORMAL,command = self.autoPlayButton)
        self.button_history = self.menu.addButton(text = 'History',state = DGG.NORMAL,command = self.showTextHistoryButton)
        self.button_skip = self.menu.addButton(text = 'Skip',state = DGG.DISABLED,command = self.startSkippingButton)
        self.button_lastchoice = self.menu.addButton(text = 'Last Choice',state = DGG.DISABLED,command = self.lastChoice)
        self.button_save = self.menu.addButton(text = 'Save',state = DGG.DISABLED, command = self.saveButton)
        self.button_load = self.menu.addButton(text = 'Load',state = DGG.NORMAL,command = self.loadButton)
        self.button_quicksave = self.menu.addButton(text = 'Quick Save',state = DGG.DISABLED,command = self.quickSaveButton)
        self.button_quickload = self.menu.addButton(text = 'Quick Load',state = DGG.DISABLED,command = self.quickLoadButton)
        self.button_title = self.menu.addButton(text = 'Title',state = DGG.NORMAL,command = self.returnToTitle)
        
        self._inputReady = True
        self.__arrow_shown = False
        self._choiceReady = True
        self._currentMessage = ''
        self.__currentSelection = None
        self.__finishing = False
        self.__lock = Lock()
        self.forcejump = False
        self.__autoInput = False
        self.__focused = False
        self.intervals = []
        self.__skipping = False
        self.__autoplaying = False
        self.__autoInterval = None
        self.__autoplaystep = None
        
        self.mapScriptSpace()
        SogalForm.__init__(self)
        self.show()
        taskMgr.add(self.loopTask,'story_manager_loop',sort = 2,priority = 1)  # @UndefinedVariable 傲娇的pydev……因为panda3D的"黑魔法"……
      
        taskMgr.doMethodLater(runtime_data.game_settings['jump_span'],self.__jumpCheck,'story_jump_check', sort = 5, priority = 1)  # @UndefinedVariable
        
        
        
        
        
    def focused(self):
        if not self.__focused:
            self.accept('mouse1', self.input, [1])
            self.accept('enter', self.input, [1])
            self.accept('mouse3', self.input, [3])
            self.accept('wheel_up', self.showTextHistory)
            self.accept('escape', self.showMenu)
            self.accept('control',self.setForceJump, [True])
            self.accept('control-up',self.setForceJump, [False])
            SogalForm.focused(self)
            self.__focused = True
    
    
    def defocused(self):
        if self.__focused:
            self.ignore('mouse1')
            self.ignore('enter')
            self.ignore('mouse3')
            self.ignore('wheel_up')
            self.ignore('escape')
            self.ignore('control')
            self.ignore('control-up')
            self.setForceJump(False)
            SogalForm.defocused(self)
            self.__arrow_shown = False
            self.gameTextBox.hideArrow()
            self.__focused = False
   
        
    def destroy(self):
        self.__destroyed = True
        taskMgr.remove('story_manager_loop')  # @UndefinedVariable
        taskMgr.remove('story_jump_check')  # @UndefinedVariable
        if self._frame:
            self._frame.destroy()
            self._frame = None
        
        if self.__currentSelection:
            self.__currentSelection.destroy()
        self.gameTextBox.destroy()
        self.storyView.destroy()
        self.menu.destroy()
        self.textHistory.destroy()
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
        if self.nextPtr is not None:
            runtime_data.RuntimeData.command_ptr = self.nextPtr
        self.gameTextBox.presave()
        self.storyView.presave()
        self.audioPlayer.presave()
        
    def reload(self):
        taskMgr.remove('storyManagerLoop')  # @UndefinedVariable
        self.nextPtr = runtime_data.RuntimeData.command_ptr
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
        self.__lock.acquire()
        if not self.__finishing:
            self.__finishing = True
            self.storyView.quickfinish()
            self.gameTextBox.quickFinish()
            for itv in self.intervals:
                itv.finish()
        self.__lock.release()
    
    def input(self,type = 1):
        self.stopSkipping()
        self.stopAutoPlaying()
        
        if not self.hasFocus():
            return
        #left mouse button or enter key
        if type == 1 :
            if not self.getSceneReady():
                self.quickfinish()
            else:
                self.setTextInputReady(True)
        #right mouse button
        elif type == 3:
            self.quickfinish()
            if self.getSceneReady():
                self.menu.show()
                
    def showMenu(self):
        self.stopSkipping()
        self.stopAutoPlaying()
        
        self.quickfinish()
        if self.getSceneReady() and not self.forcejump:
            self.menu.show()   
            
    def showTextHistory(self):
        if self.getSceneReady() and not self.forcejump:
            self.textHistory.show()
                
    def saveButton(self):
        self.menu.hide()
        base.saveForm.setData(self._currentDump, self._currentMessage)
        base.saveForm.show()
        
    def loadButton(self):
        self.menu.hide()
        base.loadForm.show()
            
    def quickSaveButton(self):
        '''quicksave the data'''
        self.menu.hide()
        self.button_quicksave['state'] = DGG.DISABLED
        self.button_quickload['state'] = DGG.DISABLED
        if self._currentDump:
            messenger.send('quick_save', [self._currentDump,self._currentMessage])
            
    def quickLoadButton(self):
        ConfirmDialog(text= '要读取吗？',command= self.__confirmedQuickLoad)
        
    def returnToTitle(self):
        ConfirmDialog(text= '回到标题界面？',command= self.__confirmedReturnToTitle)
    
    def __confirmedReturnToTitle(self):
        messenger.send('return_to_title')
        
    def showTextHistoryButton(self):
        self.menu.hide()
        self.showTextHistory()
        
    def startSkippingButton(self):
        self.menu.hide()
        self.startSkipping()
        
    def autoPlayButton(self):
        self.menu.hide()
        if self.__autoplaying:
            self.stopAutoPlaying()
        else: self.startAutoPlaying()
        
    def lastChoice(self):
        ConfirmDialog(text= '要回到上一个选择枝吗？',command= self.__confirmedLastChoice)
        
    def __confirmedQuickLoad(self):
            messenger.send('quick_load')  # @UndefinedVariable        
    
    def __confirmedLastChoice(self):
        if runtime_data.RuntimeData.last_choice:
            messenger.send('load_memory',[runtime_data.RuntimeData.last_choice])            # @UndefinedVariable
            
    def autoSave(self,info = ''):
        if not info:
            info = self._currentMessage
        messenger.send('auto_save',[self._currentDump,info])
    
    def getSceneReady(self):
        '''Get if the scene is ready'''
        textbox_ready = False
        view_ready = False
        intervals_ready = True
        
        if not self.gameTextBox.getIsWaiting():
            textbox_ready = True
            
        if not self.storyView.getIsWaiting():
            view_ready = True
            
        for itv in self.intervals:
            if itv.isPlaying():
                intervals_ready = False
                break
            
        scene_ready = textbox_ready and view_ready and intervals_ready
        
        if not scene_ready:
            return False
        
        #auto play span
        if scene_ready and self.__autoplaying:
            if self.__autoplaystep != self.step:
                self.__autoplaystep = self.step
                self.__autoInterval = Wait(runtime_data.game_settings['auto_span'])
                self.__autoInterval.start()
                scene_ready = False
            else:
                if self.__autoInterval.isPlaying():
                    scene_ready = False
                    
            if self.audioPlayer.isVoicePlaying():
                scene_ready = False
        
        return scene_ready
    
    def getInputReady(self):
        '''define is user's 'next' command given'''
        textinput_ready = self._inputReady or self.__autoInput
        choice_ready = self.getChoiceReady()
        
        if self.__autoInput:
            self.__autoInput = False
        
        if textinput_ready and choice_ready:
            return True
        return False
    
    def setTextInputReady(self, value):
        self._inputReady = value
        
    def getChoiceReady(self):
        return self._choiceReady
    

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
            
        if self.forcejump or self.__skipping:
            self.quickfinish()
        
    def nextCommand(self):
        '''Process the next command in the non-processed queue
        '''
        #TODO: 还要添加循环的支持，用到runtime_data.command_stack来暂存需要回跳的命令组和回跳节点
        #TODO：添加对条件和选择的支持
        self.__finishing = False
        
        self.__arrow_shown = False
        self.gameTextBox.hideArrow()
        
        #Dumps story data for saving or further use
        if self.__destroyed:
            return
        
        self.step += 1 
        self.presave()
        self._currentDump = copy.deepcopy(runtime_data.RuntimeData)
        
        if self.nextPtr < 0: self.nextPtr = 0
        self.__currentPtr = self.nextPtr
        self.nextPtr += 1
        
        if not self.commandList:
            return
        
        if len(self.commandList) > self.__currentPtr:
            handled = False
            if self.commandList[self.__currentPtr].command:
                comline = self.commandList[self.__currentPtr].command.strip()
                if comline.startswith('mark ')or comline.startswith('mark:'):
                    handled = True
                    
                # 条件判断处理 If condition
                elif comline.startswith('if '):
                    splited = space_cutter.split(comline, 1)
                    if len(splited)<2:
                        raise Exception('没条件玩毛线')
                    if self.scriptEval(splited[1]):
                        handled = True
                        
                    else:
                        relative_depth = 0
                        #if not match the condition, try to jump to elif or else
                        for i in range(self.__currentPtr+1,len(self.commandList)):
                            cli = self.commandList[i]
                            if cli.command:
                                cl = cli.command.strip()
                            else: continue
                            #一个嵌套循环的情况！ A inner if
                            if cl.startswith('if '):
                                relative_depth += 1
                                continue
                            elif relative_depth == 0 and cl.startswith('elif '):
                                splited = space_cutter.split(cl, 1)
                                if len(splited)<2:
                                    raise Exception('没条件玩毛线')
                                if self.scriptEval(splited[1]):
                                    self.nextPtr = i + 1
                                    handled = True
                                    break
                                else: continue
                            elif relative_depth == 0 and cl == 'else':
                                self.nextPtr = i + 1
                                handled = True
                                break
                            elif cl == 'end' or cl.startswith('end '):
                                if relative_depth == 0:
                                    self.nextPtr = i + 1
                                    handled = True
                                    break
                                else: 
                                    relative_depth -= 1
                                    continue
                                    
                #if we meet else or elif then jump to end
                elif comline.startswith('elif ') or comline == 'else':

                    relative_depth = 0
                    for i in range(self.__currentPtr+1,len(self.commandList)):
                        cli = self.commandList[i]
                        if cli.command:
                            cl = cli.command.strip()
                        else: continue
                        if cl.startswith('if '):
                            relative_depth += 1
                            continue
                        elif cl == 'end' or cl.startswith('end '):
                            if relative_depth == 0:
                                self.nextPtr = i + 1
                                handled = True
                                break
                            else: 
                                relative_depth -= 1
                                continue                        
                
                #ignore end
                elif comline == 'end' and comline.startswith('end '):
                    handled = True
                
                                     
            
            if not handled:
                self.processCommand(self.commandList[self.__currentPtr])
            
            #self.scrPtr = self.scrPtr + 1
            #runtime_data.RuntimeData.command_ptr = self.scrPtr
        
        
        if base.hasQuickData():
            self.button_quickload['state'] = DGG.NORMAL 
            
        if runtime_data.RuntimeData.last_choice:
            self.button_lastchoice['state'] = DGG.NORMAL 
            
        if self.gameTextBox.newText:
            runtime_data.RuntimeData.latest_text = self.gameTextBox.newText
        if runtime_data.RuntimeData.latest_text:
            self._currentMessage = runtime_data.RuntimeData.latest_text
            
            
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
                        self.nextPtr = i    #Solved: #this is not a good solution but this method runs at 'nextCommand', and ths scrPtr would plus 1 afterwards
                        return
        print 'unable to find mark'

    def processCommand(self,command):
        '''Process a StoryCommand
        @param command: The StoryCommand to deal with
        '''    

        
        def seval(strs):
            return self.scriptEval(strs)
        
        
        #Mark read
        if not runtime_data.read_text.has_key(command.fileLoc):
            runtime_data.read_text[command.fileLoc] = {}
        if not runtime_data.read_text[command.fileLoc].has_key(command.index):
            already_read = False
            self.stopSkipping()
        else: already_read = True
        runtime_data.read_text[command.fileLoc][command.index] = True
        if already_read:
            self.button_skip['state'] = DGG.NORMAL
        else: self.button_skip['state'] = DGG.DISABLED
        
        self.storyView.clearQuickItems()  #clear out quick items
        
        name = ''
        continuous = False
        is_script = False
        is_selection = False
        spaceCutter = space_cutter
        
        hidingtext = False

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
                        
                elif comm == 'c':
                    continuous = True
                    
                elif comm.startswith('wait '):
                    temp = spaceCutter.split(comm,1)
                    if len(temp) > 1:
                        self.sceneWait(seval(temp[1]))
                
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
                    hidingtext = True
                    self.storyView.clear()
                    
                elif comm.startswith('clear '):
                    hidingtext = True
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
                    
                elif comm == 'choice' or comm.startswith('choice '):
                    '''
                    Selection
                    '''
                    is_selection = True
                    temp = spaceCutter.split(comm, 1)
                    if len(temp) > 1:
                        striped = temp[1].strip()
                        if striped:
                            self.pushText(text = striped, speaker = None, needInput = False, read = already_read)
                            
                elif comm.startswith('jump '):
                    temp = spaceCutter.split(comm , 1)
                    self.beginScene(temp[1].strip())
                    
                elif comm.startswith('expand '):
                    temp = spaceCutter.split(comm , 1)
                    self.expandScene(temp[1].strip())
                    
                elif comm.startswith('goto '):
                    temp = spaceCutter.split(comm , 1)
                    self.goto(temp[1].strip())       
                    
                elif comm.startswith('theme '):
                    temp = spaceCutter.split(comm , 1)
                    self.reloadTheme(temp[1].strip())
               
                elif comm == 'autosave' or comm.startswith('autosave '):
                    temp = spaceCutter.split(comm , 1)
                    if len(temp) > 1:
                        self.autoSave(temp[1])
                    else:
                        self.autoSave()
        
                else: 
                    if comm:
                        print('extra command: ' + comm)
                        
        if command.text:
            if is_script:
                self.runScript(command.text)
            
            elif is_selection:
                '''
                If encountered a selection
                '''
                choiceList = []
                enablesList = []
                textlines = command.text.splitlines()
                for tl in textlines:
                    if tl.startswith('--'):  #--means disabled
                        text = tl[2:]
                        enablesList.append(False)
                    else:
                        text = tl
                        enablesList.append(True)
                    choiceList.append(text)
                self.showSelection(choiceList = choiceList, enablesList = enablesList)
            
            else:
                self.pushText(text = command.text, speaker = name, continuous = continuous, read = already_read)
            
        else:
            if hidingtext:
                self.gameTextBox.hide()    #better to hide the textbox when 'vclear'

                
    
    def pushText(self, text, speaker = None, continuous = False, needInput = True, read = False):
        
        def translate(t):
            '''
            ,实现通配，__代替空行已经在一开始实现
            '''
            return t.replace(ur'\:', ur':').replace(ur'\：',ur'：').replace(ur'\#',ur'#')
        #检查有无在文本中的name
        #name: formation checking
        textlines = text.splitlines()
        first_line = unicode(textlines[0])
        
        #匹配第一行中是否有表示name的冒号，正则表达式表示前面不是\的冒号（@name 命令行的简写形式判断）
        pattern = re.compile(ur'(?<!\\)[:(：)]',re.UNICODE)  
        
        splited = pattern.split(first_line,maxsplit = 1)
        #print(splited)    #测试用，废弃
        
        #如果存在name即分割成功
        if len(splited)>1:
            speaker = translate(splited[0]).strip()
            if splited[1].strip():
                textlines[0] = splited[1]
            else:
                textlines[0] = None
                
        final_text = ''

        #生成文本并解决转义符
        #Generate the final text
        for item in textlines:
            if item:
                final_text += translate(item) + '\n'
                
        if final_text:
            self.textHistory.append(final_text, speaker, None)
        
        self.gameTextBox.pushText(text = final_text, speaker = speaker, continuous = continuous,read= read)
        if needInput:
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
        self.nextPtr = 0 
        self.scrStack = []  #used for stack controller pointers
        self.commandList = loadScriptData(fileName)
        runtime_data.RuntimeData.command_stack = self.scrStack
        runtime_data.RuntimeData.command_list = self.commandList
        
    def expandScene(self,fileName):
        '''expand a scene, inserting another sogal file in to current point'''
        expanding = loadScriptData(fileName)
        if len(self.commandList)> self.__currentPtr+1:
            self.commandList = self.commandList[:self.__currentPtr] + expanding + self.commandList[self.__currentPtr+1:]
        else:
            self.commandList = self.commandList[:self.__currentPtr] + expanding
        runtime_data.RuntimeData.command_stack = self.scrStack
        runtime_data.RuntimeData.command_list = self.commandList
        self.nextPtr = self.__currentPtr    #Solved: # this is not a good solution but this method runs at 'nextCommand', and ths scrPtr would plus 1 afterwards
        
    def showSelection(self,choiceList = ['A','B'],enablesList = None):
        '''This method shows a selection, which sets 'last_choice' in 
        script space to player's choice. (0 is the first, 1 is the second etc.)
        you can disable some of the selections with enablesList
        for example for choiceList ['A','B','C'] and enablesList
        '''
        #Store the last selection
        rdc = copy.deepcopy(self._currentDump)
        rdc.last_choice = None
        self.__tempDumpedLastChoice = pickle.dumps(rdc, 2)

        self._choiceReady = False
        startPos = (0,0,0.1 * len(choiceList))
        frameSize = (-0.6,0.6,-0.05 - 0.1*len(choiceList), 0.1 + 0.1*len(choiceList))
        buttonSize = (-0.5,0.5,-0.050,0.10)
        margin = 0.05
        self.__currentSelection = SogalDialog(enableMask = False, fadeScreen= None, command = self.__selected, 
                                              textList= choiceList, enablesList= enablesList, sortType= 1,noFocus = True,
                                              startPos = startPos,frameSize = frameSize,margin = margin,
                                              buttonSize = buttonSize)
        
        
        
    def __selected(self,choice):
        #Store the last selection
        if self.__tempDumpedLastChoice:
            runtime_data.RuntimeData.last_choice = self.__tempDumpedLastChoice 
        
        self.script_space['last_choice'] = choice
        self._choiceReady = True
        
    def scriptEval(self,str):
        return eval(str,script_global,runtime_data.RuntimeData.script_space)
    
    def setForceJump(self,forcejump):
        if forcejump:
            if not self.forcejump:
                self.forcejump = True
                self.setTextInputReady(True)
                self.__skipping = False
                self.stopAutoPlaying()
        else:
            self.forcejump = False
            
    def __jumpCheck(self,task):
        if self.hasFocus():
            if self.forcejump or self.__skipping or self.__autoplaying:
                self.__autoInput = True
        return task.again
    
    def sceneWait(self,time,hidetextbox = True):
        waitinterval = Wait(time)
        self.intervals.append(waitinterval)
        waitinterval.start()
        if hidetextbox:
            self.gameTextBox.hide()
            
    def reloadTheme(self,theme):
        base.setStyle(theme)
        self.menu.reloadTheme()
        self.textHistory.reloadTheme()
        self.gameTextBox.reloadTheme()
        
    def stopSkipping(self):
        self.__skipping = False
        if not self.forcejump:
            self.__autoInput = False
        
    def startSkipping(self):
        self.stopAutoPlaying()
        self.__skipping = True
        
    def startAutoPlaying(self):
        self.__skipping = False
        self.__autoplaying = True
        self.button_auto['text'] = 'Stop Auto'
        
    def stopAutoPlaying(self):
        self.__autoplaying = False
        if self.__autoInterval:
            self.__autoInterval.pause()
        self.button_auto['text'] = 'Auto'
        
          
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
        index: The command index in this file, used to mark read/Unread
        fileLoc: The file that contains this StoryCommand
    '''
    
    def __init__(self, command = None, text = None, index = None, fileLoc = None):
        '''
        @param command: A string indicates the command section
        @param text: A string indicates the text section
        '''
        self.command = command
        self.text = text
        #TODO: use self.index and self.fileloc to mark read/unread
        self.index = index
        self.fileLoc = fileLoc
        
    def __repr__(self):
        return 'command: ' + str(self.command) + '\ntext: ' + str(self.text) + '\n\n'

_lsdLock = Lock()

def loadScriptData(fileName):
    '''Load the sogal script file (.sogal) 
    returns a list of StoryCommands indicating different commands
    divided by empty lines and continuous rows of @ symbol
    读取sogal脚本，将不同的命令区分成很多StoryCommand但是不做解析，仅仅是简单地区分开命令行和文本行
    参见 game_entities.StoryCommand
    '''
    
    _lsdLock.acquire()
    
    fileloc = None
    for pt in ((path,type) for path in runtime_data.game_settings['sogalscrpathes'] for type in runtime_data.game_settings['sogalscrtypes']):
        if exists(pt[0]+fileName+pt[1]):
            fileloc = pt[0]+fileName+pt[1]
            break
    
    if not fileloc:
        print('file not found: ' + fileName)
        _lsdLock.release()
        return
   
    fileHandle = open(fileloc)   #for 'from direct.stdpy.file import open', this 'open' is panda3d opereation and not the standard python operation
   
    global _current_index #I hate python below 3
    _current_index = 0 #current index of the command
    
    
    io_reader = StringIO(fileHandle.read())
    
    fileHandle.close()
    
    io_reader.seek(0)
    loaded_list = []
    global _current_command   #虽然global很讨厌……
    _current_command = None   #当前的命令文字
    global _current_text
    _current_text = None    #当前的文本
    controlAttribs_startswith = ['if ','while ','elif ','end ','mark ','mark:']
    controlAttribs_equal = ['else','end']
    
    def push_current():
        global _current_command   #如果是python3.0以上在这里用nonlocal就好了……
        global _current_text
        global _current_index
        '''将当前命令文本加入到loaded_list末尾'''
        if not _current_command and not _current_text:
            _current_command = None
            _current_text = None
            return
        else:
            loaded_list.append(StoryCommand(command = _current_command, text = _current_text,index= _current_index, fileLoc= fileloc))
            #print (_current_index,fileloc,_current_text,_current_command)
            _current_index += 1 
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
                _stripedcc = _current_command.strip()
                
                #There should be no text in control parts so it it is an control part then push
                for attr in controlAttribs_startswith:
                    if _stripedcc.startswith(attr):
                        push_current()
                for attr in controlAttribs_equal:
                    if _stripedcc == attr:
                        push_current()
                
                
            else:    #于是就剩下是文本的情况
                if _current_text:
                    _current_text += '\n'
                else: _current_text = ''
                adding = line_raw.rstrip()
                if adding.startswith('__'):
                    _current_text += ' ' #用一个空格代替空行嗯
                else: _current_text += adding
            
    _lsdLock.release()
    return loaded_list
       

    
    

        