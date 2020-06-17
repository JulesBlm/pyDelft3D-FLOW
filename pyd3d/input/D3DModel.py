import pandas as pd
import numpy as np
from os import path, walk
from cmocean.cm import deep, deep_r
import pyvista as pv
# from .mdf import Mdf
from .dep import Depth
from .grid import Grid
from .enc import Enclosure
from .bnd import Boundaries

import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from mpl_toolkits.mplot3d import Axes3D

colormap = deep

'''
its a start but its still a big mess
i really should read up on object oriented in Python
write the filenames to mdf (Filbnd, FilbcC) and bcc (TimeSeries) files
store all shared params here
Keep track of sediment names > sed mor files
Keep track of boundary labels > bnd bcc bct files
Keep track of dimensions > grid, depth, enc files
Check if mdf final time is multiple of outputtimestep, crucial or multi-runs
Ensure all times are multiple of time-step!
'''

class D3DModel(object):
    """
    Read a folder containing Delft3D4-FLOW files
    Displays all properties of model in a human readable overview
    Some convenient plot methods 
    
    Attributes
    ----------
    filenames : list
        This is where all input filenames are stored

    folderpath : str
        This is where given folder path is stored

    """
    def __init__(self, folderpath=None, *args, **kwargs):
        if not folderpath:
            raise Exception("Can't read a folder without a folderpath  ¯\_(ツ)_/¯")
        
        if not path.exists(folderpath):
            raise Exception("Looks like read folder does not exist, aborting")
        
        self.folderpath = folderpath
        
        self.filenames = self.findFiles(folderpath)

        #  try:
            # self.readGrid()
            # self.readDepth()
            # self.readBoundaries()
            # self.readEnclosure()
        # except:
            # print("Damn")
    
    def __repr__(self):
        return "Reads all Delft3D files in a folder, directs to all the other classes (WOW)"
    
    def findFiles(self, folderpath):
        basename = path.basename(folderpath)
        title, _ = path.splitext(basename)
        self.title = title
        
        filenames = {}
        
        # extensions = ("enc", "grd", "dep", "bcc", "bct", "sed", "mor", "tra", "mdf")
        
        fileproperties = [
            {"type": "Boundary", "ext": "bnd" },
            {"type": "MDF", "ext": "mdf" },
            {"type": "Sediments", "ext": "sed"},
            {"type": "Depth", "ext": "dep"},
            {"type": "Enclosure", "ext": "enc"},
            {"type": "Grid", "ext": "grd"},
            {"type": "B.C. Time series", "ext": "bct"},
            {"type": "B.C. Constituents", "ext": "bcc"},
            {"type": "Morphology", "ext": "mor"}
        ]
        
        # Find filenames in template/read folder        
        for _, _, files in walk(folderpath):
            for file in files:
                for fileprop in fileproperties:
                    ext = fileprop["ext"]
                    if file.endswith(ext):
                        # df_filenames.append({ fileprop["type"], "filename": file})
                        filenames[ext] = path.join(folderpath, file)
        
        self.filenames = filenames
        
        return filenames
        
    
    def readGrid(self):
        grid = Grid.read(self.filenames["grd"])
        
        self.grid = grid
        
        return grid

    def readDepth(self):
        if not self.grid:
            raise Exception("Grid needs to be read first")
        
        depth = Depth.read(self.filenames["dep"], self.grid.shape)
        
        self.depth = depth
        
    def readBoundaries(self):
        bnd = Boundaries.read(self.filenames["bnd"])
        
        self.bnd = bnd
    
    def readEnclosure(self):
        enc = Enclosure.read(self.filenames["enc"])
        
        self.enc = enc
        

    def plotDepthPyVista(self, screenshot=None):
        if not self.depth or not self.grid:
            raise Exception("Must define grid and depth before plotting")
        
        
        p = pv.Plotter(notebook=True)
        p.add_mesh(bottom_surface, cmap=deep_r, scalars='depth', ambient=0.2)

        p.show_grid()
        p.set_scale(zscale=25)
        p.show()
        
        return bottom_surface
    
#     def plotMap(self, depth=True, enclosure=True, grid=True):
#         '''
#         Plot map of depth
#         '''
                
#         fig, ax = plt.subplots(nrows=1, figsize=(7, 8))

#         ax.set_title('Map view of model domain', fontsize=16)
#         ax.set_aspect('equal')
        
#         # Boundary conditions
#         # ax.plot(bc_x_meters[1:][0], bc_y_meters[1:][0], c='coral', linewidth=7.5) #label='Zero discharge BC',
#         # text_zero_discharge = ax.text(8000, 35500, "Zero discharge B.C.", fontsize=13)
#         # text_zero_discharge.set_path_effects([PathEffects.withStroke(linewidth=1.5, foreground='w')])

#         if enclosure:
#             # TODO: get gridsteps from self
#             # x_gridcells, y_gridcells = grid.x.shape
#             # a hack that only works for me  ¯\_(ツ)_/¯            
#             x_gridstep = 200
#             y_gridstep = 200
            
#             enclosure_x = self.enc.x
#             enclosure_y = self.enc.y
        
#             plot_enclosure_x_meters = [i * x_gridstep for i in enclosure_x]
#             plot_enclosure_y_meters = [i * y_gridstep for i in enclosure_y]
#             ax.plot(plot_enclosure_x_meters, plot_enclosure_y_meters, c='white', linewidth=2.5, label="Enclosure")
#             # legend
#             fig.legend(loc=(0.134,.383), borderpad=0.5)

#         if depth:
#             depth = self.depth.values[0:-1,0:-1]
#             min_depth, max_depth = [np.amin(depth), np.max(depth)]
#             grid_im = ax.pcolor(self.grid.x, self.grid.y, self.depth.values[0:-1,0:-1], vmin=min_depth, vmax=max_depth, cmap=deep)
            
#         if grid:
#             x_grid = self.grid.x.data[0]
#             y_grid = self.grid.y.data[:,1]

#             ax.set_xticks(x_grid, minor=True)
#             ax.set_yticks(y_grid, minor=True)
            
            
#         ax.set_xlabel('Width $m$ [m]', fontsize=16)
#         ax.set_ylabel('Length $n$ [m]', fontsize=16)
        
#         # TODO: Don't hardcode xlim and ylim
#         ax.set_xlim(0, 26200)
#         ax.set_ylim(0, 36700)


#         ax.grid(which='minor', alpha=0.15)
#         ax.grid(which='major', alpha=0.75)

#         # discharge = ax.scatter(discharge_location_x - 100, discharge_location_y + 400, s=[175], c='coral', marker="^", edgecolors="white") # label="Discharge BC",
#         # text_discharge = ax.text(discharge_location_x - 20, discharge_location_y + 450, "Discharge B.C.", fontsize=13)
#         # text_discharge.set_path_effects([PathEffects.withStroke(linewidth=1.5, foreground='w')])

#         # colorbar
#         cbar = fig.colorbar(grid_im, ax=ax)
#         cbar.ax.set_ylabel("Depth [m]", rotation=-90, va="bottom", fontsize=16)

        
#         return fig, ax, cbar


