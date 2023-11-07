#for debugging with specific file use this at Spyder console
#runfile('C:/Users/mepdw/Git/MFMCPy/gui/gui_mk3.py', args='\'example MFMC files\' \'unit-test test file.mfmc\'', wdir='C:/Users/mepdw/Git/MFMCPy/gui')

import numpy as np

import os
import sys
import io

import tkinter as tk
from tkinter import ttk, messagebox, Menu
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,  NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Patch3DCollection

#Make sure mfmc package is on path
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
sys.path.append(os.sep.join(dir_path.split(os.sep)[0:-1]))

import mfmc as m

class cl_mfmc_explorer:
    seq_list = []
    probe_list = []
    law_list = []
    MFMC = []
    tree_ids_type = {}
    tree_ids_key = {}
    tree_ids_field = {}

    def __init__(self, root):
        self.root = root
        self.current_dir = os.getcwd()
        root.protocol("WM_DELETE_WINDOW", self.fn_on_closing)

    def fn_on_closing(self):
        try:
            m.read.fn_close_file(self.MFMC)
        except:
            pass 
        self.root.destroy()
        
    def fn_set_up_window(self):
        self.root.title("MFMC explorer")
        self.root.geometry('1550x750')
        self.root.columnconfigure(0, weight = 1)
        self.root.columnconfigure(1, weight = 1)
        self.root.columnconfigure(2, weight = 1)
        self.root.columnconfigure(3, weight = 1)
        self.root.rowconfigure(0, weight=1)
        
        #Add menu
        self.menubar = Menu(self.root)
        self.root.config(menu = self.menubar)
        
        self.file_menu = Menu(self.menubar, tearoff = 0)
        self.file_menu.add_command(label = 'Open', command = self.fn_select_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = 'Exit', command = self.root.destroy)
        self.menubar.add_cascade(label = "File", menu = self.file_menu)
        
        self.tool_menu = Menu(self.menubar, tearoff = 0)
        self.tool_menu.add_command(label = 'Check', command = self.fn_check)
        self.menubar.add_cascade(label = "Tools", menu = self.tool_menu)

        #Add tabs
        self.tabs = ttk.Notebook(root)
        
        self.tab_text = ttk.Frame(self.tabs)
        self.tab_text.columnconfigure(0, weight = 1)
        self.tab_text.rowconfigure(0, weight = 1)

        self.tab_graphic = ttk.Frame(self.tabs)
        self.tab_graphic.columnconfigure(0, weight = 1)
        self.tab_graphic.rowconfigure(0, weight = 1)
        
        self.tabs.add(self.tab_graphic, text = 'Plot')
        self.tabs.add(self.tab_text, text = 'Data')

        self.tabs.grid(column = 1, row = 0, rowspan = 1, columnspan = 3, sticky = 'nsew', padx=5, pady=5)
        
        #add the tree view
        self.tree = ttk.Treeview(self.root)
        self.tree.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'nsew', padx=5, pady=5)
        self.tree.bind('<ButtonRelease-1>', self.fn_tree_item_click)
        
        #add the text bit to the text tab
        self.text = tk.Text(self.tab_text, height = 12)
        self.text.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'nsew', padx=5, pady=5)
        
        #add the figure to the graphic tab
        #self.fig = Figure(figsize = (5, 5), dpi = 100)
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig,  master = self.tab_graphic)
        self.canvas.get_tk_widget().grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'nsew', padx=5, pady=5)

    def fn_refresh_tree(self):
        #Clear everything
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree_ids_type = {}
        self.tree_ids_field = {}
        self.tree_ids_key = {}
        #Add to tree
        self.tree.insert('', 'end', 'Sequences', text='Sequences in file', open = True)
        for i in self.seq_dict.keys():
            p = self.tree.insert('Sequences', 'end', text = i)
            self.fn_expand_item(self.seq_dict[i], p, m.strs.h5_keys.SEQUENCE, i)
            self.tree.item(p, open = False)
        self.tree.insert('', 'end', 'Probes', text='Probes in file', open = True)
        for i in self.probe_dict.keys():
            p = self.tree.insert('Probes', 'end', text = i)
            self.fn_expand_item(self.probe_dict[i], p, m.strs.h5_keys.PROBE, i)
            self.tree.item(p, open = False)
            self.tree_ids_key[p] = i
            self.tree_ids_field[p] = ''
            self.tree_ids_type[p] = m.strs.h5_keys.PROBE
        self.tree.insert('', 'end', 'Laws', text='Laws in file')
        for i in self.law_dict.keys():
            p = self.tree.insert('Laws', 'end', text = i)
            self.fn_expand_item(self.law_dict[i], p, m.strs.h5_keys.LAW, i)
            self.tree.item(p, open = False)
        return
            
    def fn_show_detail(self, d):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, fn_print_to_string(d))
        return
    
    def fn_expand_item(self, d, p, tp, k):
        for i in self.tree.get_children(p):
            self.tree.delete(i)
        for i in d.keys():
            if type(d[i]) is not str:
                s = str(d[i].shape)
                s = s.replace(', ', ' x ')
                s = s.replace(',)', ')')
                t = i + ': ' + s
            else:
                t = i + ': ' + d[i]
            j = self.tree.insert(p, 'end', text = t)
            self.tree_ids_field[j] = i
            self.tree_ids_type[j] = tp
            self.tree_ids_key[j] = k
            self.tree.item(p, open=True)
        return
    
    def fn_tree_item_click(self, ev):
        obj_type, obj, obj_field = self.fn_get_current_tree_item()
        if obj_field:
            self.fn_show_detail(obj[obj_field])
        if obj_type == m.strs.h5_keys.PROBE:
            self.fn_plot_probe(obj)
        return
    
    def fn_get_current_tree_item(self):
        s_id = self.tree.focus()
        if s_id in self.tree_ids_type.keys():
            obj_type = self.tree_ids_type[s_id]
            obj_field = self.tree_ids_field[s_id]
            if obj_type == m.strs.h5_keys.SEQUENCE:
                obj = self.seq_dict[self.tree_ids_key[s_id]]
            if obj_type == m.strs.h5_keys.PROBE:
                obj = self.probe_dict[self.tree_ids_key[s_id]]
            if obj_type == m.strs.h5_keys.LAW:
                obj = self.law_dict[self.tree_ids_key[s_id]]
        return obj_type, obj, obj_field
    
    def fn_plot_probe(self, p): 
        self.probe_checkboxes = m.graphics.fn_plot_probe(self.ax, p)
        self.canvas.draw()

    def fn_new_file_selected(self, fname):
        if not fname:
            return
        #Open file
        self.MFMC = m.read.fn_open_file_for_reading(fname)
        
        #Read in probes
        self.probe_dict = {}
        for p in m.read.fn_get_probe_list(self.MFMC):
            self.probe_dict[p] = m.read.fn_read_probe(self.MFMC, p)
        
        #Read in laws
        self.law_dict = {}
        for i in m.read.fn_get_law_list(self.MFMC):
            self.law_dict[i] = m.read.fn_read_law(self.MFMC, i)
        
        #Read in sequences
        self.seq_dict = {}
        for s in m.read.fn_get_sequence_list(self.MFMC):
            self.seq_dict[s] = m.read.fn_read_sequence_data(self.MFMC, s)
            #seq_dict[s][m.strs.h5_keys.MFMC_DATA] = m.read.fn_read_frame(MFMC, s)
        
       
        #Refresh displays
        self.fn_refresh_tree()
        return
        
    # def fn_update_text_box(self):
    #     if self.selected_item in self.seq_list:
    #          self.fn_show_detail(m.read.fn_read_sequence(self.MFMC, self.selected_item))
    #     if self.selected_item in self.probe_list:
    #          self.fn_show_detail(m.read.fn_read_probe(self.MFMC, self.selected_item))
    #     if self.selected_item in self.law_list:
    #          self.fn_show_detail(m.read.fn_read_law(self.MFMC, self.selected_item))
    #     return
    
    def fn_check(self):
        obj_type, obj, obj_field = self.fn_get_current_tree_item()
        if obj_type == m.strs.h5_keys.SEQUENCE:
            (check_log, size_table, err_list) = m.check.fn_check_sequence(self.MFMC, obj)
        pass
    
    def fn_select_file(self):
        filetypes = (
            ('MFMC files', '*.mfmc'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(title = 'Open', initialdir = self.current_dir, filetypes = filetypes)
        self.fn_new_file_selected(filename)

def fn_print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file = output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

#Actual execution code
current_dir = os.getcwd()
if len(sys.argv) > 1:
    try:
        current_dir = sys.argv[1]
    except:
        current_dir = os.getcwd()
        print('Directory does not exist')

initial_file = None
if len(sys.argv) > 2:
    try:
        initial_file = sys.argv[2]
    except:
        initial_file = None
        print('File does not exist')

current_dir = '..\\Example MFMC files'

root = tk.Tk()
mfmc_explorer = cl_mfmc_explorer(root)
mfmc_explorer.fn_set_up_window()
mfmc_explorer.current_dir = current_dir
mfmc_explorer.fn_new_file_selected(initial_file)
print(mfmc_explorer.current_dir)    
root.mainloop()

