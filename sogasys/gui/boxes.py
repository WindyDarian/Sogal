#-*- coding:utf-8 -*-
'''
originally from http://www.panda3d.org/forums/viewtopic.php?t=4174 by chombee
Modified Box from a DirectFrame to a NodePath by Windy Darian in Jul 31, 2013
This module is not under the project's Apache License
'''
"""
boxes.py

A partial implementation of the theory of packing boxes (for laying out
objects in two dimensions, although it could easily be extended to 3D)
from GTK+. This framework can be used to layout any NodePath or
DirectGui object.

Theory Of Packing Boxes
-----------------------

From GTK+. Boxes are invisible GUI widgets into which you pack other
widgets to achieve a desired layout. In a horizontal box (hbox) objects
are packed from left to right or right to left. In a vertical box (vbox)
objects are packed from top to bottom or bottom to top. You can pack
objects in both directions in the same box at the same time by using the
two different pack methods. Options control whether objects are packed
as tightly possible, or whether the objects are spread out to fill the
amount of space alloted to the box, etc.

Finally, a table is a type of box that manages a number of cells in rows
and columns. Objects are packed into the cells. A single object can
occupy multiple cells. When packing an object, you specify the range of
cells it will occupy by specifying left, right, bottom, and top cells.

What's implemented so far:

* hboxes with packing from left to right.
* vboxes with packing from top to bottom.
* You can pack boxes into boxes in any combination. Except that you
  cannot pack a box into itself.

Todo:

* Support packing in both directions.
* Option to pack objects tightly or space them out to fill a given
  width.
* Vertical alignment option for hboxes and horizontal alignment option
  for vboxes.
* Table box class.
* Refactor. Box should extend NodePath rather than DirectFrame, and
  should emulate a Python container class.  #done

"""


from panda3d.core import *
from direct.gui.DirectGuiBase import DirectGuiWidget
from direct.gui.DirectGui import *

#modified: mixin functions cancelled and use calcTightBounds instead
def calcTightBounds(obj):
    '''
    Returns the bounds of the object. 
    '''
    if isinstance(obj,DirectGuiWidget):
        l,r,b,t = obj.getBounds()
        parent = obj.getParent()
        bottom_left = parent.getRelativePoint(obj,Point3(l,0,b))
        top_right = parent.getRelativePoint(obj,Point3(r,0,t))
        return (bottom_left,top_right)
    else:
        return obj.getTightBounds()

# FIXME: I don't see any point in Box inheriting from DirectFrame
# anymore and it's starting to get in the way (e.g. Box can't emulate a
# Python container class because DirectFrame is already abusing those
# methods). Should inherit from NodePath instead to get methods like
# setPos, getPos, getTightBounds, reparentTo, etc. that Box uses, but
# this will require some refactoring work. (In theory Box shouldn't need
# to maintain its own bounds as NodePath does this correctly.)
class Box(NodePath):
    """
    Base class for HBox and VBox. Not meant to be instantiated itself.
    
    """
    
    def __init__(self):
        """Initialise the Box. **args is just passed to the DirectFrame
        initialiser.
        
        """
        NodePath.__init__(self,'box')
        self.reparentTo(aspect2d)

        # We maintain our own list of objects packed into this box,
        # rather than reusing the scene graph. This means we don't have
        # to capture new children that are added to this node in the
        # scene graph using (for example) reparentTo, and it means that
        # users can add children to this node without them being packed
        # into the box, which might be useful.
        self._objects = []
        
        # DirectFrame does not appear to maintain its bounds in any
        # useful way  so we maintain our own bounds in the same
        # format used by NodePath.
        self._tightBounds = (Point3(0,0,0),Point3(0,0,0))

    # Some convenience methods for dealing with this annoying bounds
    # structure. This is a humane API!
    def bottom_left(self):
        return self._tightBounds[0]        
    def top_right(self):
        return self._tightBounds[1]
    def left(self):
        return self.bottom_left().getX()    
    def right(self):
        return self.top_right().getX()    
    def bottom(self):
        return self.bottom_left().getZ()    
    def top(self):
        return self.top_right().getZ()    
    def set_left(self,left):
        self.bottom_left().setX(left)
    def set_right(self,right):
        self.top_right().setX(right)
    def set_bottom(self,bottom):
        self.bottom_left().setZ(bottom)
    def set_top(self,top):
        self.top_right().setZ(top)

    def __len__(self):
        return len(self._objects)
    #TODO: emulate a Python container type
    

    def pack(self,obj):
        """
        Pack a new object into this box.
        
        Box.pack handles updating the bounds of the box, appending the
        new object to the list of packed objects, and updating the scene
        graph. It calls layout() to allow the new object to be
        positioned, subclasses should override layout to implement
        different layouts.
        
        """
        # First reparent the object to the box in the scene graph, so
        # that values it returns are relative to the box.
        obj.reparentTo(self)
        
        # Give derived classes a chance to position the new object.
        self.layout(obj)

        # Get the bounds of the new object.
        bottom_left,top_right = calcTightBounds(obj)
        left = bottom_left.getX()
        right = top_right.getX()
        bottom = bottom_left.getZ()
        top = top_right.getZ()
        # Update the bounds of this box to encompass the new object.
        if left < self.left(): self.set_left(left)
        if right > self.right(): self.set_right(right)
        if bottom < self.bottom(): self.set_bottom(bottom)
        if top > self.top(): self.set_top(top)

        # Add the object to the list of packed objects.
        self._objects.append(obj)
    
    def layout(self,obj):
        """
        Position a new object that is being packed into this box.
        Subclasses should override this method to implement their
        own layouts.
        
        """
        pass
        
class HBox(Box):
    """
    A horizontal container. Objects that are packed into this box will
    be layed out along a horizontal line.
    
    """

    def __init__(self,margin=0,**args):
        """Initialise the hbox. margin specifies a horizontal gap
        between each object and the next in the box. **args is passed
        straight to Box.
        
        """
        self.margin = margin
        Box.__init__(self,**args)
            
    def layout(self,obj):
        """
        Align the left side of the new object with the right side of
        the last packed object, and align the top of the new object
        with the top of the last packed object.        
                   
        """             
        if self._objects == []:
            # This is the first object to be packed. Align it with
            # this empty box.
            right = self.right()
            top = self.top()
        else:
            # Align the new object with the last object that was
            # packed.
            last = self._objects[-1]
            bottom_left,top_right = calcTightBounds(last)
            right = top_right.getX()
            top = top_right.getZ()

        # Align the left of the new object with `right`.
        bottom_left,top_right = calcTightBounds(obj)      
        left = bottom_left.getX()
        distance = right - left
        obj.setPos(obj.getPos() + Point3(distance,0,0))
        
        # Align the top of the new object with `top`.
        t = top_right.getZ()
        distance = top - t
        obj.setPos(obj.getPos() + Point3(0,0,distance))
        
        obj.setPos(obj.getPos() + Point3(self.margin,0,0))
        
class VBox(Box):
    """
    A vertical container. Objects that are packed into this box will
    be layed out along a vertical line.
    
    """

    def __init__(self,margin=0,**args):
        """Initialise the vbox. margin specifies a vertical gap
        between each object and the next in the box. **args is passed
        straight to Box.
        
        """
        self.margin = margin
        Box.__init__(self,**args)
                
    def layout(self,obj):
        """
        Align the top side of the new object with the bottom side of
        the last packed object, and align the left of the new object
        with the left of the last packed object.        
                   
        """
        if self._objects == []:
            # This is the first object to be packed. Align it with
            # this empty box.
            bottom = self.bottom()
            left = self.left()
        else:
            # Align the new object with the last object that was
            # packed.
            last = self._objects[-1]
            bottom_left,top_right = calcTightBounds(last)
            bottom = bottom_left.getZ()
            left = bottom_left.getX()

        # Align the top of the new object with `bottom`.
        bottom_left,top_right = calcTightBounds(obj)        
        top = top_right.getZ()
        distance = bottom - top
        obj.setPos(obj.getPos() + Point3(0,0,distance))

        # Align the left of the new object with `left`.
        l = bottom_left.getX()
        distance = left - l
        obj.setPos(obj.getPos() + Point3(distance,0,0))
        
        obj.setPos(obj.getPos() + Point3(0,0,-self.margin))
    
if __name__== '__main__' :
    """
    For the test we make a grid of different-coloured cards by packing 4
    cards each into 6 vboxes, and packing the vboxes into an hbox. We
    also put an hbox on each card and pack some DirectGUI objects into
    it.
    
    """      
    import direct.directbase.DirectStart
    from random import random
    
    
    
    # Use the CardMaker to generate some nodepaths for flat,
    # card-like geometry.
    cm = CardMaker('cm')
    left,right,bottom,top = 0,2,0,-2
    width = right - left
    height = top - bottom
    cm.setFrame(left,right,bottom,top)

    hbox = HBox(margin=.05)
    hbox.setPos(-1.2,0,0.9)
    for i in range(5):        
        vbox = VBox(margin=.05)
        for j in range(4):       
            np = aspect2d.attachNewNode(cm.generate())
            np.setScale(.2)
            np.setColor(random(),random(),random())
            another_vbox = VBox(margin=.05)
            dl = DirectLabel(text="I'm a label, look at me!",scale=.2)
            another_vbox.pack(dl)
            de = DirectEntry(initialText="I'm a text entry, write on me!",scale=.2,width=4,numLines=4)
            another_vbox.pack(de)
            db = DirectButton(text="I'm a button, click me!",scale=.2,relief=None)
            another_vbox.pack(db)
            another_vbox.reparentTo(np)
            vbox.pack(np)        
        hbox.pack(vbox)
         
    run()