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
Created on Sep 19, 2013
Custom inherited panda's direct Controls
@author: Windy Darian (大地无敌)
'''
from panda3d.core import PGButton, NodePath

import direct.gui.DirectGuiGlobals as DGG
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectOptionMenu import DirectOptionMenu


class SDirectCheckBox(DirectButton):
    """
    Little improved checkbox
    Modified on direct.gui.DirectCheckBox
    """
    def __init__(self, parent = None, **kw):

        optiondefs = (
            # Define type of DirectGuiWidget
            ('pgFunc',         PGButton,   None),
            ('numStates',      4,          None),
            ('state',          DGG.NORMAL, None),
            ('relief',         None,       None),
            ('invertedFrames', (1,),       None),
            ('frameSize',      (-1,1,-1,1),None),
            ('scale',          0.05,       None),
            # Command to be called on button click
            ('command',        None,       None),
            ('extraArgs',      [],         None),
            # Which mouse buttons can be used to click the button
            ('commandButtons', (DGG.LMB,),     self.setCommandButtons),
            # Sounds to be used for button events
            ('rolloverSound', DGG.getDefaultRolloverSound(), self.setRolloverSound),
            ('clickSound',    DGG.getDefaultClickSound(),    self.setClickSound),
            # Can only be specified at time of widget contruction
            # Do the text/graphics appear to move when the button is clicked
            ('pressEffect',     1,         DGG.INITOPT),
            ('uncheckedImage',  'ui/default/checkbox_unchecked.png',      self.setUncheckedImage),
            ('checkedImage',    'ui/default/checkbox_checked.png',      self.setCheckedImage),
            ('uncheckedGeom',  None,      None),
            ('checkedGeom',    None,      None),
            ('isChecked',       False,     self.renewgeom),
            )
        
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        DirectButton.__init__(self,parent)
        
        
        self.__checkstatedumpnp = NodePath('checkstatenp')
        
        
        self.initialiseoptions(SDirectCheckBox)
        
        
    def setUncheckedImage(self):
        self['uncheckedGeom'] = OnscreenImage(self['uncheckedImage'], parent = self.__checkstatedumpnp)
        
    def setCheckedImage(self):
        self['checkedGeom'] = OnscreenImage(self['checkedImage'], parent = self.__checkstatedumpnp)
        
    def renewgeom(self):
        if self['isChecked']:
            self['geom'] = self['checkedGeom']
        else:
            self['geom'] = self['uncheckedGeom']
                
    def commandFunc(self, event):
        self['isChecked'] = not self['isChecked']
        
        self.renewgeom()
        
        if self['command']:
            # Pass any extra args to command
            apply(self['command'], [self['isChecked']] + self['extraArgs'])
            
    def destroy(self, *args, **kwargs):
        self.__checkstatedumpnp.removeNode()
        return DirectButton.destroy(self, *args, **kwargs)
            

            
class SDirectOptionMenu(DirectOptionMenu):
    def __init__(self, parent = None, **kw):
        
        optiondefs = (
                      ('itemcontent',        [],          None),
                      ('relief',             DGG.FLAT,    None),
                      ('popupMarker_relief', None,        None),
                      ('frameColor',         (0,0,0,0.5), None),
                      ('text_fg',            (1,1,1,1),   None),
                      ('item_relief',        DGG.FLAT,    None),
                      ('popupMenu_relief',   None,        None),
                     )
        self.defineoptions(kw, optiondefs)
        DirectOptionMenu.__init__(self)
        self.initialiseoptions(SDirectOptionMenu)
        self.resetFrameSize()
        
    def get(self):
        '''replaced DirectOptionMenu.get
        now if itemcontent is set, return the content of the label 
        and not the text
        '''
        if not self['itemcontent']:
            return self['items'][self.selectedIndex]
        else: 
            return self['itemcontent'][self.selectedIndex]
        
    def set(self, index, fCommand = 1):
        '''replaced DirectOptionMenu.get
        now if itemcontent is set, give the content but not the text
        to command function
        '''
        newIndex = self.index(index)
        if newIndex is not None:
            self.selectedIndex = newIndex
            item = self['items'][self.selectedIndex]
            self['text'] = item
            if fCommand and self['command']:
                # Pass any extra args to command
                if not self['itemcontent']:
                    apply(self['command'], [item] + self['extraArgs'])
                else:
                    apply(self['command'], self['itemcontent'][self.selectedIndex] + self['extraArgs'])