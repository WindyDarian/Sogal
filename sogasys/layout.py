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
Created on April 4, 2013
Layout classes
@author: Windy Darian (大地无敌)
'''
from panda3d.core import NodePath

class LayoutBase(NodePath):
    def __init__(self, parent = None):
        NodePath.__init__(self,self.__class__.__name__)
        if not parent:
            self.reparentTo(aspect2d)  # @UndefinedVariable
        else: self.reparentTo(parent)
        self._itemlist = []
        
    def append(self, directobj):
        '''inherit this to append new object'''
        pass
    
    def resort(self):
        '''inherit this to resort when needed'''
        pass
        
    def __iter__(self):
        return iter(self._itemlist)
    
    def __getitem__(self, index):
        return self._itemlist[index]
    
    def __setitem__(self, index, val):
        self._itemlist[index] = val
        self.resort()
        
    def __delitem__(self, index):
        '''note that the object is not destroyed'''
        del self._itemlist[index]
        self.resort()
        
    def __getslice__(self, i, j):
        print i,j
        return self._itemlist[i:j]

    def __setslice__(self, i, j, value):
        self._itemlist[i:j] = value
        self.resort()
    

class HLayout(LayoutBase):
    '''horizontal layout for direct objects '''
    
    def __init__(self,parent = None,margin = .05):
        LayoutBase.__init__(self, parent)
        self.__margin = margin
        
    def append(self, directobj):
        directobj.reparentTo(self)
        if not self._itemlist:
            self._applyLayout(directobj, None)
        else:
            self._applyLayout(directobj, self._itemlist[-1])
        self._itemlist.append(directobj)
        
    def resort(self):
        last = None
        for item in self:
            self._applyLayout(item, last)
            last = item
        
    def _applyLayout(self,directobj,previous):
        if previous:
            directobj.setPos(previous.getPos()[0] +
                             previous['frameSize'][1] * previous.getSx() +
                             self.__margin -
                             directobj['frameSize'][0] * directobj.getSx()
                           ,0,0)
        else:
            directobj.setPos(-directobj['frameSize'][0] * directobj.getSx(),0,0)
        #print str(self.getTightBounds()) #FIXME: make this not (0,0,0)s and make it able to contain another Layout or any NodePath
            
            
    def getMargin(self):
        return self.__margin
    
    def setMargin(self, value):
        self.__margin = value
        self.resort()
        
        
class VLayout(LayoutBase):
    '''vertical layout for direct objects '''
    
    def __init__(self,parent = None,margin = .05):
        LayoutBase.__init__(self, parent)
        self.__margin = margin
        
    def append(self, directobj):
        directobj.reparentTo(self)
        if not self._itemlist:
            self._applyLayout(directobj, None)
        else:
            self._applyLayout(directobj, self._itemlist[-1])
        self._itemlist.append(directobj)
        
    def resort(self):
        last = None
        for item in self:
            self._applyLayout(item, last)
            last = item
        
    def _applyLayout(self,directobj,previous):
        if previous:
            directobj.setPos(0,0,previous.getPos()[2] +
                                 previous['frameSize'][2] * previous.getSz() -
                                 self.__margin -
                                 directobj['frameSize'][3] * directobj.getSz())
        else:
            directobj.setPos(0,0,-directobj['frameSize'][3] * directobj.getSz())
            
    def getMargin(self):
        return self.__margin
    
    def setMargin(self, value):
        self.__margin = value
        self.resort()
    
        
