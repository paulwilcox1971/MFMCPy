# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 17:22:36 2023

@author: mepdw
"""

import numpy as np

from matplotlib.patches import Rectangle, Ellipse, Wedge
from matplotlib.collections import PatchCollection

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
    # ax.plot(x + e1x, y + e1y, 'r.')
    # ax.plot(x + e2x, y + e2y, 'g.')