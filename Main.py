from visual import *
from Tkinter import *
import threading
import tkMessageBox
import random

# set scene
scene.width = 1000
scene.height = 1000
scene.center = (0, 70, 0)
scene.range = (200, 200, 50)
straight = [(0, 0, 0)]

# crete object
beam = frame()
ground = box(pos=(0, -60, 0), size=(400, 20, 20), color=(0.5, 0.5, 0.5))
triangle = Polygon([(-25, -50), (0, -3), (25, -50)])
extrusion(pos=straight, shape=triangle, color=color.red)
arm = box(frame=beam, pos=(0, 0, 0), size=(300, 5, 20), color=color.white)

# window
commandTool = Tk()

# variable
g = 9.8  # constant
dt = 0.0005
time = 0
criticaltheta = asin(48. / 150.)  # the angle that a beam touches ground
angle_ = 0.  # initiate angle of a beam
I = 0.75  # come from I = mr^2 / 12 assume that the mass of arm is light ,so I = r^2 / 12 = 9/12 = 3/4
angularVelocity = 0  # initiate velocity of a beam
moment = 0
momentleft = 0
momentright = 0
checkSimulate = false
recentlyAdd = false
keep = []  # list of keeping object in simulation
colorlist = [color.magenta, color.orange, color.blue, color.cyan, color.green, color.red, color.yellow]
shape = IntVar()
side = IntVar()

# label
left3 = label(pos=(-150, 0, -10), text='3 M.', yoffset=180)
left2 = label(pos=(-100, 0, -10), text='2 M.', yoffset=180)
left1 = label(pos=(-50, 0, -10), text='1 M.', yoffset=180)
center = label(pos=(0, 0, -10), text='Center (0 M.)', yoffset=180)
right1 = label(pos=(50, 0, -10), text='1 M.', yoffset=180)
right2 = label(pos=(100, 0, -10), text='2 M.', yoffset=180)
right3 = label(pos=(150, 0, -10), text='3 M.', yoffset=180)
note = label(pos=(-189, 258, 0), text='Note:', color=color.red)
note1 = label(pos=(-134, 243, 0), text='1. Weight of beam is light (assume that m = 0)', color=color.red)
note2 = label(pos=(-155, 228, 0), text='2. Mass can\'t be begative value', color=color.red)
note3 = label(pos=(-155, 213, 0), text='3. Position can\'t more than 3m.', color=color.red)
note4 = label(pos=(-77, 198, 0),
              text='4. Meaning of total of moment: negative value = beam tilt left, positive value = beam tilt right',
              color=color.red)
note5 = label(pos=(-59, 183, 0),
              text='5. While simulate, a program always calculates, so you can add objects you want without pressing reset',
              color=color.red)
moment_total = label(pos=(150, 258, 0), text='Total of moment: 0.0', color=color.cyan)
moment_left = label(pos=(154, 243, 0), text='Moment on left side: 0.0', color=color.cyan)
moment_right = label(pos=(156, 228, 0), text='Moment on right side: 0.0', color=color.cyan)
acceleration = label(pos=(156, 213, 0), text='Angular acceleration: 0.0', color=color.cyan)
velocity = label(pos=(150, 198, 0), text='Angular velocity: 0.0', color=color.cyan)


class CT(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        commandTool.title('Command Tool')
        commandTool.geometry('250x250+1000-100')
        addobjectB = Button(commandTool, text='Add Object', height=3, width=10, command=addObject)
        addobjectB.place(x=0, y=195)
        simulateB = Button(commandTool, text='Simulate', height=3, width=12, command=simulate)
        simulateB.place(x=79, y=195)
        restartB = Button(commandTool, text='Reset', height=3, width=10, command=reset)
        restartB.place(x=172, y=195)

        L1 = Label(commandTool, text="Select Object")
        L1.place(x=0, y=0)
        L2 = Label(commandTool, text="Mass (kg.)")
        L2.place(x=0, y=60)
        L3 = Label(commandTool, text='Position (m. from center)')
        L3.place(x=0, y=130)
        E1 = Entry(commandTool, bd=4)
        E1.place(x=0, y=90)
        E2 = Entry(commandTool, bd=4)
        E2.place(x=0, y=160)
        R1 = Radiobutton(commandTool, text="Box", variable=shape, value=1, command=sel)
        R1.select()
        R1.place(x=20, y=30)
        R2 = Radiobutton(commandTool, text="Sphere", variable=shape, value=2, command=sel)
        R2.place(x=70, y=30)
        R3 = Radiobutton(commandTool, text="Left", variable=side, value=1, command=sel)
        R3.select()
        R3.place(x=130, y=160)
        R4 = Radiobutton(commandTool, text="Right", variable=side, value=2, command=sel)
        R4.place(x=180, y=160)

        commandTool.mass = E1
        commandTool.position = E2

    def run(self):
        commandTool.mainloop()


# method
def simulate():
    global checkSimulate

    left3.visible = false
    left2.visible = false
    left1.visible = false
    center.visible = false
    right1.visible = false
    right2.visible = false
    right3.visible = false
    checkSimulate = true


def addObject():
    global recentlyAdd

    recentlyAdd = true
    l = float(commandTool.position.get())
    m = float(commandTool.mass.get())
    if bool(m < 0) | bool(l > 3) | bool(l < 0):
        if bool(m < 0):
            tkMessageBox.showinfo("Error", "Mass can't be negative value, Please re-input again")
        elif bool(l > 3):
            tkMessageBox.showinfo("Error", "A length can't be more than 3 m., Please re-input again")
        else:
            tkMessageBox.showinfo("Error", "A length can't be negative value., Please re-input again")
    else:
        rad = 12 + (m + l) / 4
        leftx = l * (-50)
        rightx = l * (50)

        if shape.get() == 1:  # box
            if side.get() == 1:  # left
                b1 = box(frame=beam, size=(17 + l, 17 + m / 4, 20), color=getColor(), mass=m)
                b1.pos = (leftx, arm.height / 2 + b1.height / 2, 0)
                b1.tag = label(pos=(leftx, 0, -10), text=str(m) + ' kg.', yoffset=180, color=b1.color)
                b1.tag.visible = false
                checkPosition(b1)

            elif side.get() == 2:  # right
                b2 = box(frame=beam, size=(17 + l, 17 + m / 4, 20), color=getColor(), mass=m)
                b2.pos = (rightx, arm.height / 2 + b2.height / 2, 0)
                b2.tag = label(pos=(rightx, 0, -10), text=str(m) + ' kg.', yoffset=180, color=b2.color)
                b2.tag.visible = false
                checkPosition(b2)

        elif shape.get() == 2:  # sphere
            if side.get() == 1:  # left
                s1 = sphere(frame=beam, radius=rad, color=getColor(), mass=m)
                s1.pos = (leftx, arm.height / 2 + rad, 0)
                s1.tag = label(pos=(leftx, 0, -10), text=str(m) + ' kg.', yoffset=180, color=s1.color)
                s1.tag.visible = false
                checkPosition(s1)

            elif side.get() == 2:  # right
                s2 = sphere(frame=beam, radius=rad, pos=(rightx, rad, 0), color=getColor(), mass=m)
                s2.pos = (rightx, arm.height / 2 + rad, 0)
                s2.tag = label(pos=(rightx, 0, -10), text=str(m) + ' kg.', yoffset=180, color=s2.color)
                s2.tag.visible = false
                checkPosition(s2)


def reset():
    global checkSimulate
    global beam
    global angle_
    global keep
    global moment_total
    global moment_left
    global moment_right
    global acceleration
    global velocity

    for obj in keep:
        obj.visible = false
        obj.tag.visible = false
    del keep[:]
    beam.rotate(angle=-angle_, axis=(0, 0, 1))
    left3.visible = true
    left2.visible = true
    left1.visible = true
    center.visible = true
    right1.visible = true
    right2.visible = true
    right3.visible = true
    moment_total.text = 'Total of moment: 0.0'
    moment_left.text = 'Moment on left side: 0.0'
    moment_right.text = 'Moment on right side: 0.0'
    acceleration.text = 'Angular acceleration: 0.0'
    velocity.text = 'Angular velocity: 0.0'
    angle_ = 0.
    checkSimulate = false


def checkPosition(target):
    global keep

    for obj in keep:
        if target.pos.x == obj.pos.x:
            target.visible = false
            tkMessageBox.showinfo("Error", "There is an object on this position before")
            break

    keep.append(target)


def getColor():
    global colorlist

    color_random = random.choice(colorlist)
    colorlist.remove(color_random)
    if len(colorlist) == 0:
        colorlist = [color.magenta, color.orange, color.blue, color.cyan, color.green, color.red, color.yellow]
    return color_random


def sel():
    # nothing
    return


# run window
ct = CT()
ct.start()

touchGround = false

# run program
while true:
    rate(100)
    if checkSimulate == true:
        if recentlyAdd:
            moment = 0
            momentleft = 0
            momentright = 0
            for obj in keep:
                temp = (obj.pos.x / 50) * obj.mass * g
                moment += temp
                if temp < 0:
                    momentleft += -temp
                else:
                    momentright += temp
            moment_total.text = 'Total of moment: ' + str(moment)
            moment_left.text = 'Moment on left side: ' + str(momentleft)
            moment_right.text = 'Moment on right side:' + str(momentright)
            recentlyAdd = false
            touchGround = false
        for obj in keep:
            obj.tag.visible = true
            obj.tag.pos = beam.frame_to_world(obj.pos)
        if len(keep) != 0:
            angularAcceleration = moment / I  # I*alpha = sigmaFr , alpha = sigmaFr/I
            rotatedt = angularVelocity * dt
            canLowLeft = angle_- rotatedt <= criticaltheta and angle_ > 0 and not touchGround
            canLowRight = angle_ - rotatedt >= -criticaltheta and angle_ < 0 and not touchGround
            canUpLeft = angularAcceleration > 0 and touchGround
            canUpRight = angularAcceleration < 0 and touchGround
            if canUpLeft or canUpRight:
                touchGround = false
            if (canLowLeft or canLowRight or angle_ == 0) and not touchGround:
                angularVelocity += angularAcceleration * dt
                beam.rotate(angle=-rotatedt, axis=(0, 0, 1))
                angle_ -= rotatedt
            else:
                if angle_ != 0:
                    angularVelocity = 0  # if a beam touches the ground, it means that angular velocity = 0
                    angularAcceleration = 0
                    touchGround = true
            acceleration.text = 'Angular acceleration: ' + str(angularAcceleration)
            velocity.text = 'Angular velocity: ' + str(angularVelocity)
        else:
            acceleration.text = 'Angular acceleration: 0.0'
            velocity.text = 'Angular velocity: 0.0'
