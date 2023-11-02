# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 17:22:36 2023

@author: mepdw
"""

import numpy as np

from matplotlib.patches import Rectangle, Ellipse, Wedge
from matplotlib.collections import PatchCollection
from matplotlib.widgets import Button, CheckButtons

from ..strs import h5_keys
from ..strs import eng_keys

def fn_plot_probe(ax, probe):
    x, y, z = probe[h5_keys.ELEMENT_POSITION].T
    e1x, e1y, e1z = probe[h5_keys.ELEMENT_MAJOR].T
    e2x, e2y, e2z = probe[h5_keys.ELEMENT_MINOR].T
    typ = probe[h5_keys.ELEMENT_SHAPE].T
    
    w1 = np.sqrt(e1x ** 2 + e1y ** 2 )
    w2 = np.sqrt(e2x ** 2 + e2y ** 2 )
    theta = np.arctan2(e1y, e1x)
    
    ax.clear()
    ax.axis('equal')
        
    elements= []

    for xx, yy, e1xx, e2xx, e1yy, e2yy, tp in zip (x, y, e1x, e2x, e1y, e2y, typ):
        radial_width = np.sqrt(e1xx ** 2 + e1yy ** 2 )
        circ_len = np.sqrt(e2xx ** 2 + e2yy ** 2)
        an = np.arctan2(e1yy, e1xx) * 180 / np.pi
        if tp == 2: #ellipse
            elements.append(
                Ellipse((xx, yy), radial_width * 2,  circ_len * 2, angle = an)
                )
        elif tp == 3: #annular 
            rc = np.sqrt(xx ** 2 + yy ** 2)
            if rc > 0:
                tc = np.arctan2(yy, xx)
                t1 = (tc - np.abs(circ_len) / rc) * 180 / np.pi
                t2 = (tc + np.abs(circ_len) / rc) * 180 / np.pi
                elements.append(
                    Wedge((0.0, 0.0), rc + radial_width, t1, t2, width = 2 * radial_width)
                    )
            else:
                elements.append(
                    Ellipse((0.0, 0.0), radial_width * 2,  circ_len * 2, angle = an)
                    )

        else: #reactangle
            elements.append(
                Rectangle((xx - radial_width, yy - circ_len),  radial_width * 2,  circ_len * 2, angle = an, rotation_point = 'center')
                )
            
    pc = PatchCollection(elements, facecolor = np.array([1, 1, 1]) * 0.5, edgecolor = 'k', alpha = 0.25)
    lines_by_label = {}
    #ax.add_collection(pc)
    lines_by_label['Elements'] = [ax.add_collection(pc)]
    lines_by_label['Numbers'] = []
    for (xx, yy, i) in zip(x, y, range(x.size)):
        lines_by_label['Numbers'].append(ax.text(xx, yy, str(i + 1), visible = False, ha = 'center', va = 'center'))
    lines_by_label['Centres'] = ax.plot(x, y, 'k.', visible = False)
    lines_by_label['Major axes'] = ax.plot([x, x + e1x], [y, y + e1y], 'r', visible = False)
    lines_by_label['Minor axes'] = ax.plot([x, x + e2x], [y, y + e2y], 'g', visible = False)
    
    rax = ax.inset_axes([0.0, 0.0, 0.2, 0.2])
    check = CheckButtons(
        ax=rax,
        labels = lines_by_label.keys(),
        actives=[l[0].get_visible() for l in lines_by_label.values()]
        ) #'Elements', 'Centres', 'Major axes', 'Minor axes'])
    
    def fn_callback(label):
        ln = lines_by_label[label]
        for l in ln:
            l.set_visible(not l.get_visible())
            l.figure.canvas.draw_idle()
    
    check.on_clicked(fn_callback)

    return check    
