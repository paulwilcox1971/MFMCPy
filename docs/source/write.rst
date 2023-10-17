Write Functions
===============

Core functions
--------------

These are the core functions to open and MFMC file and write data to it. The
open / create functions return an HDF5 file object which is passed to subsequent
functions. In general, the write functions take a Python dictionary as input
and write the contents to the MFMC file using the dictionary keys as the datefield
names in the HDF5 file. For this reason, the dictionary keys need to exactly 
match the datafield names in the MFMC specification, and the value associated
with each key needs to match that of the data in the MFMC specification in terms
of type and shape. The MFMC datafield names are provided in mfmc/strs/h5_keys.

.. automodule:: mfmc.write.write_core_functions
   :members:
   
Helper functions
----------------

These are helper functions that return dictionaries with the keys and values
according to the MFMC specification given an input dictionary described in terms
of engineering parameters. The engineering parameter dictionary keys are provided
in mfmc/strs/eng_keys.

.. automodule:: mfmc.write.write_helper_functions
   :members:
