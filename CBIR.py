# Denise Moran, 1367222
# CSS 490 Spring 2017
# Assignment 2

# Please help figure out the problem if you have time, I have been
# working on this for so long and cannot figure out how to get the
# correct weight or picture results. Any help would be much
# appreciated. Thank You.

from Tkinter import *
from PIL import ImageTk, Image
import sys, glob, os, math, numpy

# Content Based Image Retrieval class (GUI)
class CBIR(Frame):
    def __init__(self, root,pix):

        # variables
        self.pix = pix
        self.imageList = pix.get_imageList()
        self.photoList = pix.get_photoList()
        self.intenBins = pix.get_intenCode()
        self.colorBins = pix.get_colorCode()
        self.allBins = []
        self.xmax = pix.get_xmax()+20
        self.ymax = pix.get_ymax()+10
        self.bgc = '#0c0c0c'
        self.btc = '#161616'
        self.abtc= '#c6ffeb'
        self.fgc = '#ffffff'
        self.bth = 10
        self.currentPage = 0
        self.currentPhotoList = pix.get_photoList()
        self.currentImageList = pix.get_imageList()
        self.totalPages = self.get_totalPages()
        self.checkList = dict()
        self.iteration = 0
        self.weights = []

        # main frame
        self.mainframe = Frame(root,bg=self.bgc)
        self.mainframe.pack()

        # section frames
        self.topFrame = Frame(self.mainframe,bg=self.bgc)
        self.topFrame.pack(side=RIGHT)
        self.bottomFrame = Frame(self.mainframe,bg=self.bgc)
        self.bottomFrame.pack(side = LEFT)

        # selected image
        self.selectedView = Label(self.topFrame,width=450,
                                       height=pix.get_y(),bg=self.bgc)
        self.selectedView.pack(side=TOP)
        self.update_preview(self.imageList[0].filename)
        
        # control panel
        self.controlPanel = Frame(self.topFrame,bg=self.bgc)
        self.controlPanel.pack()
        self.b_cc = Button(self.controlPanel,text="Color Code search",
                           width=40,pady=self.bth,border=0,bg=self.btc,
                           fg=self.fgc,activebackground=self.abtc,
                           command=lambda:self.find_distance("CC"))
        self.b_cc.pack()
        self.l1 = Label(self.controlPanel,bg=self.bgc,text=' ')
        self.l1.pack()
        self.b_inten = Button(self.controlPanel,text="Intensity search",
                           width=40,border=0,pady=self.bth,bg=self.btc,
                           fg=self.fgc,activebackground=self.abtc,
                           command=lambda:self.find_distance("inten"))
        self.b_inten.pack()
        self.l2 = Label(self.controlPanel,bg=self.bgc,text=' ')
        self.l2.pack()
        self.b_rf = Button(self.controlPanel,text="Color Code + Intensity",
                           width=40,pady=self.bth,border=0,bg=self.btc,
                           fg=self.fgc,activebackground=self.abtc,
                           command=lambda:self.find_distance("CC+inten"))
        self.b_rf.pack()
        self.l3 = Label(self.controlPanel,bg=self.bgc,text=' ')
        self.l3.pack()
        self.b_reset = Button(self.controlPanel,text="Reset",
                           width=40,pady=self.bth,border=0,bg=self.btc,
                           fg=self.fgc,activebackground=self.abtc,
                           command=lambda:self.reset())
        self.b_reset.pack()
        self.l4 = Label(self.controlPanel,bg=self.bgc,text=' ')
        self.l4.pack()

        # results frame
        self.resultFrame = Frame(self.bottomFrame,bg=self.bgc)
        self.resultFrame.pack()
        instr = Label(self.resultFrame,bg=self.bgc,fg='#aaaaaa',
                text="Click image to select. Checkboxes indicate relevance.")
        instr.pack()
        self.canvas = Canvas(self.resultFrame,bg=self.bgc,
                highlightthickness=0)

        # page navigation
        self.pageButtons = Frame(self.bottomFrame,bg=self.bgc)
        self.pageButtons.pack()
        self.b_prev = Button(self.pageButtons,text="<< Previous page",
                            width=30,border=0,bg=self.btc,
                            fg=self.fgc,activebackground=self.abtc,
                            command=lambda:self.prevPage())
        self.b_prev.pack(side=LEFT)
        self.pageLabel = Label(self.pageButtons,
                            text="Page 1 of " + str(self.totalPages),
                            width=43,bg=self.bgc,fg='#aaaaaa')
        self.pageLabel.pack(side=LEFT)
        self.b_next = Button(self.pageButtons,text="Next page >>",
                            width=30,border=0,bg=self.btc,
                            fg=self.fgc,activebackground=self.abtc,
                            command=lambda:self.nextPage())
        self.b_next.pack(side=RIGHT)        

        self.reset()
        
    # resets the GUI
    def reset(self):
        self.iteration = 0
        self.weights = []
        # clear checkboxes
        for img in self.imageList:
            self.checkList[img.filename] = IntVar()
            self.checkList[img.filename].set(0)
            
        # initial display photos
        self.update_preview(self.imageList[0].filename)
        self.currentImageList = self.imageList
        self.currentPhotoList = self.photoList
        il = self.currentImageList[:20]
        pl = self.currentPhotoList[:20]
        self.update_results((il, pl))
                
        
    # find selected image position
    def get_pos(self,filename):
        pos = -1
        for i in xrange(len(self.imageList)):
            f=self.imageList[i].filename.replace("\\","/")
            if filename == f:
                pos = i
        return pos

    # returns a normalized matrix for the 1st iteration
    def normalize(self,matrix):
        f,s,min_s = [],[],0
        for i in xrange(len(matrix)):
            for j in xrange(len(matrix[i])):
                f_j = [matrix[i][j]]
                if len(f) <= j:
                    f.append(f_j)
                else:
                    f[j].append(matrix[i][j])  
        u = [reduce(lambda x,y: x + y, l) / len(l) for l in f]
        for i in xrange(len(f)):
            std = numpy.std(f[i])
            if i == 0:
                min_s = std
            elif std < min_s:
                min_s = std
            s.append(std)
        n_matrix = []
        for i in xrange(len(matrix)):
            v = []
            n_matrix.append(v)
            for j in xrange(len(matrix[i])):
                std = s[j]
                if std == 0:
                    if u[j] != 0:
                        std = min_s * 0.5
                    else:
                        std = 0.0000001
                norm = (matrix[i][j] - u[j]) / std
                v.append(norm)      
        return n_matrix
    
    # averages the feature values over size for each image
    def average_values(self,matrix):
        newMatrix = []
        for i in xrange(len(matrix)):
            x,y = self.imageList[i].size
            size = x * y
            features = [feat / float(size) for feat in matrix[i]]
            newMatrix.append(features)
        return newMatrix

    # gets the weights from user feedback checkbox
    # and updates the weight for each feature
    def normalize_weight(self):
        feedback,f,s,w,i,min_s = [],[],[],[],0,0
        # finds all checked images and saves feature vectors
        feedback.append(self.allBins[self.get_pos(self.selected.filename)])
        for k,v in self.checkList.iteritems():
            if v.get() == 1:
                print k + " selected"
                pos = self.get_pos(k)
                feedback.append(self.allBins[pos])
            i+=1

        if len(feedback) > 1:
            # get feature list
            for i in xrange(len(feedback)):
                for j in xrange(len(feedback[i])):
                    if len(f) <= j:
                        f.append([feedback[i][j]])
                    else:
                        f[j].append(feedback[i][j])  
            u = [reduce(lambda x,y: x + y, l) / len(l) for l in f]

            # get standard deviations
            for i in xrange(len(f)):
                s.append(numpy.std(f[i]))
            min_s = min(filter(lambda a: a != 0,s))

            # get updated weights 1 / stdev
            w = [0.0] * len(f)
            for i in xrange(len(f)):
                if s[i] == 0 and u[i] == 0:
                    w[i] = 0
                elif s[i] == 0 and u[i] != 0:
                    w[i] = 1 / float(min_s * 0.5)
                else:
                    w[i] = 1 / float(s[i])

            # get sum of updated weights
            sum_w = reduce(lambda a,b: a + b,w)

            # get normalized weight wi / sum(wi)
            for i in xrange(len(self.weights)):
                self.weights[i] = w[i] / sum_w

            # prints out value of selected image and
            # resulting weights, could not figure out
            # why the weights are causing incorrect results
            for a,b,c in zip(feedback[0],s,self.weights):
                print str(a) + "\t" + str(b)+ "\t"+ str(c)
        
    # calculates manhattan distance
    def find_distance(self,method):
        pos = self.get_pos(self.selected.filename)
        all_vals,results = [],[]
        
        if method == 'inten':
            all_vals = self.average_values(self.intenBins)
        if method == 'CC':
            all_vals = self.average_values(self.colorBins)
        if method == 'CC+inten':
            if self.iteration == 0:
                for i in xrange(len(self.imageList)):
                    vals = self.intenBins[i] + self.colorBins[i]
                    all_vals.append(vals)
                all_vals = self.average_values(all_vals)
                all_vals = self.normalize(all_vals)
                self.allBins = all_vals
                self.weights = [1/float(len(self.imageList))]*len(all_vals[0])
            else:
                all_vals = self.allBins
                self.normalize_weight()
            self.iteration += 1
            
        i_vals = all_vals[pos]
        
        for i in xrange(len(all_vals)):
            if i != pos:
                d = 0.0
                k_vals = all_vals[i]
                for j in range(len(i_vals)):
                    d_i = abs(float(i_vals[j]) - float(k_vals[j]))
                    if method == 'CC+inten':
                        d_i *= self.weights[j]
                    d += d_i
                #print self.imageList[i].filename + "\t" + str(d)
                self.insertTo(results,(d,i))

        self.currentImageList,self.currentPhotoList = [],[]
        for img in results:
            self.currentImageList.append(self.imageList[img[1]])
            self.currentPhotoList.append(self.photoList[img[1]])
        
        iL = self.currentImageList[:20]
        pL = self.currentPhotoList[:20]
        self.currentPage = 0
        self.update_results((iL,pL))

    # inserts a tuple in order to arg array    
    def insertTo(self,arr,tup):
        # tup[0] = distance value, [1] = image number
        if len(arr) == 0:
            arr.insert(0,tup) 
        else:
            for i in range(len(arr)):
                if tup[0] < arr[i][0]:
                    arr.insert(i,tup)
                    return   
            arr.insert(len(arr),tup)
            
    # updates the photos in results window (used from sample)   
    def update_results(self,st):
        self.pageLabel.configure(text="Page " + str(self.currentPage+1) \
                                 + " of " + str(self.totalPages))
        cols = 5
        self.canvas.delete(ALL)
        self.canvas.config(width=(self.xmax)*5,height=self.ymax*4)
        self.canvas.pack()

        photoRemain = []
        for i in xrange(len(st[0])):
            f = st[0][i].filename
            img = st[1][i]
            photoRemain.append((f,img))

        rowPos = 0
        while photoRemain:
            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            for (filename, img) in photoRow:
                frame = Frame(self.canvas,bg=self.bgc,border=0)
                frame.pack()
                link = Button(frame,image=img,border=0,
                    bg=self.bgc,width=self.pix.get_xmax(),
                    activebackground=self.bgc)
                handler = lambda f=filename: self.update_preview(f)
                link.config(command=handler)
                link.pack(side=LEFT)
                chkBtn = Checkbutton(frame,variable=self.checkList[filename],
                    bg=self.bgc,bd=0,onvalue=1,offvalue=0,
                    activebackground=self.bgc)
                chkBtn.pack(side=BOTTOM)
                self.canvas.create_window(
                    colPos,
                    rowPos,
                    anchor=NW,
                    window=frame, 
                    width=self.xmax, 
                    height=self.ymax)
                colPos += self.xmax
            rowPos += self.ymax

    # updates the selected image window
    def update_preview(self,f):
        self.selected = Image.open(f.replace("\\","/"))
        self.selectedPhoto=ImageTk.PhotoImage(self.selected)
        self.selectedView.configure(image=self.selectedPhoto)

    # updates results page to previous page
    def prevPage(self):
        self.currentPage-=1
        if self.currentPage < 0:
            self.currentPage = self.totalPages-1
        start = self.currentPage * 20
        end = start + 20
        iL = self.currentImageList[start:end]
        pL = self.currentPhotoList[start:end]
        self.update_results((iL,pL))

    # updates results page to next page
    def nextPage(self):
        self.currentPage+=1
        if self.currentPage >= self.totalPages:
            self.currentPage = 0
        start = self.currentPage * 20
        end = start + 20
        iL = self.currentImageList[start:end]
        pL = self.currentPhotoList[start:end]
        self.update_results((iL,pL))
        
    # computes total pages in results
    def get_totalPages(self):
        pages = len(self.photoList) / 20
        if len(self.photoList) % 20 > 0:
            pages += 1
        return pages
    

# Pixel Info class (from sample code)
class PixInfo:
    def __init__(self, master):
    
        self.master = master
        self.imageList = []
        self.photoList = []
        self.xmax = 0
        self.ymax = 0
        self.x = 0
        self.y = 0
        self.colorCode = []
        self.intenCode = []
        
        # Add each image (for evaluation) into a list (from sample code)
        for infile in glob.glob('images/*.jpg'):
            file, ext = os.path.splitext(infile)
            im = Image.open(infile)
            pt = ImageTk.PhotoImage(im)
            # Resize the image for thumbnails.
            imSize = im.size
            x = imSize[0]
            y = imSize[1]
            if x > self.x:
              self.x = x
            if y > self.y:
              self.y = y
            x = imSize[0]/3
            y = imSize[1]/3
            imResize = im.resize((x, y), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(imResize)
            # Find the max height and width of the set of pics.
            if x > self.xmax:
              self.xmax = x
            if y > self.ymax:
              self.ymax = y
            # Add the images to the lists.
            self.imageList.append(im)
            self.photoList.append(photo)

        # look for saved values
        if os.path.isfile('intenVals.txt'):
            intenVals = open('intenVals.txt','r')
            for line in intenVals:
                line = line.replace("[","").replace("]","").replace(" ","").split(",")
                line = [int(x) for x in line]
                self.intenCode.append(line)
                
        if os.path.isfile('colorVals.txt'):
            colorVals = open('colorVals.txt','r')
            for line in colorVals:
                line = line.replace("[","").replace("]","").replace(" ","").split(",")
                line = [int(x) for x in line]
                self.colorCode.append(line)
                
        # compute the values
        else:
            for im in self.imageList[:]:
                pixList = list(im.getdata())
                CcBins, InBins = self.encode(pixList)
                self.colorCode.append(CcBins)
                self.intenCode.append(InBins)
                intenVals = open('intenVals.txt','w')
                colorVals = open('colorVals.txt','w')
                for i in xrange(len(self.colorCode)):
                    colorVals.write(str(self.colorCode[i]))
                    colorVals.write("\n")
                    intenVals.write(str(self.intenCode[i]))
                    intenVals.write("\n")
                intenVals.close()
                colorVals.close()
            
        
    # compute the color and intensity values
    def encode(self, pixlist):
        CcBins = [0]*64
        InBins = [0]*25
                        
        for inVal in pixlist:
            i = 0.299*inVal[0] + 0.587*inVal[1] + 0.114*inVal[2]
            targetBin = int(i/10)               # compute target bin to increment
            if targetBin > 24:
                targetBin = 24
            InBins[targetBin] += 1              # increment bin
                                        
            r,g,b = inVal[0],inVal[1],inVal[2]
            colorValue = int(str(self.msb(r))+str(self.msb(g))+str(self.msb(b)),2)
            CcBins[colorValue] += 1             # increment bin

        return CcBins, InBins

    # isolate the most significant 2 bits
    def msb(self, x):
        b = bin(x)              # convert to binary string
        b = b[2:]               # strip off 0b notation
        while (len(b) < 8):     # adds leading zeros
            b = '0' + b
        msb = b[:2]             # gets first 2
        return msb
    
    # Accessor functions (from sample code)
    def get_imageList(self):
        return self.imageList
    def get_photoList(self):
        return self.photoList
    def get_largePL(self):
        return self.largePL
    def get_xmax(self):
        return self.xmax
    def get_ymax(self):
        return self.ymax
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def get_colorCode(self):
        return self.colorCode    
    def get_intenCode(self):
        return self.intenCode
    
if __name__ == '__main__':
    my_path = os.path.abspath(__file__)
    mydir = os.path.dirname(my_path)
    start = os.path.join(mydir, "practiceGUI-3.py")
    root = Tk()
    root.resizable(width=False, height=False)
    pix = PixInfo(root)
    top = CBIR(root,pix)
    root.mainloop()
