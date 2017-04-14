# ImageViewer.py
# Program to conduct a content based image search in python
# Written by UW Faculty, edited by Denise Moran <morandy@uw.edu>


from Tkinter import *
from PixInfo import PixInfo
import math, os, subprocess, ttk              # for notebook

# Main app.
class CBIR(Frame):
    
    # Constructor.
    def __init__(self, master, pixInfo):
        
        Frame.__init__(self, master)
        self.master    = master
        self.pixInfo   = pixInfo
        self.colorCode = pixInfo.get_colorCode()
        self.intenCode = pixInfo.get_intenCode()
        # Full-sized images.
        self.imageList = pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()
        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()
        self.current = 0
        
        # Create Main frame.
        mainFrame = Frame(master)
        mainFrame.pack()
        
        
        # Create Picture chooser frame.
        listFrame = Frame(mainFrame)
        listFrame.pack(side=LEFT)
        
        
        # Create Control frame.
        controlFrame = Frame(mainFrame)
        controlFrame.pack(side=LEFT)
        
        
        # Create Preview frame.
        previewFrame = Frame(mainFrame, 
            width=self.xmax+45, height=self.ymax)
        previewFrame.pack_propagate(0)
        previewFrame.pack(side=LEFT)
        
        
        # Create Results frames.
        resultsFrame = ttk.Notebook(mainFrame)
        page1 = ttk.Frame(resultsFrame)
        page2 = ttk.Frame(resultsFrame)
        page3 = ttk.Frame(resultsFrame)
        page4 = ttk.Frame(resultsFrame)
        page5 = ttk.Frame(resultsFrame)
        self.canvas1 = Canvas(page1)
        self.canvas2 = Canvas(page2)
        self.canvas3 = Canvas(page3)
        self.canvas4 = Canvas(page4)
        self.canvas5 = Canvas(page5)
        resultsFrame.add(page1, text='Page 1')
        resultsFrame.add(page2, text='Page 2')
        resultsFrame.add(page3, text='Page 3')
        resultsFrame.add(page4, text='Page 4')
        resultsFrame.add(page5, text='Page 5')
        resultsFrame.pack(side=RIGHT)
        
        
        # Layout Picture Listbox.
        self.listScrollbar = Scrollbar(listFrame)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.list = Listbox(listFrame, 
            yscrollcommand=self.listScrollbar.set, 
            selectmode=BROWSE, 
            height=35)
        for i in range(len(self.imageList)):
            self.list.insert(i, self.imageList[i].filename)
        self.list.pack(side=LEFT, fill=BOTH)
        self.list.activate(1)
        self.list.bind('<<ListboxSelect>>', self.update_preview)
        self.listScrollbar.config(command=self.list.yview)
        
        
        # Layout Controls.
        button = Button(controlFrame, text="Inspect Pic", 
            fg="red", padx = 10, width=10, 
            command=lambda: self.inspect_pic(
                self.list.get(ACTIVE)))
        button.grid(row=0, sticky=E)
        
        self.b1 = Button(controlFrame, text="Color-Code", 
            padx = 10, width=10, 
            command=lambda: self.find_distance(method='CC'))
        self.b1.grid(row=1, sticky=E)
        
        self.b2 = Button(controlFrame, text="Intensity", 
            padx = 10, width=10, 
            command=lambda: self.find_distance(method='inten'))
        self.b2.grid(row=2, sticky=E)
    
        
        # Layout Preview.
        self.selectImg = Label(previewFrame, 
            image=self.photoList[0])
        self.selectImg.pack()
    
    
    # Event "listener" for listbox change.
    def update_preview(self, event):
    
        i = int(self.list.curselection()[0])
        self.current = i
        self.selectImg.configure(
            image=self.photoList[int(i)])
    
    
    # Find the Manhattan Distance of each image and return a
    # list of distances between image i and each image in the
    # directory uses the comparison method of the passed 
    # binList
    def find_distance(self, method):
        
        # gets the current image selected on the image viewer
        img = self.imageList[self.current]   
        print "current image: " + img.filename
        
        
        # stores values of current image (i) and comparison
        # images (k), type is indicated by method name input
        i_values = []
        allValues = []
        if (method == 'inten'):
            i_values = self.pixInfo.get_intenCode()[self.current]
            allValues = self.pixInfo.get_intenCode()
            method = "Intensity"
        if (method == 'CC'):
            i_values = self.pixInfo.get_colorCode()[self.current]
            allValues = self.pixInfo.get_colorCode()
            method = "Color code"
        print method + " values: " + str(i_values)
        
        
        # calculates distance using Manhattan algorithm
        # iterates over each image in imageList
        results = []        # saves the distances and associated index in tuples
        Mi,Ni = img.size    # selected image size
        i_size = Mi*Ni      # computes size
        for i in range(len(self.imageList)):
        
            # skips selected image, gets values ready
            if i != self.current:
                d = 0.0                             # distance float set to zero 
                Mk, Nk = self.imageList[i].size     # get k image size
                k_size = Mk*Nk
                k_values = allValues[i]             # get k image values
                  
                # iterate over each bin and compares vaules using
                # Manhattan distance algorithm, then stores the distance
                # and image index in a tuple, stored in a sorted array
                for j in range(len(i_values)):
                    d += abs((float(i_values[j]) / i_size) - (float(k_values[j]) / k_size))
                self.insertTo(results,(d,i))

        # changes tuple values to match updated_results method
        # requires (string, image) format
        sortedTup = []
        for tup in results:
            idx = tup[1]
            newTup = (self.imageList[idx].filename,self.photoList[idx])
            sortedTup.insert(len(results),newTup)
        
        sortedTup = tuple(sortedTup)        # convert list to tuple
        self.update_results(sortedTup)      # update the results frame
    
    # Update the results window with the sorted results.
    def update_results(self, sortedTup):
        
        cols = 5    # always 5x4 layout
        fullsize = (0, 0, (self.xmax*cols), (self.ymax*cols))
        
        # Initialize the canvas with dimensions equal to the 
        # number of results. All pages must get ready
        self.canvas1.delete(ALL)            # clears current screen
        self.canvas2.delete(ALL)
        self.canvas3.delete(ALL)
        self.canvas4.delete(ALL)
        self.canvas5.delete(ALL)
        
        self.canvas1.config(                # sets canvas dimensions
            width=self.xmax*cols, 
            height=self.ymax*cols/1.2)
        self.canvas2.config( 
            width=self.xmax*cols, 
            height=self.ymax*cols/1.2)
        self.canvas3.config( 
            width=self.xmax*cols, 
            height=self.ymax*cols/1.2)
        self.canvas4.config( 
            width=self.xmax*cols, 
            height=self.ymax*cols/1.2)
        self.canvas5.config( 
            width=self.xmax*cols, 
            height=self.ymax*cols/1.2)
            
        self.canvas1.pack()                 # make visible
        self.canvas2.pack()
        self.canvas3.pack()
        self.canvas4.pack()
        self.canvas5.pack()
        
        photoRemain = list(sortedTup)       # saves the results as a mutable list 
        pointer = 0                         # saves the current index
        
        # Place images on buttons, then on the canvas in order
        # by distance. Buttons envoke the inspect_pic method.
        rowPos = 0
        while photoRemain:
            
            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            for (filename, img) in photoRow:
                
                # resets row position when reached 20n images
                if (pointer == 20 or pointer == 40 or pointer == 60 or pointer == 80):
                    rowPos = 0
                    
                # page 1
                if (pointer < 20):
                    link = Button(self.canvas1, image=img)
                    handler = lambda f=filename: self.inspect_pic(f)
                    link.config(command=handler)
                    link.pack(side=LEFT, expand=YES)
                    self.canvas1.create_window(
                        colPos, 
                        rowPos, 
                        anchor=NW,
                        window=link, 
                        width=self.xmax, 
                        height=self.ymax)
                    colPos += self.xmax
                    
                # page 2
                elif (pointer < 40):
                    link = Button(self.canvas2, image=img)
                    handler = lambda f=filename: self.inspect_pic(f)
                    link.config(command=handler)
                    link.pack(side=LEFT, expand=YES)
                    self.canvas2.create_window(
                        colPos, 
                        rowPos, 
                        anchor=NW,
                        window=link, 
                        width=self.xmax, 
                        height=self.ymax)
                    colPos += self.xmax  
                      
                # page 3
                elif (pointer < 60):
                    link = Button(self.canvas3, image=img)
                    handler = lambda f=filename: self.inspect_pic(f)
                    link.config(command=handler)
                    link.pack(side=LEFT, expand=YES)
                    self.canvas3.create_window(
                        colPos, 
                        rowPos, 
                        anchor=NW,
                        window=link, 
                        width=self.xmax, 
                        height=self.ymax)
                    colPos += self.xmax
                          
                # page 4
                elif (pointer < 80):
                    link = Button(self.canvas4, image=img)
                    handler = lambda f=filename: self.inspect_pic(f)
                    link.config(command=handler)
                    link.pack(side=LEFT, expand=YES)
                    self.canvas4.create_window(
                        colPos, 
                        rowPos, 
                        anchor=NW,
                        window=link, 
                        width=self.xmax, 
                        height=self.ymax)
                    colPos += self.xmax
                          
                # page 5
                elif (pointer < 100):
                    link = Button(self.canvas5, image=img)
                    handler = lambda f=filename: self.inspect_pic(f)
                    link.config(command=handler)
                    link.pack(side=LEFT, expand=YES)
                    self.canvas5.create_window(
                        colPos, 
                        rowPos, 
                        anchor=NW,
                        window=link, 
                        width=self.xmax, 
                        height=self.ymax)
                    colPos += self.xmax
                    
                pointer += 1                # increments current index
                
            rowPos += self.ymax
    
    
    # Open the picture with the default operating system image
    # viewer. Uncomment the windows instruction to run on windows
    def inspect_pic(self, filename):
        
        # Windows
        #os.startfile(filename)
        
        # Linux
        subprocess.call(['xdg-open',filename])

    # inserts a tuple into the argument array in order
    def insertTo(self, arr, tup):
    
        # add if empty
        if len(arr) == 0:
            arr.insert(0,tup) 
            
        else:
            # put in front of the next largest value
            for i in range(len(arr)):
                if tup[0] < arr[i][0]:
                    arr.insert(i,tup)
                    return
                    
            arr.insert(len(arr),tup)        # insert at end if nothing larger

# Executable section.
if __name__ == '__main__':

    root = Tk()
    root.title('Content Based Image Retrieval Tool')
    pixInfo = PixInfo(root)
    imageViewer = CBIR(root, pixInfo)

    root.mainloop()

