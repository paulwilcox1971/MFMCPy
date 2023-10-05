# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 10:52:45 2023

@author: mepdw
"""
import mfmc
import numpy as np
import matplotlib.pyplot as plt

plt.close('all')

def fn_plot_probe(probe):
    ax = plt.figure().add_subplot(projection='3d')
    for (c, e1, e2, i) in zip(probe['ELEMENT_POSITION'], probe['ELEMENT_MAJOR'], probe['ELEMENT_MINOR'], range(probe['ELEMENT_POSITION'].shape[0])):
        tmp = np.vstack((c + e1 + e2, 
               c + e1 - e2, 
               c - e1 - e2, 
               c - e1 + e2,
               c + e1 + e2))
        #print(tmp)
        ax.plot(tmp[:,0], tmp[:,1], tmp[:,2], color='red')
        ax.text(c[0], c[1], c[2], str(i+1))

xtheta = 0 * np.pi / 180
ytheta = 30 * np.pi / 180
ztheta = 0 * np.pi / 180
el_pos_err = 0#0.0000001e-3

#1D linear probe creation and recovery
input_params1 = {}
input_params1[mfmc.PITCH_KEY] = 1e-3
input_params1[mfmc.ELEMENT_WIDTH_KEY] = 0.9e-3
input_params1[mfmc.ELEMENT_LENGTH_KEY] = 10e-3
input_params1[mfmc.NUMBER_OF_ELEMENTS_KEY] = 11
input_params1[mfmc.NORMAL_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([0, 0, 1], xtheta, ytheta, ztheta)
input_params1[mfmc.ACTIVE_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([1, 0, 0], xtheta, ytheta, ztheta)
#create
probe1 = mfmc.fn_linear_array(input_params1)
probe1['ELEMENT_POSITION'] += np.random.randn(*probe1['ELEMENT_POSITION'].shape) * el_pos_err
#recover
probe_details1 = mfmc.fn_test_for_1D_linear_probe(probe1)
print('')
mfmc.fn_pretty_print_dictionary(input_params1)
mfmc.fn_pretty_print_dictionary(probe_details1)
fn_plot_probe(probe1)

#2D matrix probe creation and recovery
input_params2 = {}
input_params2[mfmc.PITCH_KEY] = [1e-3, 2e-3]
input_params2[mfmc.ELEMENT_SIZE_KEY] = 0.9e-3
input_params2[mfmc.NUMBER_OF_ELEMENTS_KEY] = 11
input_params2[mfmc.NORMAL_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([0, 0, 1], xtheta, ytheta, ztheta)
input_params2[mfmc.FIRST_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([1, 0, 0], xtheta, ytheta, ztheta)
#create
probe2 = mfmc.fn_matrix_array(input_params2)
probe2['ELEMENT_POSITION'] += np.random.randn(*probe2['ELEMENT_POSITION'].shape) * el_pos_err
#recover
probe_details2 = mfmc.fn_test_for_2d_matrix_probe(probe2)
print('')
mfmc.fn_pretty_print_dictionary(input_params2)
mfmc.fn_pretty_print_dictionary(probe_details2)
fn_plot_probe(probe2)
