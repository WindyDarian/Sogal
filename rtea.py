from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.interval.FunctionInterval import Func


class Application(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.pandaActor = Actor("panda", {"walk": "panda-walk"})
        self.pandaActor.reparentTo(render)
        self.pandaActor.loop("walk")
        self.cameras = [self.cam, self.makeCamera(self.win)]
        self.cameras[1].node().getDisplayRegion(0).setActive(0)
        self.activeCam = 0
        self.cameras[0].setPos(0, -30, 6)
        self.cameras[1].setPos(30, -30, 20)
        self.cameras[1].lookAt(0, 0, 6)
        self.taskMgr.doMethodLater(5, self.toggleCam, "togglecamera")
    def toggleCam(self, task):
        self.cameras[self.activeCam].node().getDisplayRegion(0).setActive(0)
        self.activeCam = not self.activeCam
        self.cameras[self.activeCam].node().getDisplayRegion(0).setActive(1)
        return task.again
    
    
Application().run()