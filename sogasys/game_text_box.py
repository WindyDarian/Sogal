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
import math,copy

from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText



import runtime_data 
import color_themes
from sogal_text import SogalText
    
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

class GameTextBox(DirectObject, NodePath):
    '''游戏文本显示器类  Main displayer of current game text.
        继承自Panda3D的DirectFram
    Attributes:
        currentText: A list that includes current game text (see sogal_text's recordedText)
        currentSpeaker: A string that represents the speaker
        textFont: The font of the text
        properties: Properties of the text box. 
    '''
    

    
    def __init__(self):
        '''
        Constructor
        '''
        self.currentText = []
        self.currentSpeaker = ""
        self.newText = None
        self.textfont = None
        self.properties = copy.deepcopy(base.getStyle('textbox'))
        self._normal_speakerLabel = None
        self._normal_textLabel = None
        self._large_label = None
        self._frame = None
        self._textArrow = None
        self.__namescale = None
        
        NodePath.__init__(self, 'GameTextBox')
        self.reparentTo(aspect2d)
        self.reload()
    
    def presave(self):
        runtime_data.RuntimeData.current_text = [self.currentText, self.currentSpeaker]
                    
    def reload(self):
        if runtime_data.RuntimeData.gameTextBox_properties: #this creates an reference
            self.properties = runtime_data.RuntimeData.gameTextBox_properties
        else: runtime_data.RuntimeData.gameTextBox_properties = self.properties
        
        self.applyStyle()
        
        if runtime_data.RuntimeData.current_text:
            if runtime_data.RuntimeData.current_text[0]:
                self.currentText = copy.copy(runtime_data.RuntimeData.current_text[0]) 
                if self.currentTextLabel:
                    self.currentTextLabel.loadRecordedText(runtime_data.RuntimeData.current_text[0])
            if runtime_data.RuntimeData.current_text[1]:
                self.currentSpeaker = runtime_data.RuntimeData.current_text[1]
                if self._normal_speakerLabel:
                    self._normal_speakerLabel.setText(runtime_data.RuntimeData.current_text[1])
                    
    def reloadTheme(self):
        self.properties = copy.deepcopy(base.getStyle('textbox'))
        runtime_data.RuntimeData.gameTextBox_properties = self.properties
        self.applyStyle()
    
    def showArrow(self):
        if self._textArrow: 
            if self.currentTextLabel:
                '''
                self._textArrow.setPos(self._frame.getWidth()/2-self.properties['arrow_rightspace'],
                             0,
                             self.currentTextLabel.textNode.getLowerRight3d()[2]-0.03)
                '''
                apos = self._frame.getRelativePoint(self.currentTextLabel, self.currentTextLabel.getEndPos())
                apos = (self._frame.getWidth()/2-self.properties['arrow_rightspace'],
                        0,
                        apos[2])
                self._textArrow.setPos(apos)
            else: self._textArrow.setPos(0,0,0)
            self._textArrow.show()
            
    def hideArrow(self):
        if self._textArrow:
            self._textArrow.hide()
    
            
    def quickFinish(self):
        '''Finish the current text typer quickly
        '''
        if self.currentTextLabel:
            self.currentTextLabel.quickFinish()

    def destroyElements(self):
        self.currentText = []
        self.currentSpeaker = None
        self.newText = ''

        
        if self._textArrow:
            self._textArrow.removeNode()
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
        if self.currentTextLabel:
            self.currentTextLabel.destroy
        if self._frame:
            self._frame.destroy()
            self._frame = None
 
    def clearText(self):
        '''make current text empty'''

        self.currentText = []
        self.currentSpeaker = None
        self.newText = ''
        
        if self.currentTextLabel:
            self.currentTextLabel.clear()
        if self._currentStyle == GameTextBoxStyle.Normal and self._normal_speakerLabel:
            self._normal_speakerLabel.setText('')
            
        
    
    def pushText(self, text, speaker = None, continuous = False, text_speed = None, fadein = None, rate = 1.0):
        '''添加文字
        进行判断并改变文字
        parameters:
            speaker: A string contains the speaker's name. (None means no speaker)
        '''
        if self.currentTextLabel and self.currentTextLabel.isWaiting():
            self.currentTextLabel.quickFinish()
        
        #The text is necessary
        if not text:
            return
        
        text = text.rstrip('\n')
        
        text_speed = (text_speed or base.getStyle('textbox')['text_speed'] or runtime_data.game_settings['text_speed']) * rate
        if fadein is None:
            fadein = base.getStyle('textbox')['text_fadein_duration']
        fadein_style = base.getStyle('textbox')['text_fadein_style']
        
        if self._currentStyle == GameTextBoxStyle.Normal:
            if not continuous:
                self.currentTextLabel.clear()
        elif self._currentStyle == GameTextBoxStyle.Large:
            if not continuous and self.currentTextLabel.hasContent():
                self.currentTextLabel.appendText('\n') #Inserting an empty line
       

        if continuous:    #When continuous, ignore the speaker
            speaker = None  
            #self.currentSpeaker = ''
        else:
            self.currentSpeaker = speaker
        
        if self._currentStyle == GameTextBoxStyle.Normal:
            if not continuous:
                if speaker:
                    self._normal_speakerLabel.setText(self.currentSpeaker) #TODO: use SogalText
                else:
                    self._normal_speakerLabel.setText(' ')
        elif self._currentStyle == GameTextBoxStyle.Large:
            if speaker:
                self.currentTextLabel.appendText(self.currentSpeaker,custom = True, newLine = True, 
                                                 textScale = self.__namescale)
                

        self.newText = text
        
        #This is *very* useful
        print(self.newText)
        
        self.currentTextLabel.appendText(self.newText, speed = text_speed , newLine = (not continuous) , fadein = fadein, 
                                                 fadeinType = fadein_style)
        
        self.currentText = self.currentTextLabel.getCopiedText()
        
        #TODO: FADING TEXT AND TYPER AGAIN

    
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
        
        if self.properties.has_key('style'):
            self.setTextBoxStyle(self.properties['style'])
        else: self.setTextBoxStyle('normal')
            
        st = self._currentStyle
        
        if st == GameTextBoxStyle.Normal:
            height = self.properties['normal_height']
            width = self.properties['normal_width']
            
            
            self._frame = DirectFrame(
                    parent      = self,
                    frameSize   = (-width/2.0,width/2.0,-height/2.0,height/2.0),
                    frameColor  = self.properties['background_color'],
                    )
            
            if self.currentSpeaker:
                speaker = self.currentSpeaker
            else: speaker = ''
            
            self._normal_speakerLabel = OnscreenText(parent = self._frame
                                      , text = speaker
                                      , font = base.textFont
                                      , fg = self.properties['foreground_color']
                                      , mayChange = True  # @UndefinedVariable
                                      , align = TextNode.ALeft#@UndefinedVariable
                                      , scale = self.properties['normal_name_scale']
                                      )  
            
            self._normal_textLabel = SogalText(parent = self._frame,
                                               font = base.textFont,
                                               fg = self.properties['foreground_color'],
                                               scale = self.properties['normal_text_scale'],
                                               shadow = (0.1,0.1,0.1,0.5),
                                               pos = (-width/2.0 + self.properties['normal_text_pos'][0],
                                                      0,
                                                      height/2.0 + self.properties['normal_text_pos'][1]),
                                               wordwrap = self.properties['normal_text_wrap']
                                               )  
            

            self.setPos(self.properties['normal_pos'][0],0,self.properties['normal_pos'][1])
            
            
            self._normal_speakerLabel.setPos(-width/2.0 + self.properties['normal_name_pos'][0], 
                                          height/2.0 + self.properties['normal_name_pos'][1])
    
            self._normal_speakerLabel.setShadow((0.1,0.1,0.1,0.5))
            
            self._normal_textLabel.textMaker.setTabWidth(1.0)
            
            
        elif st == GameTextBoxStyle.Large:
            
           
            self.__namescale = self.properties['large_name_scale']/self.properties['large_text_scale']
            
            height = self.properties['large_height']
            width = self.properties['large_width']
              
            self._frame = DirectFrame(
                    parent      = self,
                    frameSize   = (-width/2.0,width/2.0,-height/2.0,height/2.0),
                    frameColor  = self.properties['background_color'],
                    )
            
            self._large_label = SogalText(parent = self._frame,
                                          font = base.textFont,
                                          fg = self.properties['foreground_color'],
                                          scale = self.properties['large_text_scale'],
                                          shadow = (0.1,0.1,0.1,0.5),
                                          pos = (-width/2.0 + self.properties['large_text_pos'][0],
                                                 0,
                                                 height/2.0 + self.properties['large_text_pos'][1]),
                                          wordwrap = self.properties['large_text_wrap']
                                         )  
            

            self.setPos(self.properties['large_pos'][0],0,self.properties['large_pos'][1])
            
            
    
            
            self._large_label.textMaker.setTabWidth(1.0)
           
        #generate an arrow after text 
        arrow = loader.loadModel('models/text_arrow/text_arrow.egg')  # @UndefinedVariable
        arrow.reparentTo(self._frame)
        arrow.setColor(self.properties['arrow_color'])
        arrow.setScale(self.properties['arrow_scale'])
        width = 2.0
        if self._currentStyle == GameTextBoxStyle.Normal:
            width = self.properties['normal_width']
        elif self._currentStyle == GameTextBoxStyle.Large:
            width = self.properties['large_width']

        self._textArrow = arrow
        self._textArrow.hide()

    def setTextBoxStyle(self, style):
        if style.strip() == 'normal':
            self._currentStyle = GameTextBoxStyle.Normal
        elif style.strip() == 'large':
            self._currentStyle = GameTextBoxStyle.Large
        else: print('Unknown style: ' + str(style))
        self.properties['style'] = style
        
        


    def paragraphSparator(self):
        #if self._currentStyle == GameTextBoxStyle.Large:
        self.clearText()

    def setTextBoxProperty(self, propname, value):
        runtime_data.RuntimeData.gameTextBox_properties[propname] = value

    def applyTextBoxProperties(self):
        self.applyStyle()
       
            
    def getIsWaitingForText(self):
        is_waiting = False
        
        if self.currentTextLabel:
            is_waiting = self.currentTextLabel.isWaiting()
        
        return is_waiting
    
    
    def getIsWaiting(self):
        '''Inherited from GameTextBoxBase
        Get whether the text typer is unfinished
        '''
        return self.getIsWaitingForText()


        


        