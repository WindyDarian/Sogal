import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.DirectGui import *
from direct.task import Task
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from panda3d.core import *
import direct.gui.DirectGuiGlobals as DGG
 
#add some text
bk_text = "DirectDialog- YesNoDialog Demo"
textObject = OnscreenText(text = bk_text, pos = (0.85,0.85), 
scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
 
#add some text
output = ""
textObject = OnscreenText(text = output, pos = (0.95,-0.95),
 scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
 
#callback function to set  text 
def itemSel(arg):
    if(arg):
        output = "Button Selected is: Yes"
    else:
        output = "Button Selected is: No"
    textObject.setText(output)
 
#create a frame
dialog = DirectDialog(dialogName="YesNoCancelDialog", text="Please choose:",
                      #frameSize = (-0.5,0.5,-0.5,0.5),
                     buttonTextList = ['love','HAHAHAHA','Windy Darian','love','HAHAHAHA','Windy Darian','love','HAHAHAHA','Windy Darian'], 
                     command=itemSel,
                     button_frameColor =((239/255.0,195/255.0,46/255.0,0.75),
                                         (1.0,1.0,1.0,1),
                                         (249/255.0,235/255.0,85/255.0,0.95),
                                         (0.5,0.5,0.5,0.75),),
                    
                     button_relief = DGG.FLAT,
                     relief = DGG.FLAT,
                     image = None,
                     frameColor = (239/255.0,195/255.0,46/255.0,0.3),
                     frameSize = ()
                     )
 
base.camera.setPos(0,-20,0)

run()
#run the tutorial