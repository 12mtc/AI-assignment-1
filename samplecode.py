
# for GUI things
from tkinter import *
# for parsing XML
import xml.etree.ElementTree as ET
# for math
import math

# some constants about the earth
MPERLAT = 111000 # meters per degree of latitude, approximately
MPERLON = MPERLAT * math.cos(42*math.pi/180) # meters per degree longitude at 42N

WINWIDTH = 200
WINHEIGHT = 200

class MyWin(Frame):
    def __init__(self,master,line,circle):
        thewin = Frame(master)
        w = Canvas(thewin, width=WINWIDTH, height=WINHEIGHT, cursor="crosshair")

        # callbacks for mouse events in the window, if you want:
        w.bind("<Button-1>", self.mapclick)
        #w.bind("<Motion>", self.maphover)

        # do whatever you need to do for this, lines are just defined by four pixel values
        # x1 y1 x2 y2 (and can continue x3 y3 ...)
        w.create_line(line[0], line[1], line[2], line[3])

        w.create_line(20,20,40,40,30,60,70,90)

        # same for circles (ovals), give the bounding box - for both circles and lines
        # we can pass in a tuple directly for the coordinates.
        w.create_oval(circle, outline='blue',fill='green',tag='greendot')
        # by giving it a tag we can easily poke it later (see callback)

        w.pack(fill=BOTH) # put canvas in window, fill the window

        self.canvas = w # save the canvas object to talk to it later

        cb = Button(thewin, text="Button", command=self.click)
        # put the button in the window, on the right
        # I really have not much idea how Python/Tkinter layout managers work
        cb.pack(side=RIGHT,pady=5)

        thewin.pack()

    def click(self):
        print ("Clicky!")

    def mapclick(self,event):
        self.canvas.coords('greendot',event.x-5,event.y-5,event.x+5,event.y+5)

def read_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    for item in root:
        # we will need nodes and ways, here we look at a way:
        if item.tag == 'way':
            # in OSM data, most info we want is stored as key-value pairs
            # inside the XML element (not as the usual XML elements) -
            # so instead of looking for a tag named 'name', we look for a tag
            # named 'tag' with a key inside it called 'name'
            print("lat : " + item.get())
            for subitem in item:
                if subitem.tag == 'tag' and subitem.get('k') == 'name':
                    # also note names are Unicode strings, depends on your system how
                    # they will look, I don't care too much.
                    print ("Name is " +  subitem.get('v'))
                    break

def main():
    read_xml("dbv.osm")

    master = Tk()
    line = (60,10,70,20)
    circle = (120,150,130,160)
    thewin = MyWin(master,line,circle)

    # in Python you have to start the event loop yourself:
    mainloop()

if __name__ == "__main__":
    main()
