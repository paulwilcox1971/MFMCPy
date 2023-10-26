import numpy as np

import os
import sys
import io

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,  NavigationToolbar2Tk
from matplotlib.patches import Rectangle, Ellipse, Wedge
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Patch3DCollection

#Set working directory one level up from where this file is
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-1]))
import mfmc as m

fname = os.sep.join(['example MFMC files', 'unit-test test file.mfmc'])
fname = os.sep.join(['example MFMC files', 'some probes3.mfmc'])


class cl_mfmc_explorer:
    seq_list = []
    probe_list = []
    law_list = []
    MFMC = []
    tree_ids_type = {}
    tree_ids_key = {}
    tree_ids_field = {}
    #selected_item = []

    def __init__(self, root):
        self.root = root
        root.protocol("WM_DELETE_WINDOW", self.fn_on_closing)

    def fn_on_closing(self):
        m.read.fn_close_file(self.MFMC)
        self.root.destroy()
        
    def fn_set_up_window(self):
        self.root.title("MFMC explorer")
        self.root.geometry('1550x750')
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=5)
        self.root.columnconfigure(2, weight=5)
        self.root.rowconfigure(0, weight=1)
        #add the tree view
        self.tree = ttk.Treeview(self.root)
        self.tree.grid(column = 0, row = 0, rowspan = 2, sticky = 'nsew', padx=5, pady=5)
        #add the text bit
        self.text = tk.Text(self.root, height=12)
        self.text.grid(column = 1, row = 0, rowspan = 2, sticky = 'nsew', padx=5, pady=5)
        self.tree.bind('<ButtonRelease-1>', self.fn_tree_item_click)
        
        # self.text2 = tk.Text(self.root, height=12)
        # self.text2.grid(column = 2, row = 0, rowspan = 2, sticky = 'nsew', padx=5, pady=5)
        
       
      
      
        # creating the Tkinter canvas 
        # containing the Matplotlib figure 
        
        
        self.fig = Figure(figsize = (5, 5), dpi = 100)
        self.ax = self.fig.add_subplot(111)
        # self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvasTkAgg(self.fig,  master = self.root)
        self.canvas.get_tk_widget().grid(column = 3, row = 0, rowspan = 2, sticky = 'nsew', padx=5, pady=5)
        
        
        
        

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
        s_id = self.tree.focus()
        if s_id in self.tree_ids_type.keys():
            tp = self.tree_ids_type[s_id]
            if tp == m.strs.h5_keys.SEQUENCE:
                d = self.seq_dict[self.tree_ids_key[s_id]][self.tree_ids_field[s_id]]
            if tp == m.strs.h5_keys.PROBE:
                d = self.probe_dict[self.tree_ids_key[s_id]][self.tree_ids_field[s_id]]
                self.fn_plot_probe(self.probe_dict[self.tree_ids_key[s_id]])
            if tp == m.strs.h5_keys.LAW:
                d = self.law_dict[self.tree_ids_key[s_id]][self.tree_ids_field[s_id]]
            self.fn_show_detail(d)
        
        return
    
    def fn_plot_probe(self, p): 
        # x, y, z = p[m.strs.h5_keys.ELEMENT_POSITION].T
        # list of squares 
        #y = [i**2 for i in range(101)] # adding the subplot 
        
        fn_plot_probe(self.ax, p)
      
        # plotting the graph 
        # plot1.plot(x, y, 'r.') 

        self.canvas.draw()

    def fn_new_file_selected(self, fname):
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
        
        #Close file
        m.read.fn_close_file(self.MFMC)
        
        #Refresh displays
        self.fn_refresh_tree()
        return
        
    def fn_update_text_box(self):
        if self.selected_item in self.seq_list:
             self.fn_show_detail(m.read.fn_read_sequence(self.MFMC, self.selected_item))
        if self.selected_item in self.probe_list:
             self.fn_show_detail(m.read.fn_read_probe(self.MFMC, self.selected_item))
        if self.selected_item in self.law_list:
             self.fn_show_detail(m.read.fn_read_law(self.MFMC, self.selected_item))
        return

def fn_print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file = output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

def select_file():
    filetypes = (
        ('MFMC files', '*.mfmc'),
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

def fn_plot_probe(ax, probe):
    x, y, z = probe[m.strs.h5_keys.ELEMENT_POSITION].T
    e1x, e1y, e1z = probe[m.strs.h5_keys.ELEMENT_MAJOR].T
    e2x, e2y, e2z = probe[m.strs.h5_keys.ELEMENT_MINOR].T
    typ = probe[m.strs.h5_keys.ELEMENT_SHAPE].T
    
    w1 = np.sqrt(e1x ** 2 + e1y ** 2 )
    w2 = np.sqrt(e2x ** 2 + e2y ** 2 )
    theta = np.arctan2(e1y, e1x)
    
    ax.clear()
    ax.axis('equal')
    
    # elements = [Rectangle((x - ww1, y - ww2), ww1 * 2, ww2 * 2, angle = t * 180 / np.pi, rotation_point = 'center')
    #               for x, y, ww1, ww2, t in zip(xc, yc, w1, w2, theta)]
    elements= []
    #for x, y, ww1, ww2, t, tp in zip(x, yc, w1, w2, theta, typ):
    for xx, yy, e1xx, e2xx, e1yy, e2yy, tp in zip (x, y, e1x, e2x, e1y, e2y, typ):
        wx = np.sqrt(e1xx ** 2 + e1yy ** 2 )
        wy = np.sqrt(e2xx ** 2 + e2yy ** 2)
        an = np.arctan2(e1yy, e1xx) * 180 / np.pi
        if tp == 2: #ellipse
            elements.append(
                Ellipse((xx, yy), wx * 2,  wy * 2, angle = an)
                )
        elif tp == 3: #annular 
            rc = np.sqrt(xx ** 2 + yy ** 2)
            if rc > 0:
                tc = np.arctan2(yy, xx)
                t1 = (tc - np.abs(wy) / (2 * np.pi * rc)) * 180 / np.pi
                t2 = (tc + np.abs(wy) / (2 * np.pi * rc)) * 180 / np.pi
                elements.append(
                    Wedge((0.0, 0.0), rc + wx, theta1 = t1, theta2 = t2, width = 2 * wx)
                    )
            else:
                elements.append(
                    Ellipse((0.0, 0.0), wx * 2,  wy * 2, angle = an)
                    )

        else: #reactangle
            elements.append(
                Rectangle((xx - wx, yy - wy),  wx * 2,  wy * 2, angle = an, rotation_point = 'center')
                )
                
            
    pc = PatchCollection(elements, facecolor='r',
                      edgecolor='none', alpha=0.5)
    ax.add_collection(pc)
    ax.plot(x, y, 'k.')
    ax.plot(x + e1x, y + e1y, 'r.')
    ax.plot(x + e2x, y + e2y, 'g.')

#open_button.pack(expand=True)

root = tk.Tk()

q = cl_mfmc_explorer(root)
q.fn_set_up_window()
q.fn_new_file_selected(fname)

root.mainloop()


# def fn_tree_item_click(ev):
#     i = mw['tree'].focus()
#     print(mw['tree'].item(i)['text'])
#     return


# #Open file
# MFMC = m.read.fn_open_file_for_reading(fname)
# fn_new_file_loaded(mw, MFMC)
# m.read.fn_close_file(MFMC)

# # run the application
# mw['root'].mainloop()

