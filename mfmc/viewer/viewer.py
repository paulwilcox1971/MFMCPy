# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:31:56 2023

@author: mepdw
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from ..utils import utils

class cl_sequence:
    tx_laws = []
    rx_laws = [] 
    unique_tx_laws = []
    unique_rx_laws = []
    time = []
    axes_defined = False
    
    def __init__(self, MFMC, sequence):
        self.tx_laws = utils.fn_transmit_laws_for_sequence(MFMC, sequence)
        self.rx_laws = utils.fn_receive_laws_for_sequence(MFMC, sequence)
        self.unique_tx_laws = list(set(self.tx_laws))
        self.unique_rx_laws = list(set(self.rx_laws))
        self.tx = [self.unique_tx_laws.index(i) for i in self.tx_laws]
        self.rx = [self.unique_rx_laws.index(i) for i in self.rx_laws]
        self.time = MFMC[sequence].attrs['TIME_STEP'] * range(MFMC[sequence]['MFMC_DATA'].shape[2]) + MFMC[sequence].attrs['START_TIME']
        self.axes_defined = True
        self.mfmc_data = MFMC[sequence]['MFMC_DATA']
    
    def fn_return_frame(self, frame_no = 0, tx = None, rx = None, tmin = -np.inf, tmax = np.inf):
        if not self.axes_defined:
            return None
        else:
            
            if tx != None:
                tx_rx_i = np.where(np.array(self.tx) == tx)[0]
                ascan_label =  [self.rx[i] for i in tx_rx_i]
            elif rx != None:
                tx_rx_i = np.where(np.array(self.rx) == rx)[0]
                ascan_label =  [self.tx[i] for i in tx_rx_i]
            else:
                tx_rx_i = list(range(self.mfmc_data.shape[1]))
                ascan_label = tx_rx_i
            #time_i = [t >= tmin and t <= tmax for t in self.time]
            t1 = np.min(np.where(self.time >= tmin))
            t2 = np.max(np.where(self.time <= tmax)) + 1
            return (self.time[t1:t2], ascan_label, self.mfmc_data[frame_no, tx_rx_i, t1:t2])
        

