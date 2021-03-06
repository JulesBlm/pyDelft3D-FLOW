# todo: 
# * DRY makeStructuredGridInterfaces and makeStructuredGridInterface, 
# * Too much repition in thes functions, all follow same sequence of stacking 
# * Make parent MakeBottom surface function/class and inherit from that?

import pyvista as pv
import xarray as xr
import datetime
import numpy as np
from .processNetCDF import addDepth
from .fixgrid import fixCORs, fixMeshGrid

def makeBottomSurface(dataset, timestep=-1, mystery_flag=False, ignore_zero=True):
    '''
    Make a StructuredGrid of the bathymetry
    Default timestep is last timestep
    
    Parameters
    ----------
    dataset : xarray.core.dataset.Dataset
        xarray DataSet of Delft3D-FLOW output
    
    timestep : int
        Output timestep to select
        
    ignore_zero : bool, optional
        Exclude cells that have 0 depth/height 

    mystery_flag : bool, optional
        Who knows? It's a mystery flag!
        
    Returns
    -------
    pyvista.core.pointset.StructuredGrid
        StructuredGrid of model bathymetry at timestep

        
    Examples
    --------
    >> bottom_surface_grid = makeBottomSurface(trim, ignore_zero=True)
    
    '''
    dataset = fixCORs(dataset) # cell COR's or centers?

    depth = dataset.DPS.isel(time=timestep)
    
    if ignore_zero:
        depth = depth.where(depth != 0).values # filter 0 values from depth
        plot_x_mesh = dataset.XCOR.where(depth != 0).values[1:-1,1:-1]
        plot_y_mesh = dataset.YCOR.where(depth != 0).values[1:-1,1:-1]
    else:
        plot_x_mesh = dataset.XCOR.values[1:-1,1:-1]
        plot_y_mesh = dataset.YCOR.values[1:-1,1:-1]     
        depth = depth.values
    
    plot_z_mesh = -depth[1:-1,1:-1]
    
    bottom_surface = pv.StructuredGrid(plot_x_mesh, plot_y_mesh, plot_z_mesh)
    bottom_surface["Depth"] = plot_z_mesh.ravel(order="F")
    
    return bottom_surface

# at faces or at nodes?
def makeStructuredGridDepth(dataset, keyword='SIG_LYR'):
    if keyword is not 'SIG_LYR' and keyword is not 'SIG_INTF':
        raise Exception("Keyword must be either 'SIG_INTF' or 'SIG_LYR'")
    
    if 'depth' not in dataset: # or 'depth_center'
        print("'depth' DataArray was not found in DataSet, adding it now. It's better to use a preprocessed NetCDF!")
        dataset = addDepth(dataset)
    else:
        print("'depth' DataArray already found in DataSet!")
        
    nr_sigma = dataset[keyword].size
    
    dataset = fixCORs(dataset)
    
    # XCOR or XZ?
    x_meshgrid = np.repeat(dataset.XCOR.values[:,:, np.newaxis], nr_sigma, axis=2)
    y_meshgrid = np.repeat(dataset.YCOR.values[:,:, np.newaxis], nr_sigma, axis=2)
    
    if keyword is 'SIG_LYR':
        depth = dataset.depth_center.isel(time=0)
    elif keyword is 'SIG_INTF':
        depth = dataset.depth.isel(time=0)
        
    ## FROM HERE ITS THE SAME AS THE ABOVE FUNCTION
    x_ravel = np.ravel(x_meshgrid)
    y_ravel = np.ravel(y_meshgrid)
    depth_ravel = np.ravel(depth.values)
    
    xyz_layers = np.column_stack((x_ravel, y_ravel, depth_ravel))
    print("xyz_layers.shape", xyz_layers.shape)
    
    depth_grid = pv.StructuredGrid()
    depth_grid.points = xyz_layers
    depth_grid.dimensions = [nr_sigma, dataset.N.size, dataset.M.size]
    
    return depth_grid

def makeStructuredGridUnderlayers(dataset, time=-1, LSED=0): 
    '''
    Pass the Delft3D-FLOW DataSet and pass the outputstep index; get back a 3D PyVista mesh of the underlayers with sed volfrac and (wow!)
    
    Keyword arg: sed_index LSED index to add to structuredGrid
    Why not add all sediments? Pass in dict with name and index or get names from dataset ie from dataset.NAMCON
    # Something like this:
    
    for sed in trim.LSED:
        name = dataset.NAMCOM[sed].decode('UTF-8') 
        
        vol_frac_values_at_time = dataset.LYRFRAC.isel(time=time, LSEDTOT=sed).transpose('M', 'N', 'nlyr')    
        underlayer_grid[f"Vol fraction of {name} in layer"] = mass_sed_at_time.values.ravel()

        # now do same for MSED
    '''
    print("Making StructuredGrid for underlayers at outputstep", time)
    if 'DP_BEDLYR' not in dataset: # or 'depth_center'
        raise Exception("'DP_BEDLYR' DataArray was not found in DataSet")
        
    depth_bedlayer = dataset['DP_BEDLYR'].isel(nlyrp1=slice(0,-1), time=time).transpose('M', 'N', 'nlyrp1') 
    nr_of_underlayers = dataset.nlyr.size
  
    dataset = fixCORs(dataset)
    
    x_meshgrid = np.repeat(dataset.XCOR.values[:,:, np.newaxis], nr_of_underlayers, axis=2)
    y_meshgrid = np.repeat(dataset.YCOR.values[:,:, np.newaxis], nr_of_underlayers, axis=2)
    
    x_raveled = np.ravel(x_meshgrid)
    y_raveled = np.ravel(y_meshgrid)

    # Flip z-axis (axis=2) to get the height
    height_deposits = np.flip(depth_bedlayer.values, axis=2)
    height_deposits_ravel = np.ravel(height_deposits)
    
    xyz = np.column_stack((x_raveled, y_raveled, height_deposits_ravel))
    
    underlayer_grid = pv.StructuredGrid()
    underlayer_grid.points = xyz
    underlayer_grid.dimensions = [nr_of_underlayers, dataset.N.size, dataset.M.size]
    
    vol_frac_sed_at_time = dataset.LYRFRAC.isel(time=time, LSEDTOT=0).transpose('M', 'N', 'nlyr')    
    # shouldn't hardcode title
    underlayer_grid["Volume fraction sand"] = vol_frac_sed_at_time.values.ravel()
    
    mass_sed_at_time = dataset.MSED.isel(time=time, LSEDTOT=LSED).transpose('M', 'N', 'nlyr')
    # shoudln't hardcode title    
    underlayer_grid["Mass of sand in layer"] = mass_sed_at_time.values.ravel()
    
    return underlayer_grid