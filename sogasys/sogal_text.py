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

import math

from panda3d.core import NodePath,TextNode  # @UnresolvedImport



class SogalText(NodePath):
    '''
    A text label, contains many TextLines
    '''


    def __init__(self,parent = None,text = '',font = None, wordwrap = None):
        '''
        Constructor
        :param parent: parent NodePath
        :param text: text
        :param font: font of the text
        :param wordwrap: set the width when wraping the word (note that )
        '''
        
        self.parent = parent or aspect2d
        
        self.font = font
        self.wordwrap = wordwrap
        self.textlines = []
        
        
        NodePath.__init__('')
        
        self.reparentTo(self.parent)  # @UndefinedVariable
        
            
class TextLine(NodePath):
    '''
    One line of SogalText, contains geom generated by TextNodes
    Text are unable to be changed
    '''
    def __init__(self,parent = None):
        self.parent = parent or aspect2d
        
        NodePath.__init__('line')
        self.reparentTo(self.parent)
        
    def appendWord(self,text):
        pass
                    
            
class Word(object):
    '''
    Entry of a single word added in to the SogalText
    '''
    def __init__(self,text,prop):
        self.text = text
        self.prop = prop