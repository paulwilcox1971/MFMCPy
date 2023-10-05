Modules needed
======= ======
numpy, scipy, pandas, matplotlib, h5py, openpyxl

From a Conda or Mamba prompt type
  conda create -c conda-forge -n mfmc spyder-kernels=2.4 numpy scipy pandas matplotlib h5py openpyxl
or
  mamba create -c conda-forge -n mfmc spyder-kernels=2.4 numpy scipy pandas matplotlib h5py openpyxl
to create an environmenet (mfmc) with these modules

Files in MFMCPy
===== == ======
example_write_read_check.py - example script that creates an MFMC file from Python objects, reads it back into new Python objects, and also runs the check utility on it
example_check_all_example_files.py - checks all MFMC files in Example MFMC files folder
example_analyse_probes.py - analyses all probes found in MFMC files in Example MFMC files folder assuming they are liner 1D arrays (work in progress)

Folder structure
====== =========
MFMCPy
  /mfmc - the MFMC module. Use include mfmc
    /write - tools for writing MFMC files
    /read - tools for reading MFMC files
    /check - tools for checking MFMC files
    /spec - tools related to MFMC specification
    /strs - string tables including names of fields used in MFMC files
    /utils - various utilities used by other functions
    /view - partial MFMC file viewer (work in progress)
  /docs - documents, including the specification excel file which is used as a reference by the MFMCPy module
  /Example MFMC files - what it sounds like
  /tests - unit tests
  /dev - files under development
