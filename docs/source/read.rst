Read Functions
==============

Core functions
--------------

These are the core functions to open an MFMC file and read data from it. The
open function returns an HDF5 file object which is passed to subsequent
functions. In general, the read functions read values from an MFMC file 
into a dictionary with keys set to the corresponding MFMC datafield names.
Only datafields that match mandatory or optional datafields in the MFMC 
specification will be read in. The MFMC datafield names are provided in 
mfmc/strs/h5_keys.

.. automodule:: mfmc.read.read_core_functions
   :members:
   
Helper functions
----------------

These are helper functions that attempt to extract engineering data from the
data in dictionaries read from an MFMC file using the core functions. Each
function does its best to extract the engineering parameters for a specific 
form of entity (e.g. a linear array probe) in the form of a new
dictionary from the available data. The extracted dictionary will contain a Match
key which indicates, as a percentage, how well the data matches that expected
for the form of entity (e.g. the element positions for a linear array are expected
to be in a straight line; this along with various other expectations are tested).
If the form of an entity is known then the appropriate helper function can be 
used explicitly; if not all available helper functions for that type of entity
can be tried and the one with the highest Match taken. The engineering parameter 
dictionary keys are provided in mfmc/strs/eng_keys.

.. automodule:: mfmc.read.read_helper_functions
   :members:
