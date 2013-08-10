#-*- coding:utf-8 -*-
import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.DirectGui import *
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from sogasys.sogal_text import SogalText

font = loader.loadFont('fonts/DroidSansFallbackFull.ttf') # @UndefinedVariable
font.setPixelsPerUnit(60)
font.setPageSize(512,512)
font.setLineHeight(1.2)
font.setSpaceAdvance(0.5) 

t = SogalText(text=u'\t啊啊  啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊喵喵喵喵喵喵喵喵喵喵！！！！！！！！',scale = 0.08,font = font,wordwrap = 24,spacing = 0.1,lineSpacing= 2)
t.setPos(-1,0,0.8)

run()