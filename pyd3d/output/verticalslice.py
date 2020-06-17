'''
* Could't I add depth coords to every data_var there with .map? 
* Things blew up when there are many multi-dimensional coords I think? eg depth, depth_center, N_KMAXOUT_RESTR, M_KMAXOUT_RESTR, N_KMAXOUT, M_KMAXOUT
* Think holoviews gets confused about which coords to take when there are 6 different multi-dimensional options
* How to add multiple kwargs that do the kinda the same thing? ie along_length along_width
'''

from .processNetCDF import addDepth  

def makeVerticalSlice(dataset, keyword, along_length=True, along_width=False, M=0, N=0):
    '''
    At cell centers!
    Returns DataArray that has extra coords meshgrid for convenient vertical plotting
    By default along length, set to along_length=False to get section along width
    TODO: proper time-dependant vertical meshgrid
    TODO: selecting the 0th index of YZ or XZ only works if the grid is uniform rectilinear
    '''
    if keyword not in dataset:
        raise Exception(f"Can't find {keyword} in DataSet")
    if not 'depth_center' in dataset or not 'depth' in dataset:
        print("Adding depths to DataSet...")
        dataset = addDepth(dataset)
    if along_width: # kinda ugly solution
        along_length = False
    if 'XCOR' in dataset[keyword].coords:
        print("This keyword is defined at cell interfaces, passing to makeVerticalSliceCOR function instead of this one")
        return makeVerticalSliceCOR(dataset, keyword, along_length=along_length, along_width=along_width, MC=M, NC=N)
        
    # check if this DataArray is really at centers
    if 'KMAXOUT_RESTR' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth_center=(
            ('time', 'M', 'N', 'KMAXOUT_RESTR'), dataset.depth_center.values)
        )

        if along_length:
            # make a mesh grid along length
            mesh_N_siglyr, _ = xr.broadcast(dataset.YZ[0], dataset.SIG_LYR)

            N_KMAXOUT_RESTR = xr.DataArray(mesh_N_siglyr, dims=['N', 'KMAXOUT_RESTR'], 
                                    coords={'N': dataset.N, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                    attrs={'units':'m', 'long_name': 'Y-SIG_LYR Meshgrid'})

            vertical_slice.coords["N_KMAXOUT_RESTR"] = N_KMAXOUT_RESTR   
        else: 
            mesh_M_siglyr, _ = xr.broadcast(dataset.XZ[:,0], dataset.SIG_LYR)

            M_KMAXOUT_RESTR = xr.DataArray(mesh_M_siglyr, dims=['M', 'KMAXOUT_RESTR'], 
                                        coords={'M': dataset.M, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                        attrs={'units':'m', 'long_name': 'X-SIG_LYR Meshgrid'})

            vertical_slice.coords["M_KMAXOUT_RESTR"] = M_KMAXOUT_RESTR   

    elif 'KMAXOUT' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth=(
            ('time', 'M', 'N', 'KMAXOUT'), dataset.depth.values)
        )

        if along_length:
            mesh_N_intf, _ = xr.broadcast(dataset.YZ[0], dataset.SIG_INTF)

            N_KMAXOUT = xr.DataArray(mesh_N_intf, dims=['N', 'KMAXOUT'], 
                                    coords={'N': dataset.N, 'KMAXOUT': dataset.KMAXOUT},
                                    attrs={'units':'m', 'long_name': 'Y-SIG_INTF Meshgrid'})

            vertical_slice.coords["N_KMAXOUT"] = N_KMAXOUT
        else:
            mesh_M_lyr, _ = xr.broadcast(dataset.XZ[:,0], dataset.SIG_INTF)

            M_KMAXOUT = xr.DataArray(mesh_N_lyr, dims=['M', 'KMAXOUT'], 
                                        coords={'M': dataset.M, 'KMAXOUT': dataset.KMAXOUT},
                                        attrs={'units':'m', 'long_name': 'X-SIG_INTF Meshgrid'})

            vertical_slice.coords["M_KMAXOUT"] = M_KMAXOUT
    else:
        raise Exception('This DataArray does not have the right dimensions (KMAXOUT or KMAXOUT_RESTR)')
    
    return vertical_slice

# Super ugly solution but ok
def makeVerticalSliceCOR(dataset, keyword, along_length=True, along_width=False, MC=0, NC=0):
    '''
    At cell interfaces! For vorticity and the turbulent quantities
    Returns DataArray that has extra coords meshgrid for convenient vertical plotting
    By default along length, set to along_length=False to get section along width
    TODO: proper time-dependent vertical meshgrid
    TODO: selecting the 0th index of YCOR or XCOR only works if the grid is uniform rectilinear
    '''
    if keyword not in dataset:
        raise Exception(f"Can't find {keyword} in DataSet")
    if not 'depth_center' in dataset or not 'depth' in dataset:
        print("Adding depths to DataSet...")
        dataset = addDepth(dataset)
    if along_width: # kinda ugly solution
        along_length = False
        
    # check if this DataArray is really at centers
    if 'KMAXOUT_RESTR' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth_center=(
            ('time', 'MC', 'NC', 'KMAXOUT_RESTR'), dataset.depth_center.values)
        )

        if along_length:
            # make a mesh grid along length
            mesh_NC_siglyr, _ = xr.broadcast(dataset.YCOR[0], dataset.SIG_LYR)

            NC_KMAXOUT_RESTR = xr.DataArray(mesh_NC_siglyr, dims=['NC', 'KMAXOUT_RESTR'], 
                                    coords={'NC': dataset.NC, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                    attrs={'units':'m', 'long_name': 'YCOR-SIG_LYR Meshgrid'})

            vertical_slice.coords["NC_KMAXOUT_RESTR"] = NC_KMAXOUT_RESTR   
        else: 
            mesh_MC_siglyr, _ = xr.broadcast(dataset.XCOR[:,0], dataset.SIG_LYR)

            MC_KMAXOUT_RESTR = xr.DataArray(mesh_MC_siglyr, dims=['MC', 'KMAXOUT_RESTR'], 
                                        coords={'MC': dataset.MC, 'KMAXOUT_RESTR': dataset.KMAXOUT_RESTR},
                                        attrs={'units': 'm', 'long_name': 'XCOR-SIG_LYR Meshgrid'})

            vertical_slice.coords["M_KMAXOUT_RESTR"] = M_KMAXOUT_RESTR   

    elif 'KMAXOUT' in dataset[keyword].dims:
        # add depth center coords
        vertical_slice = dataset[keyword].assign_coords(depth=(
            ('time', 'MC', 'NC', 'KMAXOUT'), dataset.depth.values)
        )

        if along_length:
            mesh_N_intf, _ = xr.broadcast(dataset.YCOR[0], dataset.SIG_INTF)

            NC_KMAXOUT = xr.DataArray(mesh_N_intf, dims=['NC', 'KMAXOUT'], 
                                    coords={'NC': dataset.NC, 'KMAXOUT': dataset.KMAXOUT},
                                    attrs={'units': 'm', 'long_name': 'YCOR-SIG_INTF Meshgrid'})

            vertical_slice.coords["NC_KMAXOUT"] = NC_KMAXOUT
        else:
            mesh_M_lyr, _ = xr.broadcast(dataset.XCOR[:,0], dataset.SIG_INTF)

            MC_KMAXOUT = xr.DataArray(mesh_N_lyr, dims=['M', 'KMAXOUT'], 
                                        coords={'M': dataset.MC, 'KMAXOUT': dataset.KMAXOUT},
                                        attrs={'units':'m', 'long_name': 'XCOR-SIG_INTF Meshgrid'})

            vertical_slice.coords["MC_KMAXOUT"] = MC_KMAXOUT
    else:
        raise Exception('This DataArray does not have the right dimensions (KMAXOUT or KMAXOUT_RESTR)')
    
    return vertical_slice