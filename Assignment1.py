
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

def node_dist(n1, n2):
    dx = (n2.pos[0]-n1.pos[0])*MPERLON
    dy = (n2.pos[1]-n1.pos[1])*MPERLAT
    return math.sqrt(dx*dx+dy*dy) # in meters

class Node():
    def __init__(self,id,p):
        self.id = id
        self.pos = p
        self.ways = []
        self.waystr = None
    def __str__(self):
        if self.waystr is None:
            self.waystr = self.get_waystr()
        return str(self.pos) + ": " + self.waystr
    def get_waystr(self):
        if self.waystr is None:
            self.waystr = ""
            self.wayset = set()
            for w in self.ways:
                self.wayset.add(w.way.name)
            for w in self.wayset:
                self.waystr += w.encode("utf-8") + " "
        return self.waystr

class Edge():
    def __init__(self, w, src, d):
        self.way = w
        self.dest = d
        self.cost = node_dist(src,d)

class SearchPath():
    def __init__(self,node,way):
        self.way = way
        self.node = node

    def search(self, start, end):
        parent = []
        cost = []
        cost[start] = 0
        q = []
        q.append(node_dist(start,end),start)
        parent[start] = None

        while q.len() not 0 :
            dist, tempnode = q.pop()
            if tempnode == end:
                return self.MakePath(parent, end)
            for path in tempnode.ways:
                tempcost = node_dist(path.pos, tempnode.pos)
                if tempcost < cost[path.pos]:
                    cost[path.pos] = tempcost
                    q.append(node_dist(path.pos,end), path.pos)

    def MakePath(self,parent,end):
        node =[]
        way =[]
        temp = end
        node.append(temp)

        while parent[temp] is not None:
            prev, way = parent[temp]
            way.append(way)
            node.append(prev)
            temp = prev
        return node, way



class MyWin(Frame):
    def __init__(self,master,node,way):
        self.whatis = {}
        self.nodes = node
        self.ways = way
        self.startnode = None
        self.goalnode = None
        self.planner = SearchPath(node, way)
        thewin = Frame(master)
        w = Canvas(thewin, width=WINWIDTH, height=WINHEIGHT)  # , cursor="crosshair")
        w.bind("<Button-1>", self.mapclick)
        w.bind("<Motion>", self.maphover)
        for waynum in self.ways:
            nlist = self.ways[waynum].nodes
            thispix = self.lat_lon_to_pix(self.nodes[nlist[0]].pos)
            if len(self.nodes[nlist[0]].ways) > 2:
                self.whatis[((int)(thispix[0]), (int)(thispix[1]))] = nlist[0]
            for n in range(len(nlist) - 1):
                nextpix = self.lat_lon_to_pix(self.nodes[nlist[n + 1]].pos)
                self.whatis[((int)(nextpix[0]), (int)(nextpix[1]))] = nlist[n + 1]
                w.create_line(thispix[0], thispix[1], nextpix[0], nextpix[1])
                thispix = nextpix


        # other visible things are hiding for now...
        w.create_line(0, 0, 0, 0, fill='orange', width=3, tag='path')

        w.create_oval(0, 0, 0, 0, outline='green', fill='green', tag='startdot')
        w.create_oval(0, 0, 0, 0, outline='red', fill='red', tag='goaldot')
        w.create_oval(0, 0, 0, 0, outline='blue', fill='blue', tag='lastdot')
        w.pack(fill=BOTH)
        self.canvas = w

        cb = Button(thewin, text="Clear", command=self.clear)
        cb.pack(side=RIGHT, pady=5)

        sb = Button(thewin, text="Plan!", command=self.plan_path)
        sb.pack(side=RIGHT, pady=5)

        nodelablab = Label(thewin, text="Node:")
        nodelablab.pack(side=LEFT, padx=5)

        self.nodelab = Label(thewin, text="None")
        self.nodelab.pack(side=LEFT, padx=5)

        elablab = Label(thewin, text="Elev:")
        elablab.pack(side=LEFT, padx=5)

        self.elab = Label(thewin, text="0")
        self.elab.pack(side=LEFT, padx=5)

        thewin.pack()

def read_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    node = dict()
    way = dict()

    for item in root:
        # we will need nodes and ways, here we look at a way:
        if item.tag == 'way':
            usable = False
            name = "unknown"

            for subitem in item:
                if subitem.tag == 'tag' and subitem.get('k') == 'highway':
                    usable = True
                if subitem.tag == 'tag' and subitem.get('k') == 'name':
                    name = subitem.get('v')

            if usable:
                way[item.get('id')] = name
                nlist = []
                for subitem in item:
                    if subitem.tag == 'nd':
                        nlist.append(subitem.get('ref'))

        elif item.tag == 'node':
            point = ((float)(item.get('lat')),(float)(item.get('lon')))
            node[(item.get('id'))] = Node(item.get('id'), point)

            thisn = nlist[0]
            for n in range(len(nlist) - 1):
                nextn = nlist[n + 1]
                node[thisn].ways.append(Edge(way[(item.get('id'))], node[thisn], node[nextn]))
                thisn = nextn
            thisn = nlist[-1]
            for n in range(len(nlist) - 2, -1, -1):
                nextn = nlist[n]
                node[thisn].ways.append(Edge(way[(item.get('id'))], node[thisn], node[nextn]))
                thisn = nextn
            way[(item.get('id'))].nodes = nlist

    return node, way

def main():
    node, way = read_xml("dbv.osm")

    master = Tk()
    line = (60,10,70,20)
    circle = (120,150,130,160)
    thewin = MyWin(master,node,way)

    # in Python you have to start the event loop yourself:
    mainloop()

if __name__ == "__main__":
    main()
