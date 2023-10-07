import numpy as np

import os
import sys



import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

#Set working directory one level up from where this file is
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-1]))

import mfmc as m

fname = os.sep.join(['example MFMC files', 'unit-test test file.mfmc'])

# #Open file
# MFMC = m.read.fn_open_file_for_reading(fname)

# #Read in probes
# probe_list = m.read.fn_get_probe_list(MFMC)
# seq_list = m.read.fn_get_sequence_list(MFMC)
# law_list = m.read.fn_get_law_list(MFMC)
# m.read.fn_close_file(MFMC)








def fn_set_up_window():
    mw = {}
    # create the root window
    mw['root'] = tk.Tk()
    mw['root'].title('Tkinter Open File Dialog')
    #mw['root'].resizable(False, False)
    mw['root'].geometry('1550x250')
    mw['root'].columnconfigure(0, weight=1)
    mw['root'].columnconfigure(1, weight=3)
    mw['root'].rowconfigure(0, weight=1)
    #add the tree view
    mw['tree'] = ttk.Treeview(mw['root'])
    mw['tree'].grid(column = 0, row = 0, rowspan = 2, sticky = 'nsew', padx=5, pady=5)
    #add the text bit
    mw['text'] = tk.Text(mw['root'], height=12)
    mw['text'].grid(column = 1, row = 0, rowspan = 2, sticky = 'nsew', padx=5, pady=5)
    return mw

def fn_new_file_loaded(mw, MFMC):
    
    #Read in lists
    probe_list = m.read.fn_get_probe_list(MFMC)
    seq_list = m.read.fn_get_sequence_list(MFMC)
    law_list = m.read.fn_get_law_list(MFMC)
    m.read.fn_close_file(MFMC)
    #Empty tree
    for i in mw['tree'].get_children():
        mw['tree'].delete(i)
    #Add to tree
    mw['tree'].insert('', 'end', 'Sequences', text='Sequences in file', open = True)
    for i in seq_list:
        mw['tree'].insert('Sequences', 'end', text = i)
    mw['tree'].insert('', 'end', 'Probes', text='Probes in file', open = True)
    for i in probe_list:
        mw['tree'].insert('Probes', 'end', text = i)
    mw['tree'].insert('', 'end', 'Laws', text='Laws in file')
    for i in law_list:
        mw['tree'].insert('Laws', 'end', text = i)
    #
    mw['tree'].bind('<ButtonRelease-1>', fn_tree_item_click)
    return

def select_file():
    filetypes = (
        ('text files', '*.mfmc'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    showinfo(
        title='Selected File',
        message=filename
    )


# open button
# open_button = ttk.Button(
#     root,
#     text='Open a File',
#     command=select_file
# )

#open_button.pack(expand=True)

mw = fn_set_up_window()

def fn_tree_item_click(ev):
    i = mw['tree'].focus()
    print(mw['tree'].item(i)['text'])
    return


#Open file
MFMC = m.read.fn_open_file_for_reading(fname)
fn_new_file_loaded(mw, MFMC)
m.read.fn_close_file(MFMC)

# run the application
mw['root'].mainloop()
