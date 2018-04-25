# eventBasedAnimationClass.py

from Tkinter import *

class EventBasedAnimationClass(object):
    def onMousePressed(self, event): pass
    def onKeyPressed(self, event): pass
    def onTimerFired(self): pass
    def redrawAll(self): pass
    def initAnimation(self): pass

    def __init__(self, width=1000, height=750):
        self.width = width
        self.height = height
        self.timerDelay = 100 # in milliseconds (set to None to turn off timer)

    def onMousePressedWrapper(self, event):
        self.onMousePressed(event)
        self.redrawAll()


    def onKeyPressedWrapper(self, event):
        self.onKeyPressed(event)
        self.redrawAll()


    def onTimerFiredWrapper(self):
        if (self.timerDelay == None):
            return # turns off timer
        self.onTimerFired()
        self.redrawAll()
        self.canvas.after(self.timerDelay, self.onTimerFiredWrapper)         

    def run(self):
        # create the root and the canvas
        self.root = Tk()
        self.root.title("AirDrums")
        global canvas
        self.canvas=Canvas(self.root, width=self.width, height=self.height)
        self.root.canvas=self.canvas.canvas=self.canvas
        self.canvas.pack()
        self.initAnimation()
        self.canvas.data ={ }
        # set up events
        # DK: You can use a local function with a closure
        # to store the canvas binding, like this:
        def f(event): self.onMousePressedWrapper(event)    
        self.root.bind("<Button-1>", f)
        # DK: Or you can just use an anonymous lamdba function, like this:
        self.root.bind("<Key>", lambda event: self.onKeyPressedWrapper(event))
        self.onTimerFiredWrapper()
        # and launch the app (This call BLOCKS, so your program waits
        # until you close the window!)
        self.root.mainloop()

# EventBasedAnimationClass(300,300).run()