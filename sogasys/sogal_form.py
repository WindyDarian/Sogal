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

from panda3d.core import NodePath,PGButton,MouseButton
from direct.showbase.DirectObject import DirectObject
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectDialog import DirectDialog

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
    
    def __init__(self,
                 pos = (0,0,0),
                 fading = False,
                 fading_position_offset = (0,0,0),
                 fading_duration = 0.5, 
                 backgroundImage = None, 
                 backgroundColor = None,
                 enableMask = False,
                 ):
        '''if fading enabled, it will apply a fading effect on show()&hide()
        Important Attributes:
        enableMask: This creates a big transparent plane (DirectButton) off screen so the directGui below won't be
        clicked (However due to this trick we won't be able to accept mouse events (I have paid back 'mouse3' by 
        self.__maskClick))
        '''
        self.__fading = fading
        self.__fadingPositionOffset = fading_position_offset
        self.__fadingDuration = fading_duration
        self.__originPos = pos
        self.__currentInterval = None
        self.__maskEnabled = enableMask
        
        self.__mask = None
        if self.__maskEnabled:
            self.__mask = DialogMask()
            #self.__mask = DirectButton(parent = aspect2d, frameColor =(1,1,1,0.1), relief = DGG.FLAT,commandButtons = [DGG.RMB],command = self.__maskClick)
            self.__mask.hide()
        NodePath.__init__(self,self.__class__.__name__)
        
        
        
        #self.accept('window-event', self.windowResize)
        
        if backgroundImage or backgroundColor:
            pass
            #TODO: you know~
        
        NodePath.hide(self)
        self.setPos(pos)
        self.reparentTo(aspect2d)  # @UndefinedVariable
    """
    def __maskClick(self,button = 2):
        '''Cuz the mask is a DirectButton it will interrupt screen mouse events so ...'''
        
        #FIXME: make the mask accept left and middle buttons
        if button == 0: #Left mouse button
            messenger.send('mouse1')
        elif button == 1: #Middle button
            messenger.send('mouse2')
        elif button == 2: #Right button
            messenger.send('mouse3')
    """ 
        

    
    def destroy(self):
        '''Call this method to destroy the form'''
        if self.__currentInterval:
            self.__currentInterval.pause
        if self.__mask:
            self.__mask.destroy()
        self.ignoreAll()
        self.removeNode()
        self.removeFocus()

        
    def show(self):
        if self.__mask:
            self.__mask.reparentTo(aspect2d,sort = self.getSort())
            self.__mask.show()
            self.reparentTo(aspect2d,sort = self.getSort())
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
                                              Func(self.removeFocus),
                                             )
            if self.__mask:
                self.__currentInterval.append(Func(self.__mask.hide))
            self.__currentInterval.start()
            
    def setPos(self, *args, **kwargs):
        NodePath.setPos(self, *args, **kwargs)
        self.__originPos = NodePath.getPos(self)

        
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
    




class DialogMask(DirectButton):
    '''used to generate a full-screen mask to prevent button-clicking below the focused window/dialog
    Added some tricks to make panda3d mouse events still available
    '''
    B1PRESS = PGButton.getPressPrefix() + MouseButton.one().getName() + '-'  
    B2PRESS = PGButton.getPressPrefix() + MouseButton.two().getName() + '-'  
    B3PRESS = PGButton.getPressPrefix() + MouseButton.three().getName() + '-'
    B4PRESS = PGButton.getPressPrefix() + MouseButton.four().getName() + '-'
    B5PRESS = PGButton.getPressPrefix() + MouseButton.five().getName() + '-'
    WHEELUP = PGButton.getReleasePrefix() + MouseButton.wheelUp().getName() + '-'
    WHEELDOWN = PGButton.getReleasePrefix() + MouseButton.wheelDown().getName() + '-'
    WHEELLEFT = PGButton.getReleasePrefix() + MouseButton.wheelLeft().getName() + '-'
    WHEELRIGHT = PGButton.getReleasePrefix() + MouseButton.wheelRight().getName() + '-'
    B1RELEASE = PGButton.getReleasePrefix() + MouseButton.one().getName() + '-'  
    B2RELEASE = PGButton.getReleasePrefix() + MouseButton.two().getName() + '-'  
    B3RELEASE = PGButton.getReleasePrefix() + MouseButton.three().getName() + '-'
    B4RELEASE = PGButton.getReleasePrefix() + MouseButton.four().getName() + '-'
    B5RELEASE = PGButton.getReleasePrefix() + MouseButton.five().getName() + '-'
    
    def __init__(self):
        DirectButton.__init__(self,parent = aspect2d, frameColor =(1,1,1,0), relief = DGG.FLAT,commandButtons = [])
        self.accept('window-event', self.windowResize)
        self.windowResize(None)
        #trick: make this re-throw mouse events
        self.bind(self.B1PRESS, self.rethrowEvent,['mouse1'])
        self.bind(self.B2PRESS, self.rethrowEvent,['mouse2'])
        self.bind(self.B3PRESS, self.rethrowEvent,['mouse3'])
        self.bind(self.B4PRESS, self.rethrowEvent,['mouse4'])
        self.bind(self.B5PRESS, self.rethrowEvent,['mouse5'])
        
        self.bind(self.WHEELUP, self.rethrowEvent, ['wheel_up'])
        self.bind(self.WHEELDOWN, self.rethrowEvent, ['wheel_down'])
        self.bind(self.WHEELLEFT, self.rethrowEvent, ['wheel_left'])
        self.bind(self.WHEELRIGHT, self.rethrowEvent, ['wheel_right'])
        
        self.bind(self.B1RELEASE, self.rethrowEvent,['mouse1-up'])
        self.bind(self.B2RELEASE, self.rethrowEvent,['mouse2-up'])
        self.bind(self.B3RELEASE, self.rethrowEvent,['mouse3-up'])
        self.bind(self.B4RELEASE, self.rethrowEvent,['mouse4-up'])
        self.bind(self.B5RELEASE, self.rethrowEvent,['mouse5-up'])
        
    def windowResize(self,arg):
        #Make this mask fill the screen
        self.reparentTo(aspect2d,sort = self.getSort())
        aspect = base.getAspectRatio()
        if aspect > 1:
            self['frameSize'] = (-aspect,aspect,-1,1)
        elif aspect: 
            hh = 1.0/aspect
            self['frameSize'] = (-1,1,-hh,hh)
            
    def setCommandButtons(self, *args, **kwargs):
        #inherited 
        pass
        
    def rethrowEvent(self,sevent,event):
        messenger.send(sevent)
        
                
    def destroy(self):
        self.ignoreAll()
        
    
    
class SogalDialog(SogalForm):
    '''
    A dialog that derived from SogalForm
    (Which contains a DirectDialog)
    '''
    def __init__(self,pos = (0,0,0),
                      fading = False,
                      fading_position_offset = (0,0,0),
                      fading_duration = 0.5, 
                      backgroundImage = None, 
                      backgroundColor = None,
                      enableMask = True, #NOTE THAT IT IS TRUE BY DEFAULT
                      ):
        SogalForm.__init__(self,
                           pos= pos, 
                           fading= fading, 
                           fading_position_offset= fading_position_offset, 
                           fading_duration= fading_duration,
                           backgroundImage= backgroundImage,
                           backgroundColor= backgroundColor,
                           enableMask = enableMask
                           )
        
        
