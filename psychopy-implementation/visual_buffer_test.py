from psychopy import visual, core
win = visual.Window([800, 600], color=[0.85, 0.85, 0.85], monitor="testMonitor", units="deg")
rect = visual.Rect(win=win, width=10, height=10)    
circ = visual.Circle(win=win, radius=5, fillColor="red")

def test():
    rect.draw()
    win.flip(clearBuffer=False)
    circ.draw()
    core.wait(1)
    win.flip()
    core.wait(1)

class Test:
    def __init__(self):
        self.win = visual.Window([800, 600], color=[0.85, 0.85, 0.85], monitor="testMonitor", units="deg")
        self.rect = visual.Rect(win=self.win, width=10, height=10)
        self.circ = visual.Circle(win=self.win, radius=5, fillColor="red")
        
    def test(self):
        self.rect.draw()
        self.win.flip(clearBuffer=False)
        self.circ.draw()
        core.wait(1)
        self.win.flip()
        core.wait(1)


# global
print("global")
rect.draw()
win.flip(clearBuffer=False)
circ.draw()
core.wait(1)
win.flip()
core.wait(1)

# local in function
print("local scope")
test()
win.close()

# local as class
t = Test()
t.test()


