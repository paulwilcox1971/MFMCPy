# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 21:14:14 2023

@author: mepdw
"""
import mfmc.write as m


fname = 'write_example5.mfmc'

spec_fname = 'docs/MFMC Specification 2.0.0.xlsx'

#Open file for writing and load spec
MFMC = m.fn_open_file_for_writing(fname)

#Create a 1D linear probe
xtheta = 0
ytheta = 0
ztheta = 0
input_params1 = {}
input_params1[m.PITCH_KEY] = 1e-3
input_params1[m.ELEMENT_WIDTH_KEY] = 0.9e-3
input_params1[m.ELEMENT_LENGTH_KEY] = 10e-3
input_params1[m.NUMBER_OF_ELEMENTS_KEY] = 32
input_params1[m.NORMAL_VECTOR_KEY] = [0, 0, 1] # mfmc.utils.fn_rotate_about_xyz_axes([0, 0, 1], xtheta, ytheta, ztheta)
input_params1[m.ACTIVE_VECTOR_KEY] = [1, 0, 0] # mfmc.utils.fn_rotate_about_xyz_axes([1, 0, 0], xtheta, ytheta, ztheta)
probe1 = m.fn_linear_array(input_params1)

#Write the probe to the file
m.fn_write_probe(MFMC, m.SPEC, probe1)


#Close file
m.fn_close_file(MFMC)
