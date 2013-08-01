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
story scene.
@author: Windy Darian(大地无敌)
'''
import math

from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenImage import OnscreenImage
from direct.stdpy.file import exists
from direct.interval.LerpInterval import LerpFunc,LerpColorInterval,LerpScaleInterval,LerpPosInterval
from direct.interval.FunctionInterval import Func,Wait
from direct.interval.IntervalGlobal import Sequence

import runtime_data



class SVIC(object):
    '''story view item category'''
    #That indicates a 2d image to be added to fgNodePath
    FG = 0 
    #That indicates a 2d image to be added to bgNodePath
    BG = 1
    #That indicates a 3d model to be added to vNodePath
    O3D = 2
    #That indicates an egg 2d animation to be added to fgNodePath
    AFG = 3
    #That indicates an 2d image to be added to pNodePath
    O2D = 4
    #That indicates an 2d image but to be added to vNodePath

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
    
    fadein = 0
    
    quickitem = False
    
    #TODO: 实现带遮罩效果的淡入？
    
    def __init__(self,key,fileName,category,pos = (0,0,0),scale = (1,1,1),color = (1,1,1,1),fadein = 0,quickitem = False):
        self.key = key
        self.fileName = fileName
        self.category = category
        self.pos = pos
        self.scale = scale
        self.color = color
        self.fadein = fadein
        self.quickitem = quickitem
        
    

class StoryView(DirectObject, NodePath):
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
    
    _sceneItems = None

    def __init__(self,sort = 20,*args,**kwargs):
        '''
        Constructor
        '''
        NodePath.__init__(self,'story_view')
        self.reparentTo(render)
        
        #sync properties and items link with runtime_data
        if runtime_data.RuntimeData.story_view_properties:  
            self.properties = runtime_data.RuntimeData.story_view_properties
        else: runtime_data.RuntimeData.story_view_properties = self.properties
        
        if runtime_data.RuntimeData.story_view_itementries:  
            self.itemEntries = runtime_data.RuntimeData.story_view_itementries
        else: runtime_data.RuntimeData.story_view_itementries = self.itemEntries
        
        self.__destroyed = False
        self.fgNodePath = None
        self.bgNodePath = None 
        self.vNodePath = None
        self._sceneItems = {}
        self._intervals = []  #seems no need atm
        self._quickitems = []
        
        self.camera = base.makeCamera(base.win)  # @UndefinedVariable 死傲娇PyDev
        self.lens = PerspectiveLens()
        self.reload()
        self.accept('window-event', self._adjustAspectRatio) # if window is resized then we need to adjuest the aspect ratio
        
        
        '''    #TEST
        d3 = loader.loadModel("models/environment")
        d3.reparentTo(self.vNodePath)
        d3.setPos(-8,42,-1)
        d3.setScale(0.25)
        d3.setTransparency(1)
        self.newItem(StoryViewItemEntry('zz','testc_dress1_normal',SVIC.FG, pos = (0.33,0,0)))
        self.newItem(StoryViewItemEntry('zz','testc_dress2_normal',SVIC.FG, pos = (-0.33,0,-0.2),color = (1,1,1,0.5)))
        self.newItem(StoryViewItemEntry('zz2','testc_dress1_normal',SVIC.O2D, pos = (0,10,0),color = (1,1,1,0.6)))
        self.newItem(StoryViewItemEntry('arrow','text_arrow/text_arrow',SVIC.O3D,pos = (0,1.5,0)))
        self.newItem(StoryViewItemEntry('__bg__','testbg',SVIC.BG))
        '''
    def presave(self):
        '''what to do before saving'''
        pass
        
        
    def reload(self):

        #sync properties and items link with runtime_data
        if runtime_data.RuntimeData.story_view_properties:  
            self.properties = runtime_data.RuntimeData.story_view_properties
        else: runtime_data.RuntimeData.story_view_properties = self.properties
        
        if runtime_data.RuntimeData.story_view_itementries:  
            self.itemEntries = runtime_data.RuntimeData.story_view_itementries
        else: runtime_data.RuntimeData.story_view_itementries = self.itemEntries
        
        '''reload the properties and the items and the camera'''
        self._resetNode()
        for key in self.itemEntries:
            self._createItem(self.itemEntries[key], ignore_fadein = true)
            
        self.lens.setMinFov(self.properties['minfov'])
        self.lens.setNearFar(self.properties['near_plane'],self.properties['far_plane'])
        self.lens.setAspectRatio(base.getAspectRatio())  # @UndefinedVariable
        self.camera.node().setLens(self.lens)
      
        self.fgNodePath.setPos(0,self.properties['fg_distance'],0)
        self.bgNodePath.setPos(0,self.properties['bg_distance'],0)
        self._calculateScale()
            
    def newItem(self, entry):
        '''Create an item according to given item entry and add it to itemEntries'''

       
        if entry.quickitem:
            entry.key += '__qi__' + str(len(self._quickitems))
            self._quickitems.append(entry.key)
        self.itemEntries[entry.key] = entry
        self._createItem(entry)
        
    def deleteItem(self,key,fadeout = 0):
        '''Delete an item from StoryView'''
        if not fadeout:
            self.itemEntries.pop(key)
            node = self._sceneItems.pop(key)
            node.removeNode()
            
        else:    #if it has a fade-out effect then add fade-out intervals
            self.itemEntries.pop(key) 
            item = self._sceneItems.pop(key)
            item.setName('removing_'+item.getName())
            color = item.getColor()
            sequcnce = Sequence(LerpColorInterval(item, fadeout, (color[0],color[1],color[2],0), color),
                                            Func(self.__deletefromScene,item),
                                            )
            self._intervals.append(sequcnce)
            sequcnce.start()
            
    def __deletefromScene(self,item):
        item.removeNode()
        
            
    def _createItem(self, entry, ignore_fadein = False):
        '''Create an item(not including adding this to itemEntries)'''
        
        imagepathes = runtime_data.game_settings['imagepathes']
        imagetypes = runtime_data.game_settings['imagetypes']
        modelpathes = runtime_data.game_settings['modelpathes']
        modeltypes = runtime_data.game_settings['modeltypes']
        
        if self._sceneItems.has_key(entry.key):
            self._sceneItems[entry.key].removeNode()
            self._sceneItems.pop(entry.key)
        item = None
        if entry.category == SVIC.FG or entry.category == SVIC.BG or entry.category == SVIC.O2D:

            
            texture = None
            for ft in ((folder,type) for folder in imagepathes for type in imagetypes):
                if exists(ft[0] + entry.fileName + ft[1]):
                    texture = loader.loadTexture(ft[0] + entry.fileName + ft[1])
                    break
            
                
            '''Alternative
            item = loader.loadModel(r"models/plain.egg")
            item.setTexture(texture, 1)
            '''
            item = OnscreenImage(texture)
            
            item.setPos(entry.pos[0],entry.pos[1],entry.pos[2])
            item.setScale(entry.scale[0]*texture.getOrigFileXSize()/float(texture.getOrigFileYSize()),entry.scale[1],entry.scale[2])  #Always make its height fill the screen normally
            color = (entry.color[0],entry.color[1],entry.color[2],entry.color[3])
            if entry.fadein:
                lv = LerpColorInterval(item, entry.fadein, color, (color[0],color[1],color[2],0) ) 
                self._intervals.append(lv)
                lv.start()
            else: item.setColor(color)
            item.setName(entry.key)
            
            if entry.category == SVIC.FG:
                item.reparentTo(self.fgNodePath)
            elif entry.category == SVIC.BG:
                item.reparentTo(self.bgNodePath)
            elif entry.category == SVIC.O2D:
                item.reparentTo(self.vNodePath)
            
        elif entry.category == SVIC.AFG:
            item = None
            for ft in ((folder,type) for folder in imagepathes for type in modeltypes):
                if exists(ft[0] + entry.fileName + ft[1]):
                    item = loader.loadModel(ft[0] + entry.fileName + ft[1])
                    break
            if not item:  item = loader.loadModel(entry.fileName)
            item.setPos(entry.pos[0],entry.pos[1],entry.pos[2])
            item.setScale(entry.scale)  #For generated egg animation with "egg-texture-cards" is a 1x1 rectangle by default
            color = (entry.color[0],entry.color[1],entry.color[2],entry.color[3])
            if entry.fadein:
                lv = LerpColorInterval(item, entry.fadein, color, (color[0],color[1],color[2],0) ) 
                self._intervals.append(lv)
                lv.start()
            else: item.setColor(color)
            item.setTransparency(1)
            item.setName(entry.key)
            item.reparentTo(self.fgNodePath)
            #item.setBin("unsorted", 0)

            
        elif entry.category == SVIC.O3D:
            item = None
            for ft in ((folder,type) for folder in modelpathes for type in modeltypes):
                if exists(ft[0] + entry.fileName + ft[1]):
                    item = loader.loadModel(ft[0] + entry.fileName + ft[1])
                    break
            if not item:  item = loader.loadModel(entry.fileName)
            item.setPos(entry.pos[0],entry.pos[1],entry.pos[2])
            item.setScale(entry.scale)  #For generated egg animation with "egg-texture-cards" is a 1x1 rectangle by default
            color = (entry.color[0],entry.color[1],entry.color[2],entry.color[3])
            if entry.fadein:
                lv = LerpColorInterval(item, entry.fadein, color, (color[0],color[1],color[2],0) ) 
                self._intervals.append(lv)
                lv.start()
            else: item.setColor(color)
            item.setTransparency(1)
            item.setName(entry.key)
            item.reparentTo(self.vNodePath)
  
        if item:
            self._sceneItems[entry.key] = item
    
    
    def _adjustAspectRatio(self,arg):
        if self.camera:
            self.lens.setAspectRatio(base.getAspectRatio())  # @UndefinedVariable
            
    def changeBackground(self,backgroundImage,fadein):
        if not fadein:
            svie = StoryViewItemEntry('__bg__',backgroundImage,SVIC.BG,pos = (0,0,0),scale = (1,1,1),color = (1,1,1,1),fadein = 0)
            self.newItem(svie)
        else:
            self.itemEntries.pop('__bg__',None) #remove the current background
            oldbg = self._sceneItems.pop('__bg__',None) #remove the old background after the new background is completely shown
            svie = StoryViewItemEntry('__bg__',backgroundImage,SVIC.BG,pos = (0,0,0),scale = (1,1,1),color = (1,1,1,1),fadein = fadein)
            self.newItem(svie)
           
            if oldbg:
                oldbg.setName('removing_'+oldbg.getName())
                sequence = Sequence(Wait(fadein),Func(self.__deletefromScene,oldbg))
                self._intervals.append(sequence)
                sequence.start()

    def destroy(self):
        self.__destroyed = True
        #Destroy the camera
        dr = self.camera.node().getDisplayRegion(0)
        base.win.removeDisplayRegion(dr)  # @UndefinedVariable 死傲娇PyDev
        self.camera.removeNode()
        if self.fgNodePath: self.fgNodePath.removeNode()
        if self.bgNodePath: self.bgNodePath.removeNode()
        if self.vNodePath: self.vNodePath.removeNode()
        self.ignoreAll()
        
        self._sceneItems = None
        
    def __del__(self):
        if not self.__destroyed:
            self.destroy()
        
    def _resetNode(self):
        
        for interval in self._intervals:
            if interval.isPlaying():  
                interval.finish()   
        self._removeDeadLerp()      
            
        if self.fgNodePath:
            self.fgNodePath.removeNode()
        if self.bgNodePath:
            self.bgNodePath.removeNode()
        if self.vNodePath:
            self.vNodePath.removeNode()
        
        self.vNodePath =  NodePath('sv3d') 
        self.vNodePath.reparentTo(self,2) 
        self.vNodePath.setTransparency(TransparencyAttrib.MMultisample)
         
        
        self.fgNodePath = NodePath('svfg') 
        self.fgNodePath.reparentTo(self,3)
        self.fgNodePath.setTransparency(TransparencyAttrib.MAlpha)
        self.fgNodePath.setBin("fixed", 40)
        self.fgNodePath.setDepthTest(False)
        self.fgNodePath.setDepthWrite(False)
        #self.fgNodePath.setAttrib(AlphaTestAttrib.make(RenderAttrib.MLess,0.25))
 
        self.bgNodePath = NodePath('svbg') 
        self.bgNodePath.reparentTo(self,1)
        self.bgNodePath.setTransparency(TransparencyAttrib.MAlpha)
        self.bgNodePath.setDepthTest(False)
        self.bgNodePath.setDepthWrite(False)
        self.bgNodePath.setBin("background",10)
        
        self._sceneItems = {}
        
    def _calculateScale(self):
        
        rfov = math.radians(self.properties['minfov']) 
        fg = self.properties['fg_distance']
        bg = self.properties['bg_distance']
        scaleo = math.tan(rfov/2)
        self.fgNodePath.setScale(fg*scaleo)
        self.bgNodePath.setScale(bg*scaleo)
        self.__distanceScale2D = scaleo
        
    def changePosColorScale(self,key,pos = None,color = None, scale = None,time = 0):
        '''Change an item's position, color, and/or scale. 
        params should be lists having a length of 3 (pos, scale) or 4 (color) floats
        '''
        if pos:
            self.itemEntries[key].pos = pos
            if not time:
                self._sceneItems[key].setPos(pos)
            else:
                ival = LerpPosInterval(self._sceneItems[key],time,pos,self._sceneItems[key].getPos())
                self._intervals.append(ival)
                ival.start()
        if color:
            self.itemEntries[key].color = color
            if not time:
                self._sceneItems[key].setColor(color)
            else:
                ival = LerpColorInterval(self._sceneItems[key],time,color,self._sceneItems[key].getColor())
                self._intervals.append(ival)
                ival.start()
        if scale:
            self.itemEntries[key].scale = scale
            if not time:
                self._sceneItems[key].setScale(self._sceneItems[key].getSx()*scale[0],
                                               self._sceneItems[key].getSy()*scale[1],
                                               self._sceneItems[key].getSz()*scale[2])
            else:
                targetscale = (self._sceneItems[key].getSx()*scale[0],
                               self._sceneItems[key].getSy()*scale[1],
                               self._sceneItems[key].getSz()*scale[2])
                ival = LerpScaleInterval(self._sceneItems[key],time,targetscale,self._sceneItems[key].getScale())
                self._intervals.append(ival)
                ival.start()
        #TODO 缩放要加参数和物体类型的判断
            
    def clear(self,fadeout = 0,bgfile = None):
        self.clearQuickItems()
        
        if not fadeout:
            self.itemEntries.clear()
            self.reload()
        else:
            dr = self.camera.node().getDisplayRegion(0)
            texture = dr.getScreenshot()
           
            w = dr.getPixelWidth()
            h = dr.getPixelHeight()
                        
            self.itemEntries.clear()
            self.reload()
            
            if bgfile:
                bgentry = StoryViewItemEntry(fileName = bgfile,key = '__bg__',category = SVIC.BG)
                self.newItem(bgentry)
            
            tempbg = OnscreenImage(texture)
            if w > h:
                tempbg.setScale(1*w/float(h),1,1)
            else: tempbg.setScale(1,1,1*h/float(w))
            tempbg.setColor(1,1,1,1)
            tempbg.reparentTo(self.bgNodePath)
            tempbg.setName('__tempbg__')
            
            li = LerpColorInterval(tempbg, fadeout, (1,1,1,0), (1,1,1,1),blendType = 'easeInOut' ) 
            self._intervals.append(li)
            li.start()

    def clearQuickItems(self):
        '''quick item can be cleared out automatically, called by StoryManager'''
        for qe in self._quickitems:
            self.deleteItem(qe)
        self._quickitems[:] = []
    
    def quickfinish(self):
        for interval in self._intervals:
            if interval.isPlaying():
                interval.finish()
        
    def getIsWaiting(self):
        for interval in self._intervals:
            if interval.isPlaying():
                return True
        return False
    
    def _removeDeadLerp(self):
        removelist = []
        for interval in self._intervals:
            if not interval.isPlaying():
                removelist.append(interval)
        for r in removelist:
            self._intervals.remove(r)
            
 
    
    
        
        