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
Created on Aug 10, 2013
Sogal's text label class
Arrange the text word by word, TextNode by TextNode
@author: Windy Darian (大地无敌)
'''
#TODO: finish this moudle and add make game_text_box use this moudle

import copy

from panda3d.core import NodePath,TextNode  # @UnresolvedImport



class SogalText(NodePath):
    '''
    A text label, contains many TextLines
    '''
    def __init__(self,
                 parent = None,
                 pos = (0,0,0),
                 text = u'',
                 wordwrap = None, 
                 maxRows = None, 
                 spacing = 0,
                 lineSpacing = 0,
                 minLineHeight = 0.5,
                 font = None,
                 fg = (1,1,1,1),
                 scale = 0.07, 
                 shadow = None,
                 shadowOffset = (0.04, 0.04),
                 textScale = None,
                 ):
        '''
        Constructor
        :param parent: parent NodePath
        :param text: text
        :param font: font of the text
        :param wordwrap: set the width when wraping the word (note that )
        :param maxRows: max row of the text
        :param spacing: spacing of words
        :param lineSpacing: spacing of lines
        :param minLineHeight: height of a line when it is empty
        :param fg: foreground color
        :param scale: scale of the text
        :param shadow: shadow color of the text
        :param shadowOffset: shadow offset of the text
        '''
        self.destroyed = False
        self.__parent = parent or aspect2d
        
        self.__font = font
        self.wordwrap = wordwrap
        self.lines = []
        self.spacing = spacing
        self.lineSpacing = lineSpacing
        self.minLineHeight = minLineHeight
        
        self.maxRows = maxRows
        
        self.recordedText = [] #recorder text sections used in backup
        
        NodePath.__init__(self,'')
        self.setScale(scale)
        self.setPos(pos)
        
        self.currentHeight = 0
        
        
        self.reparentTo(self.__parent)  # @UndefinedVariable
        
        self.textMaker = TextNode('textMaker')
        if font:
            self.setFont(font, specNode = None)
        if fg:
            self.setFg(fg, specNode = None)
        if shadow:
            self.setShadow(shadow, shadowOffset, specNode = None)
        if textScale:
            self.setTexScale(textScale,specNode = None)
        
        self.textMaker.setAlign(TextNode.ALeft)
        
        if shadow:
            pass
        if text:
            self.appendText(text)
            
    def destroy(self):
        self.clear()
        if not self.destroyed:
            self.destroyed = True
        self.textMaker = None
        self.recordedText = None
        self.removeNode()
        
    def clear(self):
        self.currentHeight = 0
        for tl in self.lines:
            tl.removeNode()
        self.lines = []
        self.recordedText = []
    
    def setFg(self, fg, specNode = None):
        node = specNode or self.textMaker
        node.setTextColor(fg[0], fg[1], fg[2], fg[3])
        
    def setFont(self,font, specNode = None):
        node = specNode or self.textMaker
        node.setFont(font)
        
    def setShadow(self, shadow, offset = (0.04, 0.04), specNode = None):
        node = specNode or self.textMaker

        if shadow[3] != 0:
            node.setShadowColor(shadow[0], shadow[1], shadow[2], shadow[3])
            node.setShadow(offset)
        else:
            node.clearShadow()
            
    def setTextScale(self, scale , specNode = None):
        node = specNode or self.textMaker
        node.setTextScale(scale)
        
    def setMaxRows(self,maxrows):
        self.maxRows = maxrows
    
    def setWordwrap(self,wordwrap):
        self.wordwrap = wordwrap
        
    def setMinLineHeight(self,minLineHeight):
        self.minLineHeight = minLineHeight
        
    
    
    def appendText(self, text, newLine = False,custom = False, font = None, textScale = 1, fg = (1,1,1,1), 
                 shadow = None, shadowOffset = (0.04, 0.04), **kwargs):
        textprops = dict(text = text,newLine = newLine, custom = custom, font = font, textScale = textScale, fg = fg, 
                 shadow = shadow, shadowOffset = shadowOffset, **kwargs)
        
        self.recordedText.append(textprops)
        
        self.appendStoredText(textprops)
            

            
    def appendStoredText(self,textprops):
        #append a text stored with appendText() or by loading self.recordedText
        text = textprops['text']
        newLine = textprops['newLine']
        custom = textprops['custom']
        if custom:
            textMaker = TextNode('temptextmaker', self.textMaker)
            font = textprops['font']
            if font:
                textMaker.setFont(font)
            textScale = textprops['textScale']
            if textScale:
                textMaker.setTextScale(textScale)
            fg = textprops['fg']
            if fg:
                self.setFg(fg, textMaker)
            shadow = textprops['shadow']
            shadowOffset = textprops['shadowOffset']
            if shadow:
                self.setShadow(shadow, shadowOffset, textMaker)
            
            #prepared to add more props here
            
        else: textMaker = self.textMaker
        
        
        if newLine or not self.lines:
            self.startLine()
        #TODO typer effect
        for word in text:
            self.appendWord(word, tm = textMaker)

            
    def appendWord(self,word,tm = None):
        if word == '\n':
            self.startLine()
            return
        
        textMaker = tm or self.textMaker
        if not self.lines:
            self.startLine()
        
        active_line = self.lines[-1] 
        textMaker.setText(word)
        width = textMaker.getWidth()
        #print 'w=' + str(width)
        height = textMaker.getHeight()
        #print 'h=' + str(height)
        node = textMaker.generate()
        textpath = NodePath('text_path')
        textpath.attachNewNode(node)
        if self.wordwrap:
            if active_line.getTotalWidth() + width > self.wordwrap:
                self.startLine()
                active_line = self.lines[-1]
        
        active_line.append(textpath, width, height,self.spacing)
        active_line.setPos(0,0,-(self.currentHeight + active_line.getLineHeight()) )
        #active_line.setPos(0,0,-self.currentHeight )
          
    def startLine(self):
        if self.lines:
            self.currentHeight += self.lines[-1].getLineHeight() + self.lineSpacing 
        line = TextLine(parent = self, height = self.minLineHeight)
        line.setPos(0,0,-self.currentHeight)
        self.lines.append(line)
    
    def removeNode(self, *args, **kwargs):
        return NodePath.removeNode(self, *args, **kwargs)
            
    def getCurrentText(self):
        return self.recordedText
    
    def getCopiedText(self):
        return copy.deepcopy(self.recordedText)
    
    def loadRecordedText(self,recorded):
        for section in recorded:
            self.appendStoredText(section)
        self.recordedText = copy.copy(recorded)
            
    def getNewText(self):
        if self.recordedText:
            return self.recordedText[0]['text']
        return ''
        
    def getEndPos(self):
        if self.lines:
            return (self.lines[-1].getEndPos()[0],0 , -(self.currentHeight + self.lines[-1].getLineHeight()))
        else: return (0,0,0)
        
    def hasContent(self):
        "get if this text label empty"
        return bool(self.lines)
        
    

            
class TextLine(NodePath):
    '''
    One line of SogalText, contains geom generated by TextNodes
    Text are unable to be changed
    '''
    def __init__(self,parent = None, height = 0):
        self.parent = parent or aspect2d
        
        NodePath.__init__(self,'line')
        self.reparentTo(self.parent)
        
        self.currentPtr = (0,0,0)
        self.lineHeight = height
        self.lineWidth = 0
        
        self.items = [] #each word/character is a NodePath
        
    def removeNode(self, *args, **kwargs):
        del self.items
        return NodePath.removeNode(self, *args, **kwargs)
        
    def append(self,text,width,height,spacing = 0):
        '''Add a NodePath that contains a generated text geom
        This method is called by SogalText
        '''
        self.items.append(text)
        text.reparentTo(self)
        text.setPos(self.currentPtr)
        self.lineWidth = self.currentPtr[0] + width
        self.lineHeight = max(height, self.lineHeight)
        self.currentPtr = (self.lineWidth + spacing, 0, 0)
        
    def getLineWidth(self):
        return self.lineWidth
    
    def getLineHeight(self):
        return self.lineHeight
    
    def getTotalWidth(self):
        return self.currentPtr[0]
    
    def getEndPos(self):
        return self.currentPtr
    

            
