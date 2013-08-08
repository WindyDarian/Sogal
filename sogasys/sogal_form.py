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

from panda3d.core import NodePath,PGButton,MouseButton,CardMaker,TransparencyAttrib
from direct.showbase.DirectObject import DirectObject
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText

from direct.interval.LerpInterval import LerpFunc,LerpPosInterval
from direct.interval.FunctionInterval import Func
from direct.interval.IntervalGlobal import Sequence,Parallel,Wait

from layout import DirectHLayout, DirectVLayout
from sogasys.layout import DirectHLayout
from sogasys.color_themes import styles
from direct.interval.MetaInterval import Parallel


def _modifyAlphaScale(value,nodePath):
    '''used in fadeing style'''
    nodePath.setAlphaScale(value)

class SogalForm(NodePath, DirectObject):
    '''Sogal form base class
    make self a NodePath under aspect
    '''
    
    def __init__(self,
                 parent = None,
                 pos = (0,0,0),
                 fading = False,
                 fading_position_offset = (0,0,0),
                 fading_duration = 0.5, 
                 backgroundImage = None, 
                 backgroundColor = None,
                 enableMask = False,
                 noFocus = False,
                 onShowing = None,
                 onHiding = None,
                 onEventExtraArgs = [],
                 ):
        '''if fading enabled, it will apply a fading effect on show()&hide()
        Important Attributes:
        enableMask: This creates a big transparent plane (DirectButton) off screen so the directGui below won't be
                    clicked (However due to this trick we won't be able to accept mouse events (I have paid back 'mouse3' by 
                    self.__maskClick))
        noFocus: if it is true, it doesn't need SogalBase to manage its focus state (it will not affect
                 other Sogalforms' focus state
        '''
        self.__fading = fading
        self.__fadingPositionOffset = fading_position_offset
        self.__fadingDuration = fading_duration
        self.__originPos = pos
        self.__currentInterval = None
        self.__maskEnabled = enableMask
        self.__noFocus = noFocus
        
        self.__onShowing = onShowing
        self.__onHiding = onHiding
        self.__onEventExtraArgs = onEventExtraArgs
        
        self.__mask = None
        if self.__maskEnabled:
            self.__mask = DialogMask()
            #self.__mask = DirectButton(parent = aspect2d, frameColor =(1,1,1,0.1), relief = DGG.FLAT,commandButtons = [DGG.RMB],command = self.__maskClick)
            self.__mask.hide()
        
        self.__backgroundImage = backgroundImage
        self.__backgroundColor = backgroundColor
        self.__bgPath = None
        self.__imagePath = None
        

        
        NodePath.__init__(self,self.__class__.__name__)
        if not parent:
            self.reparentTo(aspect2d)
        else: self.reparentTo(parent)
        
        if self.__backgroundColor:
            self.__bgPath = NodePath('bgPath')
            self.__bgPath.setTransparency(TransparencyAttrib.MAlpha)
            cm = CardMaker('cm')
            cm.setFrameFullscreenQuad()
            cm.setColor(self.__backgroundColor)
            self.__bgPath.attachNewNode(cm.generate())
            self.__bgPath.reparentTo(aspect2d,self.getSort())
            self.__bgPath.hide()
            
        #TODO: backgroundImage
        
        self.setTransparency(TransparencyAttrib.MAlpha)
        
        
        self.accept('window-event', self.windowResize)
        self.windowResize(None)

        NodePath.hide(self)
        self.setPos(pos)
        self.reparentTo(aspect2d)  # @UndefinedVariable
        
    def windowResize(self,arg):
        if self.__bgPath:
            #fill the screen
            aspect = base.getAspectRatio()
            if aspect > 1:
                self.__bgPath.setScale(aspect,0,1)
            elif aspect: 
                self.__bgPath.setScale(1,0,1.0/aspect)

    
    def destroy(self):
        '''Call this method to destroy the form'''
        
        if self.__currentInterval:
            self.__currentInterval.pause
        if self.__mask:
            self.__mask.destroy()
        if self.__bgPath:
            self.__bgPath.removeNode()
        self.ignoreAll()
        self.removeFocus()
        self.removeNode()

        
    def show(self):
        if self.__onShowing:
            self.__onShowing(*self.__onEventExtraArgs)
        
        if self.__mask or self.__bgPath:
            if self.__mask:
                self.__mask.reparentTo(aspect2d,sort = self.getSort())
                self.__mask.show()
            if self.__bgPath:
                self.__bgPath.reparentTo(aspect2d,sort = self.getSort())
                self.__bgPath.show()
        self.reparentTo(self.getParent(),sort = self.getSort())
        if not (self.__fading and self.__fadingDuration):
            NodePath.show(self)
            self.requestFocus()
        else:
            NodePath.show(self)
            self.requestFocus()
            if self.__currentInterval:
                self.__currentInterval.pause()
            pos = tuple(map(operator.add,self.__originPos,self.__fadingPositionOffset))
            
            parallel = Parallel(LerpFunc(_modifyAlphaScale,self.__fadingDuration,0,1,blendType = 'easeOut',extraArgs = [self]),
                                LerpPosInterval(self,self.__fadingDuration,
                                                self.__originPos,
                                                pos,
                                                blendType = 'easeOut')
                                )
            if self.__bgPath:
                parallel.append(LerpFunc(_modifyAlphaScale,self.__fadingDuration,0,1,blendType = 'easeOut',extraArgs = [self.__bgPath]))
            
            self.__currentInterval = Sequence(parallel)
            self.__currentInterval.start()
            
    
    def hide(self):
        if self.__onHiding:
            self.__onHiding(*self.__onEventExtraArgs)
        
        if not (self.__fading and self.__fadingDuration):
            NodePath.hide(self)
            self.removeFocus()
            if self.__mask:
                self.__mask.hide()
            if self.__bgPath:
                self.__bgPath.hide()
        else:
            #self.removeFocus()
            if self.__currentInterval:
                self.__currentInterval.pause()
            endpos = tuple(map(operator.add,self.__originPos,self.__fadingPositionOffset))
            parallel = Parallel(LerpFunc(_modifyAlphaScale,self.__fadingDuration,1,0,blendType = 'easeIn',extraArgs = [self]),
                                LerpPosInterval(self,self.__fadingDuration,
                                                endpos,
                                                self.__originPos,
                                                blendType = 'easeIn'),
                                )
            if self.__bgPath:
                parallel.append(LerpFunc(_modifyAlphaScale,self.__fadingDuration,1,0,blendType = 'easeIn',extraArgs = [self.__bgPath]))
            
            self.__currentInterval = Sequence(parallel,
                                              Func(NodePath.hide,self),
                                              Func(self.removeFocus),
                                             )
            if self.__mask:
                self.__currentInterval.append(Func(self.__mask.hide))
            if self.__bgPath:
                self.__currentInterval.append(Func(self.__bgPath.hide))
            self.__currentInterval.start()
            
    def setPos(self, *args, **kwargs):
        NodePath.setPos(self, *args, **kwargs)
        self.__originPos = NodePath.getPos(self)

        
    def requestFocus(self):
        '''let the game know this form want focus'''
        if not self.__noFocus:
            messenger.send('request_focus',[self])  # @UndefinedVariable
        else:
            self.focused()
        
    def removeFocus(self):
        '''let the game know this form want to remove focus'''
        if not self.__noFocus:
            messenger.send('remove_focus',[self])  # @UndefinedVariable
        else:
            self.defocused()
        
    def hasFocus(self):
        return base.hasFocus(self)  # @UndefinedVariable
    
    def focused(self):
        '''Define what to do when a subclass object gets focus here'''
        pass
        
    def defocused(self):
        '''Define what to do when a subclass object loses focus here'''
        pass        
    
    def _getFadingDuration(self):
        return self.__fadingDuration

    def _getFading(self):
        return self.__fading


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
        #fill the screen
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
        DirectButton.destroy(self)
    
BUTTON_SIZE = (-0.2,0.2,-0.03,0.07)
    
class SogalDialog(SogalForm):
    '''
    A dialog that derived from SogalForm
    (Which contains a DirectDialog)
    '''
    def __init__(self,
                 enableMask = True, #NOTE THAT IT IS TRUE BY DEFAULT
                 autoDestroy = True,
                 sortType = 0, #0 for horizontal, 1 for vertical
                 margin = 0.2,
                 textList = ['OK','Cancel'],
                 enablesList = None,
                 command = None,
                 frameSize = (-0.6,0.6,-0.45,0.45),
                 buttonSize = BUTTON_SIZE,
                 text = '',
                 textPos = (0,0.2),
                 startPos = (-0.4,0,-0.2),
                 extraArgs = [],
                 style = None,
                 fadeScreen = 0.5,
                 backgroundColor = None,
                 **kwargs):
        if backgroundColor:
            bgColor = backgroundColor
        elif fadeScreen is not None:
            bgColor = (0,0,0,fadeScreen)
        else:
            bgColor = None
        
        SogalForm.__init__(self,enableMask = enableMask,backgroundColor=bgColor, **kwargs)
        if enableMask:
            self.reparentTo(aspect2d, sort = 1000)
        if not style:
            self.__style = base.getStyle()
        else:
            self.__style = styles[style]
        
        self.__frame = DirectFrame(parent = self,frameSize = frameSize,**self.__style['hardframe'])
        self.__buttonList = []#DirectButton(parent = self, s)
        self.__text = OnscreenText(parent = self,text = text ,pos = textPos, **self.__style['text'])
        self.__command = command
        self.__autoDestroy = autoDestroy
        self._extraArgs = extraArgs
        
        if sortType == 0:
            self.__box = DirectHLayout(margin = margin)
        else: self.__box = DirectVLayout(margin = margin)
        self.__box.reparentTo(self)
        self.__box.setPos(startPos)
        
        for i in range(len(textList)):
            btn = DirectButton(text = textList[i], command = self.buttonCommand(i),frameSize = buttonSize, **self.__style['button'])
            self.__buttonList.append(btn)
            self.__box.append(btn)
            
        if enablesList:
            for i in range(len(enablesList)):
                if i >= len(self.__buttonList):
                    break
                if enablesList[i]:
                    self.__buttonList[i]['state'] = DGG.NORMAL
                else: self.__buttonList[i]['state'] = DGG.DISABLED
                
        self.show()
        
    def buttonCommand(self, i):
        commandindex = i
        def process():
            if self.__command:
                self.__command(commandindex, *self._extraArgs)
            if self.__autoDestroy:
                self.close()
        return process

    def close(self):
        for btn in self.__buttonList:
            btn['state'] = DGG.DISABLED
        if self._getFading():
            seq = Sequence(Func(self.hide),
                           Wait(self._getFadingDuration()+2),
                           Func(self.destroy),
                           )
            seq.start()
        else: self.destroy()        
    
            
    def destroy(self):
        for btn in self.__buttonList:
            btn.destroy()
        self.__frame.destroy()
        self.__box.removeNode()
        SogalForm.destroy(self)
        

        
        
class ConfirmDialog(SogalDialog):
    '''A continue-or-cancel dialog'''
    def __init__(self, 
                 command = None,
                 textList = ['继续','取消'],
                 margin = 0.2,
                 frameSize = (-0.6,0.6,-0.3,0.3),
                 buttonSize = BUTTON_SIZE,
                 textPos = (0,0.05),
                 startPos = (-0.5,0,-0.15) ,
                 *args,
                 **kwargs):
        self.__command = command
        SogalDialog.__init__(self,textList= textList,frameSize = frameSize,buttonSize = buttonSize, textPos = textPos, startPos = startPos,
                             command = self.confirm,*args,**kwargs)
        
    def focused(self):
        self.accept('escape', self.close)
        self.accept('mouse3', self.close)
        self.accept('enter', self.buttonCommand(0))
        
    def confirm(self,choice,*args,**kwargs):
        if choice == 0:    #if confirmed
            self.__command(*args,**kwargs)
