from IPython.display import Markdown as md 
import numpy as np

def fixCORs(dataset):
    '''
    Last column and row of XCOR and YCOR are all 0's, this function fixes that. Nice for plotting
    '''
    dataset.XCOR.load()
    dataset.YCOR.load()    
    
    dataset.XCOR[-1,:] = dataset.XCOR.isel(MC=-2).values + dataset.XCOR.isel(MC=1).values
    dataset.XCOR[:,-1] = dataset.XCOR.isel(NC=-2).values

    dataset.YCOR[:,-1] = dataset.YCOR.isel(NC=-2).values  + dataset.YCOR.isel(NC=1).values
    dataset.YCOR[-1,:] = dataset.YCOR.isel(MC=-2).values
    
    return dataset

def makeMeshGrid(length=45000, width=18000, x_gridstep=300, y_gridstep=300):
    '''
    Make a uniform meshgrid using given parameters
    TODO
    ----
    * Non-uniform meshgrids?
    * These default arguments only make sense for my current model
    '''
        
    first_x_center = int(x_gridstep/2)
    xList = [0] + [i for i in range(first_x_center, int(width) + 1 * int(x_gridstep), int(x_gridstep))] # prepend a zero

    first_y_center = int(100 - y_gridstep/2) # grid always starts at 100
    yList = [i for i in range(first_y_center, int(length) + 1 * int(y_gridstep), int(y_gridstep))] 

    xDim, yDim = [len(xList), len(yList)]
    print(xDim, "x", yDim, "grid")
 
    XZ, YZ = np.meshgrid(xList, yList) 
    
    return XZ.T, YZ.T # Why transpose again tho?

def fixMeshGrid(dataset, mystery_flag=False):
    '''
    Derives gridsteps and dimensions from passed DataSet
    Assumes uniform grid, curvilinear grid wont work here!
    Reference to XZ and YZ need to be passed explicitly because Dask loads the netCDF lazily
    
    
    Parameters
    ----------
    dataset : xarray DataSet
        The delft3d-flow dataset
    mystery_flag : bool
        The mystery flag is a Boolean because sometimes 1 and sometimes 2 gridsteps need to be subtracted
        from the length ¯\_(ツ)_/¯ , don't really know why (off-by-one? even vs uneven?)
        Maybe this is not necessary if masks are applied properly
        
    Returns
    -------
    dataset : xarray DataSet
        The delft3d-flow dataset with fixed grid
    '''
    print("● Fixing mesh grid, assuming a uniform grid ")
    dataset.XZ.load()
    dataset.YZ.load()    
    
    x_gridstep = dataset.XZ.values[2][-1] - dataset.XZ.values[1][-1]
    y_gridstep = dataset.YZ.values[-2][-1] - dataset.YZ.values[-2][-2]
    
    width = (dataset.XZ.shape[0]-2) * x_gridstep
    
    if mystery_flag:
        length = (dataset.XZ.shape[1] - 1) * y_gridstep # eeehhh hmmmm -1? sometimes -2?
    else: 
        length = (dataset.XZ.shape[1] - 2) * y_gridstep # eeehhh hmmmm -1? sometimes -2?        
    
    md(f"""
    # Times
    | Name | Value |
    | --- | --- |
    | x gridstep | {x_gridstep} |
    | y gridstep | {y_gridstep} |
    | Width | {width} |
    | Length | {length} |
    
    """)    
    
    XZ, YZ = makeMeshGrid(length=length, width=width, x_gridstep=x_gridstep, y_gridstep=y_gridstep)

    dataset.XZ.values = XZ
    dataset.YZ.values = YZ
    
    return dataset