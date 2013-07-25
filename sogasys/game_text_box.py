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
游戏文本显示器类
继承自Panda3D的DirectFrame
@author: Windy Darian (大地无敌)
'''
import math

from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from direct.interval.LerpInterval import LerpFunc

import runtime_data
    

    
class GameTextBoxBase(DirectFrame):
    '''The base type of a game text box,
    you can inherit this to develop various game text box
    '''
    def __init__(self,parent):
        
        DirectFrame.__init__(self, #parent,
                            parent,
                            #borderWidth = ( 0, 0 ),
                            #relief = DGG.FLAT,
                            #frameSize = (-1,1,-0.3,0.3),
                            #frameColor = (1,1,1,1),
                            #borderWidth = ( .01, .01),
                            )
    
    def destroy(self, *args, **kwargs):
        return DirectFrame.destroy(self, *args, **kwargs)
        
    def pushText(self, text, speaker = None, continuous = False, text_speed = runtime_data.game_settings['text_speed']):
        pass
    
    def getIsWaiting(self):
        '''得到文本框是否在等待
        如果等待完毕的话，一般情况下点鼠标就会进入下一步操作
        否则是快速完毕
        默认会总是返回False，如果要实现打字机效果则覆载。
        '''
        return False
    
    def setTextBoxStyle(self,style):
        '''inherit this to define what to do in @textboxstyle -style (.sogal script) command'''
        pass
    
    def paragraphSparator(self):
        '''inherit this to define what to do in @p (.sogal script) command'''
        pass
    
    def setTextBoxProperty(self,propname,value):
        '''inherit this to define what to do in @textbox -propname -content (.sogal script) command'''
        pass
    
    def applyTextBoxProperties(self):
        '''textbox apply'''
        pass
    
    def input(self,inputType):
        pass
    
class GameTextBoxStyle(object):
    '''表示对话框种类的枚举集合
    仅用于枚举 Enum only
    '''
    
    Normal = 0
    Large = 1
    
    """
    @property
    def Normal(self):
        '''表示普通对话框的枚举属性'''
        return 0
    
    @property
    def Large(self):
        '''表示大型对话框的枚举属性'''
        return 1
    """
class GTBI(object):
    ''' 'Game Text Box Input' The enum set of GameTextBox
    '''
    #If current text is not finished, then finish current text,
    #else go next
    DEFAULT = 0
    
    #Make the text box ready for next command
    NEXT = 1

    #Toggle auto-play
    TAUTO = 2
    
    #Toggle skip mode
    TSKIP = 3
    

class GameTextBox(GameTextBoxBase):
    '''游戏文本显示器类  Main displayer of current game text.
        继承自Panda3D的DirectFram
    Attributes:
        currentText: A string that includes current game text
        currentSpeaker: A string that represents the speaker
        textFont: The font of the text
        properties: Properties of the text box. 
    '''
    
    currentText = "" 
    currentSpeaker = ""
    newText = None
    existingText = None
 
    
    textfont = None
        
    properties = {'background_color' : (36/255.0,195/255.0,229/255.0,0.3),
                  'arrow_color' : (1,1,1,1),
                  'arrow_scale' : 0.08,
                  'arrow_rightspace' : 0.18,
                  'foreground_color' : (1,1,1,1),
                  'normal_background_image':None,
                  'normal_height': 0.6,
                  'normal_width': 2.6666667,
                  'normal_pos': (0,-0.65),
                  'normal_name_pos' : (0.14,-0.12),
                  'normal_text_pos' : (0.25,-0.25),
                  'normal_text_scale' : 0.09,
                  'normal_name_scale' : 0.07,
                  'normal_text_wrap' : 24,
                  'large_background_image':None,
                  'large_height': 1.9,
                  'large_width' :2.3,
                  'large_pos': (0,0),
                  'large_text_pos': (0.18,-0.25),
                  'large_text_scale' : 0.08,
                  'large_name_scale' : 0.06,
                  'large_text_wrap' : 24,
                }
    _normal_speakerLabel = None
    _normal_textLabel = None
    _large_label = None
    
    _frame = None
    _textArrow = None
    
    
    _typerLerpInterval = None
    
    _isWaitingForUser = False
    
    def __init__(self,parent,style = GameTextBoxStyle.Normal,currentData = None):
        '''
        Constructor
        '''
        
        self.textFont = loader.loadFont('fonts/DroidSansFallbackFull.ttf') # @UndefinedVariable
        self.textFont.setPixelsPerUnit(60)
        self.textFont.setPageSize(512,512)
        self.textFont.setLineHeight(1.2)
        
        GameTextBoxBase.__init__(self, parent = parent)
        
        if runtime_data.RuntimeData.gameTextBox_properties:
            self.properties = runtime_data.RuntimeData.gameTextBox_properties
        else: runtime_data.RuntimeData.gameTextBox_properties = self.properties

    
        self._currentStyle = style
       
        
        self.applyStyle()
        
        if currentData:
            if currentData[0]:
                self.existingText = currentData[0]
                self.currentText = currentData[0]
                if self.currentTextLabel:
                    self.currentTextLabel.setText(currentData[0])
                    self._isWaitingForUser = True
                    self.generateArrow()
            if currentData[1]:
                self.currentSpeaker = currentData[1]
                if self._normal_speakerLabel:
                    self._normal_speakerLabel.setText(currentData[1])
    
    def generateArrow(self):
        if not self._textArrow: 
            arrow = loader.loadModel('models/text_arrow/text_arrow.egg')  # @UndefinedVariable
            arrow.reparentTo(self._frame)
            arrow.setColor(self.properties['arrow_color'])
            arrow.setScale(self.properties['arrow_scale'])
            width = 2.0
            if self._currentStyle == GameTextBoxStyle.Normal:
                width = self.properties['normal_width']
            elif self._currentStyle == GameTextBoxStyle.Large:
                width = self.properties['large_width']
            arrow.setPos(width/2-self.properties['arrow_rightspace'],
                         0,
                         self.currentTextLabel.textNode.getLowerRight3d()[2]-0.03)
            self._textArrow = arrow
    
            
    def quickFinish(self):
        '''Finish the current text typer quickly
        '''
        if self._typerLerpInterval:
            self._typerLerpInterval.finish()

    def destroyElements(self):
        self.currentText = ''
        self.existingText = ''
        self.currentSpeaker = None
        self.newText = ''
        if self._typerLerpInterval:
            if not self._typerLerpInterval.isStopped():
                self._typerLerpInterval.finish()
        
        if self._textArrow:
            self._textArrow.detachNode()
            self._textArrow = None
        
        if self._normal_textLabel:
            self._normal_textLabel.destroy()
            self._normal_textLabel = None
            
        if self._normal_speakerLabel:
            self._normal_speakerLabel.destroy()
            self._normal_speakerLabel = None
            
        if self._frame:
            self._frame.destroy()
            self._frame = None
            
        if self._large_label:
            self._large_label.destroy()
            self._large_label = None
            

        
    def destroy(self, *args, **kwargs):
        self.destroyElements()
        return GameTextBoxBase.destroy(self, *args, **kwargs)
 
    def clearText(self):
        '''make current text empty'''
        if self._typerLerpInterval:
            if not self._typerLerpInterval.isStopped():
                self._typerLerpInterval.finish()
        self.currentText = ''
        self.existingText = ''
        self.currentSpeaker = None
        self.newText = ''
        
        if self.currentTextLabel:
            self.currentTextLabel.setText('')
        if self._currentStyle == GameTextBoxStyle.Normal and self._normal_speakerLabel:
            self._normal_speakerLabel.setText('')
            
        
    
    def pushText(self, text, speaker = None, continuous = False,text_speed = runtime_data.game_settings['text_speed']):
        '''添加文字
        进行判断并改变文字
        parameters:
            speaker: A string contains the speaker's name. (None means no speaker)
        '''
        #The text is necessary
        if not text:
            return
        
        self._isWaitingForUser = True
        
        if self._currentStyle == GameTextBoxStyle.Normal:
            if not continuous:
                self.currentText = ""
            else:
                self.currentText = self.currentText.rstrip('\n')
        elif self._currentStyle == GameTextBoxStyle.Large:
            if not continuous:
                if self.currentText:
                    self.currentText += '\n'
            else:
                self.currentText = self.currentText.rstrip('\n')
            
       

        if continuous:    #When continuous, ignore the speaker
            speaker = None  
        else:
            self.currentSpeaker = speaker
        
       
        
        if self._currentStyle == GameTextBoxStyle.Normal:
            if speaker:
                self._normal_speakerLabel.setText(self.currentSpeaker)
            else:
                self._normal_speakerLabel.setText('')
        elif self._currentStyle == GameTextBoxStyle.Large:
            if speaker:
                self.currentText += '\1name\1' + self.currentSpeaker + '\n\2'
                
        self.existingText = self.currentText
        
        '''    #WHY did i use StringIO? 脑洞系列
        textIO = StringIO(text)
        textIO.seek(0)
        finished = False
        while not finished:
            line = textIO.readline()
            if line:
                self.currentText += line
                #self.currentTextWithoutSpeaker += line 
            else: 
                finished = True
        '''
        self.currentText += text
        self.newText = text
        
        #This is *very* useful
        print(self.newText)
        
        #TODO: 大文本框的显示、打字机效果、渐隐效果
        if text:
            if text_speed != 0:
                duration = float(len(self.newText))/text_speed
            else: duration = 0.0
        
            self._typerLerpInterval = LerpFunc(self.showTextStep,duration = duration)
            self._typerLerpInterval.start()    #原来这里还可以乘算速度的！
    
    def showTextStep(self,lerp_value):
        '''The text typer step. lerp_Value == 1 means the text is completely typed out
        '''
        if not self.currentTextLabel:
            return
        
        text = self.existingText + self.newText[0:int(math.floor((len(self.newText)-1)*lerp_value))]
        self.currentTextLabel.setText(text)
        
        if lerp_value < 1:
            if self._textArrow:
                self._textArrow.detachNode()
                self._textArrow = None
        elif not self._textArrow: 
            self.generateArrow()
            
    
        
        
    #properties
    
    _currentStyle = None
    @property
    def currentStyle(self):
        '''Style of this box
        '''
        return self._currentStyle
    
    @property
    def currentTextLabel(self):
        '''current text label
        '''
        if self._currentStyle == GameTextBoxStyle.Normal:
            return self._normal_textLabel
        elif self._currentStyle == GameTextBoxStyle.Large:
            return self._large_label
    
    def applyStyle(self):
        '''套用风格 Apply style setting.
        override this to apply your own style
        '''
#        窝才想起来这是引用不是浅拷贝……所以构造函数中运行这个就能同步runtime_data了lol
#         if runtime_data.RuntimeData.gameTextBox_properties:  
#             self.properties = runtime_data.RuntimeData.gameTextBox_properties
#         else: runtime_data.RuntimeData.gameTextBox_properties = self.properties
        
        self.destroyElements()
        
        st = self._currentStyle
        
        if st == GameTextBoxStyle.Normal:
            height = self.properties['normal_height']
            width = self.properties['normal_width']
            
            
            self._frame = DirectFrame(
                    parent      = self,
                    frameSize   = (-width/2.0,width/2.0,-height/2.0,height/2.0),
                    frameColor  = self.properties['background_color'],
                    )
            
            self._normal_speakerLabel = OnscreenText(parent = self._frame
                                      , text = self.currentText
                                      , font = self.textFont
                                      , fg = self.properties['foreground_color']
                                      , mayChange = True  # @UndefinedVariable
                                      , align = TextNode.ALeft#@UndefinedVariable
                                      , scale = self.properties['normal_name_scale']
                                      )  
            
            self._normal_textLabel = OnscreenText(parent = self._frame
                                      , text = self.currentText
                                      , font = self.textFont
                                      , fg = self.properties['foreground_color']
                                      , mayChange = True  # @UndefinedVariable
                                      , align = TextNode.ALeft#@UndefinedVariable
                                      , scale = self.properties['normal_text_scale']
                                      )  
            

            self.setPos(self.properties['normal_pos'][0],0,self.properties['normal_pos'][1])
            
            
            self._normal_speakerLabel.setPos(-width/2.0 + self.properties['normal_name_pos'][0], 
                                          height/2.0 + self.properties['normal_name_pos'][1])
            
            self._normal_textLabel.setPos(-width/2.0 + self.properties['normal_text_pos'][0], 
                                          height/2.0 + self.properties['normal_text_pos'][1])
            
            self._normal_textLabel.setShadow((0.1,0.1,0.1,0.5))
            self._normal_speakerLabel.setShadow((0.1,0.1,0.1,0.5))
            self._normal_textLabel.textNode.setTabWidth(1.0)
            self._normal_textLabel.textNode.setWordwrap(self.properties['normal_text_wrap'])
            
            
        elif st == GameTextBoxStyle.Large:
            
            nameprops = TextProperties()  # @UndefinedVariable
            nameprops.setTextScale(self.properties['large_name_scale']/self.properties['large_text_scale'])
            TextPropertiesManager.getGlobalPtr().setProperties("name", nameprops)  # @UndefinedVariable
            
            height = self.properties['large_height']
            width = self.properties['large_width']
              
            self._frame = DirectFrame(
                    parent      = self,
                    frameSize   = (-width/2.0,width/2.0,-height/2.0,height/2.0),
                    frameColor  = self.properties['background_color'],
                    )
            
            self._large_label = OnscreenText(parent = self._frame
                                      , text = self.currentText
                                      , font = self.textFont
                                      , fg = self.properties['foreground_color']
                                      , mayChange = True  # @UndefinedVariable
                                      , align = TextNode.ALeft#@UndefinedVariable
                                      , scale = self.properties['large_text_scale']
                                      )  
            

            self.setPos(self.properties['large_pos'][0],0,self.properties['large_pos'][1])
            
            
            
            self._large_label.setPos(-width/2.0 + self.properties['large_text_pos'][0], 
                                          height/2.0 + self.properties['large_text_pos'][1])
            
            self._large_label.setShadow((0.1,0.1,0.1,0.5))
            self._large_label.textNode.setTabWidth(1.0)
            self._large_label.textNode.setWordwrap(self.properties['large_text_wrap'])

    def setTextBoxStyle(self, style):
        if style.strip() == 'normal':
            self._currentStyle = GameTextBoxStyle.Normal
        elif style.strip() == 'large':
            self._currentStyle = GameTextBoxStyle.Large
        else: print('Unknown style: ' + str(style))
        self.applyStyle()
            

    def paragraphSparator(self):
        if self._currentStyle == GameTextBoxStyle.Large:
            self.clearText()

    def setTextBoxProperty(self, propname, value):
        runtime_data.RuntimeData.gameTextBox_properties[propname] = value

    def applyTextBoxProperties(self):
        self.applyStyle()
       
    def input(self, inputType = GTBI.DEFAULT):
        '''Do as the input'''
        if inputType == GTBI.DEFAULT:
            if not self.getIsWaitingForText():
                self._isWaitingForUser = False
            else:
                self.quickFinish()
                
        elif inputType == GTBI.NEXT:
            self._isWaitingForUser = False
            if self.getIsWaitingForText():
                self.quickFinish()
            
        #TODO: 自动播放功能实现
        #TODO: 快进/Skip功能实现 
            
    def getIsWaitingForText(self):
        is_waiting = False
        if self._typerLerpInterval and self._typerLerpInterval.isPlaying():
            is_waiting = True
        
        return is_waiting
    
    def getIsWaitingForUser(self):
        return self._isWaitingForUser
    
    def getIsWaiting(self):
        '''Inherited from GameTextBoxBase
        Get whether the text typer is unfinished
        '''
        return self.getIsWaitingForText() or self.getIsWaitingForUser()


        


        