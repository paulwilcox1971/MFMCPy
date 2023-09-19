# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 21:14:14 2023

@author: mepdw
"""
import mfmc


fname = 'write_example5.mfmc'

spec_fname = 'docs/MFMC Specification 2.0.0.xlsx'

#Open file for writing and load spec
MFMC = mfmc.fn_open_file_for_writing(fname)
SPEC = mfmc.fn_load_specification(spec_fname)

#Create a 1D linear probe
xtheta = 0
ytheta = 0
ztheta = 0
input_params1 = {}
input_params1[mfmc.PITCH_KEY] = 1e-3
input_params1[mfmc.ELEMENT_WIDTH_KEY] = 0.9e-3
input_params1[mfmc.ELEMENT_LENGTH_KEY] = 10e-3
input_params1[mfmc.NUMBER_OF_ELEMENTS_KEY] = 32
input_params1[mfmc.NORMAL_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([0, 0, 1], xtheta, ytheta, ztheta)
input_params1[mfmc.ACTIVE_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([1, 0, 0], xtheta, ytheta, ztheta)
probe1 = mfmc.fn_linear_array(input_params1)

#Write the probe to the file
mfmc.fn_write_probe(MFMC, SPEC, probe1)


#Close file
mfmc.fn_close_file(MFMC)
