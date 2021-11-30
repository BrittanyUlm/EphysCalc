# vis
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import pyabf
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import Pmw
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

colordict = {}
colordict['red'] = 'r'
colordict['blue'] = 'b'
colordict['green'] = 'g'
colordict['magenta'] = 'm'
colordict['cyan'] = 'c'
colordict['orange'] = 'orange'

colorlist = ['red','blue','green','magenta','cyan','orange']

root = Tk()
root.title("Ephys Visualization")

Label(root, font='Calibri 12 bold',text="Use this tool to visualize the data").grid(columnspan=4, row=2,padx=10)
Label(root, font='Calibri 12 bold', text="Default peak parameters  are: min 20 frames between peaks, peak minimum -5mV. To change this, specify below:").grid(columnspan=4, row=3,padx=10)

Label(root, text="Frames between:").grid(column=1, row=4,padx=10,pady=10)
setwidth = StringVar()
setwidth_entry = Entry(root,width=10,textvariable=setwidth).grid(row=4,column=2)

Label(root, text="Peak minimum:").grid(column=3, row=4,padx=10,pady=10)
setheight = StringVar()
setheight_entry = Entry(root,width=10,textvariable=setheight).grid(row=4,column=4)


Label(root, foreground='green',font='Calibri 12 bold',text="This GUI was assembled by Brittany Ulm, and can be found on her GitHub account. Please cite me! https://github.com/BrittanyUlm").grid(column=1, row=5, columnspan=4,padx=10,pady=10)
Label(root, font='Calibri 12 bold',text='Select start and end times (seconds) to choose range for visualization').grid(row=7,columnspan=4)

Label(root,text='Start (sec)').grid(column=1,row=8)
setstart = StringVar()
setstart_entry = Entry(root, width=10,textvariable=setstart).grid(column=2,row=8)

Label(root,text='Duration (sec)').grid(column=3,row=8)
setend = StringVar()
setend_entry = Entry(root, width=10,textvariable=setend).grid(column=4,row=8)

be = StringVar()
pcol = StringVar()
tcol = StringVar()

def run():
    p = Path(fd.askdirectory())
    filelist = list(p.glob('**/*.abf'))
    filenamelist = []
    for x in range(np.array(filelist).shape[0]):
        filenamelist.append(str(filelist[x]))
    Label(root,text='Choose file:').grid(row=9,column=1)
    Pmw.OptionMenu(root,menubutton_textvariable=be,items=filenamelist).grid(row=9,column=2,columnspan=3)

def see():
    Label(root, text='Peak marker color:').grid(row=12,column=1,sticky=E)
    Pmw.OptionMenu(root,menubutton_textvariable=pcol,items=colorlist).grid(row=12,column=2,sticky=W)
    if pcol.get() != '':
        peakcolor = colordict[pcol.get()]
    else:
        peakcolor = 'm'
    Label(root,text='Trough marker color:').grid(row=12,column=3,sticky=E)
    Pmw.OptionMenu(root,menubutton_textvariable=tcol,items=colorlist).grid(row=12,column=4,sticky=W)
    if tcol.get() != '':
        troughcolor = colordict[tcol.get()]
    else:
        troughcolor = 'orange'

    if setwidth.get() != '':
        widthval = int(setwidth.get())
    else:
        widthval = 20
    if setheight.get() != '':
        heightval = int(setheight.get())
    else:
        heightval = -5
    name = be.get()
    rec = pyabf.ABF(name)
    begin = int(setstart.get())*rec.dataRate
    end = int(setend.get())*rec.dataRate
    why = rec.sweepY[begin:end]
    if len(rec.sweepY) < end:
        Label(text=str('Recording not that long'))
    peaks,h = find_peaks(why,distance=widthval, height=heightval)

    trs,u = find_peaks(-why,distance=widthval, height=heightval)
    vals = pd.Series(range(len(why)))/rec.dataRate
    peakdf = pd.DataFrame(why[peaks],peaks/rec.dataRate)
    tdf = pd.DataFrame(why[trs],trs/rec.dataRate)
        
    peaklist = list(peakdf.index)
    trlist = list(tdf.index)
    fintrdict = {}
    for x in range(len(peaklist)-1):
        eatrlist = []
        for y in range(len(trlist)):
            if trlist[y] > peaklist[x]:
                if trlist[y] < peaklist[x+1]:
                    eatrlist.append((trlist[y],tdf[0][trlist[y]]))
        t = pd.DataFrame(eatrlist)
        fintrdict[t[0][t[1].idxmin()]] = t[1][t[1].idxmin()]
    troughdf = pd.Series(fintrdict)

    linedf = pd.DataFrame(why,vals)
    fig = Figure(figsize=(9, 4), dpi=100)
    ax = fig.add_subplot()
    ax.plot(linedf,color='grey')
    ax.plot(peakdf,'^',color=peakcolor)
    ax.plot(troughdf,'v',color=troughcolor)
    ax.set_xlabel("time (seconds)")
    ax.set_title(str(rec.abfID))
    canvas = FigureCanvasTkAgg(fig, master=root)  
    canvas.draw()

    canvas.get_tk_widget().grid(row=14,columnspan=5)
    
ttk.Button(root, text="Choose folder", command=run).grid(column=4, row=6)
ttk.Button(root, text='Update Plot',command=see).grid(column=4,row=11)

root.mainloop()
