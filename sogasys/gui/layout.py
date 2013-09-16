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
from direct.gui.DirectFrame import DirectFrame



def getSize(obj):
    '''
    Returns the size of an object.
    For a direct frame the result is the frameSize (left, right, bottom, top),
    for Sogal GuiElement result is (0, width, 0, height)
    and for normal NodePath and other object types it returns (0,0,0,0)
    
    '''
    if isinstance(obj, DirectFrame):
        size = obj['frameSize']
        sx = obj.getSx()
        sz = obj.getSz()
        size = (size[0]*sx, size[1]*sx, size[2]*sz, size[3]*sz)
        return size
    #TODO: Support for GuiElement
    elif isinstance(obj, NodePath):
        return (0, 0, 0, 0)
    else:
        return (0, 0, 0, 0)

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
        return self._itemlist[i:j]

    def __setslice__(self, i, j, value):
        self._itemlist[i:j] = value
        self.resort()
        
        
class HLayout(LayoutBase):
    '''horizontal layout'''
    
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
        size = getSize(directobj)
        if previous:
            pSize = getSize(previous)   #size of the provious object
            directobj.setPos(previous.getPos()[0] +
                             pSize[1] +
                             self.__margin -
                             size[0]
                           ,0,0)
        else:
            directobj.setPos(-size[0],0,0)
            
     
    def getMargin(self):
        return self.__margin
    
    def setMargin(self, value):
        self.__margin = value
        self.resort()
        
        
class VLayout(LayoutBase):
    '''vertical layout'''
    
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
        size = getSize(directobj)
        if previous:
            pSize = getSize(previous)
            directobj.setPos(0,0,previous.getPos()[2] +
                                 pSize[2] -
                                 self.__margin -
                                 size[3])
        else:
            directobj.setPos(0,0,-size[3])
            
    def getMargin(self):
        return self.__margin
    
    def setMargin(self, value):
        self.__margin = value
        self.resort()
        
"""      
#Deprecated
  
class HLayOut(LayoutBase):
    '''horizontal layout for direct objects '''
    
    def __init__(self,parent = None,margin = .5):
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
            directobj.setPos(previous.getPos()[0] + self.__margin,0,0)
        else:
            directobj.setPos(0,0,0)
            
            
    def getMargin(self):
        return self.__margin
    
    def setMargin(self, value):
        self.__margin = value
        self.resort()
        
class VLayout(LayoutBase):
    '''vertical layout for direct objects'''
    
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
            directobj.setPos(0,0,previous.getPos()[2] - self.__margin)
        else:
            directobj.setPos(0,0,0)
            
    def getMargin(self):
        return self.__margin
    
    def setMargin(self, value):
        self.__margin = value
        self.resort()
    
"""        
    
"""       
class DirectHLayout(LayoutBase):
    '''horizontal layout for direct objects
    Specially for DirectObjects for it can read its frame size  
    '''
    
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
            
     
    def getMargin(self):
        return self.__margin
    
    def setMargin(self, value):
        self.__margin = value
        self.resort()
        
        
class DirectVLayout(LayoutBase):
    '''vertical layout for direct objects
    Specially for DirectObjects for it can read its frame size  
    '''
    
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
        


"""        
