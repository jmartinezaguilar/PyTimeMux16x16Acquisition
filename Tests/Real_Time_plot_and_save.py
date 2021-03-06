# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 12:19:57 2018

@author: user
"""

import matplotlib.pylab as plt
import numpy as np
import time
from PhyREC.NeoInterface import NeoSegment, NeoSignal
import PhyREC.PlotWaves as Rplt
import quantities as pq
from itertools import  cycle
import h5py
import os
import multiprocessing as mp


AxesProp = {
            'ylim': (-1, 1),
            'facecolor': '#FFFFFF00',
            'autoscaley_on': True,
            'xaxis': {'visible': False,
                      },
            'yaxis': {'visible': False,
                      },
            'ylabel': '',
            'title': None,
            }

FigProp = {'tight_layout': True,
           'size_inches': (10, 5),
#               'facecolor': '#FFFFFF00',
           }


class FileBuffer():
    def __init__(self, FileName, BufferSize, nChannels, Fs):
        os.remove(FileName)
        self.FileName = FileName
        self.h5File = h5py.File(FileName, 'w')
        self.Dset = self.h5File.create_dataset('data',
                                               shape=(0, nChannels),
                                               maxshape=(None, nChannels),
                                               compression="gzip")

        self.Buffer = np.ndarray((BufferSize, nChannels))
        self.BufferSize = BufferSize
        self.nChannels = nChannels
        self.Ind = 0
        self.Sigs = []
        self.Ts = 1/float(Fs)
        self.Fs = float(Fs)

        for i in range(nChannels):
            self.Sigs.append(NeoSignal(signal=self.Buffer[:, i],
                                       units='V',
                                       sampling_rate=Fs*pq.Hz,
                                       t_start=0*pq.s,
                                       copy=False,
                                       name='ch{}'.format(i)))

    def AddSample(self, Sample):
        self.Buffer[self.Ind, :] = Sample
        self.Ind += 1
        if self.Ind == self.BufferSize:
            self.Ind = 0

            FileInd = self.Dset.shape[0]
            self.Dset.resize((FileInd + self.BufferSize, self.nChannels))
            self.Dset[FileInd:, :] = InBuffer.Buffer
            self.h5File.flush()

            for sig in self.Sigs:
                sig.t_start = (FileInd * self.Ts)*pq.s
            return True
        return False


class Buffer():
    def __init__(self, BufferSize, nChannels):
        self.Buffer = np.ndarray((BufferSize, nChannels))
        self.BufferSize = BufferSize
        self.Ind = 0
        self.Sigs = []

    def AddSample(self, Sample):
        self.Buffer[self.Ind, :] = Sample
        self.Ind += 1
        if self.Ind == self.BufferSize:
            self.Ind = 0
            return True
        return False


if __name__ == '__main__':
    plt.close('all')

    plt.rcParams.update({'axes.grid': True})

    # Variable inputs
    Fs = float(2e3)
    Ts = 1/Fs
    Fsig = 100
    ReBufferSize = 10000
    nSamples = ReBufferSize*100

    nChannels = 8

    Pcycle = np.round(Fs/Fsig)
    Fsig = Fs/Pcycle

    tstop = Ts*(Pcycle)
    t = np.arange(0, tstop, Ts)

    samples = np.sin(2*np.pi*Fsig*t)
    InSamples = cycle(samples)
    chFacts = np.linspace(0, nChannels/10, nChannels)

    InBuffer = FileBuffer(FileName='test.h5',
                          BufferSize=ReBufferSize,
                          Fs=Fs,
                          nChannels=nChannels)

    Slots = []
    for sig in InBuffer.Sigs:
        Slots.append(Rplt.WaveSlot(sig))
    Splt = Rplt.PlotSlots(Slots, CalcSignal=False)

    Tstart = time.time()
    for i in range(nSamples):
        if InBuffer.AddSample(chFacts*next(InSamples)):
#            continue
#            print('file')
#            pl = mp.Process(target=Splt.PlotChannels, args=(None, ))
#            pl.start()
#            pl.join()
            Splt.PlotChannels(None)
            Splt.Fig.canvas.draw()
##            plt.show()
#            File.flush()
#    
#    File.close()

#    plt.plot(FileData)  
    
    Tend = time.time()
    
    ProcTime = Tend-Tstart
    print('Samples --> ', nSamples)
    print('ProcTime --> ', ProcTime)
    print('MaxSampling --> ', nSamples/ProcTime)
#    
#    file = h5py.File('test.h5', 'r')
#    data = file['data']
#    plt.figure()
#    plt.plot(data)

    
#    np.sin()

#    # Create channel names
#    ChannelNames = []
#    Columns = sorted(doColumns.keys())
#    for RowName in sorted(aiChannels.keys())[0:nRows]:
#        for ColName in sorted(doColumns.keys())[0: nColumns]:
#            ChannelNames.append(RowName+ColName)
#
#    # Init Recording to store the data
#    RecOut = NeoSegment()
#    for ChName in ChannelNames:
#        sig = NeoSignal(np.array([]),
#                        units=pq.V,
#                        t_start=0*pq.s,
#                        sampling_rate=FsCh*pq.Hz,
#                        name=ChName)
#        RecOut.AddSignal(sig)
#
#    # Init figure
#    fig, ax = plt.subplots(nColumns, nRows, sharex=True)
#    ax = ax.flatten()
#    Slots = []
#    for isl, sig in enumerate(RecOut.Signals()):
#        Slots.append(Rplt.WaveSlot(sig,
#                                   Ax=ax[isl],
#                                   ))
#    PltSl = Rplt.PlotSlots(Slots,
#                           Fig=fig,
#                           AxKwargs=AxesProp,
#                           FigKwargs=FigProp,
#                           TimeAxis=None)
#    PltSl.PlotChannels(None)
#
#    # Generate digital lines, sorting indexes and dummy samples
#    DigLines, SortDInds = GenDigitalLines(nColumns=nColumns)
#    DummySamps = GenDummySamples(nColumns=nColumns,
#                                 nRows=nRows,
#                                 nSampsCh=nSampsCh)
#
#    # Define process buffer
#    RefreshBuffer = np.zeros((ReBufferSize, nColumns*nRows))
#    BufferInd = 0
#
#    # Start timer
#    Tstart = time.time()
#
#    ##
##    f = open('TstRealTimeEval.dat', 'wb')
##    np.savetxt(f, [])
#    ##
#    for i in range(nIters):
##        DummyChSamps = SortingData_list(DigLines=DigLines,
##                                        Samps=DummySamps)
#        # Sorting input data
##        DummyChSamps = SortingData_list2(SortDInds=SortDInds,
##                                         Samps=DummySamps)
#        DummyChSamps = SortingData_list3(SortDInds=SortDInds,
#                                         Samps=DummySamps,
#                                         nCols=nColumns,
#                                         nRows=nRows,
#                                         nSampsCh=nSampsCh)
#        
#        # Store data in plealocated buffer
#        Sample = DummyChSamps.mean(axis=1)[None, :]
#        RefreshBuffer[BufferInd, :] = Sample
#        BufferInd += 1
#
#        # Update recording and plot data
#        if BufferInd == ReBufferSize:
#            for si, sn in enumerate(ChannelNames):
#                RecOut.AppendSignal(sn,
#                                    RefreshBuffer[:, si][:, None])
#                sig = RecOut.GetSignal(sn)
#            ##
##            np.savetxt(f, RefreshBuffer)
##            f.flush()
#            ##
#            BufferInd = 0
#            RefreshBuffer = np.zeros((ReBufferSize, nColumns*nRows))
#            for sl in PltSl.Slots:
#                sl.Signal = RecOut.GetSignal(sl.name)
#            PltSl.PlotChannels(None)
#
#    PltSl.AddLegend()
#    Tend = time.time()
#
##    f.close()
#
#    AcqTime = Ts*nSampsCh*nColumns
#    ProcTime = (Tend-Tstart)/nIters
#    FsMax = 1/(ProcTime/(nSampsCh*nColumns))
#    SwFreqMax = 1/((1/FsMax) * nSampsCh * nColumns)
#    print('Process time -> ', ProcTime)
#    print('Max Sampling -> ', FsMax)
#    print('Max SwitchFreq -> ', SwFreqMax)
#    print('Max RefreshFreq -> ', 1/((1/SwFreqMax)*ReBufferSize))
#    print('Acquisition time -> ', AcqTime)
#    print('TimeRefresh ->', (1/FsCh)*ReBufferSize)
#    if AcqTime < ProcTime:
#        print('BAD!!!!!!!!!!!')
#    else:
#        print('Good')
