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
Created on Apr 2, 2013
The moudle implements an base class for sogal forms (in-game window)
@author: Windy Darian
'''
import operator

from panda3d.core import NodePath
from direct.showbase.DirectObject import DirectObject

from direct.interval.LerpInterval import LerpFunc,LerpPosInterval
from direct.interval.FunctionInterval import Func
from direct.interval.IntervalGlobal import Sequence,Parallel


def _modifyAlphaScale(value,nodePath):
    '''used in fadeing style'''
    nodePath.setAlphaScale(value)

class SogalForm(NodePath, DirectObject):
    '''Sogal form base class
    make self a NodePath under aspect
    '''
    
    def __init__(self, pos = (0,0,0), fading = False, fading_position_offset = (0,0,0), fading_duration = 0.5  ):
        '''if fading enabled, it will apply a fading effect on show()&hide()'''
        self.__fading = fading
        self.__fadingPositionOffset = fading_position_offset
        self.__fadingDuration = fading_duration
        self.__originPos = pos
        self.__currentInterval = None
        
        
        NodePath.__init__(self,self.__class__.__name__)
        NodePath.hide(self)
        self.setPos(pos)
        self.reparentTo(aspect2d)  # @UndefinedVariable
        
    
    def destroy(self):
        '''Call this method to destroy the form'''
        if self.__currentInterval:
            self.__currentInterval.pause
        self.ignoreAll()
        self.removeNode()
        self.removeFocus()

        
    def show(self):
        if not (self.__fading and self.__fadingDuration):
            NodePath.show(self)
            self.requestFocus()
        else:
            NodePath.show(self)
            self.requestFocus()
            if self.__currentInterval:
                self.__currentInterval.pause()
            pos = tuple(map(operator.add,self.__originPos,self.__fadingPositionOffset))
            self.__currentInterval = Sequence(Parallel(LerpFunc(_modifyAlphaScale,self.__fadingDuration,0,1,blendType = 'easeOut',extraArgs = [self]),
                                                       LerpPosInterval(self,self.__fadingDuration,
                                                                       self.__originPos,
                                                                       pos,
                                                                       blendType = 'easeOut'),
                                              )
                                     )
            self.__currentInterval.start()
            
    
    def hide(self):
        if not (self.__fading and self.__fadingDuration):
            NodePath.hide(self)
            self.removeFocus()
        else:
            #self.removeFocus()
            if self.__currentInterval:
                self.__currentInterval.pause()
            endpos = tuple(map(operator.add,self.__originPos,self.__fadingPositionOffset))
            self.__currentInterval = Sequence(Parallel(LerpFunc(_modifyAlphaScale,self.__fadingDuration,1,0,blendType = 'easeIn',extraArgs = [self]),
                                                      LerpPosInterval(self,self.__fadingDuration,
                                                                      endpos,
                                                                      self.__originPos,
                                                                      blendType = 'easeIn'),
                                                     ),
                                              Func(NodePath.hide,self),
                                              Func(self.removeFocus)
                                             )
            self.__currentInterval.start()
            
    def setPos(self, *args, **kwargs):
        if args:
            self.__originPos = args        
        return NodePath.setPos(self, *args, **kwargs)

        
    def requestFocus(self):
        '''let the game know this form want focus'''
        messenger.send('request_focus',[self])  # @UndefinedVariable
        
    def removeFocus(self):
        '''let the game know this form want to remove focus'''
        messenger.send('remove_focus',[self])  # @UndefinedVariable
        
    def hasFocus(self):
        return base.hasFocus(self)  # @UndefinedVariable
    
    def focused(self):
        '''Define what to do when a subclass object gets focus here'''
        pass
        
    def defocused(self):
        '''Define what to do when a subclass object loses focus here'''
        pass        