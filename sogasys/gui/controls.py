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
Created on Sep 18, 2013
SOGAL's Controls. 
@author: Windy Darian (大地无敌)
'''

from panda3d.core import NodePath,PGButton

import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenImage import OnscreenImage


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
            ('isChecked',       False,     None),
            )
        
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        DirectButton.__init__(self,parent)
        
        self.initialiseoptions(SDirectCheckBox)
        
        self.renewgeom()
        
    def setUncheckedImage(self):
        self['uncheckedGeom'] = OnscreenImage(self['uncheckedImage'])
        
    def setCheckedImage(self):
        self['checkedGeom'] = OnscreenImage(self['checkedImage'])
        
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

class CheckBox(NodePath):
    '''
    Simpified interface of a 
    '''

    def __init__(self, 
                onimage = 'ui/default/checkbox_unchecked.png',
                offimage = 'ui/default/checkbox_checked.png',
                scale = 0.05
                ):
        pass
        
