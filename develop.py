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
SOGAL(七海美少女游戏引擎, Seven Ocean Galgame Engine)的主入口点，开发时用所以会经常改动
@author: 大地无敌
'''

from panda3d.core import loadPrcFile # @UnresolvedImport
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
from sogasys.story_manager import StoryManager
from direct.filter.FilterManager import FilterManager

 
class SogalEntry(ShowBase): 
    "游戏框架，继承自ShowBase"

    def __init__(self):
        "初始化"
        #读取设置文件
        loadPrcFile("config/PandaConfig.prc")
        
        #构造Panda3D的ShowBase
        ShowBase.__init__(self)
        self.cam2dp.node().getDisplayRegion(0).setSort(-20)  #Set render2dp to background
        self.disableMouse() #Disable panda3d's default mouse control
        
        #背景设置
        self.setBackgroundColor(0,0,0,1); 
        self.backgroundImage = None
        
        self.storyManager = StoryManager();
        self.storyManager.start();
        self.storyManager.addScriptData('test0')
        
        self.cam.node().getDisplayRegion(0).setActive(0)
        
#         plain = loader.loadModel("models/plain.egg")
#         cam = self.makeCamera(self.win)
#         lens = PerspectiveLens()
#         lens.setAspectRatio(16/9.0)
#         lens.setNear(1)
#         lens.setFilmSize(2,2)
#         cam.node().setLens(lens)
#         #plain = loader.loadModel("models/plane2.egg")
#         plain.setTexture(loader.loadTexture(r'images/pppp.jpg'), 1)
#         plain.reparentTo(cam)
#         plain.setPos(0,1.1,0)
#         plain.setScale(1)
#         plain.setTransparency(1)
#         self.setGameBackgroundImage('images/pppp.jpg')
        
    def setGameBackgroundImage(self,path):
        "设置背景图片"
        ''' Load a backgroundImage image behind the models '''
        if self.backgroundImage:
            self.backgroundImage.destroy()
        self.backgroundImage = OnscreenImage(parent=aspect2dp, image=path)  # @UndefinedVariable
        self.cam2dp.node().getDisplayRegion(0).setSort(-20) 
        
    storyManager = None
    mainMenu = None


if __name__ == '__main__':
    SogalEntry().run()