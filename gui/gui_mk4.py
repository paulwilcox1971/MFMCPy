#for debugging with specific file use this at Spyder console
#runfile('C:/Users/mepdw/Git/MFMCPy/gui/gui_mk3.py', args='\'example MFMC files\' \'unit-test test file.mfmc\'', wdir='C:/Users/mepdw/Git/MFMCPy/gui')

import numpy as np

import os
import sys
import io

import tkinter as tk
from tkinter import ttk,  Menu
from tkinter import filedialog as fd
#from tkinter.messagebox import showinfo

from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,  NavigationToolbar2Tk

#Make sure mfmc package is on path
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
sys.path.append(os.sep.join(dir_path.split(os.sep)[0:-1]))

import mfmc as m

class cl_mfmc_explorer:

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
        
        self.tab_graphic = ttk.Frame(self.tabs)
        self.tab_graphic.columnconfigure(0, weight = 1)
        self.tab_graphic.rowconfigure(0, weight = 1)

        self.tab_data = ttk.Frame(self.tabs)
        self.tab_data.columnconfigure(0, weight = 1)
        self.tab_data.rowconfigure(0, weight = 1)

        self.tab_check = ttk.Frame(self.tabs)
        self.tab_check.columnconfigure(0, weight = 1)
        self.tab_check.rowconfigure(0, weight = 1)
        
        self.tabs.add(self.tab_graphic, text = 'Plot')
        self.tabs.add(self.tab_data, text = 'Data')
        self.tabs.add(self.tab_check, text = 'Check')

        self.tabs.grid(column = 1, row = 0, rowspan = 1, columnspan = 3, sticky = 'nsew', padx=5, pady=5)
        
        #add the tree view
        self.tree = ttk.Treeview(self.root)
        self.tree.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'nsew', padx=5, pady=5)
        self.tree.bind('<ButtonRelease-1>', self.fn_tree_item_click)
        
        #add the text bit to the data tab
        self.tab_data_content = tk.Text(self.tab_data, height = 12)
        self.tab_data_content.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'nsew', padx=5, pady=5)
        
        #add the text bit to the check tab
        self.tab_check_content = tk.Text(self.tab_check, height = 12)
        self.tab_check_content.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'nsew', padx=5, pady=5)
        self.tab_check_content.insert(tk.END, 'Select sequence to check')
        
        self.tab_check_content.tag_configure('error', foreground = 'red')
        self.tab_check_content.tag_configure('sizetable', foreground = 'blue')
        self.tab_check_content.tag_configure('log', foreground = 'gray')
        self.tab_check_content.tag_configure('bold', relief='raised')
        
        #add the figure to the graphic tab
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig,  master = self.tab_graphic)
        self.canvas.get_tk_widget().grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'nsew', padx=5, pady=5)

            
    def fn_show_detail(self, obj_type, obj_name, obj_key):
        self.tab_data_content.delete("1.0", tk.END)
        obj = None
        plot_fn = None
        if obj_type == m.strs.h5_keys.PROBE:
            obj = m.read.fn_read_probe(self.MFMC[obj_name])
            plot_fn = self.fn_plot_probe
            #self.fn_plot_probe(self.MFMC[obj_name])
        if obj_type == m.strs.h5_keys.SEQUENCE:
            obj = m.read.fn_read_sequence_data(self.MFMC[obj_name])
            plot_fn = self.fn_plot_sequence
            #self.fn_plot_sequence(self.MFMC[obj_name])
        if obj_type == m.strs.h5_keys.LAW:
            obj = m.read.fn_read_law(self.MFMC[obj_name])
        #Add text
        if obj:
            if obj_key:
                self.tab_data_content.insert(tk.END, fn_print_to_string(obj[obj_key]))
            if plot_fn:
                self.plot_handles = plot_fn(self.MFMC[obj_name])
        return
    
    
    def fn_tree_item_click(self, ev):
        obj_type, obj_name, obj_key = self.fn_get_current_tree_item()
        if obj_name:
            self.fn_show_detail(obj_type, obj_name, obj_key)
        return
    
    def fn_get_current_tree_item(self):
        s_id = self.tree.focus()
        tags = self.tree.item(s_id)['tags']
        obj_type = tags[0]
        obj_name = tags[1]
        obj_key = tags[2]
        # print(obj_type, obj_name, obj_key)
        return obj_type, obj_name, obj_key
    
    def fn_plot_probe(self, p): 
        self.probe_checkboxes = m.graphics.fn_plot_probe(self.ax, p)
        self.canvas.draw()

    def fn_plot_sequence(self, s):
        self.sequence_checkboxes = m.graphics.fn_plot_sequence(self.ax, s)
        self.canvas.draw()
        

    def fn_new_file_selected(self, fname):
        if not fname:
            return
        #Open file
        try:
            self.MFMC = m.read.fn_open_file_for_reading(fname)
        except:
            return
        
        #Clear everything in tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        #tags indicate overall type (SEQUENCE, PROBE or LAW)
        
        #Sequences
        tp = m.strs.h5_keys.SEQUENCE
        self.tree.insert('', 'end', text='Sequences in file', open = True, iid = tp, tags = [tp, '', ''])
        for i in m.read.fn_get_sequence_list(self.MFMC):
            j = self.tree.insert(tp, 'end', text = i, tags = [tp, i, ''])
            self.fn_expand_item(m.read.fn_read_sequence_data(self.MFMC[i]), j, i, tp)
        
        #Probes
        tp = m.strs.h5_keys.PROBE
        self.tree.insert('', 'end', text='Probes in file', open = True, iid = tp, tags = [tp, '', ''])
        for i in m.read.fn_get_probe_list(self.MFMC):
            j = self.tree.insert(tp, 'end', text = i, tags = [tp, i, ''])
            self.fn_expand_item(m.read.fn_read_probe(self.MFMC[i]), j, i, tp)
        
        #Read in laws
        tp = m.strs.h5_keys.LAW
        self.tree.insert('', 'end', text='Focal laws in file', open = True, iid = tp, tags = [tp, '', ''])
        for i in m.read.fn_get_law_list(self.MFMC):
            j = self.tree.insert(tp, 'end', text = i, tags = [tp, i, ''])
            self.fn_expand_item(m.read.fn_read_law(self.MFMC[i]), j, i, tp)
        
        return
   
    def fn_expand_item(self, d, p, i, tp):
         for k in self.tree.get_children(p):
             self.tree.delete(k)
         for k in d.keys():
             if type(d[k]) is not str:
                 s = str(d[k].shape)
                 s = s.replace(', ', ' x ')
                 s = s.replace(',)', ')')
                 t = k + ': ' + s
             else:
                 t = k + ': ' + d[k]
             self.tree.insert(p, 'end', text = t, tags = [tp, i, k])
             self.tree.item(p, open = False)
         return     
        
    def fn_check(self):
        obj_type, obj, obj_field = self.fn_get_current_tree_item()
        if obj_type == m.strs.h5_keys.SEQUENCE:
            (check_log, size_table, err_list) = m.check.fn_check_sequence(self.MFMC[obj])
            self.tab_check_content.delete("1.0", tk.END)

            self.tab_check_content.insert(tk.END, '\nERRORS\n', ('error', 'bold'))
            if err_list:
                for i in err_list:
                    self.tab_check_content.insert(tk.END, '  ' + i + '\n', ('error'))    
            else:
                self.tab_check_content.insert(tk.END, '  None\n', ('error'))    
                
            self.tab_check_content.insert(tk.END, '\nSIZE TABLE\n', ('sizetable', 'bold'))
            ml = max([len(i) for i in size_table.keys()])
            for i in size_table.keys():
                self.tab_check_content.insert(tk.END, fn_print_to_string(' ' + ' ' * (ml - len(i)) + i + ': ' + str(size_table[i])), ('sizetable'))    

            ml = max([i.find(':') for i in check_log])
            self.tab_check_content.insert(tk.END, '\nCHECK LOG\n', ('log', 'bold'))    
            for i in check_log:
                self.tab_check_content.insert(tk.END, ' ' + ' ' * (ml - i.find(':')) + i + '\n', ('log'))    
            
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
initial_file = '..\\Example MFMC files\\AS example.mfmc'

root = tk.Tk()
mfmc_explorer = cl_mfmc_explorer(root)
mfmc_explorer.fn_set_up_window()
mfmc_explorer.current_dir = current_dir
mfmc_explorer.fn_new_file_selected(initial_file)
print(mfmc_explorer.current_dir)    
root.mainloop()


