#calculator
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import pyabf
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt
import Pmw

root = Tk()

root.title("Brittany's Spontaneous Recording Calculator")
#root.geometry('1000x1000')

Label(root, font='Calibri 12 bold',text="Type in the name of the file with the start and stop times:").grid(columnspan=4, row=2,padx=10)
timefiley = StringVar(root)
timefile_entry = ttk.Entry(root,width=10,textvariable=timefiley).grid(row=2,column=4)

Label(root, font='Calibri 12 bold',text="NOTE: column names are: File name, Start, Stop").grid(columnspan=4, row=3,padx=10)
Label(root, font='Calibri 12', text='NOTE: times must be listed in seconds').grid(columnspan=4, row=4,padx=10)
Label(root, font='Calibri 12', text='NOTE: file names must match those in the folder (if not in file, will not save the file’s output)',wraplength=600).grid(columnspan=4, row=5,padx=10)

Label(root, font='Calibri 12', text='Outputs: Firing rates in peaks per second (Hz.csv), Inter-spike interval (isi.csv), Inter-spike interval coefficient of variation (isicova.csv), Mean peak height (ph.csv), Mean 1/2 peak height (hph.csv), mean 1/2 peak width (hpw.csv), and mean trough height (t.csv).',wraplength=600).grid(columnspan=4, row=6,padx=10)

Label(root, font='Calibri 12 bold', text="Default peak parameters  are: min 20 frames between peaks, peak minimum -5mV. To change this, specify below:",wraplength=600).grid(columnspan=4, row=7,padx=10)

Label(root, text="Frames between:").grid(column=1, row=8,padx=10,pady=10)
setwidth = StringVar()
setwidth_entry = Entry(root,width=10,textvariable=setwidth).grid(row=8,column=2)

Label(root, text="Peak minimum:").grid(column=3, row=8,padx=10,pady=10)
setheight = StringVar()
setheight_entry = Entry(root,width=10,textvariable=setheight).grid(row=8,column=4)

Label(root, foreground='green',font='Calibri 12 bold',text="This GUI was assembled by Brittany Ulm, and can be found on her GitHub account. Please cite me! https://github.com/BrittanyUlm").grid(column=1, row=13, columnspan=4,padx=10,pady=10)

clicknum = IntVar()
click = Checkbutton(root,text="Check if you want to save PDFs of the peaks detected",variable=clicknum,onvalue=1,offvalue=0).grid(row=9,column=1,columnspan=2)

choice = StringVar()
Pmw.OptionMenu(root,menubutton_textvariable=choice,items=('Whole time','Subset')).grid(row=9,column=4)
Label(root, text="If yes, for the time analyzed or just a portion thereof?").grid(row=9,column=3)

Label(root,text='Start (sec, relative to time set)').grid(column=1,row=10)
setstart = StringVar()
setstart_entry = Entry(root, width=10,textvariable=setstart).grid(column=2,row=10)

Label(root,text='Duration (sec)').grid(column=3,row=10)
setend = StringVar()
setend_entry = Entry(root, width=10,textvariable=setend).grid(column=4,row=10)

def run():
    if setwidth.get() != '':
        widthval = int(setwidth.get())
    else:
        widthval = 20
    if setheight.get() != '':
        heightval = int(setheight.get())
    else:
        heightval = -5
    p = Path(fd.askdirectory())
    filelist = list(p.glob('**/*.abf'))
    filenamelist = []
    for x in range(np.array(filelist).shape[0]):
        filenamelist.append(str(filelist[x]))
    if 'csv' in timefiley.get():
        timefilefullname = str(str(p)+'/'+str(timefiley.get()))
        times = pd.read_csv(timefilefullname)
    hzdict = {}
    isidict = {}
    isicovadict = {}
    phdict = {}
    hphdict = {}
    hpwdict = {}
    tdict = {}
    total = len(filenamelist)
    counter = 0
    for file in filenamelist:
        counter = counter+1
        Label(text='Progress:').grid(row=21,column=1)
        Label(text = str('working on '+str(counter)+' of '+str(total))).grid(row=21,column=2,columnspan=2)
        rec = pyabf.ABF(file)
        if 'csv' in timefiley.get():
            for x in range(len(times)):
                if times['File name'][x] in file:
                    begin = int(times['Start'][x]*rec.dataRate)
                    end = int(times['Stop'][x]*rec.dataRate)
        else:
            Label(root,foreground='red',text='Choose a file and make sure it is in folder').grid(column=4,row=3)
            break
        why = rec.sweepY[begin:end]
        if len(rec.sweepY) < end:
            Label(text=str('Error, re-check time for '+str(rec.abfID)))
        peaks, heights = find_peaks(why,distance=widthval, height=heightval)

        trs, u = find_peaks(-why,distance=widthval, height=heightval)
        vals = pd.Series(range(len(why)))
        linedf = pd.DataFrame(why,vals)
        peakdf = pd.DataFrame(why[peaks],peaks)
        tdf = pd.DataFrame(why[trs],trs)
        
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
        tdict[rec.abfID] = np.nanmean(troughdf)

        results_half = peak_widths(why, peaks, rel_height=0.5)
        half_widths = results_half[0]
        half_heights = results_half[1]
        if len(peaks) >=1:
            hzdict[rec.abfID] = len(peaks)/((end-begin)/rec.dataRate)
            phdict[rec.abfID] = np.nanmean(heights['peak_heights'])
            hphdict[rec.abfID] = np.nanmean(half_heights)
            hpwdict[rec.abfID] = np.nanmean(half_widths)
            if len(peaks) >= 2:
                isivals = []
                for x in range(len(peaks)-1):
                    isivals.append(peaks[x+1] - peaks[x])
                isioverall = np.nanmean(isivals)/rec.dataRate
                isisd = np.array(isivals).std()
                isidict[rec.abfID] = isioverall
                isicovadict[rec.abfID] = isisd/isioverall
            elif len(peaks) <2:
                isidict[rec.abfID] = 'NA'
                isicovadict[rec.abfID] = 'NA'
        else:
            hzdict[rec.abfID] = 'NA'
            phdict[rec.abfID] = 'NA'
            hphdict[rec.abfID] = 'NA'
            hpwdict[rec.abfID] = 'NA'
        if clicknum.get() == 1:        #PLOTTING
            pdfname = str(rec.abfID)+'.pdf'
            if choice.get() == 'Whole time':
                vals = pd.Series(range(len(why)))/int(rec.dataRate)
                linedf = pd.DataFrame(why,vals)
                peakdf = pd.DataFrame(why[peaks],peaks/rec.dataRate)
                plt.plot(linedf,color='grey')
                plt.plot(peakdf,'^',color='m')
                plt.plot(troughdf,'v',color='c')
                plt.xlabel('Time (seconds)')
                plt.title(str(rec.abfID))
                plt.savefig(pdfname)
                print(pdfname)
                plt.close()
            else:
                newstart = int(int(setstart.get())*rec.dataRate)
                newend = int(newstart+(int(setend.get())*rec.dataRate))
                newhy = why[newstart:newend]
                newpeaks,  = find_peaks(newhy,distance=widthval, height=heightval)
                vals = pd.Series(range(len(newhy)))/rec.dataRate
                linedf = pd.DataFrame(newhy,vals)
                peakdf = pd.DataFrame(newhy[newpeaks],newpeaks/rec.dataRate)
                trs, = find_peaks(-newhy,distance=widthval, height=heightval)
                tdf = pd.DataFrame(newhy[trs],trs/rec.dataRate)

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

                plt.plot(linedf,color='grey')
                plt.plot(peakdf,'^',color='m')
                plt.plot(troughdf,'v',color='c')
                plt.xlabel('Time (seconds)')
                plt.savefig(pdfname)
                print(pdfname)
                plt.close()
    hzdf = pd.DataFrame.from_dict(hzdict,orient='index')
    hzdf.to_csv(str(str(p)+'/Hz.csv'))

    phdf = pd.DataFrame.from_dict(phdict,orient='index')
    phdf.to_csv(str(str(p)+'/ph.csv'))

    hphdf = pd.DataFrame.from_dict(hphdict,orient='index')
    hphdf.to_csv(str(str(p)+'/hph.csv'))

    hpwdf = pd.DataFrame.from_dict(hpwdict,orient='index')
    hpwdf.to_csv(str(str(p)+'/hpw.csv'))

    isidf = pd.DataFrame.from_dict(isidict,orient='index')
    isidf.to_csv(str(str(p)+'/isi.csv'))

    isicovadf = pd.DataFrame.from_dict(isicovadict,orient='index')
    isicovadf.to_csv(str(str(p)+'/isicova.csv'))

    troughfinaldf = pd.DataFrame.from_dict(tdict,orient='index')
    troughfinaldf.to_csv(str(str(p)+'/tdf.csv'))
    Label(font = 'Calibri 12 bold',text = 'DONE!',foreground='red',background='black',width=12).grid(row=21,column=2,columnspan=2)

ttk.Button(root, text="Run", command=run).grid(column=4, row=21)

root.mainloop()
