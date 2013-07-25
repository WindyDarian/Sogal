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
Created on Jul 25, 2013

@author: Windy Darian(大地无敌)
'''
import math

from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

import runtime_data

class SVIC(object):
    '''story view item category'''
    #That indicates a 2d image to be added to fgNodePath
    FG = 0 
    #That indicates a 2d image to be added to bgNodePath
    BG = 1
    #That indicates a 3d model to be added to vNodePath
    O3D = 2

class StoryViewItemEntry(object):
    '''
    An item in the story view to be added into the scene or to be stored
    '''
    fileName = ''    #name or path of the item
    
    category = SVIC.FG     #Category of the item
    
    scale = (1,1,1)   #Note that y should always be 1 for 2D objects
    
    pos = (0,0,0)    #Note that y should usually be 0 for 2D objects
    
    color = (1,1,1,1) 
    
    key = 'Windy'    #And key '__bg__' is for SOGAL script background
    

class StoryView(DirectObject):
    '''
    The display view of StoryManager 
    It is going to support both a 2D and a 3D view.In fact it has a 3D perspective
    view but i used billboard to make it a fake 2D view Easy to combine 2D characters
    and 3D background (or opposite)
    StoryManager的主要视图
    既支持2D也支持3D（至少窝是打算把它做成这样）
    Attributes:
    camera: the camera of this view, note that it is a 3D perspective camera.
    fgNodePath: NodePath presenting foreground images on camera (like a blackboard)
    bgNodePath: NodePath presenting background image on camera (if there is one)
    vNodePath: NodePath for 3D items 
    itemEntries: A collection of StoryViewItemEntries. 
    properties: a set of properties ready for use
    
    '''
    
    properties ={'minfov': 50.534016,    #atan(tan(40deg)*9/16)*2 in 16:9 the hfow is 80
                 'near_plane': 1,    #Near plane distance
                 'far_plane': 100000,    #Far plane distance
                 'fg_distance': 2,    #fgNodePath distance
                 'bg_distance': 5000,    #bgNodePath distance
                 }
    
    
    
    
    itemEntries = {}   

    def __init__(self,sort = 20,*args,**kwargs):
        '''
        Constructor
        '''
#         self.displayRegion = base.win.makeDisplayRegion()
#         self.displayRegion.setSort(20)
#  
#         self.camera = NodePath(Camera('myCam2d'))
#         lens = OrthographicLens()
#         lens.setFilmSize(2, 2)
#         lens.setNearFar(-1000, 1000)
#         self.camera.setLens(lens)
#  
#         self.viewRender = NodePath('myRender2d')
#         self.camera.reparentTo(myRender2d)
#         self.displayRegion.setCamera(myCamera2d)
     
        self.fgNodePath = None
        self.bgNodePath = None 
        self.vNodePath = None
        
        #sync properties and items link with runtime_data
        if runtime_data.RuntimeData.story_view_properties:  
            self.properties = runtime_data.RuntimeData.story_view_properties
        else: runtime_data.RuntimeData.story_view_properties = self.properties
        
        if runtime_data.RuntimeData.story_view_itementries:  
            self.itemEntries = runtime_data.RuntimeData.story_view_itementries
        else: runtime_data.RuntimeData.story_view_itementries = self.itemEntries
        
        self.construct()
        
        
    def construct(self):
        if self.fgNodePath:
            self.fgNodePath.removeNode()
        if self.bgNodePath:
            self.bgNodePath.removeNode()
        if self.vNodePath:
            self.vNodePath.removeNode()
        
        self.fgNodePath = NodePath('svfg') 
        self.fgNodePath.reparentTo(render)
        self.bgNodePath = NodePath('svbg') 
        self.bgNodePath.reparentTo(render)
        self.vNodePath =  NodePath('sv3d') 
        self.vNodePath.reparentTo(render)
        
        #plain = loader.loadModel("models/plain.egg")  # @UndefinedVariable  DON'T DO THAT PYDEV!
        
        self.camera = base.makeCamera(base.win)  # @UndefinedVariable 死傲娇PyDev
        self.lens = PerspectiveLens()
        self.lens.setMinFov(self.properties['minfov'])
        self.lens.setNearFar(self.properties['near_plane'],self.properties['far_plane'])
        self.lens.setAspectRatio(base.getAspectRatio())  # @UndefinedVariable
        self.camera.node().setLens(self.lens)
        self.accept('window-event', self._adjustAspectRatio) # if window is resized then we need to adjuest the aspect ratio

      
        self.fgNodePath.setPos(0,self.properties['fg_distance'],0)
        self.bgNodePath.setPos(0,self.properties['bg_distance'],0)
        self._calculateScale()
        
        
        #FOR TEST
        plain = loader.loadModel("models/plain.egg")
        plain.setTexture(loader.loadTexture(r'images/testc_dress1_normal.png'), 1)
        plain.reparentTo(self.fgNodePath)
        plain.setPos(0,0,0)
        
        bplain = loader.loadModel("models/plain.egg")
        bplain.setTexture(loader.loadTexture(r'images/testcg.png'), 1)
        bplain.reparentTo(self.bgNodePath)
        bplain.setPos(0,0,0)
        bplain.setScale(16/9.0,1,1)
        bplain.setTransparency(1)
#         plain.setScale(1)
#         plain.setTransparency(1)
        #self.setGameBackgroundImage('textures/pppp.jpg')
    
    def _adjustAspectRatio(self,arg):
        if self.camera:
            self.lens.setAspectRatio(base.getAspectRatio())  # @UndefinedVariable
            
    

    def destroy(self):
        
        #Destroy the camera
        dr = self.camera.node().getDisplayRegion(0)
        base.win.removeDisplayRegion(dr)  # @UndefinedVariable 死傲娇PyDev
        self.camera.removeNode()
        if self.fgNodePath: self.fgNodePath.removeNode()
        if self.bgNodePath: self.bgNodePath.removeNode()
        if self.vNodePath: self.vNodePath.removeNode()
        self.ignoreAll()
        
    def _calculateScale(self):
        rfov = math.radians(self.properties['minfov']) 
        fg = self.properties['fg_distance']
        bg = self.properties['bg_distance']
        scaleo = math.tan(rfov/2)
        self.fgNodePath.setScale(fg*scaleo)
        self.bgNodePath.setScale(bg*scaleo)
        
    
        
        